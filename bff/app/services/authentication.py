import logging
from abc import ABC, abstractmethod
from functools import lru_cache

import httpx
from authlib.integrations.requests_client import OAuth2Session
from authlib.integrations.starlette_client import OAuth
from fastapi import HTTPException, Request, status

from app.models.auth import UserTokens
from app.models.settings import Settings


class BaseAuthenticationService(ABC):
    @abstractmethod
    def setup(self):
        """Setup OAuth2 integration."""
        pass

    @abstractmethod
    async def login(self, request: Request):
        """Redirect user to the login page."""
        pass

    @abstractmethod
    async def send_otp(self, email: str):
        """Send OTP to the user's email."""
        pass

    @abstractmethod
    async def verify_otp(self, email: str, otp: str) -> UserTokens:
        """Verify the OTP for the user's email."""
        pass

    @abstractmethod
    async def callback(self, request: Request) -> UserTokens:
        """Handle the OAuth2 callback and return user information."""
        pass


class Auth0AuthenticationService(BaseAuthenticationService):
    def __init__(self):
        self.oauth = None

    def setup(self) -> None:
        if self.oauth is not None:
            return

        config = Settings()
        self.oauth = OAuth()
        self.oauth.register(
            "auth0",
            client_id=config.auth0_client_id,
            client_secret=config.auth0_client_secret,
            client_kwargs={
                "scope": "openid profile email offline_access",
            },
            server_metadata_url=f"https://{config.auth0_domain}/.well-known/openid-configuration",
        )

        logging.info("Auth0 OAuth client registered successfully.")

    async def login(self, request: Request):
        assert self.oauth is not None, "OAuth client is not initialized."
        config = Settings()
        return await self.oauth.auth0.authorize_redirect(
            request, config.auth0_callback_url, audience=config.auth0_audience
        )

    async def send_otp(self, email: str):
        """Send OTP to the user's email."""
        config = Settings()
        start_otp_url = f"https://{config.auth0_domain}/passwordless/start"
        params = {
            "client_id": config.auth0_client_id,
            "client_secret": config.auth0_client_secret,
            "connection": "email",
            "email": email,
            "send": "code",
        }
        try:
            with httpx.Client() as client:
                response = client.post(start_otp_url, json=params)
                response.raise_for_status()
                logging.info(f"OTP sent successfully to {email}.")
                return response.json()
        except Exception as e:
            logging.error(f"Error sending OTP: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to send OTP. Please try again later.",
            )

    async def verify_otp(self, email: str, otp: str) -> UserTokens:
        """Verify the OTP for the user's email."""
        config = Settings()
        verify_otp_url = f"https://{config.auth0_domain}/oauth/token"
        params = {
            "grant_type": "http://auth0.com/oauth/grant-type/passwordless/otp",
            "client_id": config.auth0_client_id,
            "client_secret": config.auth0_client_secret,
            "username": email,
            "otp": otp,
            "realm": "email",
            "audience": config.auth0_audience,
            "scope": "openid profile email offline_access",
        }
        try:
            with httpx.Client() as client:
                response = client.post(verify_otp_url, json=params)
                response.raise_for_status()
                auth0_tokens = response.json()
                user_tokens = UserTokens(
                    access_token=auth0_tokens.get("access_token"),
                    id_token=auth0_tokens.get("id_token"),
                    refresh_token=auth0_tokens.get("refresh_token"),
                )
                logging.info(f"OTP verified successfully for {email}.")
                return user_tokens
        except Exception as e:
            logging.error(f"Error verifying OTP: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or OTP. Please try again.",
            )

    async def callback(self, request: Request) -> UserTokens:
        assert self.oauth is not None, "OAuth client is not initialized."
        try:
            auth0_tokens = await self.oauth.auth0.authorize_access_token(request)
            user_tokens = UserTokens(
                access_token=auth0_tokens.get("access_token"),
                id_token=auth0_tokens.get("id_token"),
                refresh_token=auth0_tokens.get("refresh_token"),
            )
            return user_tokens
        except Exception as e:
            logging.error(f"Authentication error: {str(e)}", exc_info=True)
            raise

    async def refresh(self, refresh_token: str) -> str | None:
        assert self.oauth is not None, "OAuth client is not initialized."
        try:
            config = Settings()
            session = OAuth2Session(config.auth0_client_id, client_secret=config.auth0_client_secret)
            refresh_token_url = f"https://{config.auth0_domain}/oauth/token"
            token = session.refresh_token(
                refresh_token_url,
                refresh_token=refresh_token,
            )
            return token.get("access_token")
        except Exception as e:
            logging.error(f"Token refresh error: {str(e)}", exc_info=True)
            return None


@lru_cache()
def get_auth_service() -> BaseAuthenticationService:
    return Auth0AuthenticationService()

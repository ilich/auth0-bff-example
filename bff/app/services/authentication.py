import logging
from abc import ABC, abstractmethod
from functools import lru_cache

from authlib.integrations.requests_client import OAuth2Session
from authlib.integrations.starlette_client import OAuth
from fastapi import Request

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

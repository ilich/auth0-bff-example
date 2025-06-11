import logging
import secrets

import jwt
from fastapi import HTTPException, Request, Response

from app.core.cache import get_cache
from app.models.auth import UserTokens
from app.models.settings import Settings
from app.services.authentication import get_auth_service
from app.services.encryption import EncryptionService


class TokenManager:
    def __init__(self):
        self.cache = get_cache()
        config = Settings()
        self.crypto = EncryptionService(config.app_secret_key, config.app_secret_salt)
        self.config = config

    async def create_session_token(self, token: UserTokens, resposne: Response):
        if not token.access_token:
            raise ValueError("Access token is required to create a session token.")

        session_id = secrets.token_urlsafe(32)
        await self._update_user_id_and_exp_from_token(session_id, token.access_token)
        refresh_token_key = f"refresh_token:{session_id}"
        refresh_token = self.crypto.encrypt(token.refresh_token)
        await self.cache.set(refresh_token_key, refresh_token)
        secure_cookie = self.config.environment != "development"
        resposne.set_cookie(
            key="session_id",
            value=session_id,
            httponly=True,
            secure=secure_cookie,
            samesite="Lax",
        )

    async def refresh(self, request: Request):
        session_id = request.cookies.get("session_id")
        if not session_id:
            raise HTTPException(
                status_code=401,
                detail="Session ID cookie not found. Please log in again.",
            )

        refresh_token = await self._get_refresh_token(session_id)
        auth_client = get_auth_service()
        access_token = await auth_client.refresh(refresh_token)
        await self._update_user_id_and_exp_from_token(session_id, access_token)
        return access_token

    async def get_access_token(self, request: Request) -> str:
        session_id = request.cookies.get("session_id")
        if not session_id:
            raise HTTPException(
                status_code=401,
                detail="Session ID cookie not found. Please log in again.",
            )

        access_token_key = f"access_token:{session_id}"
        access_token = await self.cache.get(access_token_key)
        if access_token:
            access_token = self.crypto.decrypt(access_token)
            return access_token

        access_token = await self.refresh(request)
        return access_token

    async def get_user_id(self, request: Request) -> str:
        session_id = request.cookies.get("session_id")
        if not session_id:
            raise HTTPException(
                status_code=401,
                detail="Session ID cookie not found. Please log in again.",
            )

        user_id_key = f"user_id:{session_id}"
        user_id = await self.cache.get(user_id_key)
        if user_id:
            user_id = self.crypto.decrypt(user_id)
            return user_id

        await self.refresh(request)
        user_id = await self.cache.get(user_id_key)
        user_id = self.crypto.decrypt(user_id)
        return user_id

    async def _get_refresh_token(self, session_id: str) -> str:
        refresh_token_key = f"refresh_token:{session_id}"
        refresh_token = await self.cache.get(refresh_token_key)
        if not refresh_token:
            raise HTTPException(
                status_code=401,
                detail="Refresh token not found. Please log in again.",
            )
        return self.crypto.decrypt(refresh_token)

    async def _update_user_id_and_exp_from_token(self, session_id: str, access_token: str):
        try:
            decoded_token = jwt.decode(access_token, options={"verify_signature": False})
            user_id = decoded_token.get("sub")
            exp = decoded_token.get("exp")
            if not user_id or not exp:
                raise ValueError("Access token does not contain required fields.")

            user_id_key = f"user_id:{session_id}"
            user_id = self.crypto.encrypt(user_id)
            await self.cache.set(user_id_key, user_id, exat=exp)

            access_token_key = f"access_token:{session_id}"
            access_token = self.crypto.encrypt(access_token)
            await self.cache.set(access_token_key, access_token, exat=exp)
        except Exception as e:
            logging.error(f"Error updating user ID and expiration from token: {str(e)}")
            raise ValueError(f"Invalid access token: {str(e)}")

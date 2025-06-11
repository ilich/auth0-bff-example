import logging

import httpx
from authlib.jose import jwt
from fastapi import HTTPException, status

from app.models.auth import ApiUser
from app.models.settings import Settings


class AuthorizationService:
    async def get_claims(self, token: str) -> ApiUser:
        config = Settings()
        AUTH0_DOMAIN = config.auth0_domain
        API_AUDIENCE = config.auth0_audience

        jwks_url = f"https://{AUTH0_DOMAIN}/.well-known/jwks.json"
        async with httpx.AsyncClient() as client:
            response = await client.get(jwks_url)
            response.raise_for_status()
            jwks = response.json()

        try:
            claims = jwt.decode(
                token,
                jwks,
                claims_options={
                    "iss": {"essential": True, "values": [f"https://{AUTH0_DOMAIN}/"]},
                    "aud": {"essential": True, "values": [API_AUDIENCE]},
                    "exp": {"essential": True},
                },
            )
            claims.validate()
            logging.info(f"Decoded claims: {claims}")
            user_id = claims.get("sub")
            if not user_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token: missing user ID",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            permissions = set(claims.get("permissions", []))
            return ApiUser(id=user_id, permissions=permissions)
        except Exception as e:
            logging.error(f"Error decoding JWT: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )

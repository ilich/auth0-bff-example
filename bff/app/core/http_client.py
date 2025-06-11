import logging

import httpx
from fastapi import Request

from app.services.tokens import TokenManager


class SecureHttpClient(httpx.AsyncClient):
    def __init__(self, request: Request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.http_request = request
        self.token_manager = TokenManager()

    async def send(self, request: httpx.Request, **kwargs):
        logging.info(f"[SecureHttpClient] Sending: {request.method} {request.url}")
        access_token = await self.token_manager.get_access_token(self.http_request)
        if access_token:
            request.headers["Authorization"] = f"Bearer {access_token}"
        response = await super().send(request, **kwargs)
        if response.status_code == httpx.codes.UNAUTHORIZED or response.status_code == httpx.codes.FORBIDDEN:
            logging.warning("Access token expired or invalid, refreshing token.")
            await self.token_manager.refresh(self.http_request)
            access_token = await self.token_manager.get_access_token(self.http_request)
            if access_token:
                request.headers["Authorization"] = f"Bearer {access_token}"
                response = await super().send(request, **kwargs)
            else:
                logging.error("Failed to refresh access token.")
                raise httpx.HTTPStatusError("Unauthorized", request=request, response=response)
        logging.info(f"[SecureHttpClient] Got: {response.status_code}")
        return response

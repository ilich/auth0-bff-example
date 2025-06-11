from abc import ABC, abstractmethod

from fastapi import Request

from app.core.http_client import SecureHttpClient
from app.models.settings import Settings
from app.services.tokens import TokenManager


class BaseBackendService(ABC):
    @abstractmethod
    async def get_products(self):
        """Fetch products from the API."""
        pass

    @abstractmethod
    async def get_current_user(self):
        """Fetch user profile from the API."""
        pass


class SampleBackendService(BaseBackendService):
    def __init__(self, request: Request):
        config = Settings()
        self.base_url = config.backend_url.strip("/")
        self.request = request
        self.token_manager = TokenManager()

    async def get_products(self):
        async with SecureHttpClient(self.request) as client:
            endpoint = f"{self.base_url}/catalog"
            response = await client.get(endpoint, follow_redirects=True)
            response.raise_for_status()
            return response.json()

    async def get_current_user(self):
        async with SecureHttpClient(self.request) as client:
            user_id = await self.token_manager.get_user_id(self.request)
            endpoint = f"{self.base_url}/users/{user_id}"
            response = await client.get(endpoint, follow_redirects=True)
            response.raise_for_status()
            return response.json()


def get_backend_service(request: Request) -> BaseBackendService:
    return SampleBackendService(request)

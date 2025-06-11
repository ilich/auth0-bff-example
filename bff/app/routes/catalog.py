from fastapi import APIRouter, Depends

from app.services.backend import BaseBackendService, get_backend_service

router = APIRouter()


@router.get("/")
async def get_products(backend: BaseBackendService = Depends(get_backend_service)):
    return await backend.get_products()

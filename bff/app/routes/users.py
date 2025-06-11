from fastapi import APIRouter, Depends

from app.services.backend import BaseBackendService, get_backend_service

router = APIRouter()


@router.get("/me")
async def get_current_user(backend: BaseBackendService = Depends(get_backend_service)):
    return await backend.get_current_user()

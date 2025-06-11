from fastapi import APIRouter, Depends

from app.core.jwt_bearer import require_permissions
from app.models.auth import ApiUser
from app.models.user import User
from app.services.user import UserService

router = APIRouter()


@router.get("/{id}")
def get_user_by_id(id: str, user: ApiUser = Depends(require_permissions({"read:user"}))) -> User:
    service = UserService()
    return service.get_user_by_id(id)

from fastapi import APIRouter
from app.models.user import User
from app.services.user import UserService

router = APIRouter()


@router.get("/{id:int}")
def get_user_by_id(id: int) -> User:
    service = UserService()
    return service.get_user_by_id(id)

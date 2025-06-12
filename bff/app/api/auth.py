from fastapi import APIRouter

router = APIRouter()


@router.get("/callback")
def get_user_by_id():
    return {
        "id": 123,
    }

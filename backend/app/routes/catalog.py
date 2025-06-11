from fastapi import APIRouter, Depends

from app.core.jwt_bearer import require_permissions
from app.models.auth import ApiUser
from app.models.catalog import Product
from app.services.catalog import CatalogService

router = APIRouter()


@router.get("/")
def get_products(user: ApiUser = Depends(require_permissions({"read:products"}))) -> list[Product]:
    service = CatalogService()
    return service.get_catalog()

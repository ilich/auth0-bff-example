from fastapi import APIRouter
from app.models.catalog import Product
from app.services.catalog import CatalogService

router = APIRouter()


@router.get("/")
def get_products() -> list[Product]:
    service = CatalogService()
    return service.get_catalog()

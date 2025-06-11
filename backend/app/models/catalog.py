from pydantic import BaseModel, Field


class Product(BaseModel):
    id: int = Field(..., description="Unique identifier for the product")
    name: str = Field(..., description="Name of the product")
    description: str = Field(..., description="Description of the product")
    price: float = Field(..., description="Price of the product")
    stock: int = Field(..., description="Available stock for the product")

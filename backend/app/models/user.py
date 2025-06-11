from pydantic import BaseModel, EmailStr, Field


class User(BaseModel):
    id: str = Field(..., description="Unique identifier for the user")
    username: str = Field(..., min_length=3, max_length=50, description="Username of the user")
    email: EmailStr = Field(..., description="Email address of the user")
    full_name: str | None = Field(None, max_length=100, description="Full name of the user")

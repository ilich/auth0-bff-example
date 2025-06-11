from pydantic import BaseModel, Field


class ApiUser(BaseModel):
    id: str
    permissions: set[str] = Field(default_factory=set)

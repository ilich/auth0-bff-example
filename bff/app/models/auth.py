from pydantic import BaseModel


class UserTokens(BaseModel):
    access_token: str | None
    id_token: str | None
    refresh_token: str | None = None


class StatusResponse(BaseModel):
    is_authenticated: bool

from pydantic import BaseModel


class UserTokens(BaseModel):
    access_token: str | None
    id_token: str | None
    refresh_token: str | None = None


class AuthStatusResponse(BaseModel):
    is_authenticated: bool


class SendOtpRequest(BaseModel):
    email: str


class VerifyOtpRequest(BaseModel):
    email: str
    otp: str


class OtpResponse(BaseModel):
    message: str
    success: bool

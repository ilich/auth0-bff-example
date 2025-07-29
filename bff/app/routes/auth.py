import logging

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import RedirectResponse, Response

from app.core.security import get_current_user
from app.models.auth import AuthStatusResponse, OtpResponse, SendOtpRequest, VerifyOtpRequest
from app.services.authentication import BaseAuthenticationService, get_auth_service
from app.services.tokens import TokenManager

router = APIRouter()


@router.get("/login/oauth")
async def login(
    request: Request,
    return_url: str = Query(...),
    auth_service: BaseAuthenticationService = Depends(get_auth_service),
):
    request.session["return_url"] = return_url
    return await auth_service.login(request)


@router.post("/login/otp/send")
async def send_otp(
    otp_request: SendOtpRequest,
    auth_service: BaseAuthenticationService = Depends(get_auth_service),
) -> OtpResponse:
    response = await auth_service.send_otp(otp_request.email)
    logging.info(f"OTP sent to {otp_request.email}. Response: {response}")
    return OtpResponse(message="OTP sent successfully.", success=True)


@router.post("/login/otp/verify")
async def verify_otp(
    response: Response,
    otp_request: VerifyOtpRequest,
    auth_service: BaseAuthenticationService = Depends(get_auth_service),
) -> OtpResponse:
    user_token = await auth_service.verify_otp(otp_request.email, otp_request.otp)
    token_manager = TokenManager()
    print(user_token)
    await token_manager.create_session_token(user_token, response)
    model = OtpResponse(
        message="OTP verified successfully. You are now logged in.",
        success=True,
    )
    logging.info(f"OTP verified for {otp_request.email}. Session created.")
    return model


@router.get("/callback")
async def authenticate_user(
    request: Request,
    auth_service: BaseAuthenticationService = Depends(get_auth_service),
):
    try:
        return_url = request.session.get("return_url", "/")
        if "return_url" in request.session:
            del request.session["return_url"]

        user_token = await auth_service.callback(request)
        token_manager = TokenManager()
        response = RedirectResponse(url=return_url, status_code=status.HTTP_302_FOUND)
        await token_manager.create_session_token(user_token, response)
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"An error occurred during authentication: {str(e)}",
        )


@router.post("/status")
async def is_authenticated(request: Request, user_id: str = Depends(get_current_user)) -> AuthStatusResponse:
    user_id = await get_current_user(request)
    return AuthStatusResponse(
        is_authenticated=user_id is not None,
    )

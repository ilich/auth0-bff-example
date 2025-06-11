from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import RedirectResponse

from app.services.authentication import BaseAuthenticationService, get_auth_service
from app.services.tokens import TokenManager

router = APIRouter()


@router.get("/login")
async def login(
    request: Request,
    return_url: str = Query(...),
    auth_service: BaseAuthenticationService = Depends(get_auth_service),
):
    request.session["return_url"] = return_url
    return await auth_service.login(request)


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

import logging

from fastapi import HTTPException, Request

from app.services.tokens import TokenManager


async def get_current_user(request: Request) -> str:
    try:
        token_manager = TokenManager()
        user_id = await token_manager.get_user_id(request)
        if not user_id:
            raise HTTPException(
                status_code=401,
                detail="User is not authenticated. Please log in.",
            )

        return user_id
    except HTTPException as http_exc:
        logging.error(f"Authentication error: {http_exc.detail}")
        raise
    except Exception as e:
        logging.error(f"Error: {str(e)}")
        raise HTTPException(
            status_code=401,
            detail=f"Authentication failed: {str(e)}",
        )

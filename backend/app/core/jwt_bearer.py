import logging

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.models.auth import ApiUser
from app.services.auth import AuthorizationService

bearer_scheme = HTTPBearer()


async def get_current_user(token: HTTPAuthorizationCredentials = Depends(bearer_scheme)) -> ApiUser:
    try:
        service = AuthorizationService()
        user = await service.get_claims(token.credentials)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        logging.info(f"Authenticated user: {user.id} with permissions: {user.permissions}")
        return user
    except Exception as e:
        logging.error(f"Error in get_current_user: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )


def require_permissions(permissions: set[str]):
    async def permission_dependency(token: HTTPAuthorizationCredentials = Depends(bearer_scheme)) -> ApiUser:
        try:
            service = AuthorizationService()
            user = await service.get_claims(token.credentials)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            if not user.permissions.issuperset(permissions):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            logging.info(f"User {user.id} has required permissions: {permissions}")
            return user
        except Exception as e:
            logging.error(f"Error in require_permissions: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )

    return permission_dependency

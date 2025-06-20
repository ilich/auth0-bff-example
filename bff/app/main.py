import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from app.models.settings import Settings
from app.routes import auth, catalog, users
from app.services.authentication import get_auth_service

logging.basicConfig(level=logging.INFO)
app = FastAPI()

# Initialize settings and middleware
config = Settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.cors_allow_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(SessionMiddleware, secret_key=config.app_secret_key)
auth_service = get_auth_service()
auth_service.setup()

# Include routes
app.include_router(auth.router, prefix="/auth", tags=["authentication"])
app.include_router(catalog.router, prefix="/catalog", tags=["catalog"])
app.include_router(users.router, prefix="/users", tags=["users"])

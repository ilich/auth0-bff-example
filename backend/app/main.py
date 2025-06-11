import logging

from fastapi import FastAPI

from app.routes import catalog, users

logging.basicConfig(level=logging.INFO)
app = FastAPI()
app.include_router(catalog.router, prefix="/catalog", tags=["catalog"])
app.include_router(users.router, prefix="/users", tags=["users"])

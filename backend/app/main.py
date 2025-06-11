from fastapi import FastAPI
from app.api import catalog, user

app = FastAPI()
app.include_router(catalog.router, prefix="/catalog", tags=["catalog"])
app.include_router(user.router, prefix="/users", tags=["users"])

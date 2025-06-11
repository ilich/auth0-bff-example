from fastapi import FastAPI
from app.api import catalog

app = FastAPI()
app.add_route(catalog, prefix="/catalog", tags=["Product catalog"])
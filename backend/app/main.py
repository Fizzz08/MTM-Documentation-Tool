from fastapi import FastAPI
from app.api import mtm_routes

app = FastAPI(title="MTM CRUD API")

app.include_router(mtm_routes.router)

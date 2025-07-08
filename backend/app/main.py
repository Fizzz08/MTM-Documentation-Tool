from fastapi import FastAPI
from api import mtm_routes
from api import messaging_routes

app = FastAPI()
app.include_router(mtm_routes.router)
app.include_router(messaging_routes.router)


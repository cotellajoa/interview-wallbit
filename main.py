from fastapi import FastAPI

from api import exchange_routes

app = FastAPI()

app.include_router(exchange_routes.route)

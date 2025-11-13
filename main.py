from fastapi import FastAPI

from routes import exchange

app = FastAPI()

app.include_router(exchange.route)

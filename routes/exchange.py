from fastapi import APIRouter, HTTPException
import httpx
import asyncio

from services.service import dolar_blue, dolar_bolsa, dolar_contado_con_liqui, dolar_cripto, dolar_mayorista, dolar_oficial, dolar_tarjeta, todos_los_dolares

route = APIRouter(prefix="/api/exchange", tags=["exchange"])

@route.get("/")
async def get_dolar():
    res = await todos_los_dolares()
    return res
    
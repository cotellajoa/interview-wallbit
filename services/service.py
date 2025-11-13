from fastapi import HTTPException
import httpx
import asyncio
import json

DOLAR_API = "https://dolarapi.com/v1/"
async def dolar_oficial():
    DOLAR_API_URL = "https://dolarapi.com/v1/dolares/oficial"
    async with httpx.AsyncClient() as client:
        try: 
            response = await client.get(DOLAR_API_URL)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as exc:
            raise HTTPException(status_code=exc.response.status_code, detail='Error al consultar dolar oficial')

async def dolar_blue():
    DOLAR_API_URL = "https://dolarapi.com/v1/dolares/blue"
    async with httpx.AsyncClient() as client:
        try: 
            response = await client.get(DOLAR_API_URL)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as exc:
            raise HTTPException(status_code=exc.response.status_code, detail='Error al consultar dolar blue')

async def dolar_bolsa():
    DOLAR_API_URL = "https://dolarapi.com/v1/dolares/bolsa"
    async with httpx.AsyncClient() as client:
        try: 
            response = await client.get(DOLAR_API_URL)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as exc:
            raise HTTPException(status_code=exc.response.status_code, detail='Error al consultar dolar bolsa')

async def dolar_contado_con_liqui():
    DOLAR_API_URL = "https://dolarapi.com/v1/dolares/contadoconliqui"
    async with httpx.AsyncClient() as client:
        try: 
            response = await client.get(DOLAR_API_URL)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as exc:
            raise HTTPException(status_code=exc.response.status_code, detail='Error al consultar dolar contado con liqui')

async def dolar_tarjeta():
    DOLAR_API_URL = "https://dolarapi.com/v1/dolares/tarjeta"
    async with httpx.AsyncClient() as client:
        try: 
            response = await client.get(DOLAR_API_URL)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as exc:
            raise HTTPException(status_code=exc.response.status_code, detail='Error al consultar dolar tarjeta')

async def dolar_cripto():
    DOLAR_API_URL = "https://dolarapi.com/v1/dolares/cripto"
    async with httpx.AsyncClient() as client:
        try: 
            response = await client.get(DOLAR_API_URL)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as exc:
            raise HTTPException(status_code=exc.response.status_code, detail='Error al consultar dolar cripto')

async def dolar_mayorista():
    DOLAR_API_URL = "https://dolarapi.com/v1/dolares/mayorista"
    async with httpx.AsyncClient() as client:
        try: 
            response = await client.get(DOLAR_API_URL)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as exc:
            raise HTTPException(status_code=exc.response.status_code, detail='Error al consultar dolar mayorista')

async def todos_los_dolares():
    rates = []
    avg = 0
    res1 = await dolar_blue()
    res2 = await dolar_bolsa()
    res3 = await dolar_contado_con_liqui()
    res4 = await dolar_oficial()
    res5 = await dolar_cripto()
    res6 = await dolar_tarjeta()
    res7 = await dolar_mayorista()
    for i in range(7):
        aux = "res" + str(i+1)
        rates.append(aux)
    
    response = {
        "rates": rates,
        "average": avg
    }

    return json.dumps(response)



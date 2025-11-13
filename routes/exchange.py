from fastapi import APIRouter

from infrastructure.adapters.dolar_api_adapter import DolarApiAdapter

route = APIRouter(prefix="/api/exchange", tags=["exchange"])

dolar_adapter = DolarApiAdapter()


@route.get("/")
async def get_exchange_rates():
    result = await dolar_adapter.get_all_exchange_rates()
    return result
    
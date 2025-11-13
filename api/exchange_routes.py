from fastapi import APIRouter

from services.exchange_rate_service import ExchangeRateService
from repositories.exchange_rate_repository import ExchangeRateRepository
from external.dolar_api_client import DolarApiClient

route = APIRouter(prefix="/api/exchange", tags=["exchange"])

# Inyección de dependencias en cascada
api_client = DolarApiClient()
repository = ExchangeRateRepository(api_client)
service = ExchangeRateService(repository)


@route.get("/")
async def get_exchange_rates():
    result = await service.get_all_rates_with_average()
    return result

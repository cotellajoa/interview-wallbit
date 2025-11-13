from fastapi import APIRouter, Depends
from sqlmodel import Session

from services.exchange_rate_service import ExchangeRateService
from repositories.exchange_rate_repository import ExchangeRateRepository
from external.dolar_api_client import DolarApiClient
from database.connection import get_session

route = APIRouter(prefix="/api/exchange", tags=["exchange"])

# Inyección de dependencias
api_client = DolarApiClient()
api_repository = ExchangeRateRepository(api_client)
service = ExchangeRateService(api_repository)


@route.get("/")
async def get_exchange_rates(session: Session = Depends(get_session)):
    result = await service.get_all_rates_with_average(session=session, persist=True)
    return result

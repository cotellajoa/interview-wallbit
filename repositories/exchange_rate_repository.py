from typing import List
from models.exchange_rate import ExchangeRate
from external.dolar_api_client import DolarApiClient


class ExchangeRateRepository:
    def __init__(self, api_client: DolarApiClient):
        self.api_client = api_client
    
    async def get_all_rates(self) -> List[ExchangeRate]:
        raw_data = await self.api_client.fetch_all_exchange_rates()
        
        exchange_rates = []
        for item in raw_data:
            exchange_rate = ExchangeRate(
                nombre=item.get("nombre", ""),
                compra=item.get("compra", 0.0),
                venta=item.get("venta", 0.0),
                fechaActualizacion=item.get("fechaActualizacion", "")
            )
            exchange_rates.append(exchange_rate)
        
        return exchange_rates

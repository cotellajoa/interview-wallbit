from typing import List
from models.exchange_rate import ExchangeRate
from external.dolar_api_client import DolarApiClient


class ExchangeRateRepository:
    """Capa de repositorio - Transforma datos de la API externa a modelos de dominio"""
    
    def __init__(self, api_client: DolarApiClient):
        self.api_client = api_client
    
    async def get_all_rates(self) -> List[ExchangeRate]:
        """
        Obtiene todas las tasas de cambio y las convierte a modelos de dominio
        """
        # Obtener datos raw de la API externa
        raw_data = await self.api_client.fetch_all_exchange_rates()
        
        # Transformar a modelos de dominio
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

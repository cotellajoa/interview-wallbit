import httpx
from fastapi import HTTPException

from domain.models.exchange_rate import ExchangeRate, ExchangeRateResponse, ExchangeRateAverage


class DolarApiAdapter:
    def __init__(self, base_url: str = "https://dolarapi.com/v1"):
        self.base_url = base_url
    
    async def get_all_exchange_rates(self) -> ExchangeRateResponse:
        url = f"{self.base_url}/dolares"
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url)
                response.raise_for_status()
                data = response.json()
                
                exchange_rates = []
                total_compra = 0.0
                total_venta = 0.0
                
                for item in data:
                    exchange_rate = ExchangeRate(
                        nombre=item.get("nombre", ""),
                        compra=item.get("compra", 0.0),
                        venta=item.get("venta", 0.0),
                        fechaActualizacion=item.get("fechaActualizacion", "")
                    )
                    exchange_rates.append(exchange_rate)
                    total_compra += exchange_rate.compra
                    total_venta += exchange_rate.venta
                
                # Calcular promedio
                count = len(exchange_rates)
                average = ExchangeRateAverage(
                    compra=round(total_compra / count, 2) if count > 0 else 0.0,
                    venta=round(total_venta / count, 2) if count > 0 else 0.0
                )
                
                return ExchangeRateResponse(rates=exchange_rates, average=average)
                
            except httpx.HTTPStatusError as exc:
                raise HTTPException(
                    status_code=exc.response.status_code,
                    detail=f'Error al consultar las tasas de cambio: {exc.response.text}'
                )
            except Exception as exc:
                raise HTTPException(
                    status_code=500,
                    detail=f'Error inesperado: {str(exc)}'
                )

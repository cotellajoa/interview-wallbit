from models.exchange_rate import ExchangeRateResponse, ExchangeRateAverage
from repositories.exchange_rate_repository import ExchangeRateRepository


class ExchangeRateService:
    
    def __init__(self, repository: ExchangeRateRepository):
        self.repository = repository
    
    async def get_all_rates_with_average(self) -> ExchangeRateResponse:
        rates = await self.repository.get_all_rates()
        
        if not rates:
            average = ExchangeRateAverage(compra=0.0, venta=0.0)
        else:
            total_compra = sum(rate.compra for rate in rates)
            total_venta = sum(rate.venta for rate in rates)
            count = len(rates)
            
            average = ExchangeRateAverage(
                compra=round(total_compra / count, 2),
                venta=round(total_venta / count, 2)
            )
        
        return ExchangeRateResponse(rates=rates, average=average)

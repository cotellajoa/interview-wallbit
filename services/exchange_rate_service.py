from models.exchange_rate import ExchangeRateResponse, ExchangeRateAverage
from repositories.exchange_rate_repository import ExchangeRateRepository
from repositories.exchange_db_repository import ExchangeDBRepository
from sqlmodel import Session
from typing import Optional


class ExchangeRateService:    
    def __init__(
        self, 
        api_repository: ExchangeRateRepository,
        db_repository: Optional[ExchangeDBRepository] = None
    ):
        self.api_repository = api_repository
        self.db_repository = db_repository or ExchangeDBRepository()
    
    async def get_all_rates_with_average(
        self, 
        session: Optional[Session] = None,
        persist: bool = True
    ) -> ExchangeRateResponse:
        rates = await self.api_repository.get_all_rates()
        
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
        
        if persist and session is not None:
            self._persist_rates(rates, average, session)
        
        return ExchangeRateResponse(rates=rates, average=average)
    
    def _persist_rates(
        self, 
        rates: list, 
        average: ExchangeRateAverage, 
        session: Session
    ) -> None:
        avg_price = (average.compra + average.venta) / 2
        
        for rate in rates:
            current_price = (rate.compra + rate.venta) / 2
            normalized_rate = round(current_price / avg_price, 4) if avg_price > 0 else 0.0
            diff = round(current_price - avg_price, 2)

            self.db_repository.update_or_create_rate(
                type=rate.nombre.lower().replace(" ", "_"),
                buy=rate.compra,
                sell=rate.venta,
                rate=normalized_rate,
                diff=diff,
                session=session
            )

from sqlmodel import Session, select
from database.models import ExchangeRateDB
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional, List


class ExchangeDBRepository:    
    def update_or_create_rate(
        self,
        type: str,
        buy: float,
        sell: float,
        rate: float,
        diff: float,
        session: Session
    ) -> ExchangeRateDB:
        statement = select(ExchangeRateDB).where(ExchangeRateDB.type == type)
        existing_rate = session.exec(statement).first()
        
        if existing_rate:
            existing_rate.buy = Decimal(str(buy))
            existing_rate.sell = Decimal(str(sell))
            existing_rate.rate = Decimal(str(rate))
            existing_rate.diff = Decimal(str(diff))
            existing_rate.updated_at = datetime.now(timezone.utc)
            
            session.add(existing_rate)
            session.commit()
            session.refresh(existing_rate)
            
            return existing_rate
        else:
            new_rate = ExchangeRateDB(
                type=type,
                buy=Decimal(str(buy)),
                sell=Decimal(str(sell)),
                rate=Decimal(str(rate)),
                diff=Decimal(str(diff)),
                updated_at=datetime.now(timezone.utc)
            )
            
            session.add(new_rate)
            session.commit()
            session.refresh(new_rate)
            
            return new_rate
    
    def get_all_rates(self, session: Session) -> List[ExchangeRateDB]:
        statement = select(ExchangeRateDB)
        results = session.exec(statement).all()
        return list(results)
    
    def get_rate_by_type(self, type: str, session: Session) -> Optional[ExchangeRateDB]:
        statement = select(ExchangeRateDB).where(ExchangeRateDB.type == type)
        return session.exec(statement).first()

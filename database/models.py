from sqlmodel import SQLModel, Field
from datetime import datetime, timezone
from typing import Optional, ClassVar
from decimal import Decimal


class ExchangeRateDB(SQLModel, table=True):
    __tablename__: ClassVar[str] = "exchange_rates"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    type: str = Field(index=True, unique=True, max_length=50) 
    buy: Decimal = Field(default=Decimal("0.0"), max_digits=10, decimal_places=2)
    sell: Decimal = Field(default=Decimal("0.0"), max_digits=10, decimal_places=2)
    rate: Decimal = Field(default=Decimal("0.0"), max_digits=10, decimal_places=2)  
    diff: Decimal = Field(default=Decimal("0.0"), max_digits=10, decimal_places=2) 
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    class Config:
        json_encoders = {
            Decimal: float,
            datetime: lambda v: v.isoformat()
        }

from pydantic import BaseModel


class ExchangeRate(BaseModel):
    nombre: str
    compra: float
    venta: float
    fechaActualizacion: str


class ExchangeRateAverage(BaseModel):
    compra: float
    venta: float


class ExchangeRateResponse(BaseModel):
    rates: list[ExchangeRate]
    average: ExchangeRateAverage

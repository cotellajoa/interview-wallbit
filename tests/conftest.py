"""
Configuración de pytest y fixtures compartidos.
"""
import pytest
import asyncio
from sqlmodel import SQLModel, create_engine, Session
from typing import Generator

# Motor de base de datos en memoria para tests
TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="function")
def test_engine():
    """
    Crea un engine de SQLite en memoria para cada test.
    Se limpia después de cada test.
    """
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
    SQLModel.metadata.create_all(engine)
    yield engine
    SQLModel.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture(scope="function")
def test_session(test_engine) -> Generator[Session, None, None]:
    """
    Proporciona una sesión de base de datos para tests.
    """
    with Session(test_engine) as session:
        yield session


@pytest.fixture(scope="session")
def event_loop():
    """
    Crea un event loop para tests asíncronos.
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def sample_exchange_data():
    """
    Datos de ejemplo de la API de DolarAPI.
    """
    return [
        {
            "nombre": "Oficial",
            "compra": 950.0,
            "venta": 990.0,
            "fechaActualizacion": "2025-11-13T10:00:00.000Z"
        },
        {
            "nombre": "Blue",
            "compra": 1100.0,
            "venta": 1120.0,
            "fechaActualizacion": "2025-11-13T10:00:00.000Z"
        },
        {
            "nombre": "Bolsa",
            "compra": 1050.0,
            "venta": 1070.0,
            "fechaActualizacion": "2025-11-13T10:00:00.000Z"
        }
    ]

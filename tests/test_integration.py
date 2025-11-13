"""
Tests de integración end-to-end.
"""
import pytest
from sqlmodel import Session, select
from unittest.mock import AsyncMock, Mock, patch

from database.models import ExchangeRateDB
from services.exchange_rate_service import ExchangeRateService
from repositories.exchange_rate_repository import ExchangeRateRepository
from repositories.exchange_db_repository import ExchangeDBRepository
from external.dolar_api_client import DolarApiClient


class TestIntegration:
    """Tests de integración completos"""
    
    @pytest.mark.asyncio
    async def test_full_flow_api_to_database(self, test_session, sample_exchange_data):
        """Test: Flujo completo desde API externa hasta base de datos"""
        # Arrange
        with patch("external.dolar_api_client.httpx.AsyncClient") as mock_client_class:
            # Mock de la respuesta HTTP (json() es síncrono)
            mock_response = Mock()
            mock_response.json = Mock(return_value=sample_exchange_data)
            mock_response.raise_for_status = Mock()
            
            mock_client = AsyncMock()
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            
            mock_client_class.return_value = mock_client
            
            # Crear dependencias reales
            api_client = DolarApiClient()
            api_repository = ExchangeRateRepository(api_client)
            db_repository = ExchangeDBRepository()
            service = ExchangeRateService(
                api_repository=api_repository,
                db_repository=db_repository
            )
            
            # Act: Ejecutar flujo completo
            result = await service.get_all_rates_with_average(
                session=test_session,
                persist=True
            )
            
            # Assert: Verificar resultado
            assert len(result.rates) == 3
            assert result.average.compra == 1033.33
            assert result.average.venta == 1060.0
            
            # Verificar que se guardó en base de datos
            statement = select(ExchangeRateDB)
            db_rates = test_session.exec(statement).all()
            assert len(db_rates) == 3
            
            # Verificar que se calcularon normalizaciones
            blue_rate = test_session.exec(
                select(ExchangeRateDB).where(ExchangeRateDB.type == "blue")
            ).first()
            assert blue_rate is not None
            assert float(blue_rate.rate) > 0
            assert float(blue_rate.diff) != 0
    
    @pytest.mark.asyncio
    async def test_idempotency_across_multiple_calls(self, test_session, sample_exchange_data):
        """Test: Idempotencia en múltiples llamadas completas"""
        # Arrange
        with patch("external.dolar_api_client.httpx.AsyncClient") as mock_client_class:
            mock_response = Mock()
            mock_response.json = Mock(return_value=sample_exchange_data)
            mock_response.raise_for_status = Mock()
            
            mock_client = AsyncMock()
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            
            mock_client_class.return_value = mock_client
            
            api_client = DolarApiClient()
            api_repository = ExchangeRateRepository(api_client)
            db_repository = ExchangeDBRepository()
            service = ExchangeRateService(
                api_repository=api_repository,
                db_repository=db_repository
            )
            
            # Act: Ejecutar 5 veces
            for _ in range(5):
                await service.get_all_rates_with_average(
                    session=test_session,
                    persist=True
                )
            
            # Assert: Solo debe haber 3 registros (no duplicados)
            statement = select(ExchangeRateDB)
            db_rates = test_session.exec(statement).all()
            assert len(db_rates) == 3
            
            # Verificar que cada tipo existe una sola vez
            types = [rate.type for rate in db_rates]
            assert len(types) == len(set(types))  # No hay duplicados
    
    @pytest.mark.asyncio
    async def test_data_transformation_accuracy(self, test_session, sample_exchange_data):
        """Test: Precisión en transformación de datos"""
        # Arrange
        with patch("external.dolar_api_client.httpx.AsyncClient") as mock_client_class:
            mock_response = Mock()
            mock_response.json = Mock(return_value=sample_exchange_data)
            mock_response.raise_for_status = Mock()
            
            mock_client = AsyncMock()
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            
            mock_client_class.return_value = mock_client
            
            api_client = DolarApiClient()
            api_repository = ExchangeRateRepository(api_client)
            db_repository = ExchangeDBRepository()
            service = ExchangeRateService(
                api_repository=api_repository,
                db_repository=db_repository
            )
            
            # Act
            result = await service.get_all_rates_with_average(
                session=test_session,
                persist=True
            )
            
            # Assert: Verificar transformación de nombres
            oficial = test_session.exec(
                select(ExchangeRateDB).where(ExchangeRateDB.type == "oficial")
            ).first()
            assert oficial is not None
            assert float(oficial.buy) == 950.0
            assert float(oficial.sell) == 990.0
            
            blue = test_session.exec(
                select(ExchangeRateDB).where(ExchangeRateDB.type == "blue")
            ).first()
            assert blue is not None
            assert float(blue.buy) == 1100.0
            assert float(blue.sell) == 1120.0

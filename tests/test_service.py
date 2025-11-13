"""
Tests para el servicio de tasas de cambio.
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from sqlmodel import Session

from services.exchange_rate_service import ExchangeRateService
from repositories.exchange_rate_repository import ExchangeRateRepository
from repositories.exchange_db_repository import ExchangeDBRepository
from models.exchange_rate import ExchangeRate, ExchangeRateAverage


class TestExchangeRateService:
    """Tests para ExchangeRateService"""
    
    @pytest.mark.asyncio
    async def test_get_all_rates_with_average_no_persist(self, sample_exchange_data):
        """Test: Obtener tasas y calcular promedio sin persistir"""
        # Arrange
        mock_api_repo = Mock(spec=ExchangeRateRepository)
        mock_api_repo.get_all_rates = AsyncMock(return_value=[
            ExchangeRate(**data) for data in sample_exchange_data
        ])
        
        service = ExchangeRateService(api_repository=mock_api_repo)
        
        # Act
        result = await service.get_all_rates_with_average(persist=False)
        
        # Assert
        assert len(result.rates) == 3
        assert result.average.compra == 1033.33  # (950 + 1100 + 1050) / 3
        assert result.average.venta == 1060.0    # (990 + 1120 + 1070) / 3
        
        # Verificar que se llamó al repositorio API
        mock_api_repo.get_all_rates.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_all_rates_empty_list(self):
        """Test: Manejar lista vacía de tasas"""
        # Arrange
        mock_api_repo = Mock(spec=ExchangeRateRepository)
        mock_api_repo.get_all_rates = AsyncMock(return_value=[])
        
        service = ExchangeRateService(api_repository=mock_api_repo)
        
        # Act
        result = await service.get_all_rates_with_average(persist=False)
        
        # Assert
        assert len(result.rates) == 0
        assert result.average.compra == 0.0
        assert result.average.venta == 0.0
    
    @pytest.mark.asyncio
    async def test_persist_rates_calculates_normalization(self, test_session, sample_exchange_data):
        """Test: Verificar que se calculan rate y diff correctamente"""
        # Arrange
        mock_api_repo = Mock(spec=ExchangeRateRepository)
        mock_api_repo.get_all_rates = AsyncMock(return_value=[
            ExchangeRate(**data) for data in sample_exchange_data
        ])
        
        db_repo = ExchangeDBRepository()
        service = ExchangeRateService(
            api_repository=mock_api_repo,
            db_repository=db_repo
        )
        
        # Act
        result = await service.get_all_rates_with_average(
            session=test_session,
            persist=True
        )
        
        # Assert
        # Verificar que se guardaron los datos
        saved_rates = db_repo.get_all_rates(test_session)
        assert len(saved_rates) == 3
        
        # Verificar cálculos de normalización
        # Promedio: compra=1033.33, venta=1060.0 → avg_price=1046.67
        oficial_rate = db_repo.get_rate_by_type("oficial", test_session)
        assert oficial_rate is not None
        # Ensure rate is calculated and not 0.0, and handle potential None for rate
        assert oficial_rate.rate is not None and float(oficial_rate.rate) > 0
        
        # Blue debería tener rate > 1 (está por encima del promedio)
        blue_rate = db_repo.get_rate_by_type("blue", test_session)
        assert blue_rate is not None
        assert float(blue_rate.rate) > 1.0
        
        # Oficial debería tener rate < 1 (está por debajo del promedio)
        assert float(oficial_rate.rate) < 1.0
    
    @pytest.mark.asyncio
    async def test_persist_rates_idempotency(self, test_session, sample_exchange_data):
        """Test: Múltiples llamadas no duplican datos"""
        # Arrange
        mock_api_repo = Mock(spec=ExchangeRateRepository)
        mock_api_repo.get_all_rates = AsyncMock(return_value=[
            ExchangeRate(**data) for data in sample_exchange_data
        ])
        
        db_repo = ExchangeDBRepository()
        service = ExchangeRateService(
            api_repository=mock_api_repo,
            db_repository=db_repo
        )
        
        # Act: Llamar múltiples veces
        await service.get_all_rates_with_average(session=test_session, persist=True)
        await service.get_all_rates_with_average(session=test_session, persist=True)
        await service.get_all_rates_with_average(session=test_session, persist=True)
        
        # Assert: Solo debe haber 3 registros (no duplicados)
        saved_rates = db_repo.get_all_rates(test_session)
        assert len(saved_rates) == 3
    
    @pytest.mark.asyncio
    async def test_persist_without_session_does_not_persist(self, sample_exchange_data):
        """Test: Sin sesión no debe persistir"""
        # Arrange
        mock_api_repo = Mock(spec=ExchangeRateRepository)
        mock_api_repo.get_all_rates = AsyncMock(return_value=[
            ExchangeRate(**data) for data in sample_exchange_data
        ])
        
        mock_db_repo = Mock(spec=ExchangeDBRepository)
        service = ExchangeRateService(
            api_repository=mock_api_repo,
            db_repository=mock_db_repo
        )
        
        # Act: Sin sesión
        result = await service.get_all_rates_with_average(
            session=None,
            persist=True
        )
        
        # Assert: No debe llamar al DB repository
        mock_db_repo.update_or_create_rate.assert_not_called()
        assert len(result.rates) == 3

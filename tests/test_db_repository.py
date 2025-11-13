"""
Tests para el repositorio de base de datos.
"""
import pytest
from decimal import Decimal
from sqlmodel import select

from database.models import ExchangeRateDB
from repositories.exchange_db_repository import ExchangeDBRepository


class TestExchangeDBRepository:
    """Tests para ExchangeDBRepository"""
    
    def test_update_or_create_rate_new_record(self, test_session):
        """Test: Crear un nuevo registro cuando no existe"""
        # Arrange
        repository = ExchangeDBRepository()
        
        # Act
        result = repository.update_or_create_rate(
            type="blue",
            buy=1100.0,
            sell=1120.0,
            rate=1.05,
            diff=25.5,
            session=test_session
        )
        
        # Assert
        assert result.id is not None
        assert result.type == "blue"
        assert float(result.buy) == 1100.0
        assert float(result.sell) == 1120.0
        assert float(result.rate) == 1.05
        assert float(result.diff) == 25.5
        assert result.updated_at is not None
    
    def test_update_or_create_rate_update_existing(self, test_session):
        """Test: Actualizar un registro existente (idempotencia)"""
        # Arrange
        repository = ExchangeDBRepository()
        
        # Crear registro inicial
        first_result = repository.update_or_create_rate(
            type="blue",
            buy=1100.0,
            sell=1120.0,
            rate=1.05,
            diff=25.5,
            session=test_session
        )
        first_id = first_result.id
        first_updated_at = first_result.updated_at
        
        # Act: Actualizar el mismo registro
        second_result = repository.update_or_create_rate(
            type="blue",
            buy=1150.0,  # Valor actualizado
            sell=1170.0,  # Valor actualizado
            rate=1.08,
            diff=30.0,
            session=test_session
        )
        
        # Assert
        assert second_result.id == first_id  # Mismo ID (no se duplicó)
        assert float(second_result.buy) == 1150.0  # Valores actualizados
        assert float(second_result.sell) == 1170.0
        assert float(second_result.rate) == 1.08
        assert float(second_result.diff) == 30.0
        assert second_result.updated_at > first_updated_at  # Timestamp actualizado
        
        # Verificar que solo hay un registro
        statement = select(ExchangeRateDB).where(ExchangeRateDB.type == "blue")
        all_blue = test_session.exec(statement).all()
        assert len(all_blue) == 1
    
    def test_get_all_rates(self, test_session):
        """Test: Obtener todas las tasas de la base de datos"""
        # Arrange
        repository = ExchangeDBRepository()
        
        # Crear varios registros
        repository.update_or_create_rate("blue", 1100.0, 1120.0, 1.05, 25.5, test_session)
        repository.update_or_create_rate("oficial", 950.0, 990.0, 0.95, -20.0, test_session)
        repository.update_or_create_rate("bolsa", 1050.0, 1070.0, 1.00, 0.0, test_session)
        
        # Act
        all_rates = repository.get_all_rates(test_session)
        
        # Assert
        assert len(all_rates) == 3
        types = [rate.type for rate in all_rates]
        assert "blue" in types
        assert "oficial" in types
        assert "bolsa" in types
    
    def test_get_rate_by_type_exists(self, test_session):
        """Test: Obtener una tasa específica que existe"""
        # Arrange
        repository = ExchangeDBRepository()
        repository.update_or_create_rate("blue", 1100.0, 1120.0, 1.05, 25.5, test_session)
        
        # Act
        rate = repository.get_rate_by_type("blue", test_session)
        
        # Assert
        assert rate is not None
        assert rate.type == "blue"
        assert float(rate.buy) == 1100.0
    
    def test_get_rate_by_type_not_exists(self, test_session):
        """Test: Obtener una tasa que no existe devuelve None"""
        # Arrange
        repository = ExchangeDBRepository()
        
        # Act
        rate = repository.get_rate_by_type("nonexistent", test_session)
        
        # Assert
        assert rate is None
    
    def test_idempotency_multiple_updates(self, test_session):
        """Test: Múltiples actualizaciones no duplican registros"""
        # Arrange
        repository = ExchangeDBRepository()
        
        # Act: Múltiples actualizaciones del mismo tipo
        for i in range(5):
            repository.update_or_create_rate(
                type="blue",
                buy=1100.0 + i,
                sell=1120.0 + i,
                rate=1.05,
                diff=25.5,
                session=test_session
            )
        
        # Assert: Solo debe haber un registro
        all_rates = repository.get_all_rates(test_session)
        assert len(all_rates) == 1
        
        # El último valor debe ser el actual
        blue_rate = repository.get_rate_by_type("blue", test_session)
        assert blue_rate is not None
        assert float(blue_rate.buy) == 1104.0  # 1100 + 4

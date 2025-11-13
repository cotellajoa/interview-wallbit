"""
Tests para el CLI.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from typer.testing import CliRunner

from cli import app, sync_rates_async


runner = CliRunner()


class TestCLI:
    """Tests para los comandos CLI"""
    
    @pytest.mark.asyncio
    async def test_sync_rates_async_success(self, sample_exchange_data):
        """Test: sync_rates_async ejecuta correctamente"""
        # Arrange
        with patch("cli.DolarApiClient") as mock_api_client_class, \
             patch("cli.ExchangeRateRepository") as mock_api_repo_class, \
             patch("cli.ExchangeRateService") as mock_service_class, \
             patch("cli.Session") as mock_session_class:
            
            # Mock del servicio
            mock_service = MagicMock()
            mock_result = MagicMock()
            mock_result.model_dump.return_value = {
                "rates": sample_exchange_data,
                "average": {"compra": 1033.33, "venta": 1060.0}
            }
            mock_service.get_all_rates_with_average = AsyncMock(return_value=mock_result)
            mock_service_class.return_value = mock_service
            
            # Mock de la sesión
            mock_session = MagicMock()
            mock_session.__enter__ = MagicMock(return_value=mock_session)
            mock_session.__exit__ = MagicMock(return_value=None)
            mock_session_class.return_value = mock_session
            
            # Act
            result = await sync_rates_async()
            
            # Assert
            assert result is not None
            mock_service.get_all_rates_with_average.assert_called_once_with(
                session=mock_session,
                persist=True
            )
    
    def test_cli_sync_rates_command(self):
        """Test: Comando sync-rates del CLI"""
        # Arrange
        with patch("cli.asyncio.run") as mock_asyncio_run, \
             patch("cli.create_db_and_tables") as mock_create_db:
            
            mock_result = MagicMock()
            mock_result.model_dump.return_value = {
                "rates": [{"nombre": "Blue", "compra": 1100, "venta": 1120}],
                "average": {"compra": 1100, "venta": 1120}
            }
            mock_asyncio_run.return_value = mock_result
            
            # Act
            result = runner.invoke(app, ["sync-rates"])
            
            # Assert
            assert result.exit_code == 0
            mock_create_db.assert_called_once()
            mock_asyncio_run.assert_called_once()
            
            # Verificar output
            assert "Sincronizando tasas de cambio" in result.stdout
            assert "completada exitosamente" in result.stdout or "Sincronización completada" in result.stdout
    
    def test_cli_init_db_command(self):
        """Test: Comando init-db del CLI"""
        # Arrange
        with patch("cli.create_db_and_tables") as mock_create_db:
            
            # Act
            result = runner.invoke(app, ["init-db"])
            
            # Assert
            assert result.exit_code == 0
            mock_create_db.assert_called_once()
            assert "Inicializando base de datos" in result.stdout
            assert "inicializada correctamente" in result.stdout
    
    def test_cli_version_command(self):
        """Test: Comando version del CLI"""
        # Act
        result = runner.invoke(app, ["version"])
        
        # Assert
        assert result.exit_code == 0
        assert "Exchange Rates CLI" in result.stdout
        assert "v1.0.0" in result.stdout
    
    def test_cli_help_command(self):
        """Test: Comando help del CLI"""
        # Act
        result = runner.invoke(app, ["--help"])
        
        # Assert
        assert result.exit_code == 0
        assert "sync-rates" in result.stdout
        assert "init-db" in result.stdout
        assert "version" in result.stdout
    
    def test_cli_sync_rates_error_handling(self):
        """Test: Manejo de errores en sync-rates"""
        # Arrange
        with patch("cli.asyncio.run") as mock_asyncio_run, \
             patch("cli.create_db_and_tables") as mock_create_db:
            
            mock_asyncio_run.side_effect = Exception("Database error")
            
            # Act
            result = runner.invoke(app, ["sync-rates"])
            
            # Assert
            assert result.exit_code == 1
            assert "Error" in result.stdout
    
    def test_cli_init_db_error_handling(self):
        """Test: Manejo de errores en init-db"""
        # Arrange
        with patch("cli.create_db_and_tables") as mock_create_db:
            mock_create_db.side_effect = Exception("Database creation failed")
            
            # Act
            result = runner.invoke(app, ["init-db"])
            
            # Assert
            assert result.exit_code == 1
            assert "Error" in result.stdout

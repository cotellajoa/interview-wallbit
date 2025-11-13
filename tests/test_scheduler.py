"""
Tests para el scheduler de jobs.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import asyncio

from jobs.scheduler import sync_exchange_rates_job, run_sync_job


class TestScheduler:
    """Tests para el scheduler y jobs"""
    
    @pytest.mark.asyncio
    async def test_sync_exchange_rates_job_success(self, sample_exchange_data):
        """Test: Job de sincronización ejecuta correctamente"""
        # Arrange
        with patch("jobs.scheduler.DolarApiClient") as mock_api_client_class, \
             patch("jobs.scheduler.ExchangeRateRepository") as mock_api_repo_class, \
             patch("jobs.scheduler.ExchangeRateService") as mock_service_class, \
             patch("jobs.scheduler.Session") as mock_session_class, \
             patch("builtins.print") as mock_print:
            
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
            await sync_exchange_rates_job()
            
            # Assert
            mock_service.get_all_rates_with_average.assert_called_once_with(
                session=mock_session,
                persist=True
            )
            
            # Verificar que se imprimió el resultado
            print_calls = [str(call) for call in mock_print.call_args_list]
            assert any("JOB" in str(call) for call in print_calls)
            assert any("completada exitosamente" in str(call) for call in print_calls)
    
    @pytest.mark.asyncio
    async def test_sync_exchange_rates_job_error_handling(self):
        """Test: Job maneja errores correctamente"""
        # Arrange
        with patch("jobs.scheduler.DolarApiClient") as mock_api_client_class, \
             patch("jobs.scheduler.ExchangeRateRepository") as mock_api_repo_class, \
             patch("jobs.scheduler.ExchangeRateService") as mock_service_class, \
             patch("jobs.scheduler.Session") as mock_session_class, \
             patch("builtins.print") as mock_print:
            
            # Mock del servicio que lanza error
            mock_service = MagicMock()
            mock_service.get_all_rates_with_average = AsyncMock(
                side_effect=Exception("API Error")
            )
            mock_service_class.return_value = mock_service
            
            # Mock de la sesión
            mock_session = MagicMock()
            mock_session.__enter__ = MagicMock(return_value=mock_session)
            mock_session.__exit__ = MagicMock(return_value=None)
            mock_session_class.return_value = mock_session
            
            # Act & Assert
            with pytest.raises(Exception) as exc_info:
                await sync_exchange_rates_job()
            
            assert "API Error" in str(exc_info.value)
            
            # Verificar que se imprimió el error
            print_calls = [str(call) for call in mock_print.call_args_list]
            assert any("Error en sincronización" in str(call) for call in print_calls)
    
    def test_run_sync_job_wrapper(self):
        """Test: Wrapper síncrono ejecuta job asíncrono"""
        # Arrange
        with patch("jobs.scheduler.asyncio.run") as mock_asyncio_run, \
             patch("jobs.scheduler.sync_exchange_rates_job") as mock_job:
            
            # Act
            run_sync_job()
            
            # Assert
            mock_asyncio_run.assert_called_once()
            # Verificar que se llamó asyncio.run con alguna coroutine
            assert mock_asyncio_run.call_count == 1
    
    def test_start_scheduler(self):
        """Test: Scheduler se inicia correctamente"""
        # Arrange
        with patch("jobs.scheduler.BackgroundScheduler") as mock_scheduler_class, \
             patch("builtins.print") as mock_print:
            
            mock_scheduler = MagicMock()
            mock_scheduler_class.return_value = mock_scheduler
            
            # Act
            from jobs.scheduler import start_scheduler
            result = start_scheduler()
            
            # Assert
            mock_scheduler.add_job.assert_called_once()
            mock_scheduler.start.assert_called_once()
            assert result == mock_scheduler
            
            # Verificar configuración del job
            call_kwargs = mock_scheduler.add_job.call_args[1]
            assert call_kwargs['id'] == 'sync_exchange_rates'
            assert 'IntervalTrigger' in str(type(call_kwargs['trigger']))

"""
Tests para el cliente de API externa.
"""
import pytest
from unittest.mock import AsyncMock, Mock, patch
import httpx
from fastapi import HTTPException

from external.dolar_api_client import DolarApiClient


class TestDolarApiClient:
    """Tests para DolarApiClient"""
    
    @pytest.mark.asyncio
    async def test_fetch_all_exchange_rates_success(self, sample_exchange_data):
        """Test: Obtener tasas exitosamente"""
        # Arrange
        client = DolarApiClient()
        
        # Mock de httpx.AsyncClient
        with patch("external.dolar_api_client.httpx.AsyncClient") as mock_client_class:
            # response.json() es un método SÍNCRONO regular
            mock_response = Mock()
            mock_response.json = Mock(return_value=sample_exchange_data)
            mock_response.raise_for_status = Mock()
            
            mock_client = AsyncMock()
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            
            mock_client_class.return_value = mock_client
            
            # Act
            result = await client.fetch_all_exchange_rates()
            
            # Assert
            assert len(result) == 3
            assert result[0]["nombre"] == "Oficial"
            assert result[1]["nombre"] == "Blue"
            mock_client.get.assert_called_once_with(
                "https://dolarapi.com/v1/dolares"
            )
    
    @pytest.mark.asyncio
    async def test_fetch_all_exchange_rates_http_error(self):
        """Test: Manejar error HTTP de la API"""
        # Arrange
        client = DolarApiClient()
        
        with patch("external.dolar_api_client.httpx.AsyncClient") as mock_client_class:
            # Crear mock de response para el error
            mock_error_response = AsyncMock()
            mock_error_response.status_code = 500
            mock_error_response.text = "Internal Server Error"
            
            # Crear HTTPStatusError con request mock
            http_error = httpx.HTTPStatusError(
                "Error",
                request=AsyncMock(),
                response=mock_error_response
            )
            
            mock_client = AsyncMock()
            mock_client.get = AsyncMock(side_effect=http_error)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            
            mock_client_class.return_value = mock_client
            
            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                await client.fetch_all_exchange_rates()
            
            assert exc_info.value.status_code == 500
            assert "Error al consultar la API externa" in exc_info.value.detail
    
    @pytest.mark.asyncio
    async def test_fetch_all_exchange_rates_connection_error(self):
        """Test: Manejar error de conexión"""
        # Arrange
        client = DolarApiClient()
        
        with patch("external.dolar_api_client.httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.get = AsyncMock(side_effect=Exception("Connection refused"))
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            
            mock_client_class.return_value = mock_client
            
            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                await client.fetch_all_exchange_rates()
            
            assert exc_info.value.status_code == 500
            assert "Error de conexión" in exc_info.value.detail
    
    @pytest.mark.asyncio
    async def test_custom_base_url(self):
        """Test: Usar URL base personalizada"""
        # Arrange
        custom_url = "https://custom-api.com/v2"
        client = DolarApiClient(base_url=custom_url)
        
        with patch("external.dolar_api_client.httpx.AsyncClient") as mock_client_class:
            mock_response = Mock()
            mock_response.json = Mock(return_value=[])
            mock_response.raise_for_status = Mock()
            
            mock_client = AsyncMock()
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            
            mock_client_class.return_value = mock_client
            
            # Act
            await client.fetch_all_exchange_rates()
            
            # Assert
            mock_client.get.assert_called_once_with(f"{custom_url}/dolares")

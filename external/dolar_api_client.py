import httpx
from typing import List, Dict, Any
from fastapi import HTTPException


class DolarApiClient:
    def __init__(self, base_url: str = "https://dolarapi.com/v1"):
        self.base_url = base_url
    
    async def fetch_all_exchange_rates(self) -> List[Dict[str, Any]]:
        url = f"{self.base_url}/dolares"
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url)
                response.raise_for_status()
                return response.json()
                
            except httpx.HTTPStatusError as exc:
                raise HTTPException(
                    status_code=exc.response.status_code,
                    detail=f'Error al consultar la API externa: {exc.response.text}'
                )
            except Exception as exc:
                raise HTTPException(
                    status_code=500,
                    detail=f'Error de conexión con la API externa: {str(exc)}'
                )

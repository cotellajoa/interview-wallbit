#!/usr/bin/env python3
import asyncio
import json
from datetime import datetime

import typer
from rich.console import Console
from rich.panel import Panel

from sqlmodel import Session
from database.connection import engine, create_db_and_tables
from services.exchange_rate_service import ExchangeRateService
from repositories.exchange_rate_repository import ExchangeRateRepository
from external.dolar_api_client import DolarApiClient

app = typer.Typer(
    name="exchange-cli",
    help="CLI para gestión de tasas de cambio",
    add_completion=False
)
console = Console()


async def sync_rates_async():
    api_client = DolarApiClient()
    api_repository = ExchangeRateRepository(api_client)
    service = ExchangeRateService(api_repository)
    
    with Session(engine) as session:
        result = await service.get_all_rates_with_average(
            session=session, 
            persist=True
        )
        
        return result


@app.command("sync-rates")
def sync_rates():
    console.print("\nSincronizando tasas de cambio...\n")
    
    try:
        create_db_and_tables()
        
        result = asyncio.run(sync_rates_async())
        
        result_dict = result.model_dump()
        
        # Mostrar resultado
        console.print("Sincronización completada exitosamente\n")
        
        console.print(f"Tasas obtenidas: {len(result_dict['rates'])} tipos de cambio")
        console.print(f"Promedio Compra: ${result_dict['average']['compra']}")
        console.print(f"Promedio Venta: ${result_dict['average']['venta']}")
        
        console.print("\nDetalle completo:")
        result_json = json.dumps(result_dict, indent=2, ensure_ascii=False, default=str)
        console.print(Panel(result_json, title="Response JSON", border_style="green"))
        
        console.print(f"\nTimestamp: {datetime.now()}\n")
        
    except Exception as e:
        console.print(f"\nError: {str(e)}\n")
        raise typer.Exit(code=1)


@app.command("init-db")
def init_db():
    console.print("\nInicializando base de datos...\n")
    
    try:
        create_db_and_tables()
        console.print("Base de datos inicializada correctamente\n")
    except Exception as e:
        console.print(f"\nError: {str(e)}\n")
        raise typer.Exit(code=1)


@app.command("version")
def version():
    """
    Muestra la versión de la aplicación.
    """
    console.print("\n[bold]Exchange Rates CLI[/bold] - [cyan]v1.0.0[/cyan]\n")


if __name__ == "__main__":
    app()

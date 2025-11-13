from fastapi import FastAPI
from contextlib import asynccontextmanager
import os

from api import exchange_routes
from database.connection import create_db_and_tables

# Importar scheduler solo si está habilitado
ENABLE_SCHEDULER = os.getenv("ENABLE_SCHEDULER", "false").lower() == "true"

if ENABLE_SCHEDULER:
    from jobs.scheduler import start_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Maneja el ciclo de vida de la aplicación.
    Se ejecuta al inicio y al final de la aplicación.
    """
    # Startup: Crear las tablas de la base de datos
    print("🚀 Iniciando aplicación...")
    create_db_and_tables()
    print("✅ Base de datos inicializada")
    
    # Iniciar scheduler si está habilitado
    scheduler = None
    if ENABLE_SCHEDULER:
        scheduler = start_scheduler()
        print("✅ Scheduler iniciado")
    
    yield
    
    # Shutdown
    if scheduler:
        scheduler.shutdown()
        print("⏹️  Scheduler detenido")
    print("👋 Cerrando aplicación...")


app = FastAPI(
    title="Exchange Rates API",
    description="API para obtener y gestionar tasas de cambio del dólar",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(exchange_routes.route)


@app.get("/")
async def root():
    """Endpoint raíz de bienvenida"""
    return {
        "message": "Exchange Rates API",
        "version": "1.0.0",
        "endpoints": {
            "exchange_rates": "/api/exchange",
            "docs": "/docs"
        }
    }

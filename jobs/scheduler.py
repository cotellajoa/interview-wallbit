import asyncio
import json
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from sqlmodel import Session
from database.connection import engine
from services.exchange_rate_service import ExchangeRateService
from repositories.exchange_rate_repository import ExchangeRateRepository
from external.dolar_api_client import DolarApiClient


async def sync_exchange_rates_job():
    print(f"\n{'='*80}")
    print(f"[JOB] Iniciando sincronización de tasas de cambio - {datetime.now()}")
    print(f"{'='*80}\n")
    
    try:
        api_client = DolarApiClient()
        api_repository = ExchangeRateRepository(api_client)
        service = ExchangeRateService(api_repository)
        
        with Session(engine) as session:
            result = await service.get_all_rates_with_average(
                session=session, 
                persist=True
            )
            
            result_dict = result.model_dump()
            result_json = json.dumps(result_dict, indent=2, ensure_ascii=False, default=str)
            
            print("[JOB] Sincronización completada exitosamente")
            print(f"\n[JOB] Resultado:\n{result_json}\n")
            print(f"{'='*80}\n")
            
    except Exception as e:
        print(f"[JOB] Error en sincronización: {str(e)}")
        print(f"{'='*80}\n")
        raise


def run_sync_job():
    asyncio.run(sync_exchange_rates_job())


def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        func=run_sync_job,
        trigger=IntervalTrigger(hours=2),
        id='sync_exchange_rates',
        name='Sincronizar tasas de cambio cada 2 horas',
        replace_existing=True
    )
    
    scheduler.start()
    print("Job programado cada 2 horas")
    
    return scheduler


if __name__ == "__main__":
    print("Ejecutando job de prueba")
    run_sync_job()

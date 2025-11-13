# Exchange Rates API - Guía de Uso

## 📋 Contenido

1. [Configuración de Base de Datos](#configuración-de-base-de-datos)
2. [Instalación de Dependencias](#instalación-de-dependencias)
3. [Ejecutar la API](#ejecutar-la-api)
4. [Comando CLI](#comando-cli)
5. [Scheduler Automático](#scheduler-automático)
6. [Estructura del Proyecto](#estructura-del-proyecto)

---

## 🗄️ Configuración de Base de Datos

### SQLite con SQLModel

La aplicación usa **SQLite** con **SQLModel** para persistencia de datos.

**Archivo:** `database/connection.py`

```python
DATABASE_URL = "sqlite:///./exchange.db"
```

### Modelo de Base de Datos

**Archivo:** `database/models.py`

**Tabla:** `exchange_rates`

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | Integer (PK) | ID autoincremental |
| `type` | String (Index, Unique) | Tipo de cambio (ej: "blue") |
| `buy` | Decimal | Precio de compra |
| `sell` | Decimal | Precio de venta |
| `rate` | Decimal | Tasa normalizada |
| `diff` | Decimal | Diferencia con el promedio |
| `updated_at` | DateTime | Última actualización |

### Inicialización Automática

La base de datos se crea automáticamente al iniciar la aplicación:

```python
# En main.py
create_db_and_tables()  # Se ejecuta en el lifespan
```

---

## 📦 Instalación de Dependencias

```powershell
# Instalar dependencias
uv add sqlmodel apscheduler typer[all] rich
```

O manualmente en `pyproject.toml`:

```toml
dependencies = [
    "fastapi[standard]>=0.121.1",
    "httpx>=0.28.1",
    "sqlmodel>=0.0.22",
    "apscheduler>=3.10.4",
    "typer[all]>=0.12.0",
    "rich>=13.7.0"
]
```

---

## 🚀 Ejecutar la API

### Iniciar el servidor FastAPI

```powershell
# Modo desarrollo
fastapi dev main.py

# Modo producción
fastapi run main.py
```

### Endpoints Disponibles

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/` | GET | Raíz - Información de la API |
| `/api/exchange` | GET | Obtener tasas con promedio y persistir |
| `/docs` | GET | Documentación interactiva (Swagger) |

### Ejemplo de Response

```json
{
  "rates": [
    {
      "nombre": "Oficial",
      "compra": 950.0,
      "venta": 990.0,
      "fechaActualizacion": "2025-11-13T10:00:00.000Z"
    },
    {
      "nombre": "Blue",
      "compra": 1100.0,
      "venta": 1120.0,
      "fechaActualizacion": "2025-11-13T10:00:00.000Z"
    }
  ],
  "average": {
    "compra": 1025.50,
    "venta": 1055.75
  }
}
```

---

## 💻 Comando CLI

### Uso del CLI

**Archivo:** `cli.py`

```powershell
# Sincronizar tasas de cambio
python cli.py sync-rates

# Inicializar base de datos
python cli.py init-db

# Ver versión
python cli.py version

# Ver ayuda
python cli.py --help
```

### Comando `sync-rates`

Este comando:
1. ✅ Crea su propia sesión de base de datos
2. ✅ Llama al mismo método del servicio que usa la API
3. ✅ Obtiene datos de DolarAPI
4. ✅ Calcula promedio y normalizaciones
5. ✅ Persiste en SQLite usando `update_or_create`
6. ✅ Muestra el resultado en consola con formato bonito

**Ejemplo de salida:**

```
🚀 Sincronizando tasas de cambio...

✅ Sincronización completada exitosamente

📊 Tasas obtenidas: 7 tipos de cambio
📈 Promedio Compra: $1025.50
📉 Promedio Venta: $1055.75

📄 Detalle completo:
╭─ Response JSON ─────────────────╮
│ {                               │
│   "rates": [...],               │
│   "average": {...}              │
│ }                               │
╰─────────────────────────────────╯

⏰ Timestamp: 2025-11-13 10:30:45
```

---

## ⏰ Scheduler Automático

### Configuración

**Archivo:** `jobs/scheduler.py`

El scheduler ejecuta el job de sincronización **cada 2 horas**.

### Habilitar el Scheduler

```powershell
# Opción 1: Variable de entorno
$env:ENABLE_SCHEDULER="true"
fastapi dev main.py

# Opción 2: En Windows (permanente)
setx ENABLE_SCHEDULER "true"
fastapi dev main.py
```

### Funcionamiento

1. ✅ Se ejecuta automáticamente cada 2 horas
2. ✅ Crea su propia sesión de base de datos
3. ✅ Llama al mismo método del servicio
4. ✅ Imprime el resultado en consola (logs)

**Ejemplo de log:**

```
================================================================================
🕐 [JOB] Iniciando sincronización de tasas de cambio - 2025-11-13 12:00:00
================================================================================

✅ [JOB] Sincronización completada exitosamente

📊 [JOB] Resultado:
{
  "rates": [...],
  "average": {...}
}
================================================================================
```

### Testing del Job

```powershell
# Ejecutar el job manualmente (para testing)
python -c "from jobs.scheduler import run_sync_job; run_sync_job()"

# O ejecutar el archivo directamente
python jobs/scheduler.py
```

---

## 📁 Estructura del Proyecto

```
interview/
├── api/                           # Capa de Presentación
│   └── exchange_routes.py         # Endpoints FastAPI
│
├── services/                      # Capa de Lógica de Negocio
│   └── exchange_rate_service.py   # Servicio principal
│
├── repositories/                  # Capa de Acceso a Datos
│   ├── exchange_rate_repository.py    # Repositorio API externa
│   └── exchange_db_repository.py      # Repositorio Base de Datos
│
├── external/                      # Capa Externa
│   └── dolar_api_client.py        # Cliente HTTP DolarAPI
│
├── database/                      # Configuración de BD
│   ├── connection.py              # Engine y get_session
│   └── models.py                  # Modelo SQLModel
│
├── models/                        # Modelos de Dominio
│   └── exchange_rate.py           # DTOs Pydantic
│
├── jobs/                          # Jobs Programados
│   └── scheduler.py               # APScheduler configuración
│
├── cli.py                         # CLI con Typer
├── main.py                        # Aplicación FastAPI
└── exchange.db                    # Base de datos SQLite (generada)
```

---

## 🔄 Flujo de Datos Completo

```
┌─────────────────────────────────────────────────────────────┐
│                    PUNTOS DE ENTRADA                        │
├─────────────────────────────────────────────────────────────┤
│  1. API Endpoint    2. CLI Command    3. Scheduled Job     │
│  (FastAPI)          (Typer)           (APScheduler)         │
└──────────────┬──────────────┬──────────────┬───────────────┘
               │              │              │
               └──────────────┼──────────────┘
                              │
                    ┌─────────▼─────────┐
                    │  ExchangeService  │ ◄── Lógica de negocio
                    │  - get_all_rates  │     100% reutilizable
                    │  - _persist_rates │
                    └─────────┬─────────┘
                              │
                    ┌─────────▼─────────┐
                    │   API Repository  │ ◄── Obtiene datos externos
                    └─────────┬─────────┘
                              │
                    ┌─────────▼─────────┐
                    │  DolarApiClient   │ ◄── HTTP Request
                    └─────────┬─────────┘
                              │
                    ┌─────────▼─────────┐
                    │  External API     │
                    │  (DolarAPI.com)   │
                    └───────────────────┘

                    ┌───────────────────┐
                    │  DB Repository    │ ◄── Persistencia
                    │  - update_or      │
                    │    _create_rate   │
                    └─────────┬─────────┘
                              │
                    ┌─────────▼─────────┐
                    │   SQLite DB       │
                    │  (exchange.db)    │
                    └───────────────────┘
```

---

## 🎯 Características Clave

### ✅ Operación Idempotente

El método `update_or_create_rate` es **idempotente**:

```python
# Busca por 'type'
existing = session.exec(
    select(ExchangeRateDB).where(ExchangeRateDB.type == type)
).first()

if existing:
    # Actualiza
    existing.buy = buy
    existing.sell = sell
    # ...
else:
    # Crea nuevo
    new_rate = ExchangeRateDB(...)
```

### ✅ Manejo de Sesiones

- **API Endpoint**: Sesión inyectada por `Depends(get_session)`
- **CLI**: Crea su propia sesión con `Session(engine)`
- **Scheduler**: Crea su propia sesión con `Session(engine)`

### ✅ Lógica 100% Reutilizable

El mismo método `get_all_rates_with_average()` es usado por:
1. API Endpoint
2. CLI Command
3. Scheduled Job

---

## 🧪 Testing

### Probar el Endpoint

```powershell
# Con curl
curl http://localhost:8000/api/exchange

# Con httpie
http GET http://localhost:8000/api/exchange
```

### Probar el CLI

```powershell
python cli.py sync-rates
```

### Probar el Scheduler

```powershell
$env:ENABLE_SCHEDULER="true"
fastapi dev main.py
# Esperar 2 horas o ver logs inmediatos si se ejecuta manualmente
```

---

## 📝 Notas Importantes

1. **SQLite Thread Safety**: Configurado con `check_same_thread=False`
2. **Commits Automáticos**: La sesión hace commit automáticamente en el repositorio
3. **Normalizaciones**: Se calculan `rate` (normalizado) y `diff` (diferencia)
4. **Type Format**: Los tipos se guardan en lowercase con guiones bajos (ej: "contado_con_liqui")

---

## 🚨 Solución de Problemas

### Error: "No module named 'sqlmodel'"

```powershell
uv add sqlmodel
```

### Error: "No module named 'apscheduler'"

```powershell
uv add apscheduler
```

### Error: "No module named 'typer'"

```powershell
uv add "typer[all]"
```

### La base de datos no se crea

```powershell
# Ejecutar manualmente
python cli.py init-db
```

---

## 📚 Referencias

- [SQLModel Documentation](https://sqlmodel.tiangolo.com/)
- [APScheduler Documentation](https://apscheduler.readthedocs.io/)
- [Typer Documentation](https://typer.tiangolo.com/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

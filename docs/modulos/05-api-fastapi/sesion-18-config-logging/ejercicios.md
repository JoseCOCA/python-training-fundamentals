# S18 — Ejercicios

> **Tiempo estimado:** ~75 min. Tres bloques: ejercicio guiado armando `BaseSettings` + `.env` + logging en una mini-app, libres para entrenar middleware y observabilidad, y **cierre del hito M5** del integrador con tag `proyecto-m5`.

---

## 0. Antes de empezar

Tu sandbox vive en `code/m05-api-fastapi/sesion-18/`. Si todavía no lo corriste:

```bash
cd code/m05-api-fastapi/sesion-18
uv sync
cp env.example .env       # editá .env si querés, no se sube al repo
uv run uvicorn main:app --reload
uv run mypy .
uv run ruff check .
```

Abrí `http://localhost:8000/docs` y mandá unas requests para ver los logs.

## 1. Ejercicio guiado — Settings + logging + middleware

### Paso 1.1 — Config con `pydantic-settings`

Crea `mi_config.py`:

```python
from functools import lru_cache

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        env_prefix="DEMO_",
    )

    app_name: str = "demo-s18"
    debug: bool = False
    api_key: SecretStr = Field(default=SecretStr("change-me"))
    log_level: str = "INFO"


@lru_cache
def get_settings() -> Settings:
    return Settings()


if __name__ == "__main__":
    s = get_settings()
    print(f"app_name = {s.app_name}")
    print(f"debug    = {s.debug}")
    print(f"api_key  = {s.api_key}                            # ← SecretStr esconde valor")
    print(f"api_key  = {s.api_key.get_secret_value()}          # ← explícito")
```

`.env`:

```ini
DEMO_DEBUG=true
DEMO_API_KEY=secreto-local-de-pruebas
DEMO_LOG_LEVEL=DEBUG
```

Corré: `uv run python mi_config.py`. Vas a ver:
- `debug = True` (leído del `.env`).
- `api_key = SecretStr('**********')` y luego el valor real.

Probá también con env var directo:

```bash
DEMO_APP_NAME=otra-app uv run python mi_config.py
```

Las env vars **pisan** lo que hay en `.env`.

### Paso 1.2 — Logging configurable

Crea `mi_log.py`:

```python
import logging
import sys


def configurar_logging(level: str = "INFO") -> None:
    logging.basicConfig(
        level=level.upper(),
        format="%(asctime)s %(levelname)-7s %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        stream=sys.stdout,
        force=True,
    )


if __name__ == "__main__":
    from mi_config import get_settings

    s = get_settings()
    configurar_logging(s.log_level)
    log = logging.getLogger("demo")
    log.debug("debug — solo se ve si log_level=DEBUG")
    log.info("info — request OK", extra={"path": "/", "status": 200})
    log.warning("warning — algo raro")
    log.error("error — fallé pero sigo")
```

Corré: con `DEMO_LOG_LEVEL=DEBUG` ves los cuatro mensajes. Con `INFO` no ves el `debug`.

Notar que `extra={"path":..., "status":...}` no aparece en el formato default — hay que cambiar el format string para que aparezca, o usar un formatter JSON.

### Paso 1.3 — Middleware con request_id

Crea `mi_app.py`:

```python
import logging
import time
import uuid
from collections.abc import Awaitable, Callable
from typing import Any

from fastapi import Depends, FastAPI, Request
from fastapi.responses import Response

from mi_config import Settings, get_settings
from mi_log import configurar_logging

# Configurar logging una vez al cargar el módulo (en producción usá lifespan)
configurar_logging(get_settings().log_level)
log = logging.getLogger("demo.app")

app = FastAPI()


@app.middleware("http")
async def trace_middleware(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    request.state.request_id = uuid.uuid4().hex[:8]
    start = time.perf_counter()
    try:
        response = await call_next(request)
    except Exception:
        log.exception(
            "request error",
            extra={
                "method": request.method,
                "path": request.url.path,
                "request_id": request.state.request_id,
            },
        )
        raise
    latency_ms = int((time.perf_counter() - start) * 1000)
    log.info(
        "%s %s -> %d (%dms) [%s]",
        request.method,
        request.url.path,
        response.status_code,
        latency_ms,
        request.state.request_id,
    )
    response.headers["X-Request-ID"] = request.state.request_id
    return response


@app.get("/")
def root(settings: Settings = Depends(get_settings)) -> dict[str, Any]:
    return {"app": settings.app_name, "debug": settings.debug}


@app.get("/explosivo")
def explosivo() -> dict[str, str]:
    raise RuntimeError("simulación de error")
```

Levantá: `uv run uvicorn mi_app:app --reload`.

Probá:
```bash
curl -i http://localhost:8000/
# vas a ver el header X-Request-ID en la respuesta
curl http://localhost:8000/explosivo
# en los logs vas a ver "request error" con stack trace
```

### Paso 1.4 — Observar y reflexionar

Mirá los logs en la terminal donde corre uvicorn. Cada línea tiene:
- timestamp
- level
- logger name
- mensaje (con método, path, status, latencia, request_id)

Si tu cliente (frontend) reportás un bug, te puede dar el `X-Request-ID` y vos `grep` los logs por ese id para ver exactamente qué pasó. **Sin** el id, buscás en un océano de líneas.

## 2. Ejercicios libres

### 2.1. Validar `log_level`

Tu `Settings` acepta cualquier string como `log_level`. Si pongo `DEMO_LOG_LEVEL=lol`, `logging.basicConfig` falla en runtime. Mejor: validalo en pydantic.

```python
from typing import Literal


class Settings(BaseSettings):
    ...
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
```

Probá `DEMO_LOG_LEVEL=lol uv run python mi_config.py` → `ValidationError` antes de arrancar la app. Eso es **fail-fast**.

### 2.2. Listas y dicts en env vars

`pydantic-settings` parsea JSON cuando el campo es una colección:

```python
class Settings(BaseSettings):
    cors_origins: list[str] = []
    rate_limits: dict[str, int] = {}
```

```ini
DEMO_CORS_ORIGINS=["http://localhost:3000","https://app.tienda.pro"]
DEMO_RATE_LIMITS={"default":100,"premium":1000}
```

Probá levantar la app y verificar que los valores llegan. Útil para flags configurables sin redeploy.

### 2.3. Logging JSON con `python-json-logger`

Reemplazá el formato simple por JSON estructurado:

```bash
uv add python-json-logger
```

```python
from pythonjsonlogger import jsonlogger


def configurar_logging_json(level: str = "INFO") -> None:
    handler = logging.StreamHandler()
    formatter = jsonlogger.JsonFormatter(
        "%(asctime)s %(levelname)s %(name)s %(message)s"
    )
    handler.setFormatter(formatter)
    logging.basicConfig(level=level.upper(), handlers=[handler], force=True)
```

Recargá. Cada línea de log ahora es un objeto JSON. Probá:

```bash
curl http://localhost:8000/ 2>&1 | jq 'select(.levelname=="INFO")'
```

Es la forma estándar para alimentar Loki/Datadog/Splunk.

### 2.4. Excepciones que no escalan a 500

Hacé un endpoint que lanza tu excepción de dominio. Combinándolo con S17, agregá un exception handler que loguee `WARNING` (no `ERROR`) y devuelve 400. Probá: el log dice `WARNING` pero la response es 400.

Distinción: `ERROR` es bug; un 4xx por error del cliente es `WARNING` o `INFO` (no es responsabilidad tuya).

### 2.5. CORS con orígenes desde la config

Agregá CORS al middleware stack:

```python
from fastapi.middleware.cors import CORSMiddleware


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Probá desde un browser que el `OPTIONS` precheck devuelve los headers correctos. CORS es de los temas más confusos en su primer encuentro — leé MDN si te trabás.

## 3. Aporte al proyecto integrador — CIERRE DEL HITO M5

**Hoy cierra el Módulo 5.** TiendaPro Lite queda como API REST con configuración por entorno, logging estructurado y exception handling completo.

### 3.1. Agregar dependencia

En `code/proyecto-integrador/pyproject.toml`:

```toml
dependencies = [
    "pydantic>=2.6",
    "httpx>=0.27",
    "sqlalchemy>=2.0",
    "fastapi>=0.115",
    "uvicorn[standard]>=0.30",
    "pydantic-settings>=2.4",
]
```

```bash
cd /home/jose/Proyectos/python-training-fundamentals/code/proyecto-integrador
uv sync --all-groups
```

### 3.2. `src/tiendapro/config.py`

```python
"""Settings de la app: lee de env vars y .env."""

from functools import lru_cache
from typing import Literal

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        env_prefix="TIENDAPRO_",
    )

    app_name: str = "TiendaPro"
    debug: bool = False
    database_url: str = "sqlite:///tiendapro.db"
    api_key: SecretStr = Field(default=SecretStr("change-me"))
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    enable_enrichment: bool = True
    cors_origins: list[str] = ["http://localhost:3000"]


@lru_cache
def get_settings() -> Settings:
    return Settings()
```

### 3.3. `src/tiendapro/log.py`

```python
"""Configuración de logging estructurado."""

import logging
import sys


def configurar_logging(level: str = "INFO") -> None:
    logging.basicConfig(
        level=level.upper(),
        format="%(asctime)s %(levelname)-7s %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        stream=sys.stdout,
        force=True,
    )
    # Reducí el ruido de uvicorn access log; queremos NUESTRO logger
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
```

### 3.4. Refactor de `db.py` para usar `settings.database_url`

Cambiá `src/tiendapro/db.py`:

```python
"""Conexión a la base de datos: engine, sesión y bootstrap del schema."""

from collections.abc import Iterator
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from tiendapro.config import get_settings
from tiendapro.orm import Base


def _build_engine() -> Engine:
    settings = get_settings()
    return create_engine(settings.database_url, echo=False, future=True)


_engine: Engine = _build_engine()


def crear_schema() -> None:
    Base.metadata.create_all(_engine)


@contextmanager
def obtener_sesion() -> Iterator[Session]:
    session = Session(_engine)
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
```

### 3.5. Endpoints completos en `tiendapro/api/rutas.py`

Reemplaza el contenido de `src/tiendapro/api/rutas.py`:

```python
"""Rutas REST de TiendaPro (CRUD productos completo + health)."""

from fastapi import APIRouter, status

from tiendapro import repositorio
from tiendapro.api.dtos import HealthOut, ProductoCrear, ProductoOut
from tiendapro.modelos import Producto

router = APIRouter()


@router.get("/health", response_model=HealthOut, tags=["meta"])
def health() -> HealthOut:
    return HealthOut(
        servicio="tiendapro",
        estado="ok",
        productos_en_db=len(repositorio.todos()),
    )


@router.get("/productos", response_model=list[ProductoOut], tags=["productos"])
def listar(
    categoria: str | None = None,
    solo_disponibles: bool = False,
) -> list[Producto]:
    if categoria is not None:
        return repositorio.por_categoria(categoria)
    if solo_disponibles:
        return repositorio.disponibles()
    return repositorio.todos()


@router.post(
    "/productos",
    response_model=ProductoOut,
    status_code=status.HTTP_201_CREATED,
    tags=["productos"],
)
def crear(nuevo: ProductoCrear) -> Producto:
    dto = Producto.model_validate(nuevo.model_dump())
    return repositorio.crear(dto)
```

### 3.6. Refactor de `src/tiendapro/api/app.py` con lifespan + middleware

```python
"""Construye la `FastAPI()`, registra rutas, exception handlers y middleware."""

import logging
import time
import uuid
from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response

from tiendapro.api.rutas import router
from tiendapro.catalogo import inicializar
from tiendapro.config import get_settings
from tiendapro.errores import (
    CatalogoInvalido,
    IntegracionError,
    ProductoNoEncontrado,
    TiendaProError,
)
from tiendapro.log import configurar_logging

log = logging.getLogger("tiendapro.api")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    configurar_logging(settings.log_level)
    log.info("startup", extra={"app": settings.app_name, "debug": settings.debug})

    seed = Path(__file__).resolve().parents[3] / "data" / "catalogo.json"
    productos = inicializar(seed if seed.exists() else None)
    log.info("DB lista", extra={"productos_en_db": productos})

    yield
    log.info("shutdown")


def _build_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="TiendaPro API",
        description="API REST de TiendaPro Lite — proyecto integrador del curso.",
        version="0.5.0",
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(router)
    _registrar_handlers(app)
    _registrar_middleware(app)
    return app


def _registrar_middleware(app: FastAPI) -> None:
    @app.middleware("http")
    async def trace(
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        request.state.request_id = uuid.uuid4().hex[:8]
        start = time.perf_counter()
        try:
            response = await call_next(request)
        except Exception:
            log.exception(
                "request error",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "request_id": request.state.request_id,
                },
            )
            raise
        latency_ms = int((time.perf_counter() - start) * 1000)
        log.info(
            "%s %s -> %d (%dms) [%s]",
            request.method,
            request.url.path,
            response.status_code,
            latency_ms,
            request.state.request_id,
        )
        response.headers["X-Request-ID"] = request.state.request_id
        return response


def _registrar_handlers(app: FastAPI) -> None:
    @app.exception_handler(ProductoNoEncontrado)
    async def _producto_no_encontrado(
        request: Request, exc: ProductoNoEncontrado
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": str(exc)},
        )

    @app.exception_handler(IntegracionError)
    async def _integracion(request: Request, exc: IntegracionError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_502_BAD_GATEWAY,
            content={"detail": "servicio externo no disponible", "info": str(exc)},
        )

    @app.exception_handler(CatalogoInvalido)
    async def _catalogo(request: Request, exc: CatalogoInvalido) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": str(exc)},
        )

    @app.exception_handler(TiendaProError)
    async def _tiendapro(request: Request, exc: TiendaProError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": str(exc)},
        )

    @app.exception_handler(RequestValidationError)
    async def _validacion(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        errores = [
            {
                "campo": ".".join(str(x) for x in e["loc"][1:]) or "(root)",
                "mensaje": e["msg"],
                "tipo": e["type"],
            }
            for e in exc.errors()
        ]
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": "datos inválidos", "errores": errores},
        )


app = _build_app()
```

### 3.7. `env.example` (versionado)

Crea `code/proyecto-integrador/env.example`:

```ini
TIENDAPRO_DEBUG=true
TIENDAPRO_DATABASE_URL=sqlite:///tiendapro.db
TIENDAPRO_API_KEY=cambia-esto-en-prod
TIENDAPRO_LOG_LEVEL=DEBUG
TIENDAPRO_ENABLE_ENRICHMENT=true
TIENDAPRO_CORS_ORIGINS=["http://localhost:3000","http://localhost:5173"]
```

(Si querés probar con un `.env` real, copialo con `cp env.example .env` — el `.env` ya está en el `.gitignore` global del repo.)

### 3.8. Probar el server

```bash
cd code/proyecto-integrador
uv run uvicorn tiendapro.api:app --reload --port 8000
```

Abrí `http://localhost:8000/docs`. Vas a ver:
- `GET /health`
- `GET /productos` (con `categoria` y `solo_disponibles`)
- `POST /productos`

Probá unos curls y mirá los logs:

```bash
curl -i http://localhost:8000/health
curl -s "http://localhost:8000/productos?solo_disponibles=true" | head -c 200
curl -s -X POST http://localhost:8000/productos -H "Content-Type: application/json" \
    -d '{"nombre":"Producto API","categoria":"test","precio":9.99,"stock":5}'
curl -i -X POST http://localhost:8000/productos -H "Content-Type: application/json" \
    -d '{"nombre":"","precio":-1}'   # 422 con tu formato
```

Cada request loguea método, path, status, latencia y `request_id`. La response trae `X-Request-ID`.

### 3.9. Verificar todo

```bash
uv run mypy src/ main.py
uv run ruff check .
uv run ruff format --check .
```

Los tres deberían pasar limpio.

### 3.10. Commit final + tag — CIERRE M5

```bash
git add code/proyecto-integrador
git commit -m "feat(proyecto-integrador): cierra M5 con FastAPI + pydantic-settings + logging (proyecto-m5)"
git tag proyecto-m5
git push origin main
git push origin proyecto-m5
```

**Felicitaciones — terminaste el Módulo 5.** TiendaPro Lite ahora:

- Es una **API REST funcional** con CRUD de productos.
- Es **configurable por entorno** sin tocar código.
- **Loguea estructuradamente** con `request_id` por request.
- **Traduce excepciones de dominio** a HTTP correctos.
- Sigue siendo **mypy/ruff limpio**.

### 3.11. Actualizar curriculum

En `docs/00-curriculum.md`:

```markdown
- [x] Módulo 5 — Construir una API real con FastAPI (3 sesiones) — tag `proyecto-m5`
```

Y en `code/proyecto-integrador/README.md`, actualizá el "estado actual" para reflejar M5.

```bash
git add docs/00-curriculum.md code/proyecto-integrador/README.md
git commit -m "docs(curriculum): marca M5 como completado en el roadmap"
git push origin main
```

---

Cuando termines, vuelve al README y responde las preguntas de auto-evaluación. Si todas se contestan sin dudar, M5 está consolidado y puedes pasar a [M6 — Herramientas del ingeniero](../../06-herramientas-ingeniero/) (cuando esté publicado).

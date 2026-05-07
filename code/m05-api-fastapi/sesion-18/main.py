"""Demo de S18 — Configuración con pydantic-settings + logging estructurado.

Levantá el server con:
    uv run uvicorn main:app --reload

Probá:
    curl -i http://localhost:8000/
    curl -s http://localhost:8000/explosivo

Verificá tipos y estilo:
    uv run mypy .
    uv run ruff check .
    uv run ruff format --check .

La demo arma una mini-app con:

1. Settings(BaseSettings) con env_file=".env" y env_prefix="DEMO_".
2. SecretStr para api_key (no se loguea por accidente).
3. Logger configurable por nivel desde la config.
4. Middleware HTTP que inyecta X-Request-ID y loguea cada request.
5. Lifespan moderno (en lugar de @app.on_event) que configura logging
   al startup.
6. Dependency-injection de Settings en handlers via @lru_cache + Depends.

Si no tenés `.env`, copiá `env.example`:
    cp env.example .env
"""

import logging
import time
import uuid
from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import asynccontextmanager
from functools import lru_cache
from typing import Annotated, Any, Literal

from fastapi import Depends, FastAPI, Request
from fastapi.responses import Response
from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

# ---------------------------------------------------------------------------
# 1. Settings con pydantic-settings
# ---------------------------------------------------------------------------


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
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"


@lru_cache
def get_settings() -> Settings:
    """Singleton — se construye una sola vez por proceso."""
    return Settings()


# ---------------------------------------------------------------------------
# 2. Logging
# ---------------------------------------------------------------------------


def configurar_logging(level: str = "INFO") -> None:
    logging.basicConfig(
        level=level.upper(),
        format="%(asctime)s %(levelname)-7s %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        force=True,
    )
    # No queremos el access log default de uvicorn — el nuestro lo cubre
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)


log = logging.getLogger("demo")


# ---------------------------------------------------------------------------
# 3. App con lifespan + middleware
# ---------------------------------------------------------------------------


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    configurar_logging(settings.log_level)
    log.info(
        "startup app=%s debug=%s log_level=%s",
        settings.app_name,
        settings.debug,
        settings.log_level,
    )
    yield
    log.info("shutdown")


app = FastAPI(title="Demo S18 — config + logging", lifespan=lifespan)


@app.middleware("http")
async def trace_middleware(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    request.state.request_id = uuid.uuid4().hex[:8]
    start = time.perf_counter()
    try:
        response = await call_next(request)
    except Exception:
        log.exception(
            "request error method=%s path=%s req_id=%s",
            request.method,
            request.url.path,
            request.state.request_id,
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


# ---------------------------------------------------------------------------
# 4. Handlers
# ---------------------------------------------------------------------------


SettingsDep = Annotated[Settings, Depends(get_settings)]


@app.get("/", tags=["meta"])
def root(settings: SettingsDep) -> dict[str, Any]:
    """Devuelve la config NO sensible. La api_key se ve enmascarada."""
    return {
        "app": settings.app_name,
        "debug": settings.debug,
        "log_level": settings.log_level,
        # IMPORTANTE: api_key se serializa como string ('**********') gracias a SecretStr
        # — solo `get_secret_value()` lo destapa, y nunca lo hacés en un response.
        "api_key": str(settings.api_key),
    }


@app.get("/secreto", tags=["meta"])
def secreto(settings: SettingsDep) -> dict[str, str]:
    """Demo de SecretStr: muestra que `str(api_key)` esconde el valor."""
    return {
        "repr": repr(settings.api_key),
        "str": str(settings.api_key),
        # NUNCA hagas esto en un endpoint real — solo para la demo:
        "unsafe_value": settings.api_key.get_secret_value(),
    }


@app.get("/explosivo", tags=["meta"])
def explosivo() -> dict[str, str]:
    """Lanza un error a propósito para mostrar el log de excepción."""
    raise RuntimeError("simulación de error con stack trace")


@app.get("/lento", tags=["meta"])
def lento() -> dict[str, str]:
    """Simula un endpoint lento — vas a ver la latencia en el log."""
    time.sleep(0.5)
    return {"ok": "tardé 500ms"}

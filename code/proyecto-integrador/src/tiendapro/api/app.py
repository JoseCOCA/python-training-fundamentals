"""Construye la `FastAPI()`, registra rutas, exception handlers y middleware.

`app` se construye al cargar el módulo. El startup (lifespan) configura
logging y bootstrappea la DB con el seed JSON la primera vez.
"""

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
    log.info(
        "startup app=%s debug=%s log_level=%s",
        settings.app_name,
        settings.debug,
        settings.log_level,
    )

    seed = Path(__file__).resolve().parents[3] / "data" / "catalogo.json"
    productos_en_db = inicializar(seed if seed.exists() else None)
    log.info("DB lista — %d productos", productos_en_db)

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


def _registrar_handlers(app: FastAPI) -> None:
    @app.exception_handler(ProductoNoEncontrado)
    async def _producto_no_encontrado(request: Request, exc: ProductoNoEncontrado) -> JSONResponse:
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
    async def _validacion(request: Request, exc: RequestValidationError) -> JSONResponse:
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

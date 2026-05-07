"""Demo de S16 — FastAPI fundamentos.

Levantá el server con:
    uv run uvicorn main:app --reload

Después abrí:
    http://localhost:8000/        — la raíz
    http://localhost:8000/docs    — Swagger UI interactivo
    http://localhost:8000/redoc   — ReDoc (alternativa de docs)

Verificá tipos y estilo:
    uv run mypy .
    uv run ruff check .
    uv run ruff format --check .

La demo es una mini-API de productos (sin DB — datos en memoria) con:
- GET / — root.
- GET /productos — listar con query params (categoria, limit).
- GET /productos/{id} — obtener uno (404 si no existe).
- POST /productos — crear con body validado (201).
- DELETE /productos/{id} — borrar (204).

Nota: El estado vive en una variable de módulo. Eso es intencional para
la demo — en una app real (M5 hito), el estado vive en la DB del integrador.
"""

from typing import Any

from fastapi import FastAPI, HTTPException, Query, status
from pydantic import BaseModel, ConfigDict, Field

app = FastAPI(
    title="TiendaPro API (demo S16)",
    description="Mini-API de productos para entrenar los reflejos de FastAPI.",
    version="0.1.0",
)


# ---------------------------------------------------------------------------
# Modelos
# ---------------------------------------------------------------------------


class ProductoNuevo(BaseModel):
    """Modelo de entrada (request body)."""

    model_config = ConfigDict(extra="forbid")

    nombre: str = Field(min_length=1, max_length=120)
    categoria: str = Field(min_length=1, max_length=40)
    precio: float = Field(gt=0)
    stock: int = Field(ge=0, default=0)


class Producto(BaseModel):
    """Modelo de salida (response). Incluye `id` que asigna el server."""

    id: int
    nombre: str
    categoria: str
    precio: float
    stock: int


# ---------------------------------------------------------------------------
# "Base de datos" en memoria
# ---------------------------------------------------------------------------


_PRODUCTOS: dict[int, Producto] = {
    1: Producto(id=1, nombre="Cable USB", categoria="accesorios", precio=12.5, stock=30),
    2: Producto(id=2, nombre="Auriculares", categoria="audio", precio=89.99, stock=5),
    3: Producto(id=3, nombre="Teclado", categoria="computación", precio=49.5, stock=12),
    4: Producto(id=4, nombre="Monitor 4K", categoria="computación", precio=320.0, stock=3),
}
_proximo_id = 5


# ---------------------------------------------------------------------------
# Rutas
# ---------------------------------------------------------------------------


@app.get("/", tags=["meta"])
def root() -> dict[str, str]:
    return {"servicio": "TiendaPro API (demo S16)", "version": app.version}


@app.get("/productos", tags=["productos"])
def listar(
    categoria: str | None = Query(default=None, description="Filtra por categoría exacta"),
    limit: int = Query(default=20, ge=1, le=100),
) -> list[Producto]:
    productos = list(_PRODUCTOS.values())
    if categoria is not None:
        productos = [p for p in productos if p.categoria == categoria]
    return productos[:limit]


@app.get("/productos/{producto_id}", tags=["productos"])
def obtener(producto_id: int) -> Producto:
    if producto_id not in _PRODUCTOS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"producto {producto_id} no existe",
        )
    return _PRODUCTOS[producto_id]


@app.post(
    "/productos",
    tags=["productos"],
    status_code=status.HTTP_201_CREATED,
    description="Crea un producto. El `id` lo asigna el servidor.",
)
def crear(nuevo: ProductoNuevo) -> Producto:
    global _proximo_id
    producto = Producto(
        id=_proximo_id,
        nombre=nuevo.nombre,
        categoria=nuevo.categoria,
        precio=nuevo.precio,
        stock=nuevo.stock,
    )
    _PRODUCTOS[_proximo_id] = producto
    _proximo_id += 1
    return producto


@app.delete(
    "/productos/{producto_id}",
    tags=["productos"],
    status_code=status.HTTP_204_NO_CONTENT,
)
def borrar(producto_id: int) -> None:
    if producto_id not in _PRODUCTOS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"producto {producto_id} no existe",
        )
    del _PRODUCTOS[producto_id]


# ---------------------------------------------------------------------------
# Demo de async vs sync (mismo endpoint, dos sabores)
# ---------------------------------------------------------------------------


@app.get("/sync-pesado", tags=["meta"])
def sync_pesado() -> dict[str, Any]:
    """Handler sync. FastAPI lo despacha al thread pool — no bloquea el loop."""
    # Simulamos trabajo CPU-bound corto. En un caso real, esto podría ser
    # una llamada a SQLAlchemy sync, leer un archivo, etc.
    suma = sum(i * i for i in range(100_000))
    return {"resultado": suma}


@app.get("/async-ligero", tags=["meta"])
async def async_ligero() -> dict[str, str]:
    """Handler async. Útil cuando adentro hay I/O async (httpx, asyncpg, ...).

    Si vas a meter `time.sleep` o llamadas sync bloqueantes, NO lo declares
    async — bloquearías el event loop.
    """
    return {"hint": "usá async cuando tengas I/O async adentro"}

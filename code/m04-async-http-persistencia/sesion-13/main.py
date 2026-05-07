"""Demo de S13 — httpx + JSON + pydantic.

Ejecuta el programa con:
    uv run python main.py

Verifica los tipos con:
    uv run mypy .

Verifica el estilo con:
    uv run ruff check .
    uv run ruff format --check .

Cuatro demos:
1. Sync con httpx.Client + parseo a pydantic.
2. Async con httpx.AsyncClient + asyncio.gather (concurrencia real).
3. Manejo de errores: 404, 5xx, red caída, body inválido — todos a IntegracionError.
4. POST con json= y body que sale de un BaseModel.

Todas las demos corren contra un MockTransport: NO requiere internet ni servidor.
"""

import asyncio
import json
import time
from typing import Any

import httpx
from pydantic import BaseModel, ConfigDict, ValidationError, field_validator


def seccion(titulo: str) -> None:
    print()
    print("=" * 60)
    print(titulo)
    print("=" * 60)


# ---------------------------------------------------------------------------
# Modelos de dominio
# ---------------------------------------------------------------------------


class Producto(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    sku: str
    nombre: str
    precio: float
    stock: int

    @field_validator("precio")
    @classmethod
    def precio_positivo(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("precio debe ser positivo")
        return v


class IntegracionError(Exception):
    """Falla al hablar con el servicio externo."""


# ---------------------------------------------------------------------------
# Mock server con httpx.MockTransport — sin red ni servidor real
# ---------------------------------------------------------------------------


CATALOGO: dict[str, dict[str, Any]] = {
    "ABC": {"sku": "ABC", "nombre": "Cable USB", "precio": 12.5, "stock": 30},
    "XYZ": {"sku": "XYZ", "nombre": "Auriculares", "precio": 89.99, "stock": 5},
    "DEF": {"sku": "DEF", "nombre": "Teclado", "precio": 49.5, "stock": 12},
    "MAL": {"sku": "MAL", "nombre": "Roto", "precio": -1.0, "stock": 0},
}


def mock_handler(request: httpx.Request) -> httpx.Response:
    """Mini-API que simula un catálogo. Soporta GET y POST."""
    path = request.url.path

    if request.method == "GET" and path.startswith("/productos/"):
        sku = path.rsplit("/", 1)[-1]
        if sku == "BOOM":
            return httpx.Response(500, json={"error": "internal"})
        if sku in CATALOGO:
            return httpx.Response(200, json=CATALOGO[sku])
        return httpx.Response(404, json={"error": "not found", "sku": sku})

    if request.method == "POST" and path == "/productos":
        body = json.loads(request.content)
        body["sku"] = "GEN-" + str(body.get("nombre", ""))[:3].upper()
        return httpx.Response(201, json=body)

    return httpx.Response(400, json={"error": "ruta desconocida", "path": path})


def mock_transport() -> httpx.MockTransport:
    return httpx.MockTransport(mock_handler)


# ---------------------------------------------------------------------------
# 1. Sync: httpx.Client + raise_for_status + model_validate
# ---------------------------------------------------------------------------


def obtener_sync(sku: str) -> Producto:
    with httpx.Client(
        transport=mock_transport(), base_url="http://api.local", timeout=5.0
    ) as client:
        r = client.get(f"/productos/{sku}")
        r.raise_for_status()
        return Producto.model_validate(r.json())


def demo_sync() -> None:
    seccion("1. Sync — httpx.Client + pydantic.model_validate")
    p = obtener_sync("ABC")
    print(f"  {p}")
    print(f"  precio inferido: {p.precio} (tipo: {type(p.precio).__name__})")


# ---------------------------------------------------------------------------
# 2. Async: AsyncClient + gather con un cliente compartido
# ---------------------------------------------------------------------------


async def obtener_async(client: httpx.AsyncClient, sku: str) -> Producto:
    r = await client.get(f"/productos/{sku}")
    r.raise_for_status()
    return Producto.model_validate(r.json())


async def obtener_varios(skus: list[str]) -> list[Producto]:
    async with httpx.AsyncClient(
        transport=mock_transport(), base_url="http://api.local", timeout=5.0
    ) as client:
        return await asyncio.gather(*[obtener_async(client, sku) for sku in skus])


async def demo_async_concurrente() -> None:
    seccion("2. Async — AsyncClient + gather (cliente compartido)")
    inicio = time.perf_counter()
    productos = await obtener_varios(["ABC", "XYZ", "DEF"])
    print(f"  {len(productos)} productos en {time.perf_counter() - inicio:.3f}s")
    for p in productos:
        print(f"    - {p.sku}: {p.nombre}  ${p.precio}")


# ---------------------------------------------------------------------------
# 3. Manejo de errores: 404, 5xx, validación
# ---------------------------------------------------------------------------


async def obtener_seguro(client: httpx.AsyncClient, sku: str) -> Producto:
    """Traduce todos los modos de falla a IntegracionError."""
    try:
        r = await client.get(f"/productos/{sku}")
        r.raise_for_status()
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise IntegracionError(f"sku no existe: {sku}") from e
        raise IntegracionError(f"HTTP {e.response.status_code} para {sku}") from e
    except httpx.RequestError as e:
        raise IntegracionError(f"red al pedir {sku}: {e}") from e

    try:
        return Producto.model_validate(r.json())
    except ValidationError as e:
        # El producto MAL tiene precio negativo: el server lo devuelve, pero
        # nuestra validación lo rechaza acá, en la frontera.
        raise IntegracionError(f"respuesta inválida para {sku}: {e.error_count()} errores") from e


async def demo_errores() -> None:
    seccion("3. Errores — 404, 5xx y body inválido se traducen al dominio")
    async with httpx.AsyncClient(
        transport=mock_transport(), base_url="http://api.local", timeout=5.0
    ) as client:
        for sku in ["ABC", "NOPE", "BOOM", "MAL"]:
            try:
                p = await obtener_seguro(client, sku)
                print(f"  [OK ]   {sku}: {p.nombre}")
            except IntegracionError as e:
                print(f"  [ERR]   {sku}: {e}")


# ---------------------------------------------------------------------------
# 4. POST con body que sale de un BaseModel
# ---------------------------------------------------------------------------


class ProductoNuevo(BaseModel):
    nombre: str
    precio: float
    stock: int


async def crear(client: httpx.AsyncClient, nuevo: ProductoNuevo) -> Producto:
    r = await client.post("/productos", json=nuevo.model_dump())
    r.raise_for_status()
    return Producto.model_validate(r.json())


async def demo_post() -> None:
    seccion("4. POST con json=modelo.model_dump()")
    nuevo = ProductoNuevo(nombre="Mouse Pad XL", precio=15.0, stock=20)
    async with httpx.AsyncClient(
        transport=mock_transport(), base_url="http://api.local", timeout=5.0
    ) as client:
        creado = await crear(client, nuevo)
    print(f"  enviado : {nuevo}")
    print(f"  creado  : {creado}")
    print(f"  sku generado por el servidor: {creado.sku}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


async def main_async() -> None:
    await demo_async_concurrente()
    await demo_errores()
    await demo_post()


if __name__ == "__main__":
    demo_sync()
    asyncio.run(main_async())

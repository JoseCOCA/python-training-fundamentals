"""Cliente HTTP para enriquecer el catálogo desde una 'API externa'.

En este hito (M4) la API es **simulada** con `httpx.MockTransport` — no
hay servidor real ni dependencia de internet. Cuando el ecosistema lo
demande (M5/M6), el `httpx.AsyncClient` apunta a una URL real y el código
de los consumidores no necesita cambiar.

La capa expone:

- `enriquecer(nombres, paralelismo=5) -> dict[str, EnriquecimientoExterno]`

que aprovecha `asyncio.gather` con un semáforo para no saturar la API.
"""

import asyncio
from collections.abc import Iterable
from typing import Any

import httpx
from pydantic import ValidationError

from tiendapro.errores import IntegracionError
from tiendapro.modelos import EnriquecimientoExterno

# La "base de datos" de la API mock — sólo unos productos tienen entrada
DATOS_FALSOS: dict[str, dict[str, Any]] = {
    "Auriculares Bluetooth": {
        "sku": "AUR-BT",
        "descripcion": "Auriculares con cancelación activa de ruido",
        "rating": 4.4,
    },
    "Teclado Mecánico": {
        "sku": "TEC-MEC",
        "descripcion": "Teclado mecánico con switches azules",
        "rating": 4.7,
    },
    "Monitor 4K": {
        "sku": "MON-4K",
        "descripcion": 'Monitor 27" 4K UHD con HDR',
        "rating": 4.5,
    },
}


def _handler(request: httpx.Request) -> httpx.Response:
    nombre = request.url.params.get("nombre", "")
    if nombre in DATOS_FALSOS:
        return httpx.Response(200, json=DATOS_FALSOS[nombre])
    return httpx.Response(404, json={"error": "no enrichment", "nombre": nombre})


def _transporte() -> httpx.MockTransport:
    return httpx.MockTransport(_handler)


async def _enriquecer_uno(client: httpx.AsyncClient, nombre: str) -> EnriquecimientoExterno | None:
    """Devuelve el enriquecimiento si existe, `None` si la API responde 404.

    Solo eleva `IntegracionError` para fallos NO esperables (5xx, red, JSON
    inválido). Los 404 son parte normal del flujo (no todos los productos
    tienen ficha enriquecida) y se silencian devolviendo `None`.
    """
    try:
        r = await client.get("/enriquecer", params={"nombre": nombre})
        if r.status_code == 404:
            return None
        r.raise_for_status()
    except httpx.HTTPStatusError as e:
        raise IntegracionError(
            f"HTTP {e.response.status_code} pidiendo enriquecimiento de {nombre!r}"
        ) from e
    except httpx.RequestError as e:
        raise IntegracionError(f"red al enriquecer {nombre!r}: {e}") from e

    try:
        return EnriquecimientoExterno.model_validate(r.json())
    except ValidationError as e:
        raise IntegracionError(f"respuesta inválida para {nombre!r}: {e}") from e


async def enriquecer(
    nombres: Iterable[str], paralelismo: int = 5
) -> dict[str, EnriquecimientoExterno]:
    """Enriquece una lista de nombres en paralelo, limitando concurrencia.

    Devuelve un dict `{nombre → EnriquecimientoExterno}` para los nombres
    que la API conoce. Los productos sin entrada en la API NO aparecen
    en el dict (404 es parte del flujo normal).
    """
    semaforo = asyncio.Semaphore(paralelismo)

    async def _run(
        client: httpx.AsyncClient, nombre: str
    ) -> tuple[str, EnriquecimientoExterno | None]:
        async with semaforo:
            return nombre, await _enriquecer_uno(client, nombre)

    async with httpx.AsyncClient(
        transport=_transporte(), base_url="http://api.local", timeout=5.0
    ) as client:
        resultados = await asyncio.gather(*[_run(client, n) for n in nombres])

    return {nombre: enr for nombre, enr in resultados if enr is not None}

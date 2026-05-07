"""Catálogo: API que el resto de la app consume.

Hasta M3 esta capa leía un JSON. A partir del hito M4 delega en
`repositorio` — los datos viven en SQLite y la primera ejecución de
la app importa el JSON de seed automáticamente. La firma pública NO
cambió: `main.py` y `presentacion.py` siguen recibiendo `Producto`
(DTO pydantic) sin enterarse de que cambió la fuente.
"""

from collections.abc import Iterable
from pathlib import Path

from tiendapro import repositorio
from tiendapro.modelos import Producto


def inicializar(seed_json: Path | None = None) -> int:
    """Bootstrap de la DB. Idempotente."""
    return repositorio.inicializar(seed_json)


def cargar() -> list[Producto]:
    """Devuelve TODOS los productos (incluyendo los con stock 0)."""
    return repositorio.todos()


def disponibles() -> list[Producto]:
    """Productos con stock > 0, ordenados por precio asc.

    El filtro y el orden se hacen en la DB (SQL: `WHERE stock > 0
    ORDER BY precio`), no en Python. Eso escala con el catálogo.
    """
    return repositorio.disponibles()


def ordenar_por_precio(productos: Iterable[Producto]) -> list[Producto]:
    """Reordena un iterable ya cargado por precio ascendente.

    Mantiene la firma de M3 para que código que prepara listas en memoria
    siga funcionando. Para leer ordenado desde la DB, usá `disponibles()`.
    """
    return sorted(productos, key=lambda p: p.precio)

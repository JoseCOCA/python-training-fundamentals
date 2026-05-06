"""Carga, filtrado y ordenamiento del catálogo de productos."""

import json
from collections.abc import Iterable, Iterator
from pathlib import Path

from pydantic import ValidationError

from tiendapro.errores import CatalogoInvalido
from tiendapro.modelos import Producto


def cargar(ruta: Path) -> list[Producto]:
    """Lee el JSON y devuelve una lista de Producto validada con pydantic.

    Lanza:
        CatalogoInvalido: si el archivo no existe, no es JSON válido o no
            tiene la estructura esperada, o si algún producto no pasa la
            validación de dominio.
    """
    try:
        with ruta.open(encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError as e:
        raise CatalogoInvalido(f"Archivo de catálogo no encontrado: {ruta}") from e
    except json.JSONDecodeError as e:
        raise CatalogoInvalido(f"JSON inválido en {ruta}: {e.msg}") from e

    if not isinstance(data, list):
        raise CatalogoInvalido(f"El catálogo debe ser una lista, recibí {type(data).__name__}")

    productos: list[Producto] = []
    for i, item in enumerate(data):
        try:
            productos.append(Producto.model_validate(item))
        except ValidationError as e:
            raise CatalogoInvalido(f"Producto inválido en posición {i}: {e}") from e

    return productos


def disponibles(productos: Iterable[Producto]) -> Iterator[Producto]:
    """Generador de productos con stock > 0.

    Lazy: produce uno a la vez. Útil cuando el catálogo crece y se quiere
    encadenar con otros pasos del pipeline sin materializar listas
    intermedias.
    """
    for p in productos:
        if p.disponible():
            yield p


def ordenar_por_precio(productos: Iterable[Producto]) -> list[Producto]:
    """Devuelve los productos ordenados por precio ascendente."""
    return sorted(productos, key=lambda p: p.precio)

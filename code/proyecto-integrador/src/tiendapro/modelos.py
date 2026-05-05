"""Modelos de dominio de TiendaPro.

Tipos de valor inmutables (frozen=True) que representan las entidades
principales del dominio. En M3 se les agregará validación con pydantic;
por ahora la validación vive en `catalogo.py` al construir cada Producto.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Producto:
    nombre: str
    categoria: str
    precio: float
    stock: int
    moneda: str = "USD"

    def disponible(self) -> bool:
        return self.stock > 0

    def valor_inventario(self) -> float:
        return self.precio * self.stock


@dataclass(frozen=True)
class Cliente:
    """Placeholder. Se conectará con la base de datos en M4."""

    id: int
    nombre: str
    email: str

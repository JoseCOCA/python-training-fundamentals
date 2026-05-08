"""Calculadora de descuentos — código bajo test.

Funciones puras (sin IO) + un Carrito con estado mutable. La función
`tasa_iva_actual` simula una dependencia externa (en el ejercicio se
mockea con monkeypatch).
"""

from __future__ import annotations

from dataclasses import dataclass, field


def aplicar_descuento(precio: float, porcentaje: int) -> float:
    """Reduce el precio en `porcentaje` (0..100). No muta nada."""
    if porcentaje < 0 or porcentaje > 100:
        raise ValueError(f"porcentaje fuera de rango [0, 100]: {porcentaje}")
    return precio * (1 - porcentaje / 100)


def tasa_iva_actual() -> float:
    """Imaginá que esto consulta una API tributaria.

    En tests reemplazalo con monkeypatch: nunca pegamos a una API real.
    """
    return 0.21  # default razonable


def precio_con_iva(precio: float) -> float:
    """Precio + IVA, leyendo la tasa actual."""
    tasa = tasa_iva_actual()
    return round(precio * (1 + tasa), 2)


@dataclass
class Carrito:
    """Carrito simple con items (nombre, precio)."""

    items: list[tuple[str, float]] = field(default_factory=list)

    def agregar(self, nombre: str, precio: float) -> None:
        if precio <= 0:
            raise ValueError("el precio debe ser positivo")
        self.items.append((nombre, precio))

    def total(self) -> float:
        return sum(precio for _, precio in self.items)

    def total_con_descuento(self, porcentaje: int) -> float:
        return aplicar_descuento(self.total(), porcentaje)

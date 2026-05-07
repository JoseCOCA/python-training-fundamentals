"""TiendaPro Lite — paquete del proyecto integrador.

Re-exporta los símbolos públicos del paquete. Los consumidores externos
(empezando por `main.py`) deberían importar solo desde `tiendapro`, no
desde sus módulos internos.
"""

from tiendapro.errores import (
    CatalogoInvalido,
    IntegracionError,
    ProductoNoEncontrado,
    TiendaProError,
)
from tiendapro.modelos import Cliente, EnriquecimientoExterno, Producto

__all__ = [
    "CatalogoInvalido",
    "Cliente",
    "EnriquecimientoExterno",
    "IntegracionError",
    "Producto",
    "ProductoNoEncontrado",
    "TiendaProError",
]

"""TiendaPro Lite — paquete del proyecto integrador.

Re-exporta los símbolos públicos del paquete. Los consumidores externos
(empezando por `main.py`) deberían importar solo desde `tiendapro`, no
desde sus módulos internos.
"""

from tiendapro.errores import (
    CatalogoInvalido,
    ProductoNoEncontrado,
    TiendaProError,
)
from tiendapro.modelos import Cliente, Producto

__all__ = [
    "CatalogoInvalido",
    "Cliente",
    "Producto",
    "ProductoNoEncontrado",
    "TiendaProError",
]

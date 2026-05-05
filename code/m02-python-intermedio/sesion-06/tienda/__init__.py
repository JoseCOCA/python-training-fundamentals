"""Paquete `tienda` — demo del Módulo 2.

Marca este directorio como paquete importable. Aquí se pueden re-exportar
nombres para simplificar el uso desde fuera. Por ejemplo, en lugar de:

    from tienda.productos import listar
    from tienda.clientes import crear

el consumidor puede escribir:

    from tienda import listar, crear
"""

from tienda.clientes import crear
from tienda.productos import listar

__all__ = ["crear", "listar"]

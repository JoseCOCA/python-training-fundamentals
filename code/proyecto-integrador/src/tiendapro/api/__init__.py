"""Paquete de la API REST de TiendaPro.

`from tiendapro.api import app` te da la `FastAPI()` lista para servir.
"""

from tiendapro.api.app import app

__all__ = ["app"]

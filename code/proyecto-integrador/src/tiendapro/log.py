"""Configuración de logging estructurado.

`configurar_logging` se llama UNA VEZ al startup (en `api/app.py` desde
el lifespan). Después, cada módulo obtiene su logger con
`logging.getLogger(__name__)`.
"""

import logging
import sys


def configurar_logging(level: str = "INFO") -> None:
    logging.basicConfig(
        level=level.upper(),
        format="%(asctime)s %(levelname)-7s %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        stream=sys.stdout,
        force=True,
    )
    # Reducí el ruido de uvicorn access log: nuestro middleware lo cubre
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

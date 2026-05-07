"""Conexión a la base de datos: engine, sesión y bootstrap del schema.

Este módulo encapsula los detalles de SQLAlchemy. El resto del paquete
no debería tener que importar nada de `sqlalchemy.*` directamente.

La URL de conexión sale de `Settings.database_url` (S18) — por defecto
SQLite local; en producción cambia la env var y este módulo no se entera.
"""

from collections.abc import Iterator
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from tiendapro.config import get_settings
from tiendapro.orm import Base


def _build_engine() -> Engine:
    settings = get_settings()
    return create_engine(settings.database_url, echo=False, future=True)


_engine: Engine = _build_engine()


def crear_schema() -> None:
    """Crea las tablas si no existen. Idempotente."""
    Base.metadata.create_all(_engine)


@contextmanager
def obtener_sesion() -> Iterator[Session]:
    """Context manager que abre, hace commit/rollback y cierra la sesión.

    Si el bloque sale sin excepción, hace commit. Si lanza algo, hace
    rollback y re-propaga.
    """
    session = Session(_engine)
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

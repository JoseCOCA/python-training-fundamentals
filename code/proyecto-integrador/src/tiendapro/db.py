"""Conexión a la base de datos: engine, sesión y bootstrap del schema.

Este módulo encapsula los detalles de SQLAlchemy. El resto del paquete
no debería tener que importar nada de `sqlalchemy.*` directamente.

URL por default: SQLite local (`tiendapro.db` en la raíz del integrador).
Para cambiar a Postgres en producción, basta con setear la URL — el resto
del código no cambia (esa es la promesa del ORM).
"""

from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from tiendapro.orm import Base

DB_PATH = Path(__file__).resolve().parents[2] / "tiendapro.db"
URL = f"sqlite:///{DB_PATH}"

_engine = create_engine(URL, echo=False, future=True)


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

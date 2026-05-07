"""Repositorio: API de acceso a datos.

Es el ÚNICO módulo del paquete que conoce SQLAlchemy. Devuelve y recibe
DTOs pydantic. Los demás módulos (catalogo, presentacion, main) NO
importan ni `orm` ni `sqlalchemy` — esa restricción es la que desacopla
la persistencia del dominio.

Funciones públicas:

- `inicializar(seed)` — crea el schema y, si no hay productos, importa
  desde un JSON de seed.
- `todos()`, `disponibles()`, `por_categoria(categoria)` — lecturas.
- `crear(dto)` — alta.
"""

import json
from pathlib import Path

from pydantic import ValidationError
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from tiendapro.db import crear_schema, obtener_sesion
from tiendapro.errores import CatalogoInvalido
from tiendapro.modelos import Producto
from tiendapro.orm import ProductoORM


def inicializar(seed: Path | None = None) -> int:
    """Crea el schema (si falta) y, si la tabla está vacía, importa el JSON.

    Devuelve la cantidad de productos en la base al terminar.
    """
    crear_schema()
    with obtener_sesion() as session:
        existentes = session.scalar(select(func.count()).select_from(ProductoORM)) or 0
        if existentes == 0 and seed is not None:
            _importar_seed(session, seed)
            existentes = session.scalar(select(func.count()).select_from(ProductoORM)) or 0
        return int(existentes)


def todos() -> list[Producto]:
    """Devuelve TODOS los productos, ordenados por id."""
    with obtener_sesion() as session:
        rows = session.scalars(select(ProductoORM).order_by(ProductoORM.id)).all()
        return [_to_dto(p) for p in rows]


def disponibles() -> list[Producto]:
    """Productos con stock > 0, ordenados por precio asc."""
    with obtener_sesion() as session:
        rows = session.scalars(
            select(ProductoORM).where(ProductoORM.stock > 0).order_by(ProductoORM.precio.asc())
        ).all()
        return [_to_dto(p) for p in rows]


def por_categoria(categoria: str) -> list[Producto]:
    with obtener_sesion() as session:
        rows = session.scalars(
            select(ProductoORM)
            .where(ProductoORM.categoria == categoria)
            .order_by(ProductoORM.precio.asc())
        ).all()
        return [_to_dto(p) for p in rows]


def crear(dto: Producto) -> Producto:
    """Persiste un Producto y devuelve el DTO refrescado (con id asignado)."""
    with obtener_sesion() as session:
        orm = _to_orm(dto)
        session.add(orm)
        session.flush()
        return _to_dto(orm)


# ---------------------------------------------------------------------------
# Internos
# ---------------------------------------------------------------------------


def _importar_seed(session: Session, ruta: Path) -> None:
    try:
        with ruta.open(encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError as e:
        raise CatalogoInvalido(f"Archivo de catálogo no encontrado: {ruta}") from e
    except json.JSONDecodeError as e:
        raise CatalogoInvalido(f"JSON inválido en {ruta}: {e.msg}") from e

    if not isinstance(data, list):
        raise CatalogoInvalido(f"El catálogo debe ser una lista, recibí {type(data).__name__}")

    for i, item in enumerate(data):
        try:
            dto = Producto.model_validate(item)
        except ValidationError as e:
            raise CatalogoInvalido(f"Producto inválido en posición {i}: {e}") from e
        session.add(_to_orm(dto))


def _to_orm(dto: Producto) -> ProductoORM:
    return ProductoORM(
        nombre=dto.nombre,
        categoria=dto.categoria,
        precio=dto.precio,
        stock=dto.stock,
    )


def _to_dto(orm: ProductoORM) -> Producto:
    return Producto.model_validate(
        {
            "nombre": orm.nombre,
            "categoria": orm.categoria,
            "precio": orm.precio,
            "stock": orm.stock,
        }
    )

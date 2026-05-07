"""Rutas REST de TiendaPro (CRUD productos + health).

Las rutas reciben DTOs (entrada), llaman al repositorio (S15) y devuelven
los DTOs de salida `ProductoOut`. Los exception handlers globales (en
`app.py`) traducen las excepciones de dominio a HTTP — los handlers
quedan sin try/except.
"""

from fastapi import APIRouter, status

from tiendapro import repositorio
from tiendapro.api.dtos import HealthOut, ProductoCrear, ProductoOut
from tiendapro.modelos import Producto

router = APIRouter()


@router.get("/health", response_model=HealthOut, tags=["meta"])
def health() -> HealthOut:
    return HealthOut(
        servicio="tiendapro",
        estado="ok",
        productos_en_db=len(repositorio.todos()),
    )


@router.get("/productos", response_model=list[ProductoOut], tags=["productos"])
def listar(
    categoria: str | None = None,
    solo_disponibles: bool = False,
) -> list[Producto]:
    if categoria is not None:
        return repositorio.por_categoria(categoria)
    if solo_disponibles:
        return repositorio.disponibles()
    return repositorio.todos()


@router.post(
    "/productos",
    response_model=ProductoOut,
    status_code=status.HTTP_201_CREATED,
    tags=["productos"],
)
def crear(nuevo: ProductoCrear) -> Producto:
    dto = Producto.model_validate(nuevo.model_dump())
    return repositorio.crear(dto)

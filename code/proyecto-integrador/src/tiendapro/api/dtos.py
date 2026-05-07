"""DTOs de la API (Request / Response).

Separados de los modelos de dominio (`tiendapro.modelos`, BaseModel) y
de los modelos ORM (`tiendapro.orm`, SQLAlchemy). Cada DTO viaja entre
cliente y API; ninguno se persiste tal cual.
"""

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ProductoCrear(BaseModel):
    """Lo que el cliente manda en POST /productos."""

    model_config = ConfigDict(extra="forbid")

    nombre: str = Field(min_length=1, max_length=120, examples=["Cable USB-C"])
    categoria: str = Field(min_length=1, max_length=40, examples=["accesorios"])
    precio: float = Field(gt=0, le=1_000_000)
    stock: int = Field(ge=0, default=0)

    @field_validator("nombre", "categoria")
    @classmethod
    def normalizar(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("no puede estar vacío")
        return v


class ProductoOut(BaseModel):
    """Lo que la API devuelve en GET / POST. Mapea desde el DTO interno."""

    model_config = ConfigDict(from_attributes=True)

    nombre: str
    categoria: str
    precio: float
    stock: int


class HealthOut(BaseModel):
    servicio: str
    estado: str
    productos_en_db: int

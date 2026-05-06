"""Modelos de dominio de TiendaPro (validación con pydantic v2).

Los modelos son inmutables (frozen=True) y rechazan campos extra
(extra="forbid"). Las reglas de negocio (precio positivo, stock no
negativo, email con formato básico) viven aquí, no en quien construye
el modelo. Esa es la propuesta de pydantic: la validación está donde
están los datos.
"""

from pydantic import BaseModel, ConfigDict, field_validator


class Producto(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    nombre: str
    categoria: str
    precio: float
    stock: int
    moneda: str = "USD"

    @field_validator("nombre", "categoria")
    @classmethod
    def texto_no_vacio(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("no puede estar vacío")
        return v

    @field_validator("precio")
    @classmethod
    def precio_positivo(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("el precio debe ser positivo")
        return v

    @field_validator("stock")
    @classmethod
    def stock_no_negativo(cls, v: int) -> int:
        if v < 0:
            raise ValueError("el stock no puede ser negativo")
        return v

    def disponible(self) -> bool:
        return self.stock > 0

    def valor_inventario(self) -> float:
        return self.precio * self.stock


class Cliente(BaseModel):
    """Placeholder. Se conectará con la base de datos en M4."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    id: int
    nombre: str
    email: str

    @field_validator("email")
    @classmethod
    def email_basico(cls, v: str) -> str:
        v = v.strip()
        if "@" not in v or "." not in v.split("@")[-1]:
            raise ValueError("formato de email inválido")
        return v

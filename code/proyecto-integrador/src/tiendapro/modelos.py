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
    """DTO de Cliente (se conecta con `ClienteORM` en repositorio.py)."""

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


class EnriquecimientoExterno(BaseModel):
    """Datos extra que vienen de la 'API de catálogo enriquecido'.

    Es el modelo de borde para `tiendapro/integraciones.py`. Cuando llega
    una respuesta JSON desde la API externa, se valida con este modelo
    antes de exponerla al resto del paquete.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    sku: str
    descripcion: str
    rating: float

    @field_validator("rating")
    @classmethod
    def rating_en_rango(cls, v: float) -> float:
        if not 0.0 <= v <= 5.0:
            raise ValueError("rating debe estar entre 0 y 5")
        return v

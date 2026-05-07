"""Modelos SQLAlchemy v2 — la capa de persistencia.

Estos NO son los modelos de dominio (esos viven en `modelos.py` con
pydantic). Son la representación de las tablas tal como se persisten.
La traducción entre DTO pydantic y modelo ORM ocurre exclusivamente en
`repositorio.py`. El resto del paquete no importa SQLAlchemy.

Convención del integrador: las clases ORM usan sufijo `ORM` para que
nunca se confundan con los DTOs pydantic homónimos (`Producto` vs
`ProductoORM`).
"""

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class ClienteORM(Base):
    __tablename__ = "cliente"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(120), unique=True)


class ProductoORM(Base):
    __tablename__ = "producto"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(120), unique=True)
    categoria: Mapped[str] = mapped_column(String(40))
    precio: Mapped[float]
    stock: Mapped[int] = mapped_column(default=0)


class PedidoORM(Base):
    __tablename__ = "pedido"

    id: Mapped[int] = mapped_column(primary_key=True)
    cliente_id: Mapped[int] = mapped_column(ForeignKey("cliente.id"))

    lineas: Mapped[list["LineaPedidoORM"]] = relationship(
        back_populates="pedido", cascade="all, delete-orphan"
    )


class LineaPedidoORM(Base):
    __tablename__ = "linea_pedido"

    pedido_id: Mapped[int] = mapped_column(ForeignKey("pedido.id"), primary_key=True)
    producto_id: Mapped[int] = mapped_column(ForeignKey("producto.id"), primary_key=True)
    cantidad: Mapped[int]
    precio_unitario: Mapped[float]

    pedido: Mapped[PedidoORM] = relationship(back_populates="lineas")

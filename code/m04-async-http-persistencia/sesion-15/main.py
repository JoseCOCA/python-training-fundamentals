"""Demo de S15 — SQLAlchemy v2: Core + ORM, sessions, modelos relacionales.

Ejecuta el programa con:
    uv run python main.py

Verifica los tipos con:
    uv run mypy .

Verifica el estilo con:
    uv run ruff check .
    uv run ruff format --check .

Cinco demos:
1. Definición de modelos v2 con DeclarativeBase + Mapped + mapped_column.
2. Engine + Session — bootstrap del schema y poblado.
3. SELECT con select() — filtros, ordenamiento, agregaciones.
4. Relaciones (relationship + back_populates) y el problema N+1.
5. selectinload para cortar el N+1 de raíz.

Toda la demo corre contra un SQLite en memoria (`sqlite:///:memory:`),
así que no deja archivos atrás y siempre arranca limpia.
"""

from sqlalchemy import ForeignKey, String, create_engine, func, select
from sqlalchemy.engine import Engine
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    Session,
    mapped_column,
    relationship,
    selectinload,
)


def seccion(titulo: str) -> None:
    print()
    print("=" * 60)
    print(titulo)
    print("=" * 60)


# ---------------------------------------------------------------------------
# 1. Modelos con SQLAlchemy v2
# ---------------------------------------------------------------------------


class Base(DeclarativeBase):
    pass


class Cliente(Base):
    __tablename__ = "cliente"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(120), unique=True)

    pedidos: Mapped[list["Pedido"]] = relationship(back_populates="cliente")


class Producto(Base):
    __tablename__ = "producto"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(120), unique=True)
    categoria: Mapped[str] = mapped_column(String(40))
    precio: Mapped[float]
    stock: Mapped[int] = mapped_column(default=0)


class Pedido(Base):
    __tablename__ = "pedido"

    id: Mapped[int] = mapped_column(primary_key=True)
    cliente_id: Mapped[int] = mapped_column(ForeignKey("cliente.id"))

    cliente: Mapped[Cliente] = relationship(back_populates="pedidos")
    lineas: Mapped[list["LineaPedido"]] = relationship(
        back_populates="pedido", cascade="all, delete-orphan"
    )


class LineaPedido(Base):
    __tablename__ = "linea_pedido"

    pedido_id: Mapped[int] = mapped_column(ForeignKey("pedido.id"), primary_key=True)
    producto_id: Mapped[int] = mapped_column(ForeignKey("producto.id"), primary_key=True)
    cantidad: Mapped[int]
    precio_unitario: Mapped[float]

    pedido: Mapped[Pedido] = relationship(back_populates="lineas")
    producto: Mapped[Producto] = relationship()


# ---------------------------------------------------------------------------
# 2. Engine, schema y datos
# ---------------------------------------------------------------------------


def construir_engine() -> Engine:
    return create_engine("sqlite:///:memory:", echo=False, future=True)


def poblar(engine: Engine) -> None:
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        ana = Cliente(nombre="Ana Pérez", email="ana@example.com")
        bruno = Cliente(nombre="Bruno López", email="bruno@example.com")
        carla = Cliente(nombre="Carla Díaz", email="carla@example.com")

        cable = Producto(nombre="Cable USB", categoria="accesorios", precio=12.5, stock=30)
        auri = Producto(nombre="Auriculares", categoria="audio", precio=89.99, stock=5)
        teclado = Producto(nombre="Teclado", categoria="computación", precio=49.5, stock=12)
        monitor = Producto(nombre="Monitor 4K", categoria="computación", precio=320.0, stock=3)
        webcam = Producto(nombre="Webcam HD", categoria="computación", precio=79.0, stock=0)

        # Ana hizo dos pedidos; Bruno uno; Carla ninguno.
        ana.pedidos = [
            Pedido(
                lineas=[
                    LineaPedido(producto=cable, cantidad=2, precio_unitario=cable.precio),
                    LineaPedido(producto=auri, cantidad=1, precio_unitario=auri.precio),
                ]
            ),
            Pedido(
                lineas=[
                    LineaPedido(producto=teclado, cantidad=1, precio_unitario=teclado.precio),
                ]
            ),
        ]
        bruno.pedidos = [
            Pedido(
                lineas=[
                    LineaPedido(producto=monitor, cantidad=1, precio_unitario=monitor.precio),
                ]
            )
        ]
        session.add_all([ana, bruno, carla, cable, auri, teclado, monitor, webcam])
        session.commit()


def demo_bootstrap(engine: Engine) -> None:
    seccion("1-2. Modelos + engine + datos sembrados")
    poblar(engine)
    with Session(engine) as session:
        for tabla, modelo in (
            ("cliente", Cliente),
            ("producto", Producto),
            ("pedido", Pedido),
            ("linea_pedido", LineaPedido),
        ):
            n = session.scalar(select(func.count()).select_from(modelo))
            print(f"  {tabla:<14} {n} filas")


# ---------------------------------------------------------------------------
# 3. SELECT con select()
# ---------------------------------------------------------------------------


def demo_select(engine: Engine) -> None:
    seccion("3. SELECT con select() — filtros, orden, agregaciones")
    with Session(engine) as session:
        print("  Productos con stock>0 ordenados por precio:")
        stmt = select(Producto).where(Producto.stock > 0).order_by(Producto.precio.asc())
        for p in session.scalars(stmt):
            print(f"    {p.nombre:<14} {p.categoria:<14} ${p.precio:>8.2f}  stock={p.stock}")

        print("\n  Cantidad de productos por categoría:")
        stmt2 = (
            select(Producto.categoria, func.count().label("n"))
            .group_by(Producto.categoria)
            .order_by(func.count().desc())
        )
        for cat, n in session.execute(stmt2):
            print(f"    {cat:<14} {n}")

        print("\n  Cliente por email:")
        ana = session.scalar(select(Cliente).where(Cliente.email == "ana@example.com"))
        if ana is not None:
            print(f"    {ana.nombre} (id={ana.id})")


# ---------------------------------------------------------------------------
# 4. Relaciones + N+1
# ---------------------------------------------------------------------------


def demo_relaciones_n_mas_1(engine: Engine) -> None:
    seccion("4. Relaciones — el problema N+1 (lazy loading)")
    with Session(engine) as session:
        # Activamos echo solo durante esta sesión para ver las queries
        engine.echo = True
        print("  → mirá el output: por cada cliente se dispara un SELECT extra")
        print("  ──────────────────────────────────────────────────────────")
        clientes = session.scalars(select(Cliente)).all()
        for c in clientes:
            print(f"  {c.nombre}: {len(c.pedidos)} pedido(s)")
        engine.echo = False


# ---------------------------------------------------------------------------
# 5. selectinload — corta el N+1
# ---------------------------------------------------------------------------


def demo_selectinload(engine: Engine) -> None:
    seccion("5. selectinload — 2 queries en total, sin N+1")
    with Session(engine) as session:
        engine.echo = True
        print("  → ahora vas a ver SOLO 2 queries: una de cliente y una de pedido")
        print("  ──────────────────────────────────────────────────────────")
        stmt = select(Cliente).options(selectinload(Cliente.pedidos))
        clientes = session.scalars(stmt).all()
        for c in clientes:
            print(f"  {c.nombre}: {len(c.pedidos)} pedido(s)")
        engine.echo = False


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> None:
    engine = construir_engine()
    demo_bootstrap(engine)
    demo_select(engine)
    demo_relaciones_n_mas_1(engine)
    demo_selectinload(engine)


if __name__ == "__main__":
    main()

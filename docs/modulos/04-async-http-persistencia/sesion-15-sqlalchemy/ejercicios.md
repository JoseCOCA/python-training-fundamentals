# S15 — Ejercicios

> **Tiempo estimado:** ~70 min. Tres bloques: ejercicio guiado migrando el schema de S14 a SQLAlchemy v2 ORM, libres para entrenar relaciones / N+1 / refactor a repositorios, y **aporte al proyecto integrador que CIERRA el Módulo 4** con tag `proyecto-m4`.

---

## 0. Antes de empezar

Tu sandbox vive en `code/m04-async-http-persistencia/sesion-15/`. Si todavía no lo corriste:

```bash
cd code/m04-async-http-persistencia/sesion-15
uv sync
uv run python main.py
uv run mypy .
uv run ruff check .
```

Confirma que las cinco demos imprimen, mypy pasa limpio, ruff no reporta nada. Después regresa a este documento.

## 1. Ejercicio guiado — Reescribir el schema de S14 con ORM v2

### Paso 1.1 — Definir los modelos

Crea `mis_modelos.py`:

```python
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


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
    lineas: Mapped[list["LineaPedido"]] = relationship(back_populates="pedido")


class LineaPedido(Base):
    __tablename__ = "linea_pedido"

    pedido_id: Mapped[int] = mapped_column(ForeignKey("pedido.id"), primary_key=True)
    producto_id: Mapped[int] = mapped_column(ForeignKey("producto.id"), primary_key=True)
    cantidad: Mapped[int]
    precio_unitario: Mapped[float]

    pedido: Mapped[Pedido] = relationship(back_populates="lineas")
    producto: Mapped[Producto] = relationship()
```

Tres detalles a notar:
- Las clases se llaman `Cliente`, `Producto`, `Pedido`, `LineaPedido` (las del ORM).
- Las foreign keys se declaran tanto como columna (`cliente_id`) **como** relación (`cliente`).
- `back_populates` aparece en los dos lados de cada relación bidireccional.

### Paso 1.2 — Crear las tablas y poblar

```python
# mis_seed.py
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from mis_modelos import Base, Cliente, Producto


def main() -> None:
    engine = create_engine("sqlite:///mio.db", echo=True)
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        session.add_all([
            Cliente(nombre="Ana", email="ana@x.com"),
            Cliente(nombre="Bruno", email="bruno@x.com"),
            Producto(nombre="Cable USB", categoria="accesorios", precio=12.5, stock=30),
            Producto(nombre="Auriculares", categoria="audio", precio=89.99, stock=5),
        ])
        session.commit()


if __name__ == "__main__":
    main()
```

Corré: `uv run python mis_seed.py`. Vas a ver en consola **el SQL exacto** que SQLAlchemy emite (porque `echo=True`). Léelo: vas a reconocer los `CREATE TABLE` y los `INSERT` de S14, esta vez generados por el ORM.

### Paso 1.3 — Leer con `select()`

```python
# mis_queries.py
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from mis_modelos import Cliente, Producto


def main() -> None:
    engine = create_engine("sqlite:///mio.db", echo=False)

    with Session(engine) as session:
        # Un cliente por email
        ana = session.scalar(select(Cliente).where(Cliente.email == "ana@x.com"))
        print(f"ana: {ana.nombre}")

        # Productos con stock > 0 ordenados por precio
        productos = session.scalars(
            select(Producto).where(Producto.stock > 0).order_by(Producto.precio)
        ).all()
        for p in productos:
            print(f"  {p.nombre}  ${p.precio}")


if __name__ == "__main__":
    main()
```

Corré: `uv run python mis_queries.py`. Esperado: imprime "ana: Ana" y dos productos.

### Paso 1.4 — Reflexionar

| | SQL crudo (S14) | SQLAlchemy ORM (S15) |
|---|---|---|
| Definir tabla | `CREATE TABLE ...` string | `class Producto(Base): ...` |
| Insertar | `INSERT INTO ... VALUES (?, ?, ...)` | `session.add(Producto(...))` |
| Leer | `SELECT ... FROM ... WHERE ...` string | `select(Producto).where(...)` |
| Tipos | nada — strings sueltos | `Mapped[int]`, mypy ve los campos |
| Relaciones | `JOIN` a mano cada vez | `cliente.pedidos` ya es la lista |

**Lección:** el ORM no agrega capacidades nuevas — agrega **tipado y composabilidad**. El SQL sigue corriendo. `echo=True` te lo recuerda.

## 2. Ejercicios libres

### 2.1. Detectar y arreglar un N+1

Con varios pedidos en la DB (creá unos cuantos), corré:

```python
clientes = session.scalars(select(Cliente)).all()
for c in clientes:
    print(c.nombre, sum(len(p.lineas) for p in c.pedidos))
```

Activá `echo=True` y mirá el output. Vas a ver muchos SELECT — uno por cada acceso a `pedidos` y a `lineas`.

Reescribilo con `selectinload` para que sean **2-3 queries en total**, no N+1:

```python
from sqlalchemy.orm import selectinload

clientes = session.scalars(
    select(Cliente).options(
        selectinload(Cliente.pedidos).selectinload(Pedido.lineas)
    )
).all()
```

Comprobá: en el output del echo ahora hay 3 queries (cliente, pedido, linea_pedido), no N+1. Eso es la diferencia entre 1 ms y 1 s en una DB real.

### 2.2. Update con detección automática

Modificá un cliente y observá:

```python
ana = session.scalar(select(Cliente).where(Cliente.email == "ana@x.com"))
ana.email = "ana_nueva@x.com"
session.commit()                # SQLAlchemy emite el UPDATE solo
```

Corré con `echo=True`. Vas a ver un solo `UPDATE cliente SET email = ? WHERE id = ?`. SQLAlchemy detectó el cambio comparando con el estado original.

Después intentá:

```python
ana.email = "ana_nueva@x.com"   # MISMO valor
session.commit()                # ¿emite UPDATE?
```

Esperado: **no**, porque el valor no cambió. SQLAlchemy es inteligente.

### 2.3. Bulk insert: ORM vs Core

Insertá 1000 productos. Cronometrá las dos formas:

**ORM (lento):**
```python
import time

start = time.perf_counter()
for i in range(1000):
    session.add(Producto(nombre=f"item-{i}", categoria="bulk", precio=1.0, stock=1))
session.commit()
print(f"ORM: {time.perf_counter() - start:.2f}s")
```

**Core (rápido):**
```python
from sqlalchemy import insert

start = time.perf_counter()
session.execute(
    insert(Producto),
    [{"nombre": f"item-{i}", "categoria": "bulk", "precio": 1.0, "stock": 1} for i in range(1000)],
)
session.commit()
print(f"Core: {time.perf_counter() - start:.2f}s")
```

Comparalos. Para 1000 filas el ORM puede tardar 5-10× más. Para 100000 filas, la diferencia es brutal.

### 2.4. Función pydantic ↔ ORM

Definí dos DTOs pydantic equivalentes a `Cliente` y `Producto`:

```python
from pydantic import BaseModel


class ClienteDTO(BaseModel):
    nombre: str
    email: str


class ProductoDTO(BaseModel):
    nombre: str
    categoria: str
    precio: float
    stock: int = 0
```

Y dos pares de funciones:

```python
def cliente_a_orm(dto: ClienteDTO) -> Cliente: ...
def cliente_a_dto(orm: Cliente) -> ClienteDTO: ...

def producto_a_orm(dto: ProductoDTO) -> Producto: ...
def producto_a_dto(orm: Producto) -> ProductoDTO: ...
```

¿Por qué este patrón? Porque a la "frontera" (HTTP, JSON, CLI) entran y salen DTOs. La capa de persistencia trabaja con ORM. Las funciones de conversión son la cremallera.

### 2.5. Usar el modo Async (mención)

```python
import asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from mis_modelos import Producto


async def main() -> None:
    engine = create_async_engine("sqlite+aiosqlite:///mio.db")
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    async with async_session() as session:
        productos = (
            await session.scalars(select(Producto).where(Producto.stock > 0))
        ).all()
        for p in productos:
            print(p.nombre)
    await engine.dispose()


asyncio.run(main())
```

Necesitás `pip install aiosqlite` (o `uv add aiosqlite`). Corré y comparalo con el sync. Para un script CLI no hay ganancia; para un servidor con 100 requests/seg sí.

## 3. Aporte al proyecto integrador — Cierre del hito M4

**Hoy cierra el Módulo 4.** TiendaPro Lite pasa de leer un JSON a persistir en SQLite con SQLAlchemy v2, mantiene el cliente httpx que agregamos en S13, y mantiene los DTOs pydantic en los bordes.

### 3.1. Configurar dependencias

En `code/proyecto-integrador/pyproject.toml`:

```toml
[project]
# ...
dependencies = [
    "pydantic>=2.6",
    "httpx>=0.27",
    "sqlalchemy>=2.0",
]
```

```bash
cd /home/jose/Proyectos/python-training-fundamentals
uv sync --all-groups
```

### 3.2. `src/tiendapro/db.py` — engine y sesión

Crea `code/proyecto-integrador/src/tiendapro/db.py`:

```python
"""Conexión a la base de datos: engine, sesión y bootstrap del schema."""

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
    """Context manager que abre, hace commit/rollback y cierra la sesión."""
    session = Session(_engine)
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
```

### 3.3. `src/tiendapro/orm.py` — modelos SQLAlchemy

Crea `code/proyecto-integrador/src/tiendapro/orm.py`:

```python
"""Modelos SQLAlchemy v2 — la capa de persistencia.

Estos NO son los modelos de dominio (esos están en `modelos.py` con pydantic).
Son la representación de las tablas. La traducción ocurre en `repositorio.py`.
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
```

Convención del integrador: las clases ORM se nombran con sufijo `ORM` (`ProductoORM`) para que **nunca** se confundan con los DTOs pydantic (`Producto`).

### 3.4. `src/tiendapro/repositorio.py` — el único módulo que toca la DB

Crea `code/proyecto-integrador/src/tiendapro/repositorio.py`:

```python
"""Repositorio: API de acceso a datos.

Es el ÚNICO módulo del paquete que conoce SQLAlchemy. Devuelve y recibe
DTOs pydantic. Los demás módulos (catalogo, presentacion, main) no
importan ni `orm` ni `sqlalchemy` — eso desacopla la persistencia del dominio.
"""

import json
from collections.abc import Iterable
from pathlib import Path

from pydantic import ValidationError
from sqlalchemy import func, select

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
        return existentes


def _importar_seed(session, ruta: Path) -> None:  # type: ignore[no-untyped-def]
    try:
        with ruta.open(encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError as e:
        raise CatalogoInvalido(f"Archivo de catálogo no encontrado: {ruta}") from e
    except json.JSONDecodeError as e:
        raise CatalogoInvalido(f"JSON inválido en {ruta}: {e.msg}") from e

    if not isinstance(data, list):
        raise CatalogoInvalido(
            f"El catálogo debe ser una lista, recibí {type(data).__name__}"
        )

    for i, item in enumerate(data):
        try:
            dto = Producto.model_validate(item)
        except ValidationError as e:
            raise CatalogoInvalido(f"Producto inválido en posición {i}: {e}") from e
        session.add(_to_orm(dto))


def todos() -> list[Producto]:
    with obtener_sesion() as session:
        rows = session.scalars(select(ProductoORM).order_by(ProductoORM.id)).all()
        return [_to_dto(p) for p in rows]


def disponibles() -> list[Producto]:
    """Productos con stock > 0, ordenados por precio asc."""
    with obtener_sesion() as session:
        rows = session.scalars(
            select(ProductoORM)
            .where(ProductoORM.stock > 0)
            .order_by(ProductoORM.precio.asc())
        ).all()
        return [_to_dto(p) for p in rows]


def por_categoria(categoria: str) -> list[Producto]:
    with obtener_sesion() as session:
        rows = session.scalars(
            select(ProductoORM).where(ProductoORM.categoria == categoria)
        ).all()
        return [_to_dto(p) for p in rows]


def crear(dto: Producto) -> Producto:
    with obtener_sesion() as session:
        orm = _to_orm(dto)
        session.add(orm)
        session.flush()
        return _to_dto(orm)


# ---------------------------------------------------------------------------
# Conversiones entre el DTO pydantic y el modelo ORM
# ---------------------------------------------------------------------------


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


def aceptar_iterable(productos: Iterable[Producto]) -> list[Producto]:
    """Helper para los flujos que ya pasaban por la antigua API basada en JSON.

    No hace nada de magia: materializa el iterable. Existe para no obligar a
    cambiar la firma de `presentacion.imprimir_resumen` ahora.
    """
    return list(productos)
```

### 3.5. Reescribir `catalogo.py`

Reemplazá el contenido de `code/proyecto-integrador/src/tiendapro/catalogo.py`:

```python
"""Catálogo: API que el resto de la app consume.

Antes leía un JSON. Ahora delega al repositorio (que persiste en SQLite).
La firma pública NO cambió desde M3 — los consumidores (main, presentacion)
no se enteran del cambio de fondo.
"""

from collections.abc import Iterable
from pathlib import Path

from tiendapro import repositorio
from tiendapro.modelos import Producto


def inicializar(seed_json: Path | None = None) -> int:
    """Bootstrap de la DB. Idempotente."""
    return repositorio.inicializar(seed_json)


def cargar() -> list[Producto]:
    """Devuelve TODOS los productos (incluyendo stock 0)."""
    return repositorio.todos()


def disponibles(productos: Iterable[Producto] | None = None) -> list[Producto]:
    """Devuelve productos con stock > 0, ordenados por precio.

    El parámetro `productos` se mantiene por compatibilidad con M3 pero ya
    no se usa: el filtro lo hace la DB. Si te llega, lo ignoramos.
    """
    del productos
    return repositorio.disponibles()


def ordenar_por_precio(productos: Iterable[Producto]) -> list[Producto]:
    """Ordena por precio ascendente. Mantiene la firma de M3."""
    return sorted(productos, key=lambda p: p.precio)
```

### 3.6. Adaptar `main.py`

```python
"""TiendaPro Lite — Hito M4.

Punto de entrada. Bootstrappea la DB con el seed JSON la primera vez,
después lee desde la DB y enriquece con la API mock de S13.

Stack del hito M4:
- pydantic en bordes, SQLAlchemy v2 en persistencia (S15).
- httpx.AsyncClient + MockTransport para enriquecimiento opcional (S13).
- asyncio donde aporta (paralelizar las llamadas de enriquecimiento).
- mypy estricto + ruff pasan limpio.

Ejecuta con:
    uv run python main.py
"""

import asyncio
import sys
from pathlib import Path

from tiendapro import TiendaProError
from tiendapro.catalogo import disponibles, inicializar, ordenar_por_precio
from tiendapro.integraciones import enriquecer
from tiendapro.presentacion import imprimir_resumen, imprimir_tabla

RUTA_SEED = Path(__file__).parent / "data" / "catalogo.json"


async def _ejecutar() -> int:
    try:
        cantidad = inicializar(RUTA_SEED)
        print(f"Productos en DB: {cantidad}\n")

        productos = ordenar_por_precio(disponibles())
        imprimir_tabla(productos)
        imprimir_resumen(productos)

        # Enriquecimiento opcional desde la "API externa"
        nombres = [p.nombre for p in productos]
        enriquecimientos = await enriquecer(nombres)
        if enriquecimientos:
            print("\nEnriquecimiento (API externa):")
            for nombre, enr in enriquecimientos.items():
                print(f"  {nombre:<28} ★{enr.rating}  {enr.descripcion}")
    except TiendaProError as e:
        print(f"Error en TiendaPro: {e}", file=sys.stderr)
        return 1
    return 0


def main() -> int:
    return asyncio.run(_ejecutar())


if __name__ == "__main__":
    sys.exit(main())
```

### 3.7. Re-exportar lo nuevo

En `code/proyecto-integrador/src/tiendapro/__init__.py`, asegurate de re-exportar `IntegracionError`:

```python
from tiendapro.errores import (
    CatalogoInvalido,
    IntegracionError,
    ProductoNoEncontrado,
    TiendaProError,
)
from tiendapro.modelos import Cliente, EnriquecimientoExterno, Producto

__all__ = [
    "CatalogoInvalido",
    "Cliente",
    "EnriquecimientoExterno",
    "IntegracionError",
    "Producto",
    "ProductoNoEncontrado",
    "TiendaProError",
]
```

(Si hay dudas con el orden o la lista exacta, mirá el archivo actual y agregá los nuevos.)

### 3.8. Verificar todo

Desde la raíz del repo:

```bash
uv sync --all-groups
uv run mypy code/proyecto-integrador/src code/proyecto-integrador/main.py
uv run ruff check code/proyecto-integrador
uv run ruff format --check code/proyecto-integrador
cd code/proyecto-integrador && uv run python main.py
```

Esperado:

- mypy y ruff: 0 issues.
- `python main.py` imprime la tabla con los 8 productos disponibles, el resumen, y la sección de enriquecimiento con dos productos (Auriculares Bluetooth y Teclado Mecánico).
- Si corrés `python main.py` una segunda vez, **se salta el seed** (la DB ya tiene productos).

Para resetear la DB:

```bash
rm code/proyecto-integrador/tiendapro.db
```

(El archivo está en `.gitignore` por la regla `*.db`.)

### 3.9. Commit final + tag — CIERRE M4

```bash
git add code/proyecto-integrador
git commit -m "feat(proyecto-integrador): cierra M4 con SQLAlchemy v2 + httpx (proyecto-m4)"
git tag proyecto-m4
git push origin main
git push origin proyecto-m4
```

**Felicitaciones — terminaste el Módulo 4.** TiendaPro Lite ahora:

- **Persiste** en SQLite a través de SQLAlchemy v2 (Postgres-ready: solo cambia la URL).
- **Habla HTTP** con un servicio externo (mock por ahora, real más adelante).
- Mantiene la **separación pydantic (borde) ↔ ORM (DB)** que vas a respetar todo el camino restante.
- Sigue siendo **mypy/ruff limpio** — el ORM v2 con `Mapped[T]` se lleva bien con el tipado estricto.

### 3.10. Actualizar el roadmap del curso

En `docs/00-curriculum.md`, marcá M4 como completado:

```markdown
- [x] Módulo 4 — Async, HTTP y persistencia (4 sesiones) — tag `proyecto-m4`
```

Y en `code/proyecto-integrador/README.md`, actualizá el "estado actual" para reflejar M4.

```bash
git add docs/00-curriculum.md code/proyecto-integrador/README.md
git commit -m "docs(curriculum): marca M4 como completado en el roadmap"
git push origin main
```

---

Cuando termines, vuelve al README y responde las preguntas de auto-evaluación. Si todas se contestan sin dudar, M4 está consolidado y puedes pasar a [M5 — Construir una API real con FastAPI](../../05-api-fastapi/) (cuando esté publicado).

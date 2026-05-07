# S15 — SQLAlchemy v2: Core + ORM, sessions, modelos relacionales

> **Sesión 2h.** ~50 min lectura + ~70 min ejercicios. **Cierra el Módulo 4** con el hito `proyecto-m4` del integrador. En S14 escribiste SQL a mano y entendiste lo que pasa por debajo. Hoy ponés un **ORM** encima — SQLAlchemy v2 — para escribir queries en Python tipado, sin perder de vista que **el SQL sigue ejecutándose**. SQLAlchemy v2 es muy distinto a las versiones anteriores que circulan por internet: se rediseñó el API para tipado completo, y `Session` + `select()` son la nueva norma. Si te cruzás con tutoriales viejos (`session.query(...)`, `Column(Integer)`), son v1 — ignoralos.

---

## 1. Objetivos de aprendizaje

Al terminar esta sesión vas a poder:

- Distinguir **Core** (capa SQL tipada en Python) de **ORM** (modelos de objetos mapeados a tablas).
- Definir modelos con `DeclarativeBase`, `Mapped[T]` y `mapped_column(...)`.
- Crear un `Engine` y un `Session`, y entender el ciclo de vida de cada uno.
- Hacer CRUD: insertar, leer (`select`), actualizar y borrar.
- Modelar relaciones con `ForeignKey` y `relationship(...)` — uno-a-muchos y muchos-a-muchos vía tabla intermedia.
- Diferenciar **lazy loading** (default, una query extra al acceder al atributo) de **eager loading** (`selectinload`, `joinedload`) — y cuándo elegir cada uno.
- Decidir cuándo usar el ORM y cuándo bajar a Core/SQL crudo.
- Conocer que SQLAlchemy tiene **versión async** (`AsyncSession`) y entender cuándo usarla.

## 2. Prerequisitos

- [S14 — SQL fundamentals](../sesion-14-sql-fundamentos/README.md) sólida. Si no entendés `JOIN`, no vas a entender `relationship`.
- [S11 — pydantic](../../03-tipado-calidad/sesion-11-pydantic-ruff/README.md). Vamos a separar **modelo de DB** (SQLAlchemy) de **modelo de borde** (pydantic) en el integrador.
- [S10 — Type hints](../../03-tipado-calidad/sesion-10-type-hints-mypy/README.md). El API moderno de SQLAlchemy depende fuerte de los tipos genéricos (`Mapped[int]`, `list[Pedido]`).

## 3. Conceptos clave

1. **ORM (Object-Relational Mapper).** Capa que mapea **filas de tablas** a **instancias de clases** y viceversa. Escribís Python; el ORM genera SQL.
2. **Engine.** El "puente" a la base. Encapsula la URL de conexión, el pool y el dialecto (SQLite, Postgres, MySQL, etc.). Se crea **una vez por aplicación**.
3. **Session.** Un "espacio de trabajo" donde acumulás cambios y los hacés `commit()`. Mantiene un cache de identidad y trackea qué objetos modificaste.
4. **`DeclarativeBase`.** La clase base de todos tus modelos ORM. Heredarla activa el "registro" de SQLAlchemy.
5. **`Mapped[T]` + `mapped_column(...)`.** La forma moderna (v2) de declarar columnas tipadas.
6. **`ForeignKey` y `relationship(...)`.** `ForeignKey` es la columna que apunta a otra tabla. `relationship` es la **vista de objetos** que te deja navegar `pedido.cliente.nombre` sin pensar en JOINs.
7. **Lazy vs eager loading.** Por default, acceder a `pedido.lineas` dispara una query extra (lazy). Eso es útil pero puede explotar en queries N+1. `selectinload`, `joinedload` te dejan precargar.
8. **`select()`.** La función que arma queries en Core/ORM v2. Reemplaza al viejo `session.query(...)` de v1.

## 4. Teoría

### 4.1. ORM vs Core: dos capas, dos abstracciones

SQLAlchemy se divide en dos:

- **Core**: una capa Pythonic sobre SQL. Definís `Table`, `Column`, y construís queries con `select`, `insert`, `update` que se traducen a SQL. **Trabajás con tablas y filas, no con objetos.**
- **ORM**: una capa encima de Core. Los registros se materializan en instancias de clases. **Trabajás con objetos y relaciones.**

¿Cuál usar?

- **ORM** para CRUD típico de aplicaciones, modelado de dominio, navegación entre relaciones.
- **Core** para queries analíticas complejas, bulk operations, o cuando el ORM se vuelve un cuello de botella.
- **SQL crudo** para casos extremos (`text("CALL stored_procedure(?)")`), reportes muy específicos, o cuando ya tenés el SQL escrito y no querés re-derivarlo.

**Regla:** podés mezclarlos en el mismo proyecto. No es uno o el otro.

### 4.2. Engine: el motor

```python
from sqlalchemy import create_engine

engine = create_engine("sqlite:///tienda.db", echo=True)
```

- La URL es **dialecto + driver + ubicación**. Para Postgres: `postgresql+psycopg://user:pass@host:5432/dbname`.
- `echo=True` imprime cada SQL que SQLAlchemy ejecuta. **Activalo cuando aprendés.** Te muestra exactamente qué SQL produce el ORM, y ese reflejo te entrena para ver problemas (queries duplicadas, joins faltantes).
- El `Engine` mantiene un **pool de conexiones**. Se crea una vez por proceso.

### 4.3. DeclarativeBase y Mapped

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


class Pedido(Base):
    __tablename__ = "pedido"

    id: Mapped[int] = mapped_column(primary_key=True)
    cliente_id: Mapped[int] = mapped_column(ForeignKey("cliente.id"))

    cliente: Mapped[Cliente] = relationship(back_populates="pedidos")
```

**Lo importante:**

- `Mapped[int]` + `mapped_column(primary_key=True)` reemplaza al viejo `Column(Integer, primary_key=True)`. **Es tipado completo** — mypy sabe que `cliente.id` es `int`.
- El primer arg de `mapped_column` es opcional. Si está, sobreescribe el tipo SQL inferido.
- `relationship(...)` no se persiste como columna — es la **vista de objetos**. SQLAlchemy genera el JOIN cuando lo necesitás.
- `back_populates="..."` conecta los dos lados de la relación. Si modificás `pedido.cliente`, `cliente.pedidos` se actualiza.

**Crear las tablas:**

```python
Base.metadata.create_all(engine)
```

Eso ejecuta los `CREATE TABLE` necesarios. Para producción, no lo uses — usá Alembic (migraciones), que no toca lo que ya existe y permite revertir.

### 4.4. Session: el contexto de trabajo

```python
from sqlalchemy.orm import Session

with Session(engine) as session:
    cliente = Cliente(nombre="Ana", email="ana@x.com")
    session.add(cliente)
    session.commit()
    print(cliente.id)            # ya tiene id asignado
```

`Session` es **una unidad de trabajo**:

- `session.add(obj)` la marca como "para insertar".
- Modificar atributos de un objeto cargado la marca como "para actualizar".
- `session.delete(obj)` la marca como "para borrar".
- `session.commit()` materializa todo en una transacción.
- `session.rollback()` cancela.
- `session.close()` (al salir del `with`) cierra y devuelve la conexión al pool.

**Regla de oro:** no abras una sesión por request en una API web. Abrila en cada **operación lógica** y cerrá. Mantener una sesión viva durante mucho tiempo causa problemas (datos desactualizados, locks).

### 4.5. SELECT con `select()`

```python
from sqlalchemy import select

with Session(engine) as session:
    # un cliente por email
    stmt = select(Cliente).where(Cliente.email == "ana@x.com")
    cliente = session.scalar(stmt)
    print(cliente.nombre)

    # todos los clientes ordenados
    stmt = select(Cliente).order_by(Cliente.nombre)
    for c in session.scalars(stmt):
        print(c.nombre)
```

- `select(Cliente)` es como `SELECT * FROM cliente` pero sigue siendo un objeto Python que vas componiendo.
- `.where(...)` agrega `WHERE`.
- `session.scalar(stmt)` ejecuta y devuelve **el primer escalar** (un objeto `Cliente`) o `None`.
- `session.scalars(stmt)` ejecuta y devuelve un iterador de objetos.
- `.order_by(Cliente.nombre)`, `.limit(10)`, `.offset(20)` se encadenan.

**Consultas con condiciones combinadas:**

```python
from sqlalchemy import and_, or_

stmt = (
    select(Producto)
    .where(and_(Producto.stock > 0, Producto.precio < 100))
    .order_by(Producto.precio)
    .limit(5)
)
```

(En la práctica `.where(A).where(B)` ya es un AND, sin necesidad de `and_`.)

### 4.6. INSERT, UPDATE, DELETE con ORM

```python
# INSERT
nuevo = Cliente(nombre="Bruno", email="bruno@x.com")
session.add(nuevo)
session.commit()       # asigna id

# UPDATE: solo modificás el atributo
cliente.email = "ana_nuevo@x.com"
session.commit()       # SQLAlchemy detecta el cambio y emite UPDATE

# DELETE
session.delete(cliente)
session.commit()
```

El cambio se detecta por **dirty tracking**: el `Session` compara el estado actual de los objetos cargados con el estado al momento de cargarlos. Por eso muchos bugs de "mi UPDATE no se aplica" son sesiones cerradas o objetos detached.

**Bulk operations:** para insertar 10000 filas, el patrón anterior es lento (un INSERT por fila). Usá:

```python
session.add_all([Producto(nombre=n, precio=p) for n, p in datos])
session.commit()
```

Y para casos extremos, las APIs `insert()` y `update()` de Core son **mucho** más rápidas porque no construyen objetos.

### 4.7. Relaciones — el corazón del ORM

#### Uno a muchos (un cliente, varios pedidos)

```python
class Cliente(Base):
    __tablename__ = "cliente"
    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str]
    pedidos: Mapped[list["Pedido"]] = relationship(back_populates="cliente")


class Pedido(Base):
    __tablename__ = "pedido"
    id: Mapped[int] = mapped_column(primary_key=True)
    cliente_id: Mapped[int] = mapped_column(ForeignKey("cliente.id"))
    cliente: Mapped[Cliente] = relationship(back_populates="pedidos")
```

Uso:

```python
cliente = Cliente(nombre="Ana", email="ana@x.com")
cliente.pedidos.append(Pedido())          # crea el pedido y lo conecta
session.add(cliente)
session.commit()

# leer
print(cliente.pedidos[0].id)               # ya tiene id
```

#### Muchos a muchos vía tabla intermedia con datos extra (línea de pedido)

Para "un pedido tiene muchos productos, un producto está en muchos pedidos, **y la línea tiene cantidad y precio**", la tabla intermedia es **una entidad propia**:

```python
class LineaPedido(Base):
    __tablename__ = "linea_pedido"

    pedido_id: Mapped[int] = mapped_column(ForeignKey("pedido.id"), primary_key=True)
    producto_id: Mapped[int] = mapped_column(ForeignKey("producto.id"), primary_key=True)
    cantidad: Mapped[int]
    precio_unitario: Mapped[float]

    pedido: Mapped["Pedido"] = relationship(back_populates="lineas")
    producto: Mapped["Producto"] = relationship()


class Pedido(Base):
    __tablename__ = "pedido"
    id: Mapped[int] = mapped_column(primary_key=True)
    cliente_id: Mapped[int] = mapped_column(ForeignKey("cliente.id"))

    cliente: Mapped["Cliente"] = relationship(back_populates="pedidos")
    lineas: Mapped[list["LineaPedido"]] = relationship(back_populates="pedido")
```

Cuando la "tabla puente" tiene atributos propios (cantidad, precio), conviene modelarla como entidad. Si solo conecta dos tablas sin info extra, la `Table` cruda + `secondary=...` en el `relationship` alcanza.

### 4.8. N+1 queries: el bug clásico de los ORMs

```python
clientes = session.scalars(select(Cliente)).all()
for c in clientes:
    print(c.nombre, len(c.pedidos))         # ←
```

Esto parece inocente. Pero por defecto las relaciones son **lazy**: cada vez que accedés a `c.pedidos`, SQLAlchemy lanza un nuevo SELECT. Si tenés 100 clientes, son 1 + 100 = 101 queries. Si tenés 10000, 10001.

**Soluciones:**

```python
from sqlalchemy.orm import selectinload, joinedload

# selectinload: 2 queries (una por la tabla y otra IN para todos los pedidos)
clientes = session.scalars(
    select(Cliente).options(selectinload(Cliente.pedidos))
).all()

# joinedload: 1 sola query con JOIN (puede duplicar filas si la relación es 1-N)
clientes = session.scalars(
    select(Cliente).options(joinedload(Cliente.pedidos))
).unique().all()
```

`selectinload` suele ser mejor para uno-a-muchos (no infla las filas). `joinedload` es ideal cuando vas a usar muchos atributos del padre y la relación es uno-a-uno o muchos-a-uno.

**Cómo detectar N+1:** poné `echo=True` en el engine y mirá los SELECT que se imprimen. Si ves un SELECT repetido en bucle, tenés un N+1.

### 4.9. Pydantic en los bordes, ORM en el centro

En el integrador del curso vas a tener **dos jerarquías paralelas** de modelos:

- `tiendapro.modelos.*` (pydantic.BaseModel): para validar entrada/salida (JSON, HTTP).
- `tiendapro.orm.*` (SQLAlchemy `Base`): para persistir.

¿Por qué duplicar? Porque cumplen propósitos distintos:

| | pydantic | SQLAlchemy |
|---|---|---|
| Para qué | Validar datos de entrada / serializar | Persistir / consultar |
| Quién lo crea | El framework HTTP, el cliente, etc. | El ORM al cargar |
| Mutabilidad | Suelen ser frozen/inmutables | Mutables (dirty tracking) |
| Identidad | Por valor | Por primary key |

**Conversión:** funciones `to_orm(dto: ProductoDTO) -> Producto` y `to_dto(orm: Producto) -> ProductoDTO`. Hay librerías que automatizan esto (`pydantic.from_orm`, `sqlmodel`), pero conceptualmente las dos capas existen y conviene mantenerlas separadas.

(En proyectos chicos podés usar `SQLModel` —de Sebastián Ramírez— que combina ambas en una sola clase. Pero para enseñar, separarlas hace que **veas** la frontera.)

### 4.10. Async: `AsyncSession` (mención)

SQLAlchemy 2 tiene API async completa. Cambia muy poco en superficie:

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

engine = create_async_engine("sqlite+aiosqlite:///tienda.db")

async with AsyncSession(engine) as session:
    cliente = await session.scalar(select(Cliente).where(Cliente.id == 1))
```

Cuándo usarlo:
- Estás escribiendo un servidor (FastAPI) con varias requests concurrentes que tocan la DB.
- Tu código ya está mayormente async (S12, S13).

Cuándo NO:
- Es un script CLI o batch. Sync alcanza.
- Estás aprendiendo SQLAlchemy. Sync es más simple — empezá ahí.

**El integrador del módulo usa la versión sync.** En M5 (FastAPI) introduciremos la versión async cuando aporte.

### 4.11. Cuándo el ORM se vuelve enemigo

El ORM ahorra tiempo en CRUD simple. Pero hay momentos donde estorba:

- **Reportes con muchas agregaciones.** Una query de 6 JOINs y 4 GROUP BY se escribe mejor en Core o SQL crudo.
- **Bulk operations.** `INSERT INTO ... SELECT ...` con millones de filas. El ORM construiría millones de objetos.
- **Performance crítica.** Un endpoint hot-path con un SELECT simple gana descendiendo a Core.

**Aprende a leer el SQL que el ORM emite (`echo=True`).** Si el SQL te parece subóptimo, sabes que es momento de bajar de capa. El ORM no es magia — es Python que escribe SQL por vos.

## 5. Patrones y antipatrones

| ✅ Patrón | ❌ Antipatrón |
|---|---|
| `Mapped[int]` + `mapped_column(...)` | `Column(Integer, ...)` (v1, sin tipos) |
| Un `Engine` por proceso | Crear `create_engine` en cada función |
| `with Session(engine):` para cerrar limpio | Sesión global que vive todo el proceso |
| `select(Modelo).where(...)` | `session.query(Modelo).filter(...)` (v1, sin tipos) |
| `selectinload`/`joinedload` para evitar N+1 | Iterar atributos relacionados sin precargar |
| `relationship(back_populates="...")` en ambos lados | Solo uno de los lados — la sincronía se rompe |
| Modelos pydantic (DTO) ≠ modelos ORM | Reusar el mismo modelo para entrada/salida y persistencia |
| Migraciones con Alembic en producción | `Base.metadata.create_all` en producción |
| `echo=True` mientras aprendés / debuggeás | Asumir que el ORM emite el SQL óptimo |
| Bajar a Core o SQL crudo para reportes | Hacer reportes complejos con `relationship` y N+1 implícito |

## 6. Conexión con el proyecto integrador — Cierre del hito M4

**Hoy cierra el Módulo 4.** Cambios concretos al integrador:

1. **Nuevo `src/tiendapro/orm.py`** con `Base`, `Producto`, `Cliente`, `Pedido`, `LineaPedido` como modelos SQLAlchemy v2.
2. **Nuevo `src/tiendapro/db.py`** con la creación del engine (`sqlite:///tiendapro.db`) y un context manager `obtener_sesion()`.
3. **`src/tiendapro/modelos.py`** se mantiene con los DTOs `BaseModel` (Producto, Cliente, EnriquecimientoExterno). Son los modelos de **borde**, no de DB.
4. **`src/tiendapro/repositorio.py`** (nuevo) con funciones `cargar_desde_json(...)`, `obtener_disponibles()`, `obtener_por_categoria(...)`, `crear_pedido(...)`. Toda la interacción con la DB pasa por aquí — los demás módulos no importan SQLAlchemy.
5. **`main.py`** se reescribe: en vez de cargar el JSON cada vez, usa el repositorio. La primera ejecución migra el JSON a la DB; las siguientes leen directo.
6. **`tiendapro/integraciones.py`** (creada en S13) **se conecta** con el repositorio: enriquecemos los productos cargados de la DB y mostramos su descripción/rating si está.
7. **`pyproject.toml`** suma `sqlalchemy>=2.0` (más `httpx>=0.27` que ya agregamos en S13).
8. **mypy y ruff** pasan limpio. SQLAlchemy v2 está pensado para ser tipado-friendly — el plugin `sqlalchemy[mypy]` ya no es necesario en v2 si tu código usa `Mapped[T]` correctamente.
9. **Commit final + tag**:
   ```bash
   git add code/proyecto-integrador
   git commit -m "feat(proyecto-integrador): cierra M4 con SQLAlchemy v2 + httpx (proyecto-m4)"
   git tag proyecto-m4
   ```

Detalles paso a paso en `ejercicios.md`.

## 7. Resumen

1. **ORM = filas como objetos. Core = tablas como Python tipado. SQL crudo = SQL.** Los tres conviven; elegís según el caso.
2. **`Engine` se crea una vez. `Session` por unidad de trabajo.** Cerrá la sesión.
3. **`Mapped[T]` + `mapped_column(...)` es la API moderna v2.** Tipos completos, sin perder nada.
4. **`select()` reemplaza al viejo `query()`.** Encadenable, componible, tipado.
5. **`relationship` te deja navegar entre objetos** — pero por default es lazy. Cuidado con N+1.
6. **`selectinload`/`joinedload` precargan relaciones.** Evitás explosiones de queries.
7. **Modelos pydantic (borde) ≠ modelos SQLAlchemy (DB).** Mantenelos separados.
8. **Activá `echo=True` mientras aprendés.** Ver el SQL te enseña más que cualquier doc.
9. **El ORM no es mágico. Cuando estorba, bajá a Core o SQL crudo.** Es una herramienta, no una religión.
10. **Existe `AsyncSession`. Para servidor (M5) sí; para script CLI no aporta.** Sync es más simple.

## 8. Preguntas de auto-evaluación

1. ¿Qué dos capas tiene SQLAlchemy y para qué sirve cada una?
2. Diferencia entre `Engine` y `Session`. ¿Cuántos de cada uno tendrías en una aplicación típica?
3. ¿Cuál es la diferencia entre el `query()` de v1 y `select()` de v2? ¿Qué le ganás al cambio?
4. Definí un modelo `Articulo` con `id`, `titulo`, `body`, `creado_en`. ¿Cómo lo escribís en v2?
5. ¿Qué hace `relationship(back_populates="...")` y por qué se pone en los dos lados?
6. Tenés `select(Cliente)` y querés sus pedidos sin disparar N+1. ¿Qué agregás?
7. ¿Qué pasa si modificás `cliente.email` y nunca llamás `session.commit()`?
8. ¿Cuándo usarías Core o SQL crudo en lugar del ORM? Da dos ejemplos.
9. Diferencia entre `selectinload` y `joinedload`. ¿Cuándo elegís cada uno?
10. ¿Por qué en el integrador mantenemos modelos pydantic separados de los modelos SQLAlchemy?

Cuando puedas responder todas, pasa a [`ejercicios.md`](ejercicios.md) para cerrar el hito M4.

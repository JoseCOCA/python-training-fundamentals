# S15 — Código de la sesión

```bash
uv sync
uv run python main.py
uv run mypy .
uv run ruff check .
uv run ruff format --check .
```

`main.py` recorre cinco demos contra una **base SQLite en memoria** (`sqlite:///:memory:`), así que no deja archivos atrás:

1. **Modelos + engine + datos sembrados** — `DeclarativeBase`, `Mapped[T]`, `mapped_column`, `relationship` con `back_populates`. Cuatro tablas: `cliente`, `producto`, `pedido`, `linea_pedido`. Un mini-grafo de pedidos para que las demos siguientes tengan algo que mostrar.
2. **`SELECT` con `select()`** — filtros, `order_by`, agregaciones con `func.count()`, lectura de un escalar puntual.
3. **Relaciones — el N+1 al desnudo** — activamos `engine.echo = True` durante la demo y vas a ver, en consola, **un SELECT por cada cliente** cuando accedés a `c.pedidos`. Ese es el bug que el ORM puede generar si no tenés cuidado.
4. **`selectinload` cortando el N+1** — la misma operación, pero precargando la relación. Ahora son **2 queries en total** independientemente de cuántos clientes haya.

`pyproject.toml` agrega `sqlalchemy>=2.0` como única dependencia. Ruff y mypy heredan la configuración estricta del workspace.

Para experimentar:

- En el demo 4, agregá más clientes y pedidos. Vas a ver que la cantidad de SELECTs crece linealmente con la cantidad de clientes — ese es el patrón "N+1".
- Poné `engine.echo = True` antes de `poblar(engine)` para ver el SQL completo del bootstrap (CREATE TABLE + INSERTs). Es la mejor forma de aprender qué hace SQLAlchemy.
- Cambiá el `String(120)` del `nombre` del producto a `String(20)` y poblá con un nombre largo. SQLite no chequea el límite (es flexible con tipos), pero Postgres sí. Es una de las diferencias importantes a recordar al portar.
- En el demo 5, reemplazá `selectinload` por `joinedload`. Vas a ver que ahora es **una sola query con JOIN**. Mirá las filas que devuelve y comparalo con `selectinload` — `joinedload` puede multiplicar filas si la relación es 1-N.

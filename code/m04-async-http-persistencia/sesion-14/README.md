# S14 — Código de la sesión

```bash
uv sync
uv run python main.py
uv run mypy .
uv run ruff check .
uv run ruff format --check .
```

`main.py` recrea `tienda.db` (un archivo SQLite local) en cada corrida y muestra cuatro demos:

1. **Schema y datos sembrados** — cuatro tablas (`producto`, `cliente`, `pedido`, `linea_pedido`) con foreign keys y `CHECK`. La función `reconstruir_db` borra y vuelve a crear todo, así nunca te encontrás con un estado raro.
2. **`SELECT` con `WHERE`/`ORDER BY`/`GROUP BY`/`HAVING`** — top 3 más caros con stock, agregaciones por categoría, filtros sobre agregados.
3. **`JOIN`s** — `INNER JOIN` (clientes con pedidos) vs `LEFT JOIN` (todos los clientes) vs el patrón `LEFT JOIN ... WHERE ... IS NULL` (productos nunca vendidos).
4. **Transacción atómica** — un `checkout(cliente, [(producto, cantidad), ...])` que descuenta stock dentro de una transacción. Mostramos un caso feliz y un caso que falla por stock insuficiente: el `rollback` revierte el INSERT del pedido y deja el stock como estaba.

`pyproject.toml` no agrega dependencias — `sqlite3` está en la stdlib. Ruff y mypy heredan la configuración estricta del workspace.

**El archivo `tienda.db` queda en el directorio.** Podés inspeccionarlo:

```bash
uv run python -c "import sqlite3; c=sqlite3.connect('tienda.db'); c.row_factory=sqlite3.Row; \
    [print(dict(r)) for r in c.execute('SELECT * FROM producto')]"
```

O con la CLI `sqlite3` si la tenés instalada (`apt install sqlite3`):

```bash
sqlite3 tienda.db
sqlite> .tables
sqlite> .schema producto
sqlite> SELECT * FROM pedido;
```

Para experimentar:

- En `demo_transaccion`, sacá el `conn.rollback()` del `except` y volvé a correr. Vas a ver que el pedido queda creado **a medias** (con la primera línea pero sin la segunda). Ese es el desastre que la transacción evita.
- Cambiá el `CHECK (precio > 0)` del schema a `CHECK (precio > 100)`. La inserción de "Cable USB" va a fallar con `IntegrityError`. SQLite valida las CHECKs en cada `INSERT`/`UPDATE`.
- Ejecutá `EXPLAIN QUERY PLAN ...` desde Python para alguna query del `demo_select` y mirá el plan: vas a ver `SCAN` (recorrido completo) cuando no hay índice. Agregá `CREATE INDEX idx_producto_categoria ON producto(categoria);` y volvé a explicar — aparece `SEARCH USING INDEX`.

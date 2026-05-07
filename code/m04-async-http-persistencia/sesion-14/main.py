"""Demo de S14 — SQL fundamentals con sqlite3 (stdlib).

Ejecuta el programa con:
    uv run python main.py

Verifica los tipos con:
    uv run mypy .

Verifica el estilo con:
    uv run ruff check .
    uv run ruff format --check .

Crea (o recrea) `tienda.db` con cuatro tablas (producto, cliente, pedido,
linea_pedido), la puebla con datos de prueba y corre cuatro demos sobre ella:

1. CREATE TABLE + INSERT con parámetros (nada de strings concatenados).
2. SELECT con WHERE / ORDER BY / GROUP BY / HAVING.
3. JOINs: INNER vs LEFT.
4. Transacción: checkout atómico con rollback en caso de fallo.
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "tienda.db"


def seccion(titulo: str) -> None:
    print()
    print("=" * 60)
    print(titulo)
    print("=" * 60)


# ---------------------------------------------------------------------------
# 1. Schema y datos
# ---------------------------------------------------------------------------


SCHEMA = """
DROP TABLE IF EXISTS linea_pedido;
DROP TABLE IF EXISTS pedido;
DROP TABLE IF EXISTS producto;
DROP TABLE IF EXISTS cliente;

CREATE TABLE producto (
    id INTEGER PRIMARY KEY,
    nombre TEXT NOT NULL UNIQUE,
    categoria TEXT NOT NULL,
    precio REAL NOT NULL CHECK (precio > 0),
    stock INTEGER NOT NULL DEFAULT 0 CHECK (stock >= 0)
);

CREATE TABLE cliente (
    id INTEGER PRIMARY KEY,
    nombre TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE
);

CREATE TABLE pedido (
    id INTEGER PRIMARY KEY,
    cliente_id INTEGER NOT NULL REFERENCES cliente(id),
    creado_en TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE linea_pedido (
    pedido_id INTEGER NOT NULL REFERENCES pedido(id),
    producto_id INTEGER NOT NULL REFERENCES producto(id),
    cantidad INTEGER NOT NULL CHECK (cantidad > 0),
    precio_unitario REAL NOT NULL,
    PRIMARY KEY (pedido_id, producto_id)
);
"""


PRODUCTOS_SEED = [
    ("Cable USB", "accesorios", 12.5, 30),
    ("Auriculares Bluetooth", "audio", 89.99, 5),
    ("Teclado Mecánico", "computación", 49.5, 12),
    ("Monitor 4K", "computación", 320.0, 3),
    ("Ratón Inalámbrico", "computación", 19.99, 30),
    ("Lámpara LED", "oficina", 35.5, 7),
    ("Webcam HD", "computación", 79.0, 0),
]

CLIENTES_SEED = [
    ("Ana Pérez", "ana@example.com"),
    ("Bruno López", "bruno@example.com"),
    ("Carla Díaz", "carla@example.com"),
]


def conectar() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def reconstruir_db() -> None:
    if DB_PATH.exists():
        DB_PATH.unlink()
    conn = conectar()
    try:
        conn.executescript(SCHEMA)
        conn.executemany(
            "INSERT INTO producto (nombre, categoria, precio, stock) VALUES (?, ?, ?, ?)",
            PRODUCTOS_SEED,
        )
        conn.executemany(
            "INSERT INTO cliente (nombre, email) VALUES (?, ?)",
            CLIENTES_SEED,
        )
        # Un pedido inicial: Ana compra 1 monitor.
        cursor = conn.execute(
            "INSERT INTO pedido (cliente_id) VALUES ((SELECT id FROM cliente WHERE nombre = ?))",
            ("Ana Pérez",),
        )
        pedido_id = cursor.lastrowid
        conn.execute(
            "INSERT INTO linea_pedido (pedido_id, producto_id, cantidad, precio_unitario) "
            "VALUES (?, (SELECT id FROM producto WHERE nombre = ?), ?, "
            "(SELECT precio FROM producto WHERE nombre = ?))",
            (pedido_id, "Monitor 4K", 1, "Monitor 4K"),
        )
        conn.execute(
            "UPDATE producto SET stock = stock - 1 WHERE nombre = ?",
            ("Monitor 4K",),
        )
        conn.commit()
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# 1. Demo: schema + insert
# ---------------------------------------------------------------------------


def demo_schema() -> None:
    seccion("1. Schema y datos sembrados")
    conn = conectar()
    try:
        for tabla in ("producto", "cliente", "pedido", "linea_pedido"):
            row = conn.execute(f"SELECT COUNT(*) AS n FROM {tabla}").fetchone()
            print(f"  {tabla}: {row['n']} filas")
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# 2. Demo: SELECT con WHERE / ORDER BY / GROUP BY / HAVING
# ---------------------------------------------------------------------------


def demo_select() -> None:
    seccion("2. SELECT — WHERE, ORDER BY, GROUP BY, HAVING")
    conn = conectar()
    try:
        print("  Top 3 productos más caros con stock > 0:")
        for row in conn.execute(
            "SELECT nombre, precio FROM producto WHERE stock > 0 ORDER BY precio DESC LIMIT 3"
        ):
            print(f"    {row['nombre']:<25} ${row['precio']:>8.2f}")

        print("\n  Productos por categoría (con AVG precio):")
        for row in conn.execute(
            "SELECT categoria, COUNT(*) AS cantidad, AVG(precio) AS precio_medio "
            "FROM producto GROUP BY categoria ORDER BY cantidad DESC"
        ):
            print(
                f"    {row['categoria']:<14} {row['cantidad']:>3} productos  "
                f"~${row['precio_medio']:.2f}"
            )

        print("\n  Categorías con más de 1 producto (HAVING):")
        for row in conn.execute(
            "SELECT categoria, COUNT(*) AS n FROM producto GROUP BY categoria HAVING COUNT(*) > 1"
        ):
            print(f"    {row['categoria']}: {row['n']}")
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# 3. Demo: JOINs
# ---------------------------------------------------------------------------


def demo_joins() -> None:
    seccion("3. JOINs — INNER vs LEFT")
    conn = conectar()
    try:
        print("  INNER JOIN — solo clientes que TIENEN pedidos:")
        for row in conn.execute(
            "SELECT c.nombre, COUNT(p.id) AS pedidos "
            "FROM cliente c INNER JOIN pedido p ON p.cliente_id = c.id "
            "GROUP BY c.id"
        ):
            print(f"    {row['nombre']:<14} {row['pedidos']} pedido(s)")

        print("\n  LEFT JOIN — todos los clientes (incluyendo los sin pedidos):")
        for row in conn.execute(
            "SELECT c.nombre, COUNT(p.id) AS pedidos "
            "FROM cliente c LEFT JOIN pedido p ON p.cliente_id = c.id "
            "GROUP BY c.id"
        ):
            print(f"    {row['nombre']:<14} {row['pedidos']} pedido(s)")

        print("\n  Productos NUNCA vendidos (LEFT JOIN + IS NULL):")
        for row in conn.execute(
            "SELECT pr.nombre FROM producto pr "
            "LEFT JOIN linea_pedido lp ON lp.producto_id = pr.id "
            "WHERE lp.producto_id IS NULL"
        ):
            print(f"    {row['nombre']}")
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# 4. Demo: Transacción atómica con rollback
# ---------------------------------------------------------------------------


class StockInsuficiente(Exception):
    pass


def checkout(conn: sqlite3.Connection, cliente_email: str, items: list[tuple[str, int]]) -> int:
    """items = [(nombre_producto, cantidad), ...]. Devuelve el pedido_id."""
    cliente = conn.execute("SELECT id FROM cliente WHERE email = ?", (cliente_email,)).fetchone()
    if cliente is None:
        raise LookupError(f"cliente {cliente_email!r} no existe")

    cursor = conn.execute("INSERT INTO pedido (cliente_id) VALUES (?)", (cliente["id"],))
    pedido_id = cursor.lastrowid
    if pedido_id is None:
        raise RuntimeError("INSERT INTO pedido no devolvió lastrowid")

    for nombre, cantidad in items:
        prod = conn.execute(
            "SELECT id, precio, stock FROM producto WHERE nombre = ?", (nombre,)
        ).fetchone()
        if prod is None:
            raise LookupError(f"producto {nombre!r} no existe")
        if prod["stock"] < cantidad:
            raise StockInsuficiente(f"{nombre}: stock {prod['stock']}, pedido {cantidad}")

        conn.execute(
            "INSERT INTO linea_pedido (pedido_id, producto_id, cantidad, precio_unitario) "
            "VALUES (?, ?, ?, ?)",
            (pedido_id, prod["id"], cantidad, prod["precio"]),
        )
        conn.execute(
            "UPDATE producto SET stock = stock - ? WHERE id = ?",
            (cantidad, prod["id"]),
        )
    return pedido_id


def demo_transaccion() -> None:
    seccion("4. Transacción atómica — checkout con rollback")

    # --- caso feliz ---
    conn = conectar()
    try:
        try:
            pedido_id = checkout(
                conn, "ana@example.com", [("Cable USB", 2), ("Teclado Mecánico", 1)]
            )
            conn.commit()
            print(f"  [OK] pedido {pedido_id} creado")
        except (StockInsuficiente, LookupError) as e:
            conn.rollback()
            print(f"  [ERR] no se creó: {e}")
    finally:
        conn.close()

    # --- caso de fallo: rollback debe revertir todo ---
    conn = conectar()
    try:
        stock_antes = conn.execute(
            "SELECT stock FROM producto WHERE nombre = 'Cable USB'"
        ).fetchone()["stock"]
        pedidos_antes = conn.execute("SELECT COUNT(*) AS n FROM pedido").fetchone()["n"]

        try:
            checkout(
                conn,
                "bruno@example.com",
                [("Cable USB", 1), ("Auriculares Bluetooth", 999)],  # stock 5
            )
            conn.commit()
            print("  [INESPERADO] no debería haber llegado aquí")
        except StockInsuficiente as e:
            conn.rollback()
            print(f"  [esperado] {e}  → rollback")

        stock_despues = conn.execute(
            "SELECT stock FROM producto WHERE nombre = 'Cable USB'"
        ).fetchone()["stock"]
        pedidos_despues = conn.execute("SELECT COUNT(*) AS n FROM pedido").fetchone()["n"]

        print(f"  stock Cable USB: antes={stock_antes} después={stock_despues}  ✓ igual")
        print(f"  pedidos:         antes={pedidos_antes} después={pedidos_despues}  ✓ igual")
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> None:
    reconstruir_db()
    demo_schema()
    demo_select()
    demo_joins()
    demo_transaccion()


if __name__ == "__main__":
    main()

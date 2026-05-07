# S14 — Ejercicios

> **Tiempo estimado:** ~70 min. Tres bloques: ejercicio guiado donde construís un schema completo desde cero, libres para entrenar joins / agregaciones / normalización, reto con un sistema de pedidos atómico.

> **Sin aporte al integrador hoy.** El integrador migra a DB real en S15 con SQLAlchemy. Hoy escribís SQL puro para entender lo que el ORM va a hacer por debajo.

---

## 0. Antes de empezar

Tu sandbox vive en `code/m04-async-http-persistencia/sesion-14/`. Si todavía no lo corriste:

```bash
cd code/m04-async-http-persistencia/sesion-14
uv sync
uv run python main.py
```

`main.py` deja una base SQLite (`tienda.db`) creada y poblada para que la consultes con la CLI de sqlite o desde Python. También limpia y recrea el archivo en cada corrida — no necesitás migrar nada.

**Para explorar la DB en consola:**

```bash
uv run python -c "import sqlite3; conn = sqlite3.connect('tienda.db'); conn.row_factory = sqlite3.Row; print([dict(r) for r in conn.execute('SELECT * FROM producto LIMIT 3')])"
```

O si tenés `sqlite3` CLI instalado:

```bash
sqlite3 tienda.db
sqlite> .tables
sqlite> .schema producto
sqlite> SELECT * FROM producto WHERE stock > 0;
```

## 1. Ejercicio guiado — Schema, datos y primeras queries

Este ejercicio usa `tienda.db` que dejó la demo. **Las queries las podés tipiar en `sqlite3` CLI o ejecutarlas desde Python con `conn.execute(...)`.**

### Paso 1.1 — Reconocer el schema

```sql
.schema
```

Vas a ver cuatro tablas: `producto`, `cliente`, `pedido`, `linea_pedido`. Identificá:

- ¿Cuáles son las primary keys?
- ¿Qué foreign keys conectan las tablas?
- ¿Por qué `linea_pedido` tiene primary key compuesta?

### Paso 1.2 — Lecturas básicas

Escribí **una query SQL** que conteste cada pregunta:

1. Listar todos los productos ordenados por precio descendente.
2. Productos con stock entre 5 y 20 (ambos inclusive), de la categoría "computación".
3. Cantidad de productos por categoría.
4. Categoría con el precio promedio más alto.
5. Top 3 productos más caros con stock > 0.

(Si te trabás, las soluciones están al final de este archivo en la sección "Pistas".)

### Paso 1.3 — Lecturas con joins

1. Para cada cliente, listar la cantidad de pedidos que hizo (incluyendo los que tienen 0).
2. Para cada pedido, mostrar nombre del cliente y total del pedido (suma de `cantidad * precio_unitario` de sus líneas).
3. Productos que aparecen en al menos un pedido.
4. Productos que **nunca** aparecieron en un pedido (pista: `LEFT JOIN` + `WHERE ... IS NULL`).
5. Cliente con más unidades compradas en total (sumando todas las cantidades de todas sus líneas).

### Paso 1.4 — Escrituras con transacción

Hoy Ana compra 3 unidades del producto "Cable USB". Tu trabajo:

1. Crear un nuevo `pedido` con `cliente_id` el de Ana.
2. Buscar el `producto.id` de "Cable USB" y su precio actual.
3. Insertar una `linea_pedido` con `cantidad = 3`, `precio_unitario = precio actual`.
4. Decrementar `producto.stock` en 3.
5. **Todo en una transacción.** Si cualquier paso falla, revertís todo.

Pista del esqueleto:

```python
import sqlite3

conn = sqlite3.connect("tienda.db")
conn.row_factory = sqlite3.Row
conn.execute("PRAGMA foreign_keys = ON")     # SQLite no las activa por defecto

try:
    cliente = conn.execute("SELECT id FROM cliente WHERE nombre = ?", ("Ana",)).fetchone()
    producto = conn.execute(
        "SELECT id, precio, stock FROM producto WHERE nombre = ?", ("Cable USB",)
    ).fetchone()

    if producto["stock"] < 3:
        raise RuntimeError("stock insuficiente")

    cursor = conn.execute(
        "INSERT INTO pedido (cliente_id) VALUES (?)", (cliente["id"],)
    )
    pedido_id = cursor.lastrowid

    conn.execute(
        "INSERT INTO linea_pedido (pedido_id, producto_id, cantidad, precio_unitario) "
        "VALUES (?, ?, ?, ?)",
        (pedido_id, producto["id"], 3, producto["precio"]),
    )

    conn.execute(
        "UPDATE producto SET stock = stock - ? WHERE id = ?",
        (3, producto["id"]),
    )

    conn.commit()
    print(f"pedido {pedido_id} creado")
except Exception:
    conn.rollback()
    raise
finally:
    conn.close()
```

Después corré una query y verificá:

- El pedido nuevo aparece en `pedido`.
- La línea aparece en `linea_pedido`.
- El stock de "Cable USB" bajó en 3.

### Paso 1.5 — Forzar un fallo y ver el rollback

Modificá el script: hacé que el `UPDATE` del stock pida `stock - 9999` (más del disponible). Vas a tener que agregar un `CHECK (stock >= 0)` en la tabla, que ya viene en el schema. Verificá que:

- La operación falla con `IntegrityError`.
- El rollback **deshace** el INSERT del pedido y la línea.
- El stock queda como antes.

**Lección:** ese es el valor real de las transacciones. No es ceremonia — es la barrera que impide que tus datos terminen en estado inconsistente.

## 2. Ejercicios libres

### 2.1. Migrar de "una tabla gigante" a 3NF

Te dan este dataset (en CSV o como dict en Python):

```
| pedido | cliente | email      | producto    | categoria   | precio | cantidad |
|--------|---------|------------|-------------|-------------|--------|----------|
| 1      | Ana     | ana@x.com  | Cable USB   | accesorios  | 12.5   | 3        |
| 1      | Ana     | ana@x.com  | Auriculares | audio       | 89.99  | 1        |
| 2      | Bruno   | bru@x.com  | Cable USB   | accesorios  | 12.5   | 2        |
| 3      | Ana     | ana@x.com  | Teclado     | computación | 49.5   | 1        |
```

Diseñá las tablas necesarias para representar lo mismo en 3NF (debería darte: `cliente`, `producto`, `pedido`, `linea_pedido`). Escribí los `CREATE TABLE` y los `INSERT` correspondientes para poblar las cuatro tablas a partir del dataset. Confirmá que:

- El email de Ana aparece **una sola vez**.
- El precio del Cable USB aparece **una sola vez** en la tabla producto, pero queda **congelado** en cada `linea_pedido`.

### 2.2. Subqueries

1. Productos cuyo precio es mayor al promedio.
   ```sql
   SELECT * FROM producto WHERE precio > (SELECT AVG(precio) FROM producto);
   ```
2. Clientes que tienen al menos un pedido por más de $100 (suma de su línea más cara).
3. La categoría con menor stock total.
4. Productos que **nunca** se vendieron (pista: `WHERE id NOT IN (SELECT producto_id FROM linea_pedido)`).

### 2.3. UPSERT (INSERT ... ON CONFLICT)

Tenés un script que importa productos desde un CSV. Si el producto ya existe (por nombre, que es UNIQUE), querés actualizar precio y stock; si no, insertarlo. Eso es UPSERT.

```sql
INSERT INTO producto (nombre, categoria, precio, stock)
VALUES ('Cable USB', 'accesorios', 14.99, 45)
ON CONFLICT(nombre) DO UPDATE SET
    precio = excluded.precio,
    stock = excluded.stock;
```

Probá esto sobre un producto existente y sobre uno nuevo. Verificá que:

- En el primer caso, **no se crea una fila** nueva — solo se actualiza la existente.
- En el segundo, se inserta normal.

`excluded` es la pseudo-tabla que contiene los valores que **intentaron** insertarse. Es como decir "los valores nuevos del INSERT".

### 2.4. Vista (VIEW)

Una vista es un `SELECT` guardado. Definí:

```sql
CREATE VIEW pedido_resumen AS
SELECT
    p.id AS pedido_id,
    c.nombre AS cliente,
    SUM(lp.cantidad * lp.precio_unitario) AS total,
    p.creado_en
FROM pedido p
JOIN cliente c ON c.id = p.cliente_id
JOIN linea_pedido lp ON lp.pedido_id = p.id
GROUP BY p.id;
```

Después usala como si fuera una tabla:

```sql
SELECT * FROM pedido_resumen WHERE total > 50;
```

¿Para qué sirve esto? Para encapsular una query compleja detrás de un nombre. El resto del código no necesita conocer el join.

### 2.5. EXPLAIN QUERY PLAN

Tirá esta query con y sin índice:

```sql
EXPLAIN QUERY PLAN SELECT * FROM producto WHERE categoria = 'computación';
```

Sin índice vas a ver `SCAN producto`. Después:

```sql
CREATE INDEX idx_producto_categoria ON producto(categoria);
```

Y volvé a tirar el EXPLAIN. Ahora aparece `SEARCH producto USING INDEX idx_producto_categoria`. Esa es la diferencia que un índice hace en el plan de ejecución.

## 3. Reto — Mini-sistema de checkout con integridad

Diseñá una función `checkout(cliente_id: int, items: list[tuple[int, int]]) -> int` que:

1. `items` es una lista de `(producto_id, cantidad)`.
2. **Reserva una transacción** y dentro:
   - Verifica que **cada** producto exista y tenga `stock >= cantidad`.
   - Si alguno no cumple, lanza `StockInsuficiente` y hace rollback.
   - Crea un pedido nuevo, mete las líneas y descuenta los stocks.
3. Devuelve el `pedido_id` del pedido creado.

**Reglas:**

- Capturá `sqlite3.IntegrityError` y traducila a una excepción de tu dominio.
- Si el cliente no existe, lanzá `ClienteNoEncontrado`.
- Si la lista de items está vacía, lanzá `PedidoVacio`.
- Asegurate de que el `precio_unitario` en cada línea sea el precio actual del producto en el momento del checkout.

Probala con tres casos:
- Un checkout válido con dos items.
- Un cliente que no existe.
- Un item con `cantidad > stock`.

**Por qué este patrón importa:** un checkout real (Mercado Libre, Amazon) hace exactamente esto: chequear stock, congelar precio, decrementar inventario, todo atómicamente. Si un paso falla, ningún paso ocurrió. La transacción es el único contrato que te garantiza eso.

## 4. Pistas de las queries de la sección 1.2 y 1.3

Solo abrí esto si te trabaste 10+ minutos en una.

```sql
-- 1.2.1
SELECT * FROM producto ORDER BY precio DESC;

-- 1.2.2
SELECT * FROM producto
WHERE stock BETWEEN 5 AND 20 AND categoria = 'computación';

-- 1.2.3
SELECT categoria, COUNT(*) FROM producto GROUP BY categoria;

-- 1.2.4
SELECT categoria, AVG(precio) AS promedio
FROM producto GROUP BY categoria
ORDER BY promedio DESC LIMIT 1;

-- 1.2.5
SELECT * FROM producto WHERE stock > 0
ORDER BY precio DESC LIMIT 3;

-- 1.3.1
SELECT c.nombre, COUNT(p.id) AS pedidos
FROM cliente c
LEFT JOIN pedido p ON p.cliente_id = c.id
GROUP BY c.id;

-- 1.3.2
SELECT p.id, c.nombre,
       SUM(lp.cantidad * lp.precio_unitario) AS total
FROM pedido p
JOIN cliente c ON c.id = p.cliente_id
JOIN linea_pedido lp ON lp.pedido_id = p.id
GROUP BY p.id;

-- 1.3.3
SELECT DISTINCT pr.* FROM producto pr
JOIN linea_pedido lp ON lp.producto_id = pr.id;

-- 1.3.4
SELECT pr.* FROM producto pr
LEFT JOIN linea_pedido lp ON lp.producto_id = pr.id
WHERE lp.producto_id IS NULL;

-- 1.3.5
SELECT c.nombre, SUM(lp.cantidad) AS total_unidades
FROM cliente c
JOIN pedido p ON p.cliente_id = c.id
JOIN linea_pedido lp ON lp.pedido_id = p.id
GROUP BY c.id
ORDER BY total_unidades DESC LIMIT 1;
```

---

Cuando termines, vuelve al README y responde las preguntas de auto-evaluación. Si todas se contestan sin dudar, S14 está consolidada y puedes pasar a [S15 — SQLAlchemy v2](../sesion-15-sqlalchemy/README.md), donde el SQL queda atrás del ORM pero **vos ya sabés qué hace**.

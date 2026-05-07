# S14 — SQL fundamentals: queries, joins, normalización

> **Sesión 2h.** ~50 min lectura + ~70 min ejercicios. Antes de tocar un ORM hay que entender la base de datos. Esta sesión es **SQL puro**: tablas, queries, joins y la idea de normalización. La herramienta es `sqlite3` (incluida en la stdlib, sin instalar nada). El concepto sirve igual para PostgreSQL, MySQL o cualquier RDBMS — la sintaxis varía 5%, las ideas son las mismas. Cuando llegues a S15 con SQLAlchemy, ya vas a saber **qué SQL está corriendo por debajo** del ORM, que es la única forma de usarlo bien.

---

## 1. Objetivos de aprendizaje

Al terminar esta sesión vas a poder:

- Explicar qué es una base de datos relacional y por qué supera al JSON para datos de negocio.
- Diseñar un esquema con tablas, columnas, tipos y `PRIMARY KEY`.
- Escribir queries `SELECT` con `WHERE`, `ORDER BY`, `LIMIT`, `GROUP BY`, `HAVING`.
- Insertar, actualizar y borrar filas con `INSERT`, `UPDATE`, `DELETE`.
- Combinar tablas con `INNER JOIN` y `LEFT JOIN` y entender la diferencia.
- Normalizar un esquema duplicado a 3NF (un nivel de normalización suficiente para 95% de las apps).
- Usar `FOREIGN KEY` para conectar tablas relacionadas.
- Entender qué es una **transacción**, cuándo se hace `COMMIT` y cuándo `ROLLBACK`.
- Conocer qué es un **índice**, cuándo agregarlo y cuándo no.

## 2. Prerequisitos

- Estructuras de datos (S03) — diccionarios y listas. Las filas son dicts; las tablas, listas de dicts conceptualmente.
- Manejo de errores (S07) — vamos a capturar `sqlite3.IntegrityError`.
- Tener `sqlite3` instalado: viene con Python, no hace falta nada extra.

## 3. Conceptos clave

1. **RDBMS (Relational Database Management System).** Software que guarda datos en tablas relacionadas y te deja hacerles preguntas con SQL. Ejemplos: SQLite, PostgreSQL, MySQL, MariaDB.
2. **Tabla.** Estructura tabular con columnas (atributos) y filas (registros). Cada columna tiene un **tipo** y restricciones.
3. **Schema.** El conjunto de tablas, sus columnas, tipos y relaciones. Es "la forma" de tu base.
4. **Primary key.** Columna(s) que identifica(n) cada fila de forma única. Típicamente `id INTEGER PRIMARY KEY`.
5. **Foreign key.** Columna que apunta a la primary key de otra tabla. Es lo que conecta las tablas.
6. **Query.** Una pregunta a la base. Las cuatro grandes: `SELECT` (leer), `INSERT` (crear), `UPDATE` (modificar), `DELETE` (borrar).
7. **JOIN.** Operación que combina filas de dos o más tablas siguiendo una condición — típicamente foreign key = primary key.
8. **Transacción.** Bloque de operaciones que pasa entero o no pasa: o todo se aplica (`COMMIT`) o nada (`ROLLBACK`).
9. **Índice.** Estructura auxiliar que acelera búsquedas en una columna a costa de escrituras más lentas. Las primary keys tienen índice automático.
10. **Normalización.** Proceso de eliminar duplicación reorganizando datos en varias tablas con foreign keys.

## 4. Teoría

### 4.1. Por qué una base de datos y no un JSON

Hasta ahora TiendaPro vive en un archivo JSON. Funciona para 10 productos en una máquina. ¿Y para?

- **10000 productos.** Cargar todo en memoria empieza a doler.
- **Búsquedas por categoría.** Tenés que iterar TODA la lista. Lento.
- **Pedidos.** Cada pedido apunta a productos y a clientes. Modelar relaciones en JSON es duplicar IDs por todos lados.
- **Concurrencia.** Si dos procesos escriben al JSON al mismo tiempo, te lo corrompen.
- **Búsquedas con condiciones combinadas.** "Productos de categoría X con stock > 0 ordenados por precio". Cuatro líneas en SQL, treinta en Python.
- **Integridad.** ¿Qué pasa si alguien borra un cliente y deja pedidos huérfanos? El JSON no te frena. La DB sí.

Una base de datos resuelve los seis a la vez. Es la herramienta correcta cuando **los datos importan más que el código**.

### 4.2. SQLite vs PostgreSQL: ¿cuál usar?

**SQLite.** Una base entera vive en **un archivo**. Sin servidor, sin cuentas, sin red. Viene incluida con Python (`import sqlite3`). Perfecta para aprender y para apps embebidas. Tiene 95% del SQL estándar.

**PostgreSQL.** Servidor de DB de verdad. Concurrencia robusta, JSON nativo, full-text search, extensions, replicación. Es lo que vas a usar en producción.

Para este curso: **aprendemos con SQLite** porque no requiere setup. El SQL que escribís sirve casi igual en Postgres — los conceptos se trasladan 1:1.

### 4.3. CREATE TABLE: definir el schema

```sql
CREATE TABLE producto (
    id INTEGER PRIMARY KEY,
    nombre TEXT NOT NULL,
    precio REAL NOT NULL,
    stock INTEGER NOT NULL DEFAULT 0,
    categoria TEXT NOT NULL,
    creado_en TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

Tres cosas a notar:

- **Tipos.** `INTEGER`, `REAL` (float), `TEXT`, `BLOB`. SQLite es flexible con tipos (técnicamente "type affinity"); Postgres es estricto. **Tratá los tipos como si fueran estrictos** y vas a estar bien en ambos.
- **Restricciones.** `NOT NULL` (no acepta nulo), `DEFAULT x` (valor si no se pasa), `UNIQUE` (no se repite), `CHECK (precio > 0)` (regla custom).
- **`id INTEGER PRIMARY KEY`** en SQLite es **autoincremental**. En Postgres se escribe `id SERIAL PRIMARY KEY` o `id BIGSERIAL PRIMARY KEY`.

Convenciones de nombres del curso:
- Tablas en singular, snake_case: `producto`, `cliente`, `pedido`, `linea_pedido`.
- Columnas snake_case: `precio`, `nombre_completo`, `creado_en`.
- Foreign keys nombradas con el patrón `<tabla_referenciada>_id`: `producto_id`, `cliente_id`.

### 4.4. INSERT: crear filas

```sql
INSERT INTO producto (nombre, precio, stock, categoria)
VALUES ('Cable USB', 12.5, 30, 'accesorios');

-- múltiples filas en una sola sentencia:
INSERT INTO producto (nombre, precio, stock, categoria) VALUES
    ('Mouse', 19.99, 50, 'computación'),
    ('Teclado', 49.5, 12, 'computación');
```

**Nunca concatenes valores en strings de SQL** — eso es SQL injection. Usá **parámetros**:

```python
import sqlite3

conn = sqlite3.connect("tienda.db")
conn.execute(
    "INSERT INTO producto (nombre, precio, stock, categoria) VALUES (?, ?, ?, ?)",
    ("Cable USB", 12.5, 30, "accesorios"),
)
conn.commit()
```

Los `?` son **placeholders**. La librería se encarga de escapar correctamente. **Siempre** así.

### 4.5. SELECT: leer filas

```sql
-- todo
SELECT * FROM producto;

-- columnas específicas
SELECT nombre, precio FROM producto;

-- filtrar
SELECT * FROM producto WHERE categoria = 'computación';

-- combinaciones
SELECT * FROM producto
WHERE categoria = 'computación' AND stock > 0
ORDER BY precio ASC
LIMIT 5;

-- contar, sumar, promedios
SELECT COUNT(*) FROM producto;
SELECT SUM(precio * stock) AS valor_inventario FROM producto;
SELECT categoria, COUNT(*) AS cantidad, AVG(precio) AS precio_medio
FROM producto
GROUP BY categoria
HAVING COUNT(*) > 1;
```

**Operadores `WHERE` que vas a usar más:**

- `=`, `!=`, `<`, `>`, `<=`, `>=`
- `BETWEEN x AND y` (rango)
- `IN (a, b, c)` (lista)
- `LIKE 'cab%'` (texto que empieza con "cab")
- `IS NULL` / `IS NOT NULL` (NUNCA `= NULL`, eso siempre es falso)

**`ORDER BY` y `LIMIT`** son la forma estándar de paginar:

```sql
SELECT * FROM producto ORDER BY id LIMIT 20 OFFSET 40;   -- página 3 de 20
```

### 4.6. UPDATE y DELETE

```sql
-- actualizar
UPDATE producto SET stock = stock - 1 WHERE id = 42;

-- borrar
DELETE FROM producto WHERE stock = 0;
```

**Regla de seguridad:** antes de `UPDATE` o `DELETE`, escribí el `SELECT` con el mismo `WHERE` y mirá qué filas afecta. Si te equivocás de condición, un `UPDATE producto SET stock = 0` **sin WHERE** te pone en cero **todas** las filas. Es el clásico desastre.

### 4.7. JOIN: combinar tablas

Imaginá dos tablas:

```sql
CREATE TABLE cliente (
    id INTEGER PRIMARY KEY,
    nombre TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE
);

CREATE TABLE pedido (
    id INTEGER PRIMARY KEY,
    cliente_id INTEGER NOT NULL REFERENCES cliente(id),
    total REAL NOT NULL,
    creado_en TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

#### INNER JOIN — solo las filas que **matchean en ambos lados**

```sql
SELECT cliente.nombre, pedido.id, pedido.total
FROM cliente
INNER JOIN pedido ON pedido.cliente_id = cliente.id;
```

Devuelve los pedidos junto al nombre del cliente. **Si un cliente no tiene pedidos, no aparece.**

#### LEFT JOIN — todas las filas de la izquierda; lo de la derecha puede ser `NULL`

```sql
SELECT cliente.nombre, COUNT(pedido.id) AS cantidad_pedidos
FROM cliente
LEFT JOIN pedido ON pedido.cliente_id = cliente.id
GROUP BY cliente.id;
```

Devuelve **todos** los clientes, con la cantidad de pedidos (0 si no tiene ninguno).

**Mental model:**

- **`INNER JOIN`** = intersección. "Las filas que cumplen en los dos lados".
- **`LEFT JOIN`** = todo de la izquierda. "Todas las filas de A; si no hay match en B, los campos de B son NULL".
- (Existen `RIGHT JOIN` y `FULL JOIN`, pero LEFT cubre el 99% de los casos. `RIGHT` es invertir el orden.)

### 4.8. Normalización: el porqué de tener varias tablas

**Anti-ejemplo (todo en una tabla):**

```
| pedido_id | cliente_nombre | cliente_email | producto_nombre | precio_unitario | cantidad |
|-----------|----------------|---------------|-----------------|------------------|----------|
| 1         | Ana            | ana@x.com     | Cable USB       | 12.5             | 3        |
| 1         | Ana            | ana@x.com     | Auriculares     | 89.99            | 1        |
| 2         | Bruno          | bruno@x.com   | Cable USB       | 12.5             | 2        |
```

Problemas:

- **Duplicación.** El email de Ana aparece dos veces. Si Ana lo cambia, ¿actualizás cuántas filas?
- **Anomalías de inserción.** ¿Cómo registrás un cliente que todavía no compró? Tendrías que dejar las columnas de producto en NULL — feo.
- **Anomalías de eliminación.** Si borrás el último pedido de Bruno, perdés que Bruno existió.

**Solución (3NF):**

```sql
-- entidad cliente: una fila por cliente
CREATE TABLE cliente (
    id INTEGER PRIMARY KEY,
    nombre TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE
);

-- entidad producto: una fila por producto
CREATE TABLE producto (
    id INTEGER PRIMARY KEY,
    nombre TEXT NOT NULL,
    precio REAL NOT NULL,
    stock INTEGER NOT NULL DEFAULT 0
);

-- entidad pedido: una fila por pedido
CREATE TABLE pedido (
    id INTEGER PRIMARY KEY,
    cliente_id INTEGER NOT NULL REFERENCES cliente(id),
    creado_en TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- relación pedido↔producto: muchos a muchos
CREATE TABLE linea_pedido (
    pedido_id INTEGER NOT NULL REFERENCES pedido(id),
    producto_id INTEGER NOT NULL REFERENCES producto(id),
    cantidad INTEGER NOT NULL,
    precio_unitario REAL NOT NULL,
    PRIMARY KEY (pedido_id, producto_id)
);
```

Ahora:

- El email de Ana vive en **una sola fila** de `cliente`. Cambiar es un `UPDATE` puntual.
- Podés tener un cliente sin pedidos (Ana existe en `cliente` aunque no haya nada en `pedido`).
- La duplicación se eliminó.

**Las tres reglas de la normalización (versión simple):**

1. **1NF**: cada celda contiene **un valor atómico** (no listas, no JSON anidado).
2. **2NF**: si tu primary key es compuesta, las columnas no-clave dependen de **toda** la clave, no de una parte.
3. **3NF**: las columnas no-clave dependen **solo de la primary key**, no de otra columna no-clave.

Para 95% de los esquemas, "una entidad → una tabla, repeticiones se desnormalizan a tablas separadas con foreign keys" alcanza. Si conocés esa intuición, tu schema va a estar bien.

**Cuándo desnormalizar a propósito:** performance crítica, datos de solo lectura (dashboards), análisis. Pero **arrancá normalizado** y desnormalizá cuando midas un cuello de botella concreto.

### 4.9. Transacciones: todo o nada

Una **transacción** es un bloque atómico:

```sql
BEGIN;
UPDATE cuenta SET saldo = saldo - 100 WHERE id = 1;
UPDATE cuenta SET saldo = saldo + 100 WHERE id = 2;
COMMIT;
```

Si algo falla entre los dos `UPDATE`, hacés `ROLLBACK` y la base vuelve al estado previo. **Nunca te queda media transferencia hecha.**

En Python con sqlite3:

```python
conn = sqlite3.connect("tienda.db")
try:
    conn.execute("UPDATE cuenta SET saldo = saldo - ? WHERE id = ?", (100, 1))
    conn.execute("UPDATE cuenta SET saldo = saldo + ? WHERE id = ?", (100, 2))
    conn.commit()
except Exception:
    conn.rollback()
    raise
```

Por defecto, sqlite3 abre una transacción automáticamente con la primera operación de escritura. **`commit()` la cierra. Si nunca llamás `commit()`, los cambios se pierden cuando cerrás la conexión.** Ese es uno de los errores más comunes de los principiantes.

### 4.10. Índices: cómo acelerar las búsquedas

Cuando hacés `SELECT * FROM producto WHERE categoria = 'computación'` en una tabla con un millón de filas, la base lee **todas las filas**. Con un índice:

```sql
CREATE INDEX idx_producto_categoria ON producto(categoria);
```

La base mantiene una estructura ordenada (B-tree) que le permite encontrar las filas con `categoria = 'computación'` en log(n) en vez de n.

**Cuándo agregar un índice:**

- ✅ Columnas que aparecen frecuentemente en `WHERE`, `JOIN`, `ORDER BY`.
- ✅ Foreign keys (en muchos RDBMS te lo recomiendan).
- ❌ Columnas que cambian todo el tiempo (cada UPDATE actualiza también el índice).
- ❌ Columnas con muy pocos valores distintos (`activo BOOLEAN`).

**Las primary keys tienen índice automático.** No tenés que crearlo.

**Regla general:** arrancá sin índices custom. Cuando una query es lenta, mirás el plan de ejecución (`EXPLAIN QUERY PLAN ...`) y agregás un índice si hace falta. No agregues índices "por las dudas".

### 4.11. SQLite con Python: lo mínimo

```python
import sqlite3

# 1. Conectar (crea el archivo si no existe)
conn = sqlite3.connect("tienda.db")
conn.row_factory = sqlite3.Row     # filas accesibles como dicts

# 2. Ejecutar DDL
conn.executescript("""
    CREATE TABLE IF NOT EXISTS producto (
        id INTEGER PRIMARY KEY,
        nombre TEXT NOT NULL,
        precio REAL NOT NULL
    );
""")

# 3. Insertar (con parámetros)
conn.execute(
    "INSERT INTO producto (nombre, precio) VALUES (?, ?)",
    ("Cable USB", 12.5),
)
conn.commit()

# 4. Leer
for row in conn.execute("SELECT * FROM producto WHERE precio < ?", (50,)):
    print(row["nombre"], row["precio"])

# 5. Cerrar
conn.close()
```

Notas:

- `sqlite3.Row` te deja acceder por nombre (`row["nombre"]`) **además** de por índice.
- `executescript` para múltiples sentencias DDL separadas por `;`.
- `executemany` para insertar muchas filas con una iteración.
- En el integrador (M4 hito) y en S15 vamos a envolver esto detrás de SQLAlchemy. **Acá lo escribís a mano para entender qué hace por debajo.**

## 5. Patrones y antipatrones

| ✅ Patrón | ❌ Antipatrón |
|---|---|
| Parámetros con `?` | Concatenar strings (`f"... WHERE id = {id}"`) — SQL injection |
| Schema con tablas separadas + foreign keys | Una tabla gigante con columnas duplicadas |
| `commit()` después de las operaciones | Olvidarse y descubrir que los cambios "se perdieron" |
| `WHERE` antes de `UPDATE`/`DELETE` (siempre) | `UPDATE producto SET stock = 0` sin WHERE |
| Foreign keys + `REFERENCES` | Foreign keys "implícitas" sin restricción |
| Índices en columnas que se filtran mucho | Índices "por las dudas" en cada columna |
| Empezar normalizado, desnormalizar con datos | Desnormalizar de movida "para que vaya rápido" |
| `SELECT col1, col2 FROM ...` | `SELECT * FROM ...` cuando solo necesitás dos columnas |
| `BEGIN/COMMIT` explícito en operaciones de varias sentencias | Operaciones críticas sin transacción |
| `IS NULL` / `IS NOT NULL` | `= NULL` / `!= NULL` (siempre falso) |

## 6. Conexión con el proyecto integrador

Hoy todavía **no migramos el integrador a una DB real** — eso pasa en S15 con SQLAlchemy. Pero ya podemos diseñar **el schema** que vamos a usar:

```sql
-- producto: catalogo
CREATE TABLE producto (
    id INTEGER PRIMARY KEY,
    nombre TEXT NOT NULL UNIQUE,
    categoria TEXT NOT NULL,
    precio REAL NOT NULL CHECK (precio > 0),
    stock INTEGER NOT NULL DEFAULT 0 CHECK (stock >= 0)
);

-- cliente: futuros usuarios de la API
CREATE TABLE cliente (
    id INTEGER PRIMARY KEY,
    nombre TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE
);

-- pedido: la tabla "puente" entre cliente y producto
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
```

**Por qué `precio_unitario` en `linea_pedido` y no solo en `producto`**: el precio del producto puede cambiar mañana; el precio que pagó Ana en el pedido de ayer es **histórico** y no se modifica. La línea del pedido **congela** el precio del momento.

Ese tipo de decisiones aparecen al diseñar schemas reales y no son obvias hasta que las ves.

## 7. Resumen

1. **Una base de datos resuelve cinco problemas que JSON no:** búsqueda, concurrencia, integridad, escala, relaciones.
2. **SQLite y PostgreSQL hablan SQL casi idéntico.** Aprendé en SQLite, escalá a Postgres en producción.
3. **El schema es la forma de tu base.** Tablas, columnas, tipos, primary keys, foreign keys.
4. **Cuatro queries fundamentales: `SELECT`, `INSERT`, `UPDATE`, `DELETE`.** Con `WHERE`, `ORDER BY`, `LIMIT` cubrís el 80% del trabajo.
5. **Joins:** `INNER JOIN` para "filas que cumplen ambos lados", `LEFT JOIN` para "todas las del izquierdo, los nulos en el otro".
6. **Normalizá hasta 3NF**: una entidad por tabla, sin duplicación, foreign keys conectan.
7. **Las transacciones son atómicas: `COMMIT` o `ROLLBACK`.** Sin `commit()`, los cambios no persisten.
8. **Índices aceleran lecturas y enlentecen escrituras.** Empezá sin índices custom.
9. **Parámetros con `?`, NUNCA strings concatenados.** SQL injection es un bug clásico evitable.
10. **El precio en `linea_pedido` es histórico**: se congela porque el precio del producto puede cambiar.

## 8. Preguntas de auto-evaluación

1. ¿Qué cinco problemas resuelve un RDBMS que un archivo JSON no resuelve?
2. Diferencia entre `INNER JOIN` y `LEFT JOIN` — escribí dos queries que devuelvan resultados distintos sobre el mismo dataset.
3. ¿Por qué es peligroso `UPDATE producto SET stock = 0` sin `WHERE`? ¿Cuál es la disciplina para evitar ese error?
4. Diseñá el schema (tablas + foreign keys) de un blog: usuarios, posts y comentarios.
5. ¿Por qué `SELECT * FROM x WHERE col = NULL` no devuelve nunca filas con `col` nulo?
6. ¿Qué hace una transacción? ¿Cuándo usás `ROLLBACK`?
7. ¿Cómo agregarías un índice a la columna `email` de la tabla `cliente`? ¿En qué casos te conviene? ¿Cuándo te perjudica?
8. Tenés `producto(precio)` que cambia con el tiempo. ¿Cómo guardás el precio que pagó cada cliente en su pedido **sin** que se vea afectado por cambios futuros?
9. ¿Qué pasa si insertás `INSERT INTO pedido (cliente_id, ...) VALUES (999, ...)` y `cliente.id = 999` no existe? ¿Qué te garantiza esa protección?
10. ¿Qué hace 3NF? Da un ejemplo de un schema **no** normalizado y normalizalo.

Cuando puedas responder todas, pasa a [`ejercicios.md`](ejercicios.md).

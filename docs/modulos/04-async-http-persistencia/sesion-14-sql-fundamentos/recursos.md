# S14 — Recursos

## Documentación oficial

- **`sqlite3` — Python stdlib** ([docs.python.org/3/library/sqlite3.html](https://docs.python.org/3/library/sqlite3.html)). Referencia del módulo Python que usamos en los ejercicios. Lee al menos "How to use placeholders" y "Transaction control".
- **SQLite Documentation** ([www.sqlite.org/docs.html](https://www.sqlite.org/docs.html)). La doc oficial de SQLite. La sección "Quirks, Caveats, and Gotchas" es **obligatoria** si pensás usar SQLite en producción.
- **PostgreSQL Documentation** ([www.postgresql.org/docs/current/](https://www.postgresql.org/docs/current/)). Si vas a producción con Postgres, la sección "Tutorial" y "SQL Language" son tu base.
- **PostgreSQL — SQL Language Statements** ([www.postgresql.org/docs/current/sql-commands.html](https://www.postgresql.org/docs/current/sql-commands.html)). Referencia exhaustiva de cada sentencia SQL.

## Lecturas guiadas

- **SQLBolt** ([sqlbolt.com](https://sqlbolt.com/)). Tutorial interactivo con ejercicios. Si lo pasás entero, pasaste todo lo de S14 con creces.
- **Mode Analytics — SQL Tutorial** ([mode.com/sql-tutorial](https://mode.com/sql-tutorial/)). Otro tutorial gratis muy bueno, especialmente para queries de análisis.
- **Use The Index, Luke!** ([use-the-index-luke.com](https://use-the-index-luke.com/)). Markus Winand explica índices y planes de ejecución como nadie. Si querés entender por qué tu query es lenta, este es el sitio.
- **Real Python — Introduction to Python SQL Libraries** ([realpython.com/python-sql-libraries](https://realpython.com/python-sql-libraries/)). Recorrido por sqlite3, MySQL connector y psycopg2.

## Para profundizar

- **Designing Data-Intensive Applications** (Martin Kleppmann, O'Reilly). Capítulos 2 (Modelos de datos) y 3 (Almacenamiento) son la mejor explicación moderna de **por qué** las bases de datos son como son.
- **The Art of PostgreSQL** (Dimitri Fontaine) ([theartofpostgresql.com](https://theartofpostgresql.com/)). Libro práctico que te muestra cuánto SQL "moderno" no estás usando.
- **Database Design for Mere Mortals** (Michael J. Hernandez). La referencia clásica para aprender a normalizar bien.
- **Pragmatic SQL** ([Sql Coloring Book / cualquier curso de Pragmatic AI Labs en YouTube](https://www.youtube.com)). Charlas sueltas de mucha calidad.

## Herramientas que vale la pena conocer

- **`sqlite3` CLI** — viene con SQLite. Comandos clave: `.tables`, `.schema TABLA`, `.mode column`, `.headers on`. Es tu repl de SQL.
- **DBeaver** ([dbeaver.io](https://dbeaver.io/)). Cliente gráfico libre que conecta a casi cualquier RDBMS. Útil para explorar bases existentes.
- **DB Browser for SQLite** ([sqlitebrowser.org](https://sqlitebrowser.org/)). Más simple que DBeaver, específico para SQLite. Bueno para visualizar el schema y hacer queries ad-hoc.
- **`pgcli`** y **`litecli`** — REPLs mejorados para Postgres y SQLite con autocomplete y syntax highlight.

## Referencias para resolver dudas puntuales

- **"Mis cambios no se guardan"** — falta `conn.commit()`. SQLite abre una transacción automática; sin commit, los cambios quedan en la transacción y se descartan al cerrar.
- **"`PRAGMA foreign_keys = ON` no funciona"** — tenés que ejecutarlo **en cada conexión nueva** de SQLite. No es persistente. (Postgres no tiene este problema — siempre las respeta.)
- **"`UNIQUE` me deja insertar duplicados"** — chequeá que la columna sea `NOT NULL`. `NULL != NULL` para SQLite, así que dos NULLs no se consideran duplicados.
- **"`ORDER BY` con strings ordena raro (mayúsculas antes de minúsculas)"** — comparación lexicográfica. Usá `ORDER BY LOWER(col)` o configurá la collation.
- **"`UPDATE`/`DELETE` afectó muchas más filas que esperaba"** — siempre revisá el `WHERE` con un `SELECT` primero. Es el debug más barato.

## Errores comunes

- **SQL injection** — concatenar valores en strings. La cura: parámetros con `?` SIEMPRE.
- **`SELECT *` en producción** — devuelve más datos de los que necesitás, rompe cuando agregás columnas, y oculta el costo de cada query. Listá las columnas.
- **Foreign keys sin índice** — un `JOIN ... ON pedido.cliente_id = cliente.id` puede ser lento si `cliente_id` no tiene índice. Por defecto en SQLite hay que crearlo a mano.
- **NULL = NULL** — siempre falso en SQL. Para chequear nulos: `IS NULL`, `IS NOT NULL`.
- **N+1 queries** — el clásico. Hacés un `SELECT` y por cada fila otro `SELECT`. Con 1000 filas son 1001 queries. La cura: un `JOIN`.
- **Olvidar transacciones en operaciones multi-step** — cualquier flujo "modificar A y luego B" debería ir en una transacción. Si no, una caída entre los dos te deja con datos inconsistentes.

## Si vas hacia el curso 2

En AI Engineering hay dos contextos donde SQL aparece:

- **Persistencia tradicional**. Logs de conversaciones, metadatos de documentos, auditoría de llamadas a LLMs. Todo esto vive en una DB relacional (típicamente Postgres).
- **Vector databases híbridas**. Postgres con `pgvector`, ParadeDB, Supabase. Combinás búsqueda vectorial (embeddings) con queries SQL clásicas (filtrar por usuario, por fecha, por tags). El SQL **no desaparece** — convive con la búsqueda semántica.

Saber escribir SQL a mano —no solo leer— te diferencia. Las herramientas tipo "AI SQL generator" están bien para empezar, pero terminás depurando lo que generan, y para eso hay que **leer SQL fluido**.

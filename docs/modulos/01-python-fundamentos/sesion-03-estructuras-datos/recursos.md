# S03 — Recursos

---

## Documentación oficial

- **Python tutorial — Data Structures** — https://docs.python.org/3/tutorial/datastructures.html
  Cubre `list`, `tuple`, `dict`, `set` con detalle. Lectura obligatoria.

- **Python docs — Built-in Types** — https://docs.python.org/3/library/stdtypes.html
  Referencia completa de métodos de cada tipo. Úsala como consulta.

- **`collections` module** — https://docs.python.org/3/library/collections.html
  Estructuras avanzadas: `Counter`, `defaultdict`, `deque`, `namedtuple`, `OrderedDict`. Cuando la solución idiomática se ponga repetitiva, mira aquí.

---

## Lecturas recomendadas

- **"Facts and Myths about Python names and values"** — Ned Batchelder.
  https://nedbatchelder.com/text/names.html
  Lo recomendamos en S01. Si no lo leíste todavía, S03 es el momento ideal — la mutabilidad y la asignación se vuelven críticas aquí.

- **"Python Data Structures: A Beginner's Guide"** — Real Python.
  Versión en artículo de lo que cubre la sesión, con visualizaciones.

- **"Time Complexity"** — Python Wiki.
  https://wiki.python.org/moin/TimeComplexity
  Tabla con la complejidad de cada operación (search, insert, delete) sobre cada estructura. Útil cuando tu código es lento y quieres saber por qué.

---

## Visualizaciones

- **Python Tutor** — https://pythontutor.com/
  Especialmente útil para entender mutabilidad. Pega el ejemplo de "asignar a otra variable" del ejercicio 2 y verás cómo dos nombres apuntan al mismo objeto.

---

## Sobre estructuras avanzadas que vas a ver

A medida que avances en el curso vas a encontrar:

- **`collections.Counter`** — un dict especializado para contar. `Counter(lista)` te devuelve `{elemento: cuenta, ...}`.
- **`collections.defaultdict`** — un dict que crea automáticamente entradas con un valor default. Evita el típico `if clave in d: ... else ...`.
- **`collections.namedtuple`** — una tupla con nombres para los campos. Reemplazada parcialmente por `dataclasses` (M2) en código moderno.
- **`frozenset`** — un set inmutable. Sirve cuando quieres un set como clave de dict.

No las uses en M1. Vas a verlas naturalmente cuando las necesites.

---

## Sobre la complejidad (importante para AI Engineering)

En el curso 2 (`python-ai-engineer-training`) vas a manipular catálogos de productos, embeddings de millones de filas, conjuntos de IDs. La diferencia entre buscar en una `list` (~O(n)) y un `set` (~O(1)) deja de ser teórica:

- 1.000 elementos: ambos son rápidos, no importa.
- 100.000 elementos: la lista tarda ~50 ms, el set tarda ~0.001 ms.
- 10.000.000 elementos: la lista tarda ~5 segundos. El set sigue tardando ~0.001 ms.

Internalizar esto desde M1 te ahorra refactors enteros más adelante.

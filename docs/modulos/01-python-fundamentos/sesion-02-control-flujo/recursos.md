# S02 — Recursos

---

## Documentación oficial

- **Python tutorial — Control Flow** — https://docs.python.org/3/tutorial/controlflow.html
  Cubre `if`, `for`, `while`, `break`, `continue`, `else` en bucles. Vale la pena leer.

- **Python docs — `range`** — https://docs.python.org/3/library/stdtypes.html#range
  El detalle completo de `range()` y sus variantes.

- **Python docs — `enumerate` y `zip`** — https://docs.python.org/3/library/functions.html
  Búscalas en la lista de built-ins. Léelas — son funciones que vas a usar todos los días.

---

## Lecturas recomendadas

- **"Looping in Python: 5 Techniques"** — Real Python.
  Cubre `for`, `enumerate`, `zip`, `reversed`, comprensiones. Con ejemplos prácticos.

- **PEP 8 — Indentation** — https://peps.python.org/pep-0008/#indentation
  Sección específica sobre indentación. Léela una vez para internalizar las reglas.

- **"List Comprehensions in Python"** — Real Python.
  Profundiza en comprensiones, incluyendo cuándo NO usarlas. Útil después de S02.

---

## Visualización paso a paso

- **Python Tutor** — https://pythontutor.com/
  Útil para ver cómo cambia el estado de las variables en cada iteración. Si te confundís con un bucle (especialmente con `break`/`continue`), ejecútalo en Python Tutor.

---

## Sobre comprensiones avanzadas

Existen más tipos que las que vimos:

- **Generator expression** — `(x*2 for x in range(10))`. Igual sintaxis que list comprehension pero con paréntesis. No genera la lista entera en memoria — la calcula bajo demanda. Útil para colecciones gigantes. Lo profundizamos en S09.

- **Set comprehension** — `{x for x in lista}`. Construye un set (sin duplicados). La diferencia con dict es que no tiene `:`.

- **Comprensiones anidadas** — `[x*y for x in lista1 for y in lista2]`. Equivale a un doble `for`. Se vuelven ilegibles muy rápido — evítalas salvo en casos triviales.

---

## Notas sobre `match` (Python 3.10+)

Python 3.10 introdujo `match/case` (similar al `switch` de otros lenguajes pero más potente). No lo cubrimos en M1 porque la mayoría del código que vas a leer todavía usa cadenas de `if/elif`. Cuando llegues a casos donde tu cadena de `if/elif` se vuelva incómoda, mira la doc de [`match`](https://docs.python.org/3/tutorial/controlflow.html#match-statements). Por ahora, `if/elif` es suficiente.

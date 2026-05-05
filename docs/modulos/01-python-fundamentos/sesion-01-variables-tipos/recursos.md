# S01 — Recursos

Material complementario para profundizar. Nada obligatorio, pero útil cuando vuelvas a esta sesión más adelante.

---

## Documentación oficial

- **Python tutorial — An informal introduction** — https://docs.python.org/3/tutorial/introduction.html
  La introducción oficial. Cubre números, strings y listas (las listas las vemos en S03). Lectura corta, vale la pena.

- **Python data model — built-in types** — https://docs.python.org/3/library/stdtypes.html
  Referencia completa de los tipos primitivos. Densa pero exhaustiva. Úsala como consulta, no como lectura lineal.

- **PEP 8 — Style Guide for Python Code** — https://peps.python.org/pep-0008/
  La guía de estilo oficial de Python. La sección "Naming Conventions" es la que más importa para esta sesión.

---

## Lecturas recomendadas

- **"Facts and Myths about Python names and values"** — Ned Batchelder.
  https://nedbatchelder.com/text/names.html
  La explicación canónica de "variables como vínculo, no como caja". Si te quedó alguna duda del §4.1 de la sesión, esta charla la resuelve. Hay versión escrita y versión video (PyCon).

- **"What Every Computer Scientist Should Know About Floating-Point Arithmetic"** — David Goldberg.
  https://docs.oracle.com/cd/E19957-01/806-3568/ncg_goldberg.html
  Paper clásico y exhaustivo sobre por qué `0.1 + 0.2 != 0.3`. Es denso. No tienes que leerlo entero — lee la introducción y la sección 1.

- **Real Python — Operators and Expressions** — https://realpython.com/python-operators-expressions/
  Cubre operadores con muchos ejemplos. Útil si te quedaste con dudas concretas sobre algún operador.

---

## Visualización paso a paso

- **Python Tutor** — https://pythontutor.com/
  Te permite ejecutar código Python paso a paso y ver gráficamente qué pasa con las variables y la memoria. Increíblemente útil cuando estés con dudas de "¿por qué pasó eso?". La explicación de "variables como vínculo" se vuelve obvia mirando los ejemplos en Python Tutor.

---

## Sobre operadores menos comunes

Python tiene varios operadores que no cubrimos en la sesión por ser secundarios. Los menciono para que los reconozcas si los ves:

- **Operadores bit a bit:** `&`, `|`, `^`, `~`, `<<`, `>>`. Trabajan a nivel binario. Útiles para optimizaciones específicas y networking. No los vas a necesitar en este curso.
- **Operador walrus (`:=`)**: introducido en Python 3.8. Asignación que es expresión. Útil pero opcional.
- **Operador de identidad (`is` / `is not`):** compara si dos variables apuntan al **mismo** objeto en memoria, no si tienen el mismo valor. Lo usamos solo con `None`. La diferencia con `==` es sutil pero importante — la profundizamos en S03.

---

## Diferencias con otros lenguajes (si vienes de otro)

Si tienes alguna exposición previa a otro lenguaje, estas son las diferencias más comunes que confunden al principio:

| Tema | Python | Otros lenguajes (C, Java, JS) |
|---|---|---|
| División entera con `/` | Devuelve `float` siempre | Devuelve entero si los operandos son enteros |
| `True`, `False`, `None` | Mayúscula inicial | `true`, `false`, `null` (minúsculas) |
| Concatenar string + número | Error explícito | Algunos lo hacen implícitamente (JS) |
| Tamaño de enteros | Sin límite | Limitado por bits (32 o 64) |
| Comparar strings | `==` compara contenido | En C, `==` compara puntero |
| Asignación múltiple | `a, b = 1, 2` (tupla) | Generalmente no existe |

---

## Una nota sobre estilo

Mucho del estilo Pythónico (snake_case, espacios alrededor de operadores, líneas cortas) lo vas a aprender por osmosis al leer código bien escrito. **No te obsesiones con la perfección de estilo en M1** — concéntrate en entender qué hace tu código. El estilo lo automatizamos con `ruff` en M3 y a partir de ahí no tienes que pensarlo más.

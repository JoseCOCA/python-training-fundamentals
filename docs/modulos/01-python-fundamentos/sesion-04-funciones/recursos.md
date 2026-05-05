# S04 — Recursos

---

## Documentación oficial

- **Python tutorial — Defining Functions** — https://docs.python.org/3/tutorial/controlflow.html#defining-functions
  Cubre `def`, parámetros, defaults, `*args`, `**kwargs`. Lectura corta y obligatoria.

- **Python tutorial — More on Defining Functions** — https://docs.python.org/3/tutorial/controlflow.html#more-on-defining-functions
  Profundiza en argumentos por nombre, posicional-only y keyword-only.

- **PEP 257 — Docstring conventions** — https://peps.python.org/pep-0257/
  Las convenciones para escribir docstrings. Léelo una vez.

---

## Lecturas recomendadas

- **"Python's Mutable vs Immutable Types: What's the Difference?"** — Real Python.
  Recapitula mutabilidad y se conecta directamente con el gotcha de `default=[]`.

- **"Pure Functions"** — Wikipedia.
  https://en.wikipedia.org/wiki/Pure_function
  Concepto de programación funcional. Útil para internalizar por qué las funciones puras son más fáciles de testear.

- **"Why mutable default arguments are bad"** — varios artículos.
  Buscá "python mutable default arguments" en cualquier blog. Es un gotcha tan famoso que tiene literatura propia.

---

## Sobre conceptos relacionados que vienen después

- **Type hints en funciones** (Módulo 3): `def calcular_total(precio: float, cantidad: int) -> float:`. Le dice a mypy y al editor qué tipos esperás.
- **Decoradores** (S09 del Módulo 2): funciones que envuelven otras funciones para agregarles comportamiento. Por ejemplo, `@cache` o `@property`. Conceptualmente avanzado pero útil.
- **Funciones lambda** (S04 brevemente, profundas en programación funcional): funciones anónimas de una línea. `lambda x: x * 2`. Las usaste en S03 con `sorted(..., key=...)`.
- **Cierres (closures)** (M2): cuando una función "interior" recuerda variables de la "exterior". Tema avanzado.

---

## Sobre style guides para funciones

PEP 8 te da reglas de estilo:
- Nombres en `snake_case`.
- 4 espacios de indentación.
- Línea en blanco entre funciones de nivel superior.
- Una línea en blanco entre métodos de una clase (M2).

`ruff` lo automatiza por ti. Por ahora, escríbelo a mano para internalizarlo.

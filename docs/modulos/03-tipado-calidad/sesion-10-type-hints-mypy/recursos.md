# S10 — Recursos

## Documentación oficial — Python

- **`typing` module** ([docs.python.org/3/library/typing.html](https://docs.python.org/3/library/typing.html)). Referencia completa de los tipos. Léela como un diccionario: cuando dudes de un tipo, abre la doc, busca y vuelve.
- **PEP 484 — Type Hints** ([peps.python.org/pep-0484/](https://peps.python.org/pep-0484/)). El PEP fundacional. Vale la pena leer las secciones de "Goals" y "Abstract" para entender por qué los type hints existen y por qué son **anotaciones, no enforcement**.
- **PEP 604 — Allow writing union types as `X | Y`** ([peps.python.org/pep-0604/](https://peps.python.org/pep-0604/)). El PEP que introdujo `int | str` en lugar de `Union[int, str]`. Para curiosidad histórica.
- **PEP 585 — Type hinting generics in standard collections** ([peps.python.org/pep-0585/](https://peps.python.org/pep-0585/)). El PEP que introdujo `list[int]` en lugar de `List[int]`.
- **PEP 544 — Protocols: Structural subtyping** ([peps.python.org/pep-0544/](https://peps.python.org/pep-0544/)). La motivación detrás de `Protocol`. Si trabajas en un equipo que mezcla herencia clásica y duck typing, vale leerlo entero.

## Documentación oficial — mypy

- **mypy documentation** ([mypy.readthedocs.io/](https://mypy.readthedocs.io/en/stable/)). La doc completa. Empieza por "Getting started" y "Type system reference".
- **Common issues and solutions** ([mypy.readthedocs.io/en/stable/common_issues.html](https://mypy.readthedocs.io/en/stable/common_issues.html)). Cuando mypy te reporta algo y no sabes qué hacer, casi seguro está aquí.
- **Configuring mypy** ([mypy.readthedocs.io/en/stable/config_file.html](https://mypy.readthedocs.io/en/stable/config_file.html)). Todas las flags. Ojo con `--strict`: activa varias cosas a la vez. La página explica qué activa cada una.
- **Cheat sheet** ([mypy.readthedocs.io/en/stable/cheat_sheet_py3.html](https://mypy.readthedocs.io/en/stable/cheat_sheet_py3.html)). Una hoja con la sintaxis típica. Útil para imprimir y tener al lado.

## Lecturas opcionales

- **Real Python — Type Checking in Python** ([realpython.com/python-type-checking/](https://realpython.com/python-type-checking/)). Recorrido extenso con ejemplos visuales y prácticos.
- **mypy blog — "The State of Static Typing in Python"** ([mypy-lang.blogspot.com/](https://mypy-lang.blogspot.com/)). Posts ocasionales del equipo de mypy. Históricos pero útiles para entender la evolución.

## Para profundizar

- **Fluent Python (Luciano Ramalho), capítulo 8 — "Type Hints in Functions"**. Tratamiento extenso una vez que tengas los fundamentos.
- **Fluent Python, capítulo 13 — "More about Type Hints"**. Cubre Protocols, TypeVars, callables, type narrowing.
- **"Writing types" — Brett Cannon** ([snarky.ca/](https://snarky.ca/)). Brett es core dev y mantiene típing. Sus posts son técnicos pero claros.

## Referencias para resolver dudas puntuales

- **`Optional[X]` vs `X | None`** — son **literalmente** equivalentes. Usa la moderna en proyectos 3.10+.
- **`Any` vs `object`** — `Any` desactiva el chequeo, `object` lo activa pero requiere narrowing. Si quieres "cualquier tipo pero verificame", usa `object`.
- **¿Cuándo usar `cast`?** — solo cuando mypy NO puede deducir el tipo aunque tú sepas que es correcto. La mayoría de las veces se reemplaza por `assert isinstance(...)` que también narrowea.
- **Type narrowing y `match` (Python 3.10+)** — el `match` también narrowea el tipo en cada `case`. Útil cuando tienes uniones grandes.

## Ecosistema de type checkers

- **mypy** — el más común, mantenido por la comunidad.
- **pyright** — el de Microsoft. Más rápido y a veces más estricto. Es el motor de Pylance en VS Code.
- **pyre** — el de Meta.
- **pytype** — el de Google.

Para este curso, **mypy es la elección por defecto**. Pero si trabajas con un IDE como VS Code, pyright probablemente ya está corriendo en background sin que lo sepas.

## Si vas hacia el curso 2

En AI Engineering trabajas con:

- **Tipos de respuesta de LLMs** — `dict[str, Any]` con estructura conocida. Aquí TypedDict te salva la vida.
- **pydantic** (S11) para validar runtime que las respuestas tengan la forma esperada.
- **Tools tipadas** — un agente recibe llamadas a tools cuyos parámetros tienen que ser tipados estrictamente (pydantic los valida).

Sin tipos sólidos, AI Engineering se vuelve una caja negra. **No avances con dudas en mypy** — es cimiento.

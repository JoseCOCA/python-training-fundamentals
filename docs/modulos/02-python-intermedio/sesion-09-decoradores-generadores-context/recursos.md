# S09 — Recursos

## Documentación oficial — Python

- **Generators — The Python Tutorial** ([docs.python.org/3/tutorial/classes.html#generators](https://docs.python.org/3/tutorial/classes.html#generators)). Parte del capítulo 9 del tutorial. Cubre `yield`, generator expressions y casos típicos. Lectura obligatoria.
- **`functools` module** ([docs.python.org/3/library/functools.html](https://docs.python.org/3/library/functools.html)). Documenta `wraps`, `cache`, `lru_cache`, `partial` y otras herramientas. La sección de `wraps` es obligatoria.
- **`contextlib` module** ([docs.python.org/3/library/contextlib.html](https://docs.python.org/3/library/contextlib.html)). Documenta `@contextmanager`, `suppress`, `closing`, `ExitStack`. Empieza con `@contextmanager`.
- **The `with` statement — language reference** ([docs.python.org/3/reference/compound_stmts.html#the-with-statement](https://docs.python.org/3/reference/compound_stmts.html#the-with-statement)). Cómo se traduce un `with` al protocolo `__enter__/__exit__`. Útil cuando necesitas entender el orden exacto.
- **PEP 343 — The "with" Statement** ([peps.python.org/pep-0343/](https://peps.python.org/pep-0343/)). El PEP que introdujo `with`. Si quieres entender la motivación histórica, vale.
- **PEP 318 — Decorators for Functions and Methods** ([peps.python.org/pep-0318/](https://peps.python.org/pep-0318/)). El PEP que introdujo la sintaxis `@`. Para curiosidad histórica.

## Lecturas opcionales

- **Real Python — Primer on Python Decorators** ([realpython.com/primer-on-python-decorators/](https://realpython.com/primer-on-python-decorators/)). Recorrido completo con ejemplos visuales.
- **Real Python — Python Generators 101** ([realpython.com/introduction-to-python-generators/](https://realpython.com/introduction-to-python-generators/)). Generadores desde cero con casos prácticos.
- **Real Python — Context Managers and Python's `with` Statement** ([realpython.com/python-with-statement/](https://realpython.com/python-with-statement/)). Buen complemento al README de la sesión.
- **David Beazley — Generator Tricks for Systems Programmers** ([dabeaz.com/generators/](https://www.dabeaz.com/generators/)). Charla de PyCon que cambió la forma en que mucha gente piensa los pipelines de procesamiento. Si te interesa el tema, es lectura/visualización casi obligatoria.

## Para profundizar

- **Fluent Python (Luciano Ramalho), capítulo 14 — "Iterables, Iterators, and Generators"**. Una vez que tengas los fundamentos, este capítulo es la mejor referencia.
- **Fluent Python, capítulo 9 — "Decorators and Closures"**. Misma calidad para decoradores.
- **Raymond Hettinger — "Transforming Code into Beautiful, Idiomatic Python"** ([youtube.com/watch?v=OSGv2VnC0go](https://www.youtube.com/watch?v=OSGv2VnC0go)). Charla clásica con varios ejemplos de generadores y decoradores aplicados a código real.

## Patrones del ecosistema

- **`@retry`** — la librería [tenacity](https://tenacity.readthedocs.io/) implementa un decorador de reintentos sofisticado. No la uses todavía — primero escribe el tuyo en los ejercicios. Pero es bueno saber que existe.
- **Logging con context managers** — la librería estándar `logging` tiene `LogRecord` y filtros que se combinan con context managers para agregar metadata temporalmente.
- **`@dataclass(frozen=True)` + `@functools.lru_cache`** — patrón común: una clase de valor inmutable como clave de cache.

## Si vas hacia el curso 2

En AI Engineering los tres conceptos aparecen constantemente:

- **Generadores asíncronos** (`async def` + `yield`) para streamear respuestas de LLMs token a token.
- **Decoradores** para registrar tools de un agente, agregar telemetría, retry con backoff exponencial.
- **Context managers** para manejar sesiones HTTP, transacciones de base de datos, MCP servers.

Si esta sesión te queda débil, los conceptos del curso 2 se vuelven mágicos. **No avances con dudas en estas tres herramientas** — son cimiento.

# S07 — Recursos

## Documentación oficial — Python

- **Errors and Exceptions** ([docs.python.org/3/tutorial/errors.html](https://docs.python.org/3/tutorial/errors.html)). Capítulo 8 del tutorial oficial. Cubre `try`/`except`, `raise`, jerarquía y excepciones definidas por el usuario. Lectura obligatoria.
- **Built-in Exceptions** ([docs.python.org/3/library/exceptions.html](https://docs.python.org/3/library/exceptions.html)). Tabla completa de la jerarquía estándar. Léelo una vez para tener la lista en la cabeza, y vuelve cuando dudes qué excepción lanzar.
- **The `try` statement — language reference** ([docs.python.org/3/reference/compound_stmts.html#the-try-statement](https://docs.python.org/3/reference/compound_stmts.html#the-try-statement)). Referencia formal del statement. Útil para entender el orden exacto de evaluación de `try/except/else/finally`.
- **`logging` — Logging facility** ([docs.python.org/3/library/logging.html](https://docs.python.org/3/library/logging.html)). En producción, antes de re-lanzar (o como parte del recovery) probablemente vas a logear. La intro del módulo es suficiente para empezar.

## Lecturas opcionales

- **Real Python — Python Exceptions: An Introduction** ([realpython.com/python-exceptions/](https://realpython.com/python-exceptions/)). Mismo material que el tutorial oficial pero con más ejemplos y diagramas.
- **Real Python — The `try`/`except`/`else`/`finally` Block** ([realpython.com/python-exceptions/#the-try-and-except-block-handling-exceptions](https://realpython.com/python-exceptions/#the-try-and-except-block-handling-exceptions)). Foco en el orden de ejecución de los cuatro bloques.
- **PEP 3134 — Exception Chaining and Embedded Tracebacks** ([peps.python.org/pep-3134/](https://peps.python.org/pep-3134/)). El PEP que introdujo `raise X from Y`. Si te interesa la motivación histórica del feature, vale.
- **Joel Spolsky — "Don't Let Architecture Astronauts Scare You"** ([joelonsoftware.com/2001/04/21/dont-let-architecture-astronauts-scare-you/](https://www.joelonsoftware.com/2001/04/21/dont-let-architecture-astronauts-scare-you/)). No es sobre excepciones, pero el principio aplica: una jerarquía de errores con 30 clases no es "robusto", es over-engineering. Tres o cuatro clases bien pensadas suelen alcanzar.

## Discusión clásica

- **EAFP vs LBYL** — [stackoverflow.com/q/11360858](https://stackoverflow.com/questions/11360858/what-is-the-eafp-principle-in-python). Hilo con la respuesta canónica y un par de ejemplos prácticos.
- **¿Cuándo crear excepciones de dominio?** — [stackoverflow.com/q/1319615](https://stackoverflow.com/questions/1319615/proper-way-to-declare-custom-exceptions-in-modern-python). Respuestas concisas con el patrón estándar.
- **`except: pass` y por qué es peligroso** — [docs.python.org/3/howto/logging.html#exceptions](https://docs.python.org/3/howto/logging.html#exceptions). La doc oficial recomienda `logger.exception(...)` cuando capturas y no re-lanzas.

## Para profundizar

- **Fluent Python (Luciano Ramalho), capítulo "Control flow"**. Cuando ya tengas los fundamentos, este capítulo trata el modelo de excepciones con profundidad y con ejemplos no triviales.
- **The Zen of Python** (`import this` en una sesión Python). Lee la línea "Errors should never pass silently. Unless explicitly silenced." — esa frase resume el espíritu de esta sesión.

## Si vas hacia el curso 2

En AI Engineering vas a manejar errores de:

- APIs externas (`httpx.HTTPStatusError`, timeouts, reintentos).
- Parseo de respuestas de LLMs (JSON malformado, validación pydantic).
- Tools que el LLM "alucina" (parámetros con tipos incorrectos).

Las excepciones de dominio que aprendiste hoy son la base de cómo se estructura el manejo de fallos en pipelines de agentes. Si esta sesión te queda débil, vuelve antes de avanzar.

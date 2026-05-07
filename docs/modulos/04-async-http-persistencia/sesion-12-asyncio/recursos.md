# S12 — Recursos

## Documentación oficial

- **`asyncio` — Asynchronous I/O** ([docs.python.org/3/library/asyncio.html](https://docs.python.org/3/library/asyncio.html)). Punto de entrada. Lee primero "asyncio — Asynchronous I/O" → "Coroutines and Tasks".
- **PEP 492 — Coroutines with `async` and `await` syntax** ([peps.python.org/pep-0492](https://peps.python.org/pep-0492/)). El PEP que introdujo `async def` y `await`. Útil para entender el porqué de la sintaxis.
- **PEP 654 — Exception Groups and `except*`** ([peps.python.org/pep-0654](https://peps.python.org/pep-0654/)). El motivo por el que `TaskGroup` agrupa excepciones.
- **PEP 3156 — Asynchronous IO Support Rebooted** ([peps.python.org/pep-3156](https://peps.python.org/pep-3156/)). El PEP histórico que dio origen a `asyncio`. Lectura larga, opcional, pero te muestra el modelo conceptual desde la base.
- **`asyncio.TaskGroup`** ([docs.python.org/3/library/asyncio-task.html#asyncio.TaskGroup](https://docs.python.org/3/library/asyncio-task.html#asyncio.TaskGroup)). La API moderna para concurrencia.
- **`asyncio.timeout`** ([docs.python.org/3/library/asyncio-task.html#asyncio.timeout](https://docs.python.org/3/library/asyncio-task.html#asyncio.timeout)). El reemplazo moderno de `wait_for`.

## Lecturas guiadas

- **Real Python — Async IO in Python: A Complete Walkthrough** ([realpython.com/async-io-python](https://realpython.com/async-io-python/)). Recorrido largo y didáctico. Si te quedaron dudas con el README, este artículo cierra los huecos.
- **Łukasz Langa — "Asyncio in Python: A Practical Tutorial"** (varios formatos en la web). Łukasz es uno de los release managers de Python; sus charlas sobre async son técnicamente impecables.
- **David Beazley — "Build Your Own Async"** ([youtu.be/Y4Gt3Xjd7G8](https://www.youtube.com/watch?v=Y4Gt3Xjd7G8)). Charla clásica donde Beazley construye un mini event loop desde cero. Después de verla, asyncio deja de ser "magia".
- **Yury Selivanov — "Async/Await in Python"**. Yury es el autor del PEP 492. Búsquelo en YouTube — su charla en EuroPython 2017 sigue siendo referencia.

## Para profundizar

- **Curio y Trio.** Otras librerías de async para Python que tomaron decisiones de diseño distintas a asyncio. Trio (de Nathaniel Smith) es la más interesante conceptualmente — introdujo los **structured concurrency principles** que después inspiraron `TaskGroup`. [trio.readthedocs.io](https://trio.readthedocs.io/).
- **"Notes on structured concurrency, or: Go statement considered harmful"** ([vorpus.org/blog/notes-on-structured-concurrency-or-go-statement-considered-harmful](https://vorpus.org/blog/notes-on-structured-concurrency-or-go-statement-considered-harmful/)). El artículo que cambió cómo se piensa la concurrencia en muchos lenguajes. Lectura obligada si te interesa el tema.
- **GIL y por qué async es relevante en Python.** ([wiki.python.org/moin/GlobalInterpreterLock](https://wiki.python.org/moin/GlobalInterpreterLock)). Entender por qué Python necesita asyncio (en vez de threads para todo) requiere conocer el GIL.

## Referencias para resolver dudas puntuales

- **"Mi función `async` no se ejecuta"** — probablemente la llamaste sin `await`. Revisa que estés haciendo `await foo()` o `asyncio.run(foo())`.
- **"`gather` se cuelga"** — alguna corutina no termina. Agrega un `asyncio.timeout(...)` para acotarlo y descubrir cuál.
- **"Estoy mezclando `requests` con `asyncio`"** — no lo hagas. Cambia a `httpx` (S13). `requests` bloquea el loop entero.
- **"Tengo que llamar a una librería sync en un proyecto async"** — `await asyncio.to_thread(funcion, args)`. Es la salida estándar.
- **"`TaskGroup` me dice que no es subscriptable"** — ya estás capturando el `ExceptionGroup` mal. Recuerda: `except*` con asterisco.

## Errores comunes

- **`time.sleep` adentro de async** — bloquea el loop entero. Siempre `asyncio.sleep`.
- **`asyncio.run` llamado dos veces en el mismo programa** — cada `asyncio.run` crea y destruye un loop. Si lo necesitas más de una vez, reestructura el código para tener una sola corutina raíz.
- **Olvidarte de `await` en una llamada async** — Python solo te lo dice como `RuntimeWarning`, no como error. Lee los warnings.
- **`asyncio.gather` con una sola corutina** — funciona, pero es ceremonia inútil. Si solo tienes una, simplemente `await foo()`.
- **Usar `Future`/`ensure_future` en código nuevo** — APIs viejas. Hoy se usa `create_task` o `TaskGroup`.

## Si vas hacia el curso 2

En AI Engineering, async es la **norma**, no la excepción:

- Las APIs de los LLM (OpenAI, Anthropic, etc.) tienen versiones async. Procesar 100 prompts en paralelo es trivial.
- FastAPI (que viene en M5) es async-first. Tus handlers van a ser `async def`.
- Los frameworks de agentes (LangGraph, etc.) usan async para coordinar pasos de un grafo.
- Los servicios de embeddings, vector stores y bases de datos modernas (Postgres con asyncpg, Redis async) están todos en el mundo async.

Salir del curso 1 con una intuición sólida sobre **cuándo async aporta y cuándo es ceremonia** te ahorra horas de pelearte con bugs raros en el curso 2.

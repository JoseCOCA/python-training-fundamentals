# S16 — Recursos

## Documentación oficial

- **FastAPI documentation** ([fastapi.tiangolo.com](https://fastapi.tiangolo.com/)). La doc oficial es **excepcional** — es lectura obligada del módulo. Empezá por "First Steps" → "Path Parameters" → "Query Parameters" → "Request Body" → "Response Model".
- **FastAPI tutorial** ([fastapi.tiangolo.com/tutorial/](https://fastapi.tiangolo.com/tutorial/)). El tutorial entero es de altísima calidad. Si lo terminás, sabés más FastAPI que el 90% de la industria.
- **Starlette** ([www.starlette.io](https://www.starlette.io/)). FastAPI está construido sobre Starlette. Cuando necesites algo de bajo nivel (websockets, middleware custom), vas a Starlette.
- **Uvicorn** ([www.uvicorn.org](https://www.uvicorn.org/)). El servidor ASGI que usamos. Lee "Settings" para entender flags como `--workers`, `--reload`, `--log-level`.
- **ASGI Specification** ([asgi.readthedocs.io](https://asgi.readthedocs.io/)). El protocolo. Lectura opcional pero esclarecedora si querés saber qué pasa "abajo".

## Lecturas guiadas

- **Sebastián Ramírez (tiangolo) — Conferencias** (varias en YouTube). Sebastián es el autor de FastAPI; sus charlas explican las decisiones de diseño.
- **Real Python — FastAPI tutorials** ([realpython.com](https://realpython.com/)). Múltiples artículos progresivos sobre FastAPI con SQLAlchemy y testing.
- **Testdriven.io — FastAPI courses** ([testdriven.io](https://testdriven.io/)). Cursos pagos pero con artículos gratuitos muy completos sobre testing y deploy de FastAPI.
- **Awesome FastAPI** ([github.com/mjhea0/awesome-fastapi](https://github.com/mjhea0/awesome-fastapi)). Lista curada de recursos, librerías, tutoriales y ejemplos.

## Para profundizar

- **HTTP/REST APIs design** — buscá "REST API design best practices" (varios autores). Convenciones de versionado, paginación, idempotencia, hypermedia.
- **The Twelve-Factor App** ([12factor.net](https://12factor.net/)). Las doce reglas para apps que escalan. Antes de poner FastAPI en producción, lee al menos los factores III (config), V (build/release/run), VIII (concurrency) y XI (logs).
- **High Performance Python** (capítulos sobre concurrencia y servidores). Te ayuda a entender por qué `uvicorn --workers N` es la respuesta a "mi API es lenta".
- **OpenAPI Specification** ([swagger.io/specification/](https://swagger.io/specification/)). El estándar que FastAPI implementa para `/docs`. Útil saber leer un OpenAPI.json para integraciones.

## Herramientas que vale la pena conocer

- **HTTPie** ([httpie.io](https://httpie.io/)). Cliente CLI para HTTP, mucho más legible que `curl`. `http POST :8000/notas titulo=hola`.
- **Postman** y **Insomnia** — clientes gráficos para probar APIs. Pueden importar el `openapi.json` que FastAPI genera y armar la collection sola.
- **ngrok** ([ngrok.com](https://ngrok.com/)). Expone tu FastAPI local a Internet. Útil cuando tenés que probar webhooks de un servicio externo.
- **`scalar`** o **`swagger-ui`** — alternativas para visualizar APIs. FastAPI ya viene con Swagger UI y ReDoc, pero podés cambiar.

## Referencias para resolver dudas puntuales

- **"`/docs` no se actualiza"** — `--reload` falla a veces con caché de browser. Hard reload (Ctrl-Shift-R) suele alcanzar. Si no, reiniciá uvicorn.
- **"Mi handler `async` se cuelga 5 segundos"** — estás haciendo I/O sync adentro. Pasalo a `def` (FastAPI lo lleva al thread pool) o usá la versión async de la librería.
- **"FastAPI me devuelve 422 con un mensaje raro"** — leé el body de la respuesta: tiene la lista `detail` con `loc`, `msg`, `type` por campo. Es exactamente el `ValidationError` de pydantic serializado.
- **"`Optional[int]` vs `int | None`"** — son lo mismo. FastAPI los entiende ambos. Preferí `int | None` (3.10+).
- **"`startup_event` está deprecado"** — sí, en favor de `lifespan`. Para el curso usamos `@app.on_event("startup")` que sigue funcionando; en proyectos nuevos usá `lifespan` (te lo mostramos en el integrador).

## Errores comunes

- **`uvicorn main:app` cuando no tenés `app` en `main.py`** — `main:app` es "archivo:variable". Si tu archivo se llama `notas.py`, es `uvicorn notas:app`.
- **Devolver `BaseModel` y declarar también `response_model=`** — está bien, no es error, pero el `response_model` PISA al type hint. Suele ser intencional (filtrar campos), pero confunde.
- **Usar `request.json()` directo** — perdés validación. Si querés el body, declaralo como `BaseModel`. Si necesitás el body crudo (raro), pedí `request: Request` y `await request.body()`.
- **Variables globales mutables como "estado"** — funcionan en desarrollo con un solo worker, pero con `--workers N` cada worker tiene su copia y los datos divergen. La realidad es: el estado vive en una DB, no en memoria.
- **Olvidar `--host 0.0.0.0` en Docker** — el contenedor escucha en `127.0.0.1` (su loopback) y desde fuera no se ve. Para Docker, `--host 0.0.0.0`.
- **`app.include_router(...)` sin tags ni prefix** — funcionalmente OK, pero los `/docs` quedan desorganizados. Con `prefix="/v1/productos"` y `tags=["productos"]` quedan agrupados.

## Si vas hacia el curso 2

En AI Engineering, FastAPI es **el** framework para servir LLMs y agentes:

- **Endpoint que envuelve un LLM**: `POST /chat` recibe `{messages: [...]}`, llama a Claude/GPT, devuelve la respuesta. La validación de pydantic te garantiza el contrato.
- **Streaming de tokens**: FastAPI soporta `StreamingResponse` para devolver tokens del LLM mientras se generan (Server-Sent Events).
- **Observabilidad**: middleware de FastAPI para inyectar `request_id`, latencia, métricas a un sistema (Prometheus, Datadog).
- **Auth**: `Depends(get_current_user)` con JWT, rate limiting, scopes — todo pydantic-typed.

La disciplina del curso 1 — pydantic en bordes, separación DTO/ORM, exception handlers — se traslada **idéntica** al curso 2. Solo cambia qué hay adentro de los handlers: en lugar de `repositorio.crear(producto)`, hay `await llm.complete(prompt)`.

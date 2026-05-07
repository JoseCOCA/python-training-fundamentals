# S18 — Recursos

## Documentación oficial

- **pydantic-settings** ([docs.pydantic.dev/latest/concepts/pydantic_settings/](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)). Documentación oficial de `BaseSettings`. Cubre fuentes (env, `.env`, archivos secret, AWS Secrets Manager).
- **FastAPI — Lifespan events** ([fastapi.tiangolo.com/advanced/events/](https://fastapi.tiangolo.com/advanced/events/)). Alternativa moderna a `@app.on_event`. La que usamos en el integrador.
- **FastAPI — Middleware** ([fastapi.tiangolo.com/tutorial/middleware/](https://fastapi.tiangolo.com/tutorial/middleware/)). Cómo escribir middleware HTTP propio.
- **FastAPI — CORS** ([fastapi.tiangolo.com/tutorial/cors/](https://fastapi.tiangolo.com/tutorial/cors/)). El middleware CORS y por qué a veces lo necesitás (cuando el frontend está en otro dominio que el backend).
- **Python `logging` — HOWTO** ([docs.python.org/3/howto/logging.html](https://docs.python.org/3/howto/logging.html)). Tutorial oficial. Cubre niveles, handlers, formatters.
- **Python `logging` — Cookbook** ([docs.python.org/3/howto/logging-cookbook.html](https://docs.python.org/3/howto/logging-cookbook.html)). Recetas concretas para casos avanzados (rotación, JSON, contextual).

## Lecturas guiadas

- **The Twelve-Factor App** ([12factor.net](https://12factor.net/)). Lectura corta y obligatoria. Lee al menos III (Config), V (Build/Release/Run), XI (Logs).
- **Real Python — Python Logging Best Practices** ([realpython.com/python-logging/](https://realpython.com/python-logging/)). Recorrido práctico.
- **Distributed Tracing in Practice** (Jaeger/OpenTelemetry tutorials). Cuando tengas más de un servicio, los logs solos dejan de alcanzar.
- **structlog Documentation** ([www.structlog.org](https://www.structlog.org/en/stable/)). Si te quedás corto con `logging`, `structlog` es la siguiente parada.

## Para profundizar

- **Designing Data-Intensive Applications** (Martin Kleppmann), capítulo "Reliability". Por qué los logs son la **prueba** de que tu sistema hizo lo que decía.
- **Site Reliability Engineering** (Google), capítulos sobre observabilidad y SLOs. Cuando "logs" se vuelve un sistema en sí mismo.
- **OpenTelemetry para Python** ([opentelemetry.io/docs/instrumentation/python/](https://opentelemetry.io/docs/instrumentation/python/)). El estándar industria para traces y métricas. Con el integrador de FastAPI, instrumentás toda la app en 5 líneas.
- **Honeycomb / Datadog APM** (blogs de cada uno). Tienen escritos excelentes sobre cómo modelar trazas en sistemas reales.

## Herramientas que vale la pena conocer

- **`python-json-logger`** — formatter JSON para logging stdlib. Una línea para emitir logs estructurados a stdout.
- **`structlog`** — librería de logging estructurado pensada desde cero. Más ergonómica para casos serios.
- **`loguru`** — librería de logging muy popular (no compatible con stdlib). Fan favorite por su simplicidad. En libros y tutoriales recientes lo vas a ver.
- **`watchdog` + `--reload`** — uvicorn `--reload` usa watchdog/watchfiles. Pierde milisegundos cuando el archivo cambia.
- **`gunicorn` con `uvicorn.workers.UvicornWorker`** — para producción cuando querés balanceo entre workers. Alternativa: `uvicorn --workers N`.
- **`hypercorn`** — otro servidor ASGI, alternativa a uvicorn. Soporta HTTP/2 y HTTP/3 nativos.

## Referencias para resolver dudas puntuales

- **"Mi `.env` no se lee"** — chequeá: ¿el archivo está en el directorio donde corrés uvicorn? ¿el prefijo coincide (`TIENDAPRO_X` vs `X`)? ¿el modelo declara `env_file=".env"` en `SettingsConfigDict`?
- **"`SecretStr` no funciona"** — `.get_secret_value()` te da el string. Si lo pasás a una librería que espera `str`, no se rompe nada — `SecretStr` es solo defensa contra `repr()`/`model_dump()` accidental.
- **"Mis logs salen duplicados"** — algún módulo upstream ya configuró `logging.basicConfig`. Usá `force=True` en `basicConfig` para resetear handlers, o configurá un logger named en lugar del root.
- **"`@lru_cache` sobre `get_settings()` y los tests no respetan el `.env` de test"** — usá `app.dependency_overrides[get_settings] = lambda: Settings(...)` en pytest, o limpiá la cache con `get_settings.cache_clear()` antes de cada test.
- **"Mi middleware se ejecuta dos veces"** — chequeá que no estés agregando el mismo middleware en dos lugares (con `@app.middleware("http")` y con `app.add_middleware(...)`).
- **"CORS no funciona en producción"** — chequeá el orden: `CORSMiddleware` debe ser de los primeros agregados. Y `allow_credentials=True` requiere orígenes específicos (no `*`).

## Errores comunes

- **Hardcodear la `database_url`** — todo el resto del módulo predica lo contrario. La URL viene de la config; la config viene del entorno.
- **Loguear el body completo de cada request** — explosivo en producción (PII, tokens, archivos binarios). Logueá la **forma**: status, content-length, request_id.
- **Reusar `print` en vez de `logger`** — funciona en dev, falla en prod (se mezcla con stdout, no respeta niveles, no estructura). Convertilos en `logger.debug(...)` o `logger.info(...)`.
- **Configurar `logging.basicConfig` mil veces** — Python solo lo configura la primera vez. Si lo llamás de nuevo y querés que tome efecto, `force=True`.
- **`@lru_cache` sin tipo de retorno** — mypy puede confundirse. Tipá explícitamente: `def get_settings() -> Settings:`.
- **`.env` versionado por accidente** — agregalo al `.gitignore` desde el día 1. Si ya está versionado, sacalo con `git rm --cached .env` y rotá los secretos (asumí que se filtraron).
- **Usar `.env` en producción** — `.env` es para desarrollo. En prod, las env vars las setea el orquestador (Docker, k8s secrets, AWS Parameter Store). No subas un `.env` con credenciales reales a un servidor.

## Si vas hacia el curso 2

En AI Engineering, **observabilidad es vital** porque los LLMs son cajas negras y costosas:

- **Logs estructurados** con `model`, `prompt_tokens`, `completion_tokens`, `latency_ms`, `temperature` — para auditar, debuggear y facturar.
- **Métricas** sobre cada llamada — error rate, p99 latency, costo por hora.
- **Trazas** que cruzan agente → tool → LLM → otra API. Sin trazas, debuggear un agente con cinco pasos es imposible.
- **`pydantic-settings`** se vuelve el lugar canónico de cosas como `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `MAX_RETRIES`, `MODEL_NAME`. La disciplina de `SecretStr` es exactamente para esto.

La base que pones hoy — `request_id`, structured logging, config tipada — es lo que vas a expandir en el curso 2 hacia métricas y trazas. Sin ella, tu sistema AI deja de ser observable a las primeras 1000 requests.

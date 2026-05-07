# S18 — Configuración con pydantic-settings, secretos, logging estructurado

> **Sesión 2h.** ~45 min lectura + ~75 min ejercicios. **Cierra el Módulo 5.** En S16 y S17 viste la API. Hoy le agregamos las dos cosas que la separan de un experimento: **configuración** (cómo el comportamiento cambia entre local, staging y producción sin tocar el código) y **logging** (cómo entendés qué pasó cuando algo falla a las 3 AM en producción). El cierre del módulo deja TiendaPro como una API REST real, configurable por entorno y con logs útiles.

---

## 1. Objetivos de aprendizaje

Al terminar esta sesión vas a poder:

- Explicar el principio "config en el entorno, no en el código" (Twelve-Factor App, factor III).
- Definir un `BaseSettings` con `pydantic-settings` que lea de variables de entorno y de `.env`.
- Manejar secretos con `SecretStr` (que no se loguea por accidente).
- Distinguir cuándo cargás la config (al startup, una sola vez) y cuándo la inyectás (en handlers via `Depends`).
- Configurar logging con el módulo `logging` de la stdlib, formatos estructurados y niveles.
- Decidir qué loguear y qué no loguear (NO contraseñas, NO PII en producción).
- Agregar middleware de FastAPI para inyectar `request_id` en los logs y trazar peticiones de punta a punta.
- Cerrar el hito M5 con TiendaPro Lite como API REST con configuración + logging + endpoints completos.

## 2. Prerequisitos

- [S16 — FastAPI fundamentos](../sesion-16-fastapi-fundamentos/README.md) y [S17 — Validación + DTOs](../sesion-17-validacion-dtos/README.md). La estructura de la API tiene que estar clara.
- [S11 — pydantic v2](../../03-tipado-calidad/sesion-11-pydantic-ruff/README.md). `pydantic-settings` es pydantic con un par de fuentes adicionales (env, `.env`, secret files).

## 3. Conceptos clave

1. **Config en el entorno.** Twelve-Factor App, factor III: la configuración (URLs, claves, flags) viene de **variables de entorno**, no de código ni archivos versionados. `.env` para desarrollo local; en prod, las setea el orquestador (Docker, k8s, systemd).
2. **`BaseSettings`.** Clase de `pydantic-settings` que **automáticamente** lee variables de entorno con el mismo nombre que sus campos. Validación, defaults, types — todo igual a `BaseModel`.
3. **`SecretStr`.** Tipo que envuelve un string sensible: no aparece en `repr()`, ni en `model_dump()` (a menos que pidas su valor explícito con `.get_secret_value()`). Evita filtrar secretos en logs por accidente.
4. **`Depends(get_settings)`.** Patrón FastAPI para inyectar la config en handlers. Combinado con `lru_cache`, se construye una sola vez y se reutiliza.
5. **Logging estructurado.** Logs con campos clave-valor (JSON o key=value), no strings sueltos. Permiten que `grep`, `jq` o un sistema de observabilidad (Loki, Datadog) filtren por `request_id`, `user`, `latency_ms`.
6. **Niveles de log.** `DEBUG` (info detallada para dev), `INFO` (eventos normales), `WARNING` (algo raro pero recuperable), `ERROR` (operación falló), `CRITICAL` (sistema en peligro).

## 4. Teoría

### 4.1. Por qué config separada del código

El mismo código tiene que correr en:

- Tu laptop con SQLite y `DEBUG=True`.
- Un staging con Postgres y observabilidad.
- Producción con Postgres replicado y secretos rotados cada 30 días.

Si la URL de la DB y la API key viven en el código, **tenés que cambiar el código** entre entornos. Eso es un anti-patrón histórico (lleva a errores: subir staging a prod con flags de debug, leakear claves al repo, branches paralelos por entorno).

**La regla**: las cosas que cambian entre entornos viven en variables de entorno. El código las **lee**, no las **define**.

### 4.2. `pydantic-settings`: lo que pydantic siempre debió ser

```python
from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    app_name: str = "TiendaPro"
    debug: bool = False
    database_url: str = "sqlite:///tiendapro.db"
    api_key: SecretStr = SecretStr("change-me")
    log_level: str = "INFO"
    cors_origins: list[str] = ["http://localhost:3000"]
```

Lectura automática:

| Campo | Variable de entorno | Default |
|---|---|---|
| `app_name` | `APP_NAME` | `"TiendaPro"` |
| `debug` | `DEBUG` (acepta `1/0`, `true/false`, `yes/no`) | `False` |
| `database_url` | `DATABASE_URL` | `"sqlite:///..."` |
| `api_key` | `API_KEY` | `SecretStr("change-me")` |
| `log_level` | `LOG_LEVEL` | `"INFO"` |
| `cors_origins` | `CORS_ORIGINS` (JSON: `["a","b"]`) | `["http://localhost:3000"]` |

Si querés un prefijo común (que evite chocar con otras vars):

```python
class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="TIENDAPRO_", env_file=".env")
```

Ahora `database_url` se lee de `TIENDAPRO_DATABASE_URL`. Útil cuando deployás varios servicios en la misma VM.

**`.env` ejemplo:**

```ini
TIENDAPRO_DEBUG=true
TIENDAPRO_DATABASE_URL=sqlite:///tiendapro.db
TIENDAPRO_API_KEY=secreto-local-de-pruebas
TIENDAPRO_LOG_LEVEL=DEBUG
```

**Crítico**: `.env` NUNCA va al repo (está en `.gitignore`). Versioná `env.example` con los nombres y valores de muestra.

### 4.3. `SecretStr`: el centinela de los logs

```python
class Settings(BaseSettings):
    api_key: SecretStr


settings = Settings(api_key="abc123")
print(settings)
# Settings(api_key=SecretStr('**********'))  ← NO loguea el valor

print(settings.api_key.get_secret_value())   # "abc123" — solo cuando lo pedís
```

Sin `SecretStr`, basta con que alguien meta el `Settings` en un log estructurado y la API key viaja a tu sistema de observabilidad. Con `SecretStr`, hace falta llamar explícitamente al `.get_secret_value()`. Es disciplina ofrecida por el tipo.

Cuándo usar `SecretStr`:

- API keys, tokens.
- Contraseñas de DB.
- Secretos de firma JWT, HMAC keys.
- Cualquier string cuyo valor te dolería ver en CloudWatch.

Cuándo NO:

- URLs públicas (la URL de la DB es un caso límite — depende de si tiene credenciales en el querystring; en general usá `SecretStr` para `database_url` cuando incluya credenciales).

### 4.4. Inyectar la config en handlers: `Depends` + `lru_cache`

```python
from functools import lru_cache

from fastapi import Depends


@lru_cache
def get_settings() -> Settings:
    return Settings()                  # se construye UNA VEZ por proceso


@app.get("/")
def root(settings: Settings = Depends(get_settings)) -> dict[str, str]:
    return {"app": settings.app_name, "debug": str(settings.debug)}
```

`Depends(get_settings)` le dice a FastAPI: "antes de invocar este handler, llamá `get_settings()` y pasame el resultado". `lru_cache` hace que sea singleton — sin él, leerías `.env` por cada request.

Para overridear en tests:

```python
app.dependency_overrides[get_settings] = lambda: Settings(database_url="sqlite:///:memory:")
```

(Lo vas a usar en M6 cuando escribamos tests.)

### 4.5. Logging: la versión sin frameworks

```python
import logging
import sys


def configurar_logging(level: str = "INFO") -> None:
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)-7s %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        stream=sys.stdout,
    )


logger = logging.getLogger(__name__)
logger.info("servicio arrancando", extra={"version": "0.5.0"})
```

Niveles, en orden de menor a mayor severidad:

- `DEBUG` — todo (queries SQL, valores intermedios). Solo en desarrollo.
- `INFO` — eventos normales (request entró, request salió).
- `WARNING` — algo raro pero la app sigue (rate limit cerca del cap, retry exitoso al tercer intento).
- `ERROR` — operación falló pero el proceso sigue (un endpoint devolvió 500, un job se canceló).
- `CRITICAL` — el proceso está por morir (no puede conectar a la DB, OOM inminente).

**Regla:** seteá el nivel **al inicio** según `settings.log_level`. En desarrollo `DEBUG`, en prod `INFO` o `WARNING`.

### 4.6. Logging estructurado: por qué importa

Compará:

```
2026-05-07 14:32:11 INFO  tiendapro | request OK
2026-05-07 14:32:12 INFO  tiendapro | request OK
2026-05-07 14:32:13 INFO  tiendapro | request FAILED
```

Vs:

```json
{"ts":"2026-05-07T14:32:11Z","level":"INFO","msg":"request","method":"GET","path":"/productos","status":200,"latency_ms":12,"request_id":"a1"}
{"ts":"2026-05-07T14:32:12Z","level":"INFO","msg":"request","method":"GET","path":"/productos/42","status":200,"latency_ms":7,"request_id":"a2"}
{"ts":"2026-05-07T14:32:13Z","level":"ERROR","msg":"request","method":"POST","path":"/productos","status":500,"latency_ms":120,"request_id":"a3","error":"DBConnectionError"}
```

Con el segundo, podés correr `jq 'select(.status == 500)'` y filtrar todos los errores. Con el primero, `grep` y rezar.

Para esta sesión, la versión "key-value" es suficiente:

```python
logger.info("request", extra={
    "method": request.method,
    "path": str(request.url.path),
    "status": response.status_code,
    "latency_ms": int((time.perf_counter() - start) * 1000),
    "request_id": request.state.request_id,
})
```

(Con `python-json-logger` o `structlog` se puede emitir el JSON directo; lo vas a sumar en producción real.)

### 4.7. Middleware: `request_id` y trace de cada request

Un middleware es una función que se ejecuta **antes** y **después** de cada handler:

```python
import time
import uuid

from fastapi import Request


@app.middleware("http")
async def request_logger(request: Request, call_next):
    request.state.request_id = str(uuid.uuid4())[:8]
    start = time.perf_counter()
    try:
        response = await call_next(request)
    except Exception:
        logger.exception(
            "request error",
            extra={
                "method": request.method,
                "path": str(request.url.path),
                "request_id": request.state.request_id,
            },
        )
        raise
    latency_ms = int((time.perf_counter() - start) * 1000)
    logger.info(
        "request",
        extra={
            "method": request.method,
            "path": str(request.url.path),
            "status": response.status_code,
            "latency_ms": latency_ms,
            "request_id": request.state.request_id,
        },
    )
    response.headers["X-Request-ID"] = request.state.request_id
    return response
```

Beneficios:

- Cada request tiene un `request_id` único (corto: 8 chars).
- Se loguean método, path, status, latencia.
- `X-Request-ID` viaja al cliente para que pueda referenciarlo en un soporte ticket.
- Si algo falla, `logger.exception(...)` también captura la traza.

### 4.8. Qué NO loguear

Reglas sin matiz:

- **Contraseñas, API keys, tokens** — usar `SecretStr` ayuda, pero también hay que evitar loguear `request.headers` o `request.body` crudos.
- **PII (Información Personal Identificable)** — emails, DNI, teléfonos, dirección. En la EU es ley (GDPR); en el resto de tu carrera, es decencia.
- **El body crudo de requests/responses** — pueden tener cualquier cosa. Logueá la **forma** (status, content-length) no el **contenido**.
- **Stack traces enteros con datos privados** — `logger.exception(...)` ya da la traza; no agregues `extra={"body": request.body}` porque sí.

Pregunta antes de loguear: "¿estaría tranquilo si esto saliera publicado mañana?"

### 4.9. La pirámide del observabilidad (mención)

Logs son **uno** de los tres pilares. Los otros:

- **Métricas** — números agregados (requests/seg, latencia p99, error rate). Prometheus, Datadog metrics.
- **Trazas distribuidas** — un request que cruza 5 servicios, ves cuánto tarda en cada uno. OpenTelemetry, Jaeger.

En este curso solo cubrimos logs. En el curso 2 (AI Engineering) las métricas se vuelven críticas (tokens consumidos, latencia del LLM, tasa de fallos por modelo). La disciplina de hoy — `request_id`, structured fields — es lo que va a permitir conectar logs ↔ métricas ↔ trazas mañana.

### 4.10. Cuándo se ejecuta cada cosa

```
Proceso arranca
    ↓
    Settings() ← lee .env y env vars (UNA vez)
    ↓
    configurar_logging(settings.log_level)
    ↓
    crear_schema() ← S15
    ↓
    app = FastAPI()
    ↓
    uvicorn corre el server
    ↓
    Loop infinito:
        Request entra
            → middleware (request_id, logger)
                → exception handlers, dependencies
                    → handler
                        → repositorio → DB
                    ←
                ←
            ← middleware (latencia, status)
        Response sale
```

`Settings`/`logging` se setean al **arrancar**, una sola vez. Los handlers asumen que ya están listos.

### 4.11. Cierre M5 — TiendaPro como API REST

Lo que el integrador queda al final de la sesión:

- `tiendapro/api/`: app FastAPI con CRUD productos, exception handlers de S17, logging middleware de hoy.
- `tiendapro/config.py`: `Settings(BaseSettings)` con `database_url`, `log_level`, `enable_enrichment`, etc.
- `tiendapro/log.py`: `configurar_logging` invocado desde el lifespan.
- `tiendapro/db.py` (S15): el engine se construye **a partir de la config**, no de un literal.
- `main.py` deja de ser CLI puro y arranca el server: `uv run python main.py` o `uv run uvicorn tiendapro.api:app`.

## 5. Patrones y antipatrones

| ✅ Patrón | ❌ Antipatrón |
|---|---|
| Config con `pydantic-settings` + `.env` (en `.gitignore`) | Hardcodear URLs y keys en el código |
| `SecretStr` para todo lo sensible | Strings normales para keys (se filtran en logs) |
| `@lru_cache` sobre `get_settings()` | Construir `Settings()` por request |
| `Depends(get_settings)` en handlers | Variable global mutable que cargás "alguna vez" |
| `logger = logging.getLogger(__name__)` por módulo | `print` para debug |
| Logs estructurados con `extra={...}` | Strings concatenados con `f"latency={x}"` |
| Middleware que inyecta `request_id` y trace | Logs sin correlación entre request y errores |
| Headers `X-Request-ID` echo back al cliente | Logs sin forma de cruzar con un soporte ticket |
| `env.example` versionado, `.env` ignorado | `.env` versionado con secretos reales |
| Niveles distintos por entorno (`DEBUG` local, `INFO` prod) | Todo en `DEBUG` siempre |
| NO loguear PII / passwords / bodies | Loguear "todo por las dudas" |

## 6. Conexión con el proyecto integrador — Cierre del hito M5

**Hoy cierra el Módulo 5.** TiendaPro Lite queda como **API REST funcional**, configurable por entorno, con logging estructurado y exception handling completo.

1. **`src/tiendapro/config.py`** con `BaseSettings`: `database_url`, `log_level`, `app_name`, `debug`, `enable_enrichment`.
2. **`src/tiendapro/log.py`** con `configurar_logging(level)`.
3. **`src/tiendapro/api/app.py`** (de S17) ahora:
   - Usa `lifespan` (en lugar de `@app.on_event`) para configurar logging y el seed.
   - Registra el middleware de `request_id` + logger.
   - El startup llama a `inicializar(seed)` de S15.
4. **`src/tiendapro/db.py`** (de S15) construye el engine usando `settings.database_url`.
5. **Endpoints completos**: GET/POST/DELETE de productos + GET por categoría + health.
6. **`env.example`** con los nombres de variables.
7. **Verificación**: `uv run uvicorn tiendapro.api:app --reload` levanta el server, `/docs` muestra todo, los logs tienen `request_id`.
8. **Commit final + tag**:
   ```bash
   git add code/proyecto-integrador
   git commit -m "feat(proyecto-integrador): cierra M5 con FastAPI + pydantic-settings + logging (proyecto-m5)"
   git tag proyecto-m5
   ```

Detalles paso a paso en `ejercicios.md`.

## 7. Resumen

1. **Config en el entorno, no en el código.** `pydantic-settings` la lee con tipos y validación.
2. **`BaseSettings` lee env vars y `.env` automáticamente.** Sin parseo a mano.
3. **`SecretStr` esconde el valor del `repr()` y `model_dump()`.** Defensa contra leaks por logs.
4. **`Depends(get_settings)` + `@lru_cache`** = config inyectable y singleton.
5. **Logging estructurado con `extra={...}`** te da datos accionables, no strings sueltos.
6. **Middleware de `request_id`** correlaciona requests, errores y soporte tickets.
7. **NO loguées PII, passwords, bodies crudos.** "¿Estaría tranquilo si esto saliera publicado?"
8. **Niveles por entorno: DEBUG local, INFO prod.** Cambias por env var, no por código.
9. **`.env` en `.gitignore`; `env.example` versionado.**
10. **Logging es UNO de los tres pilares de observabilidad.** Métricas y trazas vienen después.

## 8. Preguntas de auto-evaluación

1. ¿Por qué la config de la app vive en variables de entorno y no en el código?
2. Definí un `Settings(BaseSettings)` con `database_url`, `api_key` (secreto), `debug`. ¿Qué nombre tiene cada env var por default?
3. ¿Qué hace `SecretStr` que un `str` no?
4. ¿Cómo inyectás la config en un handler de FastAPI? ¿Por qué `@lru_cache`?
5. ¿Qué pasa si llamás `Settings()` cien veces sin `lru_cache`? ¿Por qué importa?
6. Diferencia entre `logger.info("msg %s", x)` y `logger.info("msg", extra={"x": x})`. ¿Cuál preferís y por qué?
7. ¿Qué nivel de log usarías para: una request normal, un retry exitoso al tercer intento, un endpoint que devolvió 500, no poder conectar a la DB al startup?
8. ¿Para qué sirve un middleware con `request_id`? ¿Qué se logueás en cada request?
9. Listá tres cosas que NUNCA deberías loguear y explicá por qué.
10. Tu app necesita correr en local (SQLite) y en prod (Postgres). ¿Qué cambia en el código? ¿Qué cambia en el entorno?

Cuando puedas responder todas, pasa a [`ejercicios.md`](ejercicios.md) para cerrar el hito M5.

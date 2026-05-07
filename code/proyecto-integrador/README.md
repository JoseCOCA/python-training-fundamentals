# TiendaPro Lite — Proyecto integrador

API REST de e-commerce que vas a construir a lo largo del curso, módulo a módulo. Al final del curso queda lista para producción (testeada con pytest, empaquetada en Docker, persistida en PostgreSQL).

Es **el mismo producto** sobre el que arranca el curso 2 ([`python-ai-engineer-training`](https://github.com/JoseCOCA/python-ai-engineer-training)). Cuando termines este curso vas a tomar este código tal como está y empezar a sumarle capacidades de IA encima.

---

## Estado actual: hito M5

Desde el hito M5 TiendaPro Lite **es una API REST funcional**, configurable por entorno y con observabilidad básica:

- **API REST con FastAPI** (`tiendapro.api.app`): CRUD de productos + health check + filtros (`categoria`, `solo_disponibles`).
- **Tres modelos por entidad**: ORM (`tiendapro.orm`), DTO de dominio (`tiendapro.modelos`) y DTOs de API (`tiendapro.api.dtos`). Cada uno cumple su frontera.
- **Configuración con `pydantic-settings`** en `tiendapro.config`: lee de env vars y `.env`, con `SecretStr` para `api_key` y `Literal` para `log_level`.
- **Logging estructurado** en `tiendapro.log`, configurado al startup desde el lifespan.
- **Middleware HTTP** que inyecta `X-Request-ID` y loguea método/path/status/latencia por request.
- **Exception handlers globales** que traducen `ProductoNoEncontrado` → 404, `IntegracionError` → 502, `RequestValidationError` → 422 con formato propio, etc. Los handlers quedan **sin `try/except`**.
- **CORS configurable** por env var (`TIENDAPRO_CORS_ORIGINS`).
- **mypy estricto** y **ruff** siguen pasando limpio.

Lo que **todavía no tiene** y se agrega en M6:

| Módulo | Hito | Capacidades agregadas |
|--------|------|----------------------|
| M1 | `proyecto-m1` | Lee JSON, filtra, ordena, imprime |
| M2 | `proyecto-m2` | Catálogo modelado con dataclasses, errores de dominio, código en paquete |
| M3 | `proyecto-m3` | Validación pydantic, mypy estricto, ruff + pre-commit |
| M4 | `proyecto-m4` | SQLAlchemy v2 + httpx + asyncio donde aporta |
| **M5 (aquí estamos)** | `proyecto-m5` | API REST con FastAPI, pydantic-settings, logging estructurado |
| M6 | `proyecto-m6` | Tests con pytest, Dockerfile, README final |

---

## Cómo correrlo

### Modo CLI (heredado de M4)

Desde dentro de este directorio:

```bash
uv sync --all-groups
uv run python main.py
```

Imprime la tabla, el resumen y el enriquecimiento mock — útil para verificar que la persistencia y la integración HTTP siguen sanas.

### Modo API (nuevo en M5)

```bash
cp env.example .env       # opcional — el .env está en .gitignore
uv run uvicorn tiendapro.api:app --reload --port 8000
```

Abrí:
- `http://localhost:8000/docs` — Swagger UI interactivo.
- `http://localhost:8000/health` — health check.
- `http://localhost:8000/productos` — listar (acepta `?categoria=...` y `?solo_disponibles=true`).

Probá un POST:

```bash
curl -X POST http://localhost:8000/productos \
    -H "Content-Type: application/json" \
    -d '{"nombre":"Producto API","categoria":"test","precio":9.99,"stock":5}'
```

Observá los logs del server: cada request loguea método, path, status, latencia y `request_id`. La response trae `X-Request-ID`.

**Para resetear la DB:**

```bash
rm tiendapro.db
```

(Está en `.gitignore` por la regla `*.db`.)

## Configuración (variables de entorno)

Todas las variables se prefijan con `TIENDAPRO_` y pueden ir en `.env` o ser env vars del sistema.

| Variable | Default | Descripción |
|---|---|---|
| `TIENDAPRO_APP_NAME` | `TiendaPro` | Nombre del servicio en logs y `/docs` |
| `TIENDAPRO_DEBUG` | `false` | Flag de debug |
| `TIENDAPRO_DATABASE_URL` | `sqlite:///tiendapro.db` | URL SQLAlchemy. Postgres-ready |
| `TIENDAPRO_API_KEY` | `change-me` | Secret (SecretStr) |
| `TIENDAPRO_LOG_LEVEL` | `INFO` | `DEBUG`/`INFO`/`WARNING`/`ERROR`/`CRITICAL` |
| `TIENDAPRO_ENABLE_ENRICHMENT` | `true` | Si la app llama a la "API externa" |
| `TIENDAPRO_CORS_ORIGINS` | `["http://localhost:3000"]` | Lista JSON de orígenes permitidos |

`env.example` está versionado — `.env` no.

## Verificación de calidad

```bash
uv run mypy src/ main.py        # cero issues
uv run ruff check .              # cero issues
uv run ruff format --check .     # formato correcto
```

Los tres son la línea base de cualquier commit.

## Estructura

```
proyecto-integrador/
├── README.md                       ← este archivo
├── pyproject.toml                  ← deps + tool.ruff + tool.mypy
├── env.example                     ← plantilla de variables (versionada)
├── data/
│   └── catalogo.json               ← seed inicial (se importa una sola vez)
├── tiendapro.db                    ← SQLite local (no versionado)
├── main.py                         ← entry CLI (compatibilidad con M4)
└── src/
    └── tiendapro/
        ├── __init__.py             ← re-exports públicos
        ├── modelos.py              ← DTOs de dominio (pydantic)
        ├── errores.py              ← TiendaProError + sub-clases
        ├── orm.py                  ← modelos SQLAlchemy v2 (M4)
        ├── db.py                   ← engine + obtener_sesion() — usa Settings (M5)
        ├── repositorio.py          ← API de acceso a datos (único módulo con SQLAlchemy)
        ├── integraciones.py        ← cliente httpx para enriquecimiento (M4)
        ├── catalogo.py             ← API que el resto consume; delega en repositorio
        ├── presentacion.py         ← imprimir_tabla, imprimir_resumen (modo CLI)
        ├── config.py               ← Settings(BaseSettings) (M5)
        ├── log.py                  ← configurar_logging (M5)
        └── api/                    ← capa API (M5)
            ├── __init__.py
            ├── app.py              ← FastAPI(), lifespan, middleware, handlers
            ├── dtos.py             ← ProductoCrear, ProductoOut, HealthOut
            └── rutas.py            ← @router.get/post/...
```

## Cómo se construyó

Cada módulo agrega una capa.

- **M1** estableció las bases: leer datos, filtrarlos, ordenarlos, presentarlos.
- **M2** transformó el script en un paquete real: dataclasses inmutables, excepciones de dominio, generadores y context managers.
- **M3** lo blindó con calidad: validación runtime con pydantic, mypy estricto, ruff y pre-commit.
- **M4** lo conectó con el mundo: persistencia con SQLAlchemy v2, integración HTTP con httpx, asyncio donde de verdad aporta.
- **M5 (este hito)** lo expuso como **API REST** con FastAPI: tres modelos por entidad (ORM/dominio/API), configuración por entorno con `pydantic-settings`, logging estructurado con `request_id`, exception handlers que traducen excepciones de dominio a HTTP. La API está lista para que un frontend consuma TiendaPro o para integrarse a una arquitectura más grande.

## Para los alumnos

Si estás cursando el módulo y todavía no llegaste al final, **no leas el código de `src/tiendapro/` todavía**. Es la implementación de referencia. Primero implementa tú tu propia versión siguiendo los ejercicios del módulo correspondiente.

Después compárala con la referencia — vas a aprender más viendo las diferencias entre tu solución y la de referencia que mirando la referencia primero.

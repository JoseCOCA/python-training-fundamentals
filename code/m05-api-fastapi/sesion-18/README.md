# S18 — Código de la sesión

```bash
uv sync
cp env.example .env       # opcional — el .env está gitignoreado
uv run uvicorn main:app --reload
uv run mypy .
uv run ruff check .
uv run ruff format --check .
```

`main.py` arma una mini-app con los seis patrones de la sesión:

1. **`Settings(BaseSettings)`** con `env_prefix="DEMO_"` y `env_file=".env"`. Lee variables tipadas y validadas.
2. **`SecretStr`** para `api_key` — `repr()` y `str()` muestran `'**********'`. `get_secret_value()` te da el valor real (NO lo uses en responses).
3. **`configurar_logging`** + niveles (`DEBUG`/`INFO`/`WARNING`/`ERROR`/`CRITICAL`).
4. **Middleware HTTP** que inyecta `X-Request-ID` y loguea cada request con método, path, status, latencia y request_id.
5. **`lifespan`** moderno (en lugar de `@app.on_event`) que configura logging al startup.
6. **`Depends(get_settings)`** + `@lru_cache` = config inyectable y singleton.

Endpoints:

- `GET /` — devuelve la config no-sensible (api_key enmascarada por `SecretStr`).
- `GET /secreto` — muestra cómo `repr()` y `str()` de `SecretStr` esconden el valor.
- `GET /explosivo` — lanza un `RuntimeError`; vas a ver el `logger.exception` con stack trace.
- `GET /lento` — espera 500 ms; mirá el `latency_ms` en el log.

`pyproject.toml` agrega `fastapi`, `uvicorn[standard]`, `pydantic>=2.6` y **`pydantic-settings>=2.4`**.

Para experimentar:

- Cambiá `DEMO_LOG_LEVEL=DEBUG` por `INFO` y reiniciá. Los logs de bajo nivel desaparecen.
- Probá levantar la app con env vars sin `.env`:
  ```bash
  DEMO_APP_NAME=otra DEMO_DEBUG=false uv run uvicorn main:app
  ```
  La env var pisa el `.env`.
- Tirá `DEMO_LOG_LEVEL=lol uv run python -c "from main import get_settings; get_settings()"`. `Literal` rechaza el valor con `ValidationError` antes de arrancar — fail-fast.
- Hacé `curl -i http://localhost:8000/` y mirá el header `X-Request-ID`. Después buscalo en los logs (`grep <request_id>`) — tenés el rastro completo del request.
- Llamá `/explosivo` y mirá los logs. Vas a ver el stack trace + `request error` con `request_id`. Esa es la magia de `logger.exception(...)`.

# S16 — Código de la sesión

```bash
uv sync
uv run uvicorn main:app --reload
uv run mypy .
uv run ruff check .
uv run ruff format --check .
```

`main.py` arma una mini-API de productos en memoria con cinco rutas:

- **`GET /`** — health/info del servicio.
- **`GET /productos`** — listar con query params (`categoria`, `limit` con `Query(ge=1, le=100)`).
- **`GET /productos/{producto_id}`** — obtener uno; 404 propio con `HTTPException` si no existe.
- **`POST /productos`** — crear con body `ProductoNuevo` (validado con `Field`), responde `201 Created` con el `Producto` (incluye el `id` asignado).
- **`DELETE /productos/{producto_id}`** — borrar; `204 No Content` con 404 si no existe.

Y dos rutas de demostración del async vs sync:

- **`GET /sync-pesado`** — handler `def` (FastAPI lo despacha al thread pool).
- **`GET /async-ligero`** — handler `async def` (sin I/O dentro: hoy nada que esperar; usaríamos esto para `httpx.AsyncClient`).

Una vez levantado, abrí `http://localhost:8000/docs` — Swagger UI te deja probar cada ruta sin escribir un solo `curl`.

`pyproject.toml` agrega tres deps: `fastapi`, `uvicorn[standard]` (con `uvloop`/`httptools` para mejor performance) y `pydantic>=2.6`. Mantiene la línea de base de M3 (ruff E/W/F/I/B/UP/RUF + mypy estricto + plugin pydantic).

Para experimentar:

- Mandá `POST /productos` con `{"nombre": "", "precio": -1}`. FastAPI te devuelve **422 Unprocessable Entity** con la lista detallada por campo (`min_length`, `gt`).
- Cambiá `extra="forbid"` en `ProductoNuevo` por `extra="ignore"` y mandá `{"nombre": "X", "categoria": "y", "precio": 1, "campo_extra": 123}`. Ahora el campo extra se silencia. Las dos opciones tienen casos de uso — `forbid` en APIs externas estrictas, `ignore` cuando aceptás clientes con campos futuros.
- Llamá `GET /sync-pesado` y `GET /async-ligero` desde `/docs`. Las dos responden rápido. Si en `sync_pesado` agregaras `time.sleep(2)`, sería un bloqueo del thread pool, no del loop — pero igual contraproducente.

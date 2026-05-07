# S13 — Código de la sesión

```bash
uv sync
uv run python main.py
uv run mypy .
uv run ruff check .
uv run ruff format --check .
```

`main.py` recorre cuatro demos contra un **mock-server local** (`httpx.MockTransport`) — no requiere internet ni servidor:

1. **Sync** — `httpx.Client` con `with`, `raise_for_status` y `model_validate` en una llamada.
2. **Async concurrente** — `httpx.AsyncClient` compartido entre tres corutinas que disparan en paralelo y validan la respuesta.
3. **Errores** — los SKUs `ABC` (200 ok), `NOPE` (404), `BOOM` (500) y `MAL` (200 con body que rompe el `field_validator` del precio) se traducen todos a `IntegracionError`.
4. **POST con body desde BaseModel** — `client.post("/productos", json=nuevo.model_dump())` y validación de la respuesta.

`pyproject.toml` agrega `httpx` y `pydantic` como dependencias. Mantiene la línea de base de M3 (ruff E/W/F/I/B/UP/RUF + mypy estricto + plugin pydantic).

Para experimentar:

- En la demo 2, agregá `print(f"start {sku}")` al inicio y `print(f"done {sku}")` al final de `obtener_async`. Vas a ver tres `start` casi simultáneos antes que cualquier `done` — eso es la concurrencia.
- En la demo 3, cambiá el handler para que `MAL` devuelva un body con un campo extra (`{"sku":..., "extra":"x"}`). Como `ConfigDict(extra="forbid")`, `model_validate` lo rechaza con un mensaje específico.
- En la demo 4, sacá el `model_dump()` y mandá `nuevo` directamente como `json=`. Vas a ver un `TypeError` — httpx no sabe serializar un `BaseModel`.

# S12 — Código de la sesión

```bash
uv sync
uv run python main.py
uv run mypy .
uv run ruff check .
uv run ruff format --check .
```

`main.py` recorre cuatro demos:

1. **Sync vs async secuencial vs async concurrente** — los mismos cinco trabajos cronometrados con cada estrategia. Verás que la versión async secuencial no acelera nada; la concurrente sí.
2. **TaskGroup** — la API moderna (Python 3.11+) para lanzar varias corutinas y esperarlas con cancelación estructurada.
3. **`asyncio.to_thread`** — cómo integrar código síncrono pesado sin bloquear el event loop.
4. **Cancelación y `ExceptionGroup`** — qué pasa cuando una task del `TaskGroup` falla y cómo capturar las excepciones con `except*`.

`pyproject.toml` no agrega dependencias — `asyncio` está en la stdlib. Mantiene la línea de base de M3 (ruff E/W/F/I/B/UP/RUF + mypy estricto).

Para experimentar:

- En la demo 1, cambia `asyncio.sleep(0.3)` por `time.sleep(0.3)` adentro de `llamada_async`. Mira cómo la versión "concurrente" se vuelve secuencial otra vez (estás bloqueando el loop).
- En la demo 2, agrega `print(f"empezó {i}")` al inicio de `trabajador` y `print(f"terminó {i}")` al final. Vas a ver el orden de inicio (todos casi al mismo tiempo) vs el orden de fin (más cortos terminan antes).
- En la demo 4, agrega un tercer tipo de excepción (`asyncio.CancelledError` se maneja distinto) y observa qué pasa con las tasks que estaban a punto de terminar.

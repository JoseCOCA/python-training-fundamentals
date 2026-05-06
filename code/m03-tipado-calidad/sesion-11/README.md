# S11 — Código de la sesión

```bash
uv sync
uv run python main.py
uv run mypy .
uv run ruff check .
uv run ruff format --check .
```

`main.py` recorre cuatro demos:

1. **BaseModel básico** — construcción y `model_validate` con conversión de tipos.
2. **Validators** — `@field_validator` (precio > 0, nombre no vacío) y `@model_validator` (salida > entrada).
3. **ValidationError** — los tres problemas reportados juntos con `loc` y `msg` por campo.
4. **Serialización y modelos anidados** — `Cliente` con `Direccion` adentro, `model_dump`, `model_dump_json` y validación que falla en el sub-modelo.

`pyproject.toml` configura ruff (con ruleset E/W/F/I/B/UP/RUF), mypy estricto con plugin de pydantic, y declara pydantic como dependencia.

Para experimentar:

- En la demo de validators, cambia `precio = 0` y observa el `ValidationError`.
- Quita `extra="forbid"` del `model_config` y agrega `"extra_field": "x"` al input de `Producto`. Compara el comportamiento.
- Agrega un campo nuevo a `Cliente` y observa cómo `model_dump_json` lo refleja sin tocar nada más.

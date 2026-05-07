# S17 — Código de la sesión

```bash
uv sync
uv run uvicorn main:app --reload
uv run mypy .
uv run ruff check .
uv run ruff format --check .
```

`main.py` arma una mini-API de **biblioteca** (entidad `Libro`) que ejercita los cuatro patrones de la sesión:

1. **Tres modelos por entidad**:
   - `LibroDB` (`@dataclass` simulando el ORM): tiene `creado_en`, `creado_por` (interno).
   - `LibroCrear` (`BaseModel` para request): solo lo que el cliente puede setear, con `Field` y validators.
   - `LibroOut` (`BaseModel` con `from_attributes=True`): mapea desde `LibroDB` y filtra `creado_por`.

2. **Validación profunda** con tres herramientas:
   - `Field(min_length=..., gt=..., le=..., examples=[...])` → constraints declarativas.
   - `field_validator` → normaliza (strip + título no vacío).
   - `model_validator(mode="after")` → regla que cruza campos (`paginas_resumen < paginas`).

3. **Excepciones de dominio + exception handlers globales**:
   - `LibroNoEncontrado` → 404.
   - `LibroDuplicado` → 409 con el título.
   - `BibliotecaError` (fallback) → 400.
   - Los handlers (`obtener`, `crear`) **no tienen `try/except`** — solo lanzan.

4. **Custom 422 handler** (`RequestValidationError`) que reformatea el response al estilo de la app: `{"detail": "datos inválidos", "errores": [...]}`.

`pyproject.toml` agrega `fastapi`, `uvicorn[standard]`, `pydantic>=2.6`. Mantiene la línea de base de M3 (mypy estricto + plugin pydantic + ruff E/W/F/I/B/UP/RUF).

Para experimentar:

- `POST /libros` con `{"titulo": "Test", "autor": "X", "paginas": 100, "paginas_resumen": 50}` → 201 + `LibroOut` (sin `creado_por`).
- Repetir el mismo POST → 409 con tu detail propio.
- `POST /libros` con `{"titulo": "X", "autor": "Y", "paginas": 100, "paginas_resumen": 200}` → 422 con tu formato (`detail`, `errores`).
- `GET /libros/999` → 404 con `{"detail": "libro 999 no existe", "libro_id": 999}` — el exception handler lee el atributo `libro_id` de la excepción.
- Sacá el `from_attributes=True` de `LibroOut` y mirá el error: pydantic exige un dict, no un `@dataclass` con atributos.

Los handlers se mantienen **delgados**: solo lógica de dominio. Toda la traducción a HTTP vive en los exception handlers, una sola vez.

# S10 — Código de la sesión

```bash
uv run python main.py
uv run mypy .
```

`main.py` recorre cuatro demos:

1. **Genéricos** — `list[int]`, `dict[str, float]`, `tuple`, `Callable`.
2. **`X | None` y type narrowing** — `Usuario | None` y cómo `if u is None: return` afina el tipo.
3. **`TypedDict` y `Literal`** — un dict tipado y un parámetro restringido a tres valores literales.
4. **Protocol** — duck typing tipado: `Producto` y `Factura` pasan como `Imprimible` sin heredar.

`pyproject.toml` tiene `[tool.mypy]` con flags estrictas (`disallow_untyped_defs`, `no_implicit_optional`, etc.).

Para experimentar:

- En `demo_typeddict`, descomenta la línea `ranking(productos, "color")` y vuelve a correr `mypy .`. Vas a ver el error sin haber ejecutado el programa.
- Quita el método `render` de `Factura` y observa que mypy se queja al pasarla como `Imprimible`.
- Cambia `Usuario | None` por `Usuario` en `buscar_por_email` y mira el error que mypy reporta sobre el `return None`.

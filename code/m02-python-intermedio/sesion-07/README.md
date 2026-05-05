# S07 — Código de la sesión

```bash
uv run python main.py
```

`main.py` recorre seis escenarios:

1. Caso feliz — el SKU existe y tiene precio numérico.
2. SKU no encontrado — captura específica de `ProductoNoEncontrado`.
3. Producto sin precio — captura específica de `ProductoIncompleto`.
4. Precio no numérico — misma excepción, distinto mensaje.
5. Captura por base del dominio — un solo `except CatalogoError` atrapa los tres tipos.
6. `raise from` — la última demo deja propagar la excepción para que veas el traceback con encadenamiento.

`errores.py` define la jerarquía de dominio (`CatalogoError` → `ProductoNoEncontrado`, `ProductoIncompleto`).

`catalogo.py` muestra cómo traducir excepciones de bajo nivel (`KeyError`, `ValueError`) a errores de dominio con `raise ... from e`.

Para experimentar, agrega un cuarto producto al `CATALOGO` con un campo nuevo y otra forma de fallar (por ejemplo, `precio` negativo). Decide si vale una excepción nueva o si encaja en `ProductoIncompleto`.

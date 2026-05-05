# S09 — Código de la sesión

```bash
uv run python main.py
```

`main.py` recorre cuatro demos:

1. **Decorador `@cronometro`** con `functools.wraps`. Verás que `trabajo_lento.__name__` se preserva.
2. **Pipeline de generadores** sobre una fuente infinita (`naturales()`). Composición de tres generadores produce los primeros 5 cuadrados pares con memoria constante.
3. **Context manager con clase** (`CronometroBloque` con `__enter__`/`__exit__`).
4. **Context manager con `@contextmanager`** (`cronometro_simple` como generador con `try/finally` alrededor del `yield`). Misma API, mucho menos código.

Para experimentar:

- Saca `@functools.wraps` del decorador y observa cómo `trabajo_lento.__name__` cambia a `'envoltorio'`.
- Lanza una excepción dentro del `with cronometro_simple(...)` y verifica que el tiempo se imprime igual (gracias al `try/finally`).
- Compón los generadores en otro orden (`cuadrado(pares(naturales()))`) y observa cómo cambia el output.

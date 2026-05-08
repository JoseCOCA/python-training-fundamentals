# Sandbox de S21 — pytest

Sandbox para practicar testing con pytest. Tiene dos módulos para ejercitar:

- `descuentos.py` — funciones puras + `Carrito`. Para tests unit con fixtures, parametrize y monkeypatch.
- `mini_api.py` — mini FastAPI con `/saludo` y `/eco`. Para integration tests con `TestClient`.

## Cómo correr

```bash
uv sync --all-groups
uv run pytest                       # debería decir "no tests ran" — los escribís vos
```

Una vez que escribas los tests siguiendo `ejercicios.md`, debería verse algo como:

```
tests/test_descuentos.py ...........  [85%]
tests/test_mini_api.py ...           [100%]

13 passed in 0.42s
```

## Coverage

```bash
uv run pytest --cov=descuentos --cov=mini_api --cov-report=term-missing
```

## Qué hay para mejorar

`descuentos.py` tiene casos de borde no cubiertos en `aplicar_descuento` (¿qué pasa con `porcentaje=100`? ¿con un `precio` negativo?). Tu trabajo es decidir qué casos vale la pena testear y cuáles son fuera de contrato.

Pasos detallados en [`ejercicios.md`](../../../docs/modulos/06-herramientas-ingeniero/sesion-21-pytest/ejercicios.md).

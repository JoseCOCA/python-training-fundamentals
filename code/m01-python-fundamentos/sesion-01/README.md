# S01 — Código de la sesión

Demos ejecutables de los conceptos de S01.

## Cómo correr el script

Desde dentro de este directorio:

```bash
uv run python main.py
```

## Qué hace `main.py`

Muestra en orden los temas de la sesión:

1. Variables y tipos primitivos (con `type()` en cada uno).
2. Operadores aritméticos en un cálculo de subtotal con descuento.
3. Conversiones de tipo (`str` → `float`, truncamiento de `int`).
4. Comparaciones y operadores booleanos.
5. La trampa de la precisión de `float` (`0.1 + 0.2`).

## Después de correrlo

Modifica el script. Cambia valores, agrega expresiones nuevas, rómpelo a propósito (por ejemplo: borra el `float()` de la línea 50 y observa el error). El objetivo no es que el script funcione siempre — es que entiendas por qué hace lo que hace.

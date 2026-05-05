# S06 — Código de la sesión

```bash
uv run python main.py
```

`main.py` recorre las cuatro demos:

1. **Import de un módulo simple** — `saludador.py` con función pública y constante.
2. **Import desde un paquete** — `tienda/` con `productos.py` y `clientes.py`, re-exportados desde `__init__.py`.
3. **`__name__`** — qué vale cuando ejecutas directamente vs cuando importas.
4. **`sys.path`** — la lista de directorios donde Python busca módulos.

Para ver el guard en acción:

```bash
uv run python saludador.py     # ejecuta la demo del módulo
uv run python -c "import saludador"   # NO ejecuta la demo, solo importa
```

Después, modifica:
- Agrega un nuevo módulo `pedidos.py` dentro de `tienda/` con una función `crear_pedido(cliente_id, productos)` y re-expórtala desde `__init__.py`.
- Cambia un `import` absoluto por uno relativo dentro de `tienda/__init__.py` y observa que sigue funcionando.
- Borra el `__init__.py` y vuelve a correr — entiende qué cambia (o qué no, porque Python 3 lo permite como namespace package).

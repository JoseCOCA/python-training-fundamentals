# S08 — Código de la sesión

```bash
uv run python main.py
```

`main.py` recorre cinco demos:

1. **Clase mínima a mano** — `ProductoManual` con `__init__`, métodos y `__repr__` escritos a mano.
2. **`@dataclass`** — el mismo modelo con menos código y `__eq__` automático.
3. **Atributos seguros** — `field(default_factory=list)` para evitar la trampa del default mutable compartido.
4. **`frozen=True`** — tipo de valor inmutable, comparable y hasheable.
5. **Composición vs herencia** — `ProductoConModificadores` con flags en lugar de una jerarquía combinatoria.

Para experimentar:

- Quita `frozen=True` de `Punto` y observa que `hash(p1)` empieza a fallar (no se puede hashear un objeto mutable por defecto).
- Convierte `ProductoManual` también en `@dataclass` y compara visualmente cuántas líneas se ahorran.
- Diseña una jerarquía con herencia equivalente a `ProductoConModificadores` y cuenta cuántas clases necesitas para soportar tres modificadores combinables.

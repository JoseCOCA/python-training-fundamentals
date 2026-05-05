# S08 — Ejercicios

> **Tiempo estimado:** ~75 min. Vamos a partir de la versión "todo es dict" del integrador y migrarla a `@dataclass` con criterio. Después practicas casos donde **no** deberías usar clases (esa parte importa tanto como la otra).

---

## 0. Antes de empezar

Tu sandbox vive en `code/m02-python-intermedio/sesion-08/`. Si todavía no lo corriste:

```bash
cd code/m02-python-intermedio/sesion-08
uv run python main.py
```

Confirma que ves las cinco demos. Después regresa a este documento.

## 1. Ejercicio guiado — De `dict` a `@dataclass`

### Paso 1.1 — Versión `dict`

Crea `dict_version.py` en un proyecto nuevo (`uv init --no-readme --bare ejercicio-08 && cd ejercicio-08`):

```python
# dict_version.py
PRODUCTOS = [
    {"sku": "A001", "nombre": "Auriculares", "precio": 89.99, "stock": 5},
    {"sku": "A002", "nombre": "Cable USB", "precio": 12.50, "stock": 0},
    {"sku": "A003", "nombre": "Cargador", "precio": 24.00, "stock": 12},
]


def valor_total(p: dict) -> float:
    return p["precio"] * p["stock"]


def disponible(p: dict) -> bool:
    return p["stock"] > 0


def imprimir(productos):
    for p in productos:
        marca = "✓" if disponible(p) else "✗"
        print(f"{marca} {p['sku']:<6} {p['nombre']:<15} ${p['precio']:>7.2f} (stock: {p['stock']})")


if __name__ == "__main__":
    imprimir(PRODUCTOS)
    total = sum(valor_total(p) for p in PRODUCTOS)
    print(f"\nValor total del inventario: ${total:.2f}")
```

Córrelo. Funciona. Pero observa los problemas:

- Cada función tiene que confiar en que el `dict` tiene las claves correctas. Si hay un typo (`p["stok"]`), explota en runtime.
- El tipado es `dict` — no dice nada útil.
- Las funciones (`valor_total`, `disponible`) están sueltas, "afuera" del dato al que pertenecen.

### Paso 1.2 — Versión `@dataclass`

Crea `dataclass_version.py`:

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class Producto:
    sku: str
    nombre: str
    precio: float
    stock: int

    def valor_total(self) -> float:
        return self.precio * self.stock

    def disponible(self) -> bool:
        return self.stock > 0


PRODUCTOS = [
    Producto("A001", "Auriculares", 89.99, 5),
    Producto("A002", "Cable USB", 12.50, 0),
    Producto("A003", "Cargador", 24.00, 12),
]


def imprimir(productos: list[Producto]) -> None:
    for p in productos:
        marca = "✓" if p.disponible() else "✗"
        print(f"{marca} {p.sku:<6} {p.nombre:<15} ${p.precio:>7.2f} (stock: {p.stock})")


if __name__ == "__main__":
    imprimir(PRODUCTOS)
    total = sum(p.valor_total() for p in PRODUCTOS)
    print(f"\nValor total del inventario: ${total:.2f}")
```

Córrelo. El output es idéntico. Las diferencias importantes están en otra parte:

- `Producto("A001", ...)` — el constructor tipa explícitamente cada parámetro.
- `p.precio` en lugar de `p["precio"]` — mypy y tu editor te avisan si te equivocas en el nombre.
- `p.disponible()` lee mejor que `disponible(p)` cuando la función "pertenece" al dato.
- `frozen=True` te garantiza que nadie mutará un producto por error en otro lugar del código.

### Paso 1.3 — Probar `frozen` y la igualdad automática

Agrega al final de `dataclass_version.py`:

```python
a = Producto("X", "Test", 10.0, 1)
b = Producto("X", "Test", 10.0, 1)

print(a == b)        # → True (igualdad estructural, no de identidad)
print(a is b)        # → False (son objetos distintos en memoria)

# a.precio = 99.99    ← descomenta y mira el error
```

Por defecto `==` en Python compara identidad (¿es el mismo objeto?). `@dataclass` lo redefine para comparar **campo por campo**. Esa es la diferencia entre un objeto-de-valor y un objeto cualquiera.

### Paso 1.4 — Reflexionar

| | `dict` | `@dataclass` |
|---|---|---|
| Líneas para definir el modelo | 0 | 6 |
| Errores de tipeo detectados antes de runtime | no | sí (con mypy o el editor) |
| Métodos viven con los datos | no | sí |
| Inmutabilidad | imposible | una flag (`frozen=True`) |
| Comparación estructural | manual | automática |

Las 6 líneas extra te compran cuatro propiedades importantes. **Por eso los dominios serios en Python moderno se modelan con `@dataclass` (o pydantic, que viene en M3).**

## 2. Ejercicios libres

### 2.1. Modelo de `Pedido`

Diseña un `@dataclass` `Pedido` con:

- `id: int`
- `cliente_id: int`
- `items: list[tuple[Producto, int]]` — cada tupla es `(producto, cantidad)`
- `creado_en: datetime` (importa `from datetime import datetime`)

Agrega métodos:

- `total() -> float` — suma de `producto.precio * cantidad` por item.
- `cantidad_items() -> int` — total de unidades, no de líneas.

Decide si el `Pedido` debe ser `frozen` o no. Argumenta tu decisión en un comentario al final del archivo.

### 2.2. Defaults mutables: el bug clásico

Escribe esta clase y ejecútala:

```python
from dataclasses import dataclass

@dataclass
class Carrito:
    items: list = []      # ❌

c1 = Carrito()
c1.items.append("manzana")
c2 = Carrito()
print(c2.items)
```

Vas a obtener un `ValueError` al definir la clase (Python detecta el problema desde Python 3.11+). Léelo, entiéndelo y arréglalo con `field(default_factory=list)`.

Después responde con tus palabras: ¿por qué la lista compartida es un bug y no una "feature de eficiencia"?

### 2.3. Composición vs herencia

Modela este dominio **dos veces**:

> Un negocio vende productos. Algunos productos tienen impuesto, otros no. Algunos están en oferta, otros no.

**Versión A (herencia, mala):**

```
Producto
 ├── ProductoConImpuesto
 └── ProductoEnOferta
```

¿Qué pasa cuando aparece `ProductoConImpuestoYEnOferta`? ¿Y cuando hay tres modificadores combinables?

**Versión B (composición, buena):**

```python
@dataclass
class Producto:
    nombre: str
    precio: float
    impuesto_pct: float = 0.0
    descuento_pct: float = 0.0

    def precio_final(self) -> float:
        con_impuesto = self.precio * (1 + self.impuesto_pct / 100)
        con_descuento = con_impuesto * (1 - self.descuento_pct / 100)
        return con_descuento
```

Implementa ambas y compara cuántas líneas requiere agregar **un cuarto modificador** (por ejemplo, "envío gratis si pasa de cierto monto"). La diferencia es la respuesta.

### 2.4. La trampa de la "utility class"

Refactoriza este código a algo más Pythonic:

```python
class TextUtils:
    @staticmethod
    def normalizar(s: str) -> str:
        return s.strip().lower()

    @staticmethod
    def es_email(s: str) -> bool:
        return "@" in s and "." in s.split("@")[-1]

    @staticmethod
    def slugify(s: str) -> str:
        return s.strip().lower().replace(" ", "-")
```

Pista: las funciones no necesitan estar dentro de una clase para vivir juntas. ¿Qué objeto del lenguaje sirve para agrupar funciones relacionadas?

### 2.5. `__repr__` informativo

Define una clase `Reserva` (sin `@dataclass`, a mano) con:

- `huesped: str`
- `entrada: date`
- `salida: date`
- `habitacion: int`

Define `__repr__` para que imprima:

```
Reserva(habitacion=205, huesped='Ana López', del 2026-05-10 al 2026-05-15)
```

Después conviértela a `@dataclass` y compara cuál `__repr__` te da más información de un solo vistazo. Decide cuál prefieres y por qué.

## 3. Reto

Modela una mini-tienda con dataclasses inmutables. Reglas:

- `Producto`, `Cliente` y `Pedido` son `@dataclass(frozen=True)`.
- `Pedido` tiene un método `agregar_item(producto, cantidad)` que **no muta** sino que **devuelve un Pedido nuevo** con el item agregado. Esto es el patrón de "datos persistentes inmutables".
- `Pedido.total()` recibe un `descuento_pct: float = 0.0` opcional.
- Si la cantidad es <= 0, lanza `ValueError`.
- Si el producto está sin stock, lanza una excepción de dominio que tú definas (relee S07).

Escribe un `main.py` que:

1. Cree tres productos.
2. Cree un cliente.
3. Cree un pedido vacío y le agregue items en cadena: `pedido.agregar_item(p1, 2).agregar_item(p2, 1)`.
4. Imprima el `__repr__` del pedido final.
5. Capture la excepción al intentar agregar un producto sin stock.

Si lo terminas, considera si valdría agregar un método `quitar_item` y qué propiedades preservaría (también devolver `Pedido` nuevo, idem `total`).

## 4. Aporte al proyecto integrador

Hoy migras los datos del integrador de `dict` a `@dataclass`.

### 4.1. Crear `src/tiendapro/modelos.py`

```python
"""Modelos de dominio de TiendaPro."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Producto:
    sku: str
    nombre: str
    precio: float
    stock: int
    moneda: str = "USD"

    def disponible(self) -> bool:
        return self.stock > 0

    def valor_total(self) -> float:
        return self.precio * self.stock


@dataclass(frozen=True)
class Cliente:
    id: int
    nombre: str
    email: str
```

### 4.2. Adaptar `src/tiendapro/catalogo.py`

- La función `cargar()` ahora devuelve `list[Producto]`, no `list[dict]`.
- Al construir cada `Producto`, captura los `KeyError`/`TypeError` y lanza `CatalogoInvalido` con un mensaje útil (relee el patrón de S07).
- `filtrar_disponibles()` recibe y devuelve `list[Producto]`.
- `ordenar_por_precio()` recibe y devuelve `list[Producto]`. Usa `key=lambda p: p.precio`.

### 4.3. Adaptar `src/tiendapro/presentacion.py`

`imprimir_tabla()` recibe `list[Producto]`. Usa atributos tipados (`p.precio`, `p.nombre`) en lugar de claves de diccionario.

### 4.4. Re-exportar en `__init__.py`

```python
from tiendapro.errores import CatalogoInvalido, ProductoNoEncontrado, TiendaProError
from tiendapro.modelos import Cliente, Producto

__all__ = [
    "Cliente",
    "Producto",
    "CatalogoInvalido",
    "ProductoNoEncontrado",
    "TiendaProError",
]
```

### 4.5. Verificar

`uv run python main.py` debe producir el mismo output que antes — el comportamiento no cambia, solo el modelo. Si algo se rompe, **léelo con calma**: probablemente es una clave de `dict` que quedó suelta y ahora es atributo.

### 4.6. Commit

```bash
git add code/proyecto-integrador
git commit -m "feat(proyecto-integrador): migra modelos de dict a dataclasses (Producto, Cliente)"
```

> **Importante:** falta S09 para cerrar M2. La S09 introduce `with` (que vas a usar para abrir el JSON correctamente) y generadores. El commit final + tag `proyecto-m2` ocurre al final de S09.

---

Cuando termines, vuelve al README y responde las preguntas de auto-evaluación. Si todas se contestan sin dudar, pasa a [S09 — Decoradores, generadores y context managers](../sesion-09-decoradores-generadores-context/README.md).

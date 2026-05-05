# S10 — Ejercicios

> **Tiempo estimado:** ~75 min. Cuatro bloques: ejercicio guiado armando un módulo tipado desde cero, libres para entrenar reflejos sobre tipos genéricos / Optional / Protocol, reto, y aporte al integrador haciendo que mypy pase limpio.

---

## 0. Antes de empezar

Tu sandbox vive en `code/m03-tipado-calidad/sesion-10/`. Si todavía no lo corriste:

```bash
cd code/m03-tipado-calidad/sesion-10
uv run python main.py
uv run mypy .
```

Confirma que ves cuatro demos y que mypy reporta cero errores. Después regresa a este documento.

## 1. Ejercicio guiado — Tipar un módulo desde cero

Vamos a escribir un mini-módulo de ranking de productos completamente tipado. Después le pasamos mypy y vemos su reporte.

### Paso 1.1 — Crear el sandbox del ejercicio

```bash
cd code/m03-tipado-calidad
uv init --no-readme --bare ejercicio-10
cd ejercicio-10
uv add --dev mypy
```

### Paso 1.2 — Escribir el código sin tipos (la versión que NO debes dejar)

`ranking.py`:

```python
def ranking(productos, criterio):
    return sorted(productos, key=lambda p: p[criterio])


def top_n(productos, criterio, n):
    return ranking(productos, criterio)[:n]


productos = [
    {"sku": "A", "precio": 10, "stock": 3},
    {"sku": "B", "precio": 5,  "stock": 8},
    {"sku": "C", "precio": 20, "stock": 1},
]

print(top_n(productos, "precio", 2))
```

Córrelo. Funciona. Pero ningún humano sabe qué espera `productos`, qué tipos acepta `criterio`, ni qué devuelve `top_n`.

### Paso 1.3 — Tipar primer pasada

```python
from typing import TypedDict


class Producto(TypedDict):
    sku: str
    precio: float
    stock: int


def ranking(productos: list[Producto], criterio: str) -> list[Producto]:
    return sorted(productos, key=lambda p: p[criterio])


def top_n(productos: list[Producto], criterio: str, n: int) -> list[Producto]:
    return ranking(productos, criterio)[:n]
```

Córrelo y después corre:

```bash
uv run mypy ranking.py
```

Vas a ver algo así:

```
ranking.py:11: error: Returning Any from function declared to return "list[Producto]"  [no-any-return]
ranking.py:11: error: No overload variant of "__getitem__" of "TypedDict" matches argument type "str"
```

mypy detecta que `criterio: str` es demasiado vago — un `TypedDict` solo soporta acceso con claves **literales**. Vamos a afinarlo.

### Paso 1.4 — Tipar con `Literal`

```python
from typing import Literal, TypedDict


class Producto(TypedDict):
    sku: str
    precio: float
    stock: int


Criterio = Literal["sku", "precio", "stock"]


def ranking(productos: list[Producto], criterio: Criterio) -> list[Producto]:
    return sorted(productos, key=lambda p: p[criterio])


def top_n(productos: list[Producto], criterio: Criterio, n: int) -> list[Producto]:
    return ranking(productos, criterio)[:n]
```

Corre mypy de nuevo. Debería pasar limpio. Y como bonus, si llamas `top_n(productos, "color", 2)`, mypy te avisa **antes** de ejecutar. **Eso** es la diferencia.

### Paso 1.5 — Reflexionar

Compara las dos versiones desde el punto de vista de un consumidor:

| | Sin tipos | Tipado con `Literal` |
|---|---|---|
| ¿Qué claves son válidas? | hay que leer el código | está en la firma |
| ¿Qué pasa si paso `"foo"`? | TypeError en runtime | mypy te avisa |
| ¿El IDE autocompleta? | no | sí, los tres literales |

**Esa es la propuesta de valor:** no es solo "menos bugs" — es **información que el sistema te da gratis**.

## 2. Ejercicios libres

### 2.1. Anotar funciones de la librería estándar

Sin mirar la doc, escribe la firma tipada de estas funciones (usando type hints modernos):

- `len(obj)` — devuelve un entero. ¿Qué tipo recibe?
- `max(iterable, key=...)` — versión simplificada que recibe un iterable de números.
- `sorted(iterable, key=...)` — recibe un iterable de `T`, una función `T -> K` (con K comparable), devuelve `list[T]`.
- `dict.get(key, default=...)` — versión simplificada.

Después busca la firma real en la doc o con `help(...)`. Compara y aprende dónde te quedó corta tu intuición.

### 2.2. Optional vs `| None`

Anota correctamente esta función:

```python
def buscar_por_email(usuarios, email):
    """Devuelve el usuario o None si no existe."""
    for u in usuarios:
        if u.email == email:
            return u
    return None
```

Asume que `usuarios: list[Usuario]` y que `Usuario` es una dataclass con `email: str` y `nombre: str`. Versión moderna sin `Optional`.

### 2.3. `Callable` en práctica

Escribe una función `aplicar_a_todos` con esta especificación:

- Recibe una lista de elementos de tipo `T`.
- Recibe una función `T -> R`.
- Devuelve `list[R]`.

Usa `Callable` y los TypeVars necesarios:

```python
from collections.abc import Callable
from typing import TypeVar

T = TypeVar("T")
R = TypeVar("R")


def aplicar_a_todos(items: list[T], f: Callable[[T], R]) -> list[R]:
    return [f(x) for x in items]
```

Ahora pruébalo con `aplicar_a_todos([1, 2, 3], str)` y observa que mypy infiere correctamente `list[str]`.

### 2.4. Type narrowing

Tienes esta función:

```python
def procesar(valor: int | str | None) -> str:
    # ...
```

Escribe el cuerpo con narrowing limpio:

- Si `valor` es `None`, devuelve `"vacío"`.
- Si `valor` es `int`, devuelve `f"entero: {valor}"`.
- Si es `str`, devuelve `valor.upper()`.

Hazlo SIN usar `cast`. Solo `is None` e `isinstance`. Verifica con `uv run mypy ranking.py` que mypy entiende cada rama.

### 2.5. Protocol vs herencia

Define una `Renderable` como `Protocol` con un método `render() -> str`. Después escribe:

- Una clase `Producto` que NO hereda de `Renderable` pero implementa `render`.
- Una clase `Cliente` igual.
- Una función `pintar(items: list[Renderable]) -> None` que llama `render` en cada uno.

Pasa mypy. Después comenta el método `render` en una de las clases y observa cómo mypy se queja sin necesidad de heredar.

## 3. Reto

Toma el sandbox de S08 (`code/m02-python-intermedio/sesion-08/`), agrega `mypy` como dev dependency:

```bash
cd code/m02-python-intermedio/sesion-08
uv add --dev mypy
```

Corre `uv run mypy .` y arregla todos los errores que aparezcan **sin tocar el comportamiento del código**. La meta es: cero errores en mypy, cero cambios en el output del programa.

Pista: probablemente tengas que:

- Anotar `__init__` de `ProductoManual`.
- Anotar parámetros y retorno de las funciones de demo.
- Pensar el tipo correcto para los items de la lista en `ProductoConModificadores`.

Si mypy no te encuentra nada, sube la configuración a `strict = true` y vuelve a correrlo. Algo va a aparecer.

## 4. Aporte al proyecto integrador

Hoy haces que el integrador pase mypy limpio.

### 4.1. Configurar mypy en el integrador

En `code/proyecto-integrador/pyproject.toml`, agrega:

```toml
[dependency-groups]
dev = [
    "mypy>=1.10",
]

[tool.mypy]
python_version = "3.12"
warn_unused_ignores = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
no_implicit_optional = true
warn_redundant_casts = true
warn_return_any = true
```

Después:

```bash
cd code/proyecto-integrador
uv sync
uv run mypy src/ main.py
```

### 4.2. Resolver los errores

Probablemente vas a ver errores en:

- Funciones sin retorno tipado.
- `dict` sin parametrizar (de cuando construías el catálogo desde JSON).
- Variables locales con tipo inferido como `Any`.

**Resuelvelos uno por uno**, sin caer en `# type: ignore` salvo que tengas razón documentada. Si un error te confunde, lee el mensaje completo — mypy explica qué espera y qué encontró.

### 4.3. Verificar que el comportamiento no cambió

```bash
uv run python main.py
```

Output esperado: idéntico al hito M2 ($7,267.00 en 8 productos disponibles). Si cambió algo, **deshace** y vuelve a tipar — la regla de esta sesión es **no romper comportamiento al tipar**.

### 4.4. Commit

```bash
git add code/proyecto-integrador
git commit -m "feat(proyecto-integrador): tipa el paquete y configura mypy estricto"
```

> **Importante:** todavía falta S11 para cerrar M3. La S11 agrega pydantic (validación runtime de los datos cargados desde JSON) y ruff (linter). El commit final + tag `proyecto-m3` ocurre al final de S11.

---

Cuando termines, vuelve al README y responde las preguntas de auto-evaluación. Si todas se contestan sin dudar, pasa a [S11 — pydantic + ruff + pre-commit](../sesion-11-pydantic-ruff/README.md).

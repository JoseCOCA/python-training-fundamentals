# S10 — Type hints, mypy y refactoring guiado por tipos

> **Sesión 2h.** ~45 min lectura + ~75 min ejercicios. **Abre el Módulo 3.** Hasta aquí el tipado fue opcional — ahora se vuelve **norma de calidad**. Esta sesión cambia tu forma de leer y escribir Python: el tipo deja de ser metadata decorativa y empieza a ser **documentación ejecutable** que un verificador como mypy puede comprobar antes de correr una sola línea.

---

## 1. Objetivos de aprendizaje

Al terminar esta sesión vas a poder:

- Anotar funciones, variables y atributos con type hints idiomáticos.
- Usar tipos genéricos (`list[int]`, `dict[str, float]`, `tuple[int, ...]`).
- Distinguir `Optional[X]`, `X | None`, `Union[A, B]` y `A | B`.
- Anotar funciones que reciben otras funciones (`Callable[..., T]`).
- Configurar **mypy** y leer sus reportes.
- Aplicar **type narrowing** con `isinstance` y `assert`.
- Reconocer cuándo `Protocol` es la herramienta correcta (duck typing tipado).
- Refactorizar código existente guiándote por los errores que encuentra mypy.

## 2. Prerequisitos

- M1 y M2 completos. En particular: funciones (S04), dataclasses (S08), errores de dominio (S07).
- Curiosidad por entender por qué algunos errores aparecen "antes de tiempo" cuando hay un type checker mirando.

## 3. Conceptos clave

1. **Type hint.** Anotación que describe el tipo esperado de una variable, parámetro o valor de retorno. **No se chequea en runtime** por Python; sirve a herramientas externas (mypy, pyright, IDEs).
2. **Tipo estructural vs nominal.** Python combina ambos. La herencia es nominal ("es-un X explícito"). `Protocol` es estructural ("se comporta como X aunque no lo declare").
3. **`Optional[X]` / `X | None`.** "Puede ser X o `None`". Una de las anotaciones más usadas porque modela lo que en otros lenguajes son nullables.
4. **`Any`.** El tipo "escapa de toda regla". Si lo usas, mypy no puede ayudarte. Es la salida de emergencia, no una herramienta diaria.
5. **mypy.** Verificador estático de tipos. Lee tu código sin ejecutarlo y reporta inconsistencias.
6. **Type narrowing.** El proceso por el cual mypy "afina" el tipo dentro de una rama: si el tipo era `int | None` y haces `if x is not None:`, dentro del `if` mypy sabe que `x` es `int`.

## 4. Teoría

### 4.1. Por qué tipar Python

Python es dinámicamente tipado: una variable puede contener cualquier cosa y cambiar de tipo a mitad de programa. Esa flexibilidad es buena para scripts pequeños y mala para sistemas grandes.

Un type hint no cambia el runtime. Lo que cambia es:

- **mypy te avisa antes de ejecutar.** Errores como pasar `str` donde se esperaba `int` aparecen al instante.
- **El IDE te autocompleta mejor.** Si declaras que `producto` es `Producto`, tu editor sabe qué métodos tiene.
- **El código se autodocumenta.** No necesitas comentar "esto es una lista de strings" — se lee solo.
- **Los refactors se vuelven seguros.** Cambias el tipo de retorno; mypy te marca todos los lugares afectados.

**El argumento clásico contra tipar — "Python es dinámico, dejalo así" — pierde fuerza con el tamaño del proyecto.** Para un script de 50 líneas, tal vez. Para una API de 50 archivos, los tipos pagan en horas ahorradas de debugging.

### 4.2. Sintaxis básica

```python
# Variables (raras veces necesario, salvo cuando el tipo no es obvio)
nombre: str = "Ana"
edad: int = 30
activo: bool = True

# Funciones — anotar parámetros y retorno
def saludar(nombre: str) -> str:
    return f"Hola, {nombre}"

def sumar(a: int, b: int) -> int:
    return a + b

# Si la función no devuelve nada útil, anota -> None
def imprimir(mensaje: str) -> None:
    print(mensaje)
```

**Reglas prácticas:**

- Anota siempre los **parámetros** y el **retorno** de las funciones públicas.
- Anota variables solo cuando el tipo no se infiere obvio (`x = []` no se sabe si es `list[int]` o `list[str]`).
- Las anotaciones son **strings o expresiones** evaluadas. Python las guarda en `__annotations__` pero no las usa para nada en runtime.

### 4.3. Tipos genéricos: colecciones tipadas

Desde Python 3.9 puedes usar los builtin types directamente como genéricos:

```python
def filtrar_pares(numeros: list[int]) -> list[int]:
    return [n for n in numeros if n % 2 == 0]

def precios_por_sku(catalogo: dict[str, float]) -> list[float]:
    return list(catalogo.values())

def punto() -> tuple[float, float]:
    return (3.14, 2.72)

# Tuplas heterogéneas con tamaño fijo
def triple() -> tuple[int, str, bool]:
    return (1, "uno", True)

# Tuplas homogéneas con tamaño variable
def coords() -> tuple[float, ...]:
    return (1.0, 2.0, 3.0, 4.0)
```

**No uses `List`, `Dict`, `Tuple` de `typing`** salvo que necesites compatibilidad con Python <3.9. La forma moderna es `list`, `dict`, `tuple` directos.

### 4.4. `Optional[X]` y `X | None`

Un tipo "puede ser X o `None`":

```python
# Forma vieja (todavía funciona)
from typing import Optional

def buscar(sku: str) -> Optional[Producto]:
    ...

# Forma moderna (Python 3.10+)
def buscar(sku: str) -> Producto | None:
    ...
```

`Optional[X]` es **literalmente** lo mismo que `X | None`. La forma con `|` es la idiomática moderna.

**Convención importante:** si una función puede no devolver nada útil, **declara `| None` explícitamente**. No dejes que el lector infiera por contexto.

### 4.5. Uniones: `Union[A, B]` y `A | B`

Cuando un valor puede ser de varios tipos:

```python
# Forma vieja
from typing import Union
def procesar(valor: Union[int, str]) -> str: ...

# Forma moderna (3.10+)
def procesar(valor: int | str) -> str: ...
```

**Cuidado:** uniones complejas suelen ser olor a problema. Si tienes `int | str | float | bool | None`, probablemente el diseño se puede simplificar.

### 4.6. Funciones como argumentos: `Callable`

```python
from collections.abc import Callable

def aplicar(f: Callable[[int, int], int], a: int, b: int) -> int:
    return f(a, b)

aplicar(lambda x, y: x + y, 2, 3)        # → 5
```

`Callable[[args...], retorno]`. Los corchetes internos describen los parámetros; el segundo parámetro de `Callable` es el tipo de retorno.

Casos especiales:

```python
Callable[..., int]            # cualquier signatura, devuelve int
Callable[[], None]             # sin parámetros, devuelve None
```

### 4.7. `Any`: la salida de emergencia

```python
from typing import Any

def deserializar_json(payload: str) -> Any:
    import json
    return json.loads(payload)
```

`Any` significa "este valor no tiene tipo verificable; tratemoslo como cualquier cosa". mypy **no chequea** las operaciones sobre un `Any`. Útil cuando:

- Estás en la frontera con el mundo exterior (JSON parsing, datos de archivos, requests HTTP).
- Tienes que migrar código sin tipar y el tipo real es complejo de modelar.

**Antipatrón:** usar `Any` por flojera. Si declaras `def f(x: Any) -> Any`, mypy te queda mudo. Solo usa `Any` cuando no haya alternativa razonable.

### 4.8. `TypedDict`: dicts con forma conocida

A veces tienes un `dict` que en realidad tiene **siempre las mismas claves**. Para esos casos:

```python
from typing import TypedDict

class ProductoJSON(TypedDict):
    nombre: str
    categoria: str
    precio: float
    stock: int


def imprimir(p: ProductoJSON) -> None:
    print(f"{p['nombre']}: ${p['precio']}")
```

Ahora `p["nbmre"]` (typo) lo cazas con mypy antes de runtime.

**Cuándo usarlo:** cuando trabajas con JSON crudo (antes de convertir a dataclass) y necesitas tipado sin pagar el costo de construir objetos. Para todo lo demás, `@dataclass` o `pydantic` (S11) son mejores.

### 4.9. Configurar mypy

Ya está en tu `pyproject.toml` raíz, pero es bueno entender qué configura. Configuración mínima:

```toml
[tool.mypy]
python_version = "3.12"
strict = false             # arranca blando, sube progresivamente
warn_unused_ignores = true
disallow_untyped_defs = true   # las funciones DEBEN tener anotaciones
```

Correr mypy:

```bash
uv run mypy src/
```

Output típico:

```
src/tiendapro/catalogo.py:42: error: Argument 1 to "cargar" has incompatible type "str"; expected "Path"
Found 1 error in 1 file (checked 5 source files)
```

**Lectura del reporte:**

- Archivo y línea exactos.
- Qué esperaba el tipo.
- Qué recibió.

mypy es tu **segunda persona revisando el código** sin necesitar a otra persona.

### 4.10. Type narrowing: cómo mypy refina los tipos

Dentro de un bloque condicional, mypy "afina" el tipo automáticamente:

```python
def imprimir_largo(valor: str | None) -> None:
    if valor is None:
        return                          # aquí mypy sabe que valor es None
    print(len(valor))                  # aquí mypy sabe que valor es str
```

Otras formas de narrowing:

```python
def procesar(x: int | str) -> str:
    if isinstance(x, int):
        return f"entero: {x}"          # mypy sabe que x es int
    return x.upper()                    # mypy sabe que x es str

def procesar2(x: object) -> int:
    assert isinstance(x, int)
    return x + 1                        # mypy sabe que x es int
```

**Patrón clave:** chequear `is None` o `isinstance` y salir temprano. mypy te lleva de la mano.

### 4.11. Protocols: tipado estructural

Hasta aquí los tipos son **nominales**: tienen que coincidir por nombre/herencia. Pero a veces solo te importa que un objeto **tenga ciertos métodos**, sin importar su jerarquía.

```python
from typing import Protocol


class Imprimible(Protocol):
    def imprimir(self) -> None: ...


class Producto:
    def imprimir(self) -> None:
        print("producto")


class Factura:
    def imprimir(self) -> None:
        print("factura")


def imprimir_todo(items: list[Imprimible]) -> None:
    for x in items:
        x.imprimir()


imprimir_todo([Producto(), Factura()])  # ✅ ambos cumplen el protocolo
```

Ni `Producto` ni `Factura` heredan de `Imprimible`. Pero **estructuralmente** lo cumplen — tienen el método `imprimir()`. Esto es **duck typing** con verificación estática: lo mejor de los dos mundos.

**Cuándo usar Protocol:** cuando definirías una "interfaz" en otros lenguajes. Cuando tu función opera sobre "cosas que tienen ciertos métodos", sin importar su tipo concreto.

### 4.12. Refactoring guiado por tipos

Caso real: tienes una función con bug latente.

```python
def buscar_producto(catalogo, sku):
    for p in catalogo:
        if p["sku"] == sku:
            return p
    return None
```

Sin tipos, esa función puede fallar de muchas formas: `catalogo` no es iterable, los items no son dicts, `sku` es int en vez de str. Agregás tipos:

```python
def buscar_producto(catalogo: list[dict[str, str]], sku: str) -> dict[str, str] | None:
    for p in catalogo:
        if p["sku"] == sku:
            return p
    return None
```

mypy ahora chequea cada llamada a la función. Pero más importante: mientras anotabas, te diste cuenta de que ese `dict[str, str]` está mintiendo — el catálogo tiene `precio: float` también. **El acto de tipar te obligó a pensar la estructura real**, y aparece el siguiente paso natural: convertir el dict a una dataclass `Producto`.

**Esa es la propuesta de valor del tipado estricto:** no es solo "evitar bugs"; es "pensar mejor el código mientras lo escribes".

## 5. Patrones y antipatrones

| ✅ Patrón | ❌ Antipatrón |
|---|---|
| `list[int]`, `dict[str, float]` | `List[int]`, `Dict[str, float]` (forma vieja sin necesidad) |
| `X | None` (Python 3.10+) | `Optional[X]` cuando el proyecto ya está en 3.10+ |
| Funciones públicas siempre tipadas | Mezcla aleatoria de tipadas y no tipadas |
| `Any` solo en bordes (parseo JSON, datos externos) | `Any` por flojera |
| `Protocol` para "duck typing tipado" | Heredar de una clase abstracta solo para tipar |
| `assert isinstance(...)` para narrowing en lugar de `cast` | `cast(X, valor)` cuando hay una verificación posible |
| Tipos genéricos precisos (`list[Producto]`) | `list` sin parametrizar |
| `mypy --strict` o `disallow_untyped_defs` activos en proyectos nuevos | Tipar "cuando me acuerdo" |
| Escribir el tipo, dejarlo a mypy verificar | Escribir el tipo y agregar `if not isinstance(x, ...)` defensivo encima |

## 6. Conexión con el proyecto integrador — Camino al hito M3

El integrador ya tiene buen tipado básico de S08 (las dataclasses). Hoy:

1. **Configurar `[tool.mypy]` en el `pyproject.toml`** del integrador con `disallow_untyped_defs = true`.
2. **Correr `uv run mypy src/` y leer los reportes.** Va a haber cosas que arreglar — eso es bueno, eso es la sesión funcionando.
3. **Anotar las funciones que falten.** Especialmente en `catalogo.py` y `presentacion.py`.
4. **Reemplazar `dict` sueltos por `TypedDict` o dataclass** donde aplique.

Esto NO cierra el hito M3 todavía. La S11 agrega pydantic (validación runtime) y ruff (linter). El cierre es al final de S11.

## 7. Resumen

1. **Type hints son anotaciones que no afectan runtime.** Sirven a mypy y a tu IDE.
2. **Sintaxis moderna:** `list[int]`, `dict[str, float]`, `X | None`, `int | str`. Olvídate de `List`, `Dict`, `Optional` salvo en código viejo.
3. **`Callable[[A, B], R]`** para funciones como argumento.
4. **`Any` es la salida de emergencia.** Úsala con disciplina, solo en bordes.
5. **mypy es un revisor adicional.** Corrélo seguido. Lee sus reportes con calma.
6. **Type narrowing** con `is None`, `isinstance`, `assert` te deja escribir código limpio sin casts.
7. **Protocols = duck typing tipado.** La interfaz sin la herencia.
8. **Tipar es pensar mejor.** Casi siempre encuentras un mejor diseño cuando intentas tipar el código existente.

## 8. Preguntas de auto-evaluación

1. ¿Qué hace Python en runtime con un type hint? ¿Y mypy?
2. ¿Cuál es la diferencia entre `Optional[X]` y `X | None`? ¿Cuál usarías hoy?
3. Anota correctamente esta función: "recibe un dict que mapea SKUs a precios y devuelve el SKU del más barato (o None si está vacío)".
4. Diferencia entre `Any` y `object`. ¿Cuál es más estricto?
5. Tienes `def f(x: int | str) -> str:`. Dentro del cuerpo, ¿cómo le indicas a mypy "ahora confía en que es str"?
6. Define un `Protocol` para "cualquier cosa que tenga un método `precio() -> float`". Después escribe una función `total(items)` que sume los precios.
7. ¿Cuándo usarías `TypedDict` en lugar de `@dataclass`?
8. ¿Qué hace `mypy --strict`? Nombra al menos tres flags que activa.
9. Tienes `def f(x): return x.nombre`. ¿Qué hace mypy si no tiene anotaciones? ¿Qué cambia si declaras `x: Any`?
10. Explica con tus palabras qué es **type narrowing** y por qué hace que uses menos `cast()` en código bien tipado.

Cuando puedas responder todas, pasa a [`ejercicios.md`](ejercicios.md).

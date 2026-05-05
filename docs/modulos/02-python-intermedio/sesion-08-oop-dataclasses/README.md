# S08 — Programación orientada a objetos: clases, dataclasses y diseño con criterio

> **Sesión 2h.** ~45 min lectura + ~75 min ejercicios. La OOP es la herramienta más poderosa y más sobre-utilizada del software. Esta sesión te enseña a usarla **cuando agrega valor** y a no usarla cuando una función basta. Salir de aquí con la idea de "usa clases para todo" sería un fracaso pedagógico.

---

## 1. Objetivos de aprendizaje

Al terminar esta sesión vas a poder:

- Definir una clase con `__init__`, atributos y métodos.
- Distinguir **atributos de instancia** de **atributos de clase**.
- Usar `@dataclass` para clases-de-datos sin escribir `__init__` a mano.
- Implementar `__repr__` y `__str__` para hacer tus objetos imprimibles.
- Modelar herencia simple sin caer en jerarquías profundas.
- **Decidir cuándo NO usar clases** — el caso más importante de la sesión.

## 2. Prerequisitos

- [S04 — Funciones](../../01-python-fundamentos/sesion-04-funciones/README.md) sólida. Un método es una función con `self` adelante.
- [S07 — Errores](../sesion-07-errores/README.md). Vas a lanzar excepciones de dominio desde tus clases.
- Tipos básicos (S01) y estructuras (S03).

## 3. Conceptos clave

1. **Clase.** Un molde que describe un tipo de objeto: qué datos tiene y qué puede hacer. Por convención, los nombres de clase van en `PascalCase`: `Producto`, `Cliente`.
2. **Instancia.** Un objeto concreto creado a partir de la clase. Tres `Producto` son tres instancias distintas, cada una con sus propios datos.
3. **`__init__`.** El método que se ejecuta cuando creas la instancia. Recibe `self` y los argumentos del constructor. Su trabajo es **inicializar atributos**.
4. **`self`.** La referencia al objeto actual. Dentro de un método, `self.algo` es "el `algo` _de esta instancia_".
5. **`@dataclass`.** Un decorador del módulo `dataclasses` que escribe `__init__`, `__repr__` y `__eq__` por ti, a partir de los atributos declarados. Es el atajo idiomático para clases-de-datos.
6. **Herencia.** Decir que una clase `B` "es-un" tipo de clase `A`. `B` hereda los atributos y métodos de `A` y puede agregar o sobreescribir.

## 4. Teoría

### 4.1. Antes de la primera clase: ¿para qué quieres usar OOP?

Una clase sirve cuando tienes **datos + comportamiento que viven juntos**. El caso de uso clásico:

> "Tengo un producto con `nombre`, `precio` y `stock`. Quiero saber su `valor_total`, decidir si está `disponible`, y formatearlo para mostrar."

Función pura sería:

```python
def valor_total(producto: dict) -> float:
    return producto["precio"] * producto["stock"]

def disponible(producto: dict) -> bool:
    return producto["stock"] > 0
```

Y eso **funciona perfectamente**. La OOP gana cuando:

1. Tienes muchas funciones operando sobre los mismos datos (más de 4-5).
2. Hay **invariantes** que quieres garantizar (precio nunca negativo, stock nunca menor a 0).
3. Quieres distintos tipos del mismo concepto con comportamiento parcialmente compartido (`ProductoFisico`, `ProductoDigital`).

Si no se cumple ninguna de las tres, **una función es mejor**. No empieces a "convertir todo a clases" porque sí.

### 4.2. La clase mínima

```python
class Producto:
    def __init__(self, nombre: str, precio: float, stock: int) -> None:
        self.nombre = nombre
        self.precio = precio
        self.stock = stock

    def valor_total(self) -> float:
        return self.precio * self.stock

    def disponible(self) -> bool:
        return self.stock > 0
```

Uso:

```python
auriculares = Producto("Auriculares", 89.99, 5)
print(auriculares.nombre)               # → "Auriculares"
print(auriculares.valor_total())        # → 449.95
print(auriculares.disponible())         # → True
```

**Lo que tienes que entender:**

- `class Producto:` declara la clase.
- `__init__` es el constructor. **No lo llamas tú** — lo llama Python cuando haces `Producto(...)`.
- `self` no es una palabra reservada — es el primer parámetro de cualquier método y representa la instancia. Por convención, **siempre** se llama `self`.
- Los atributos se asignan con `self.nombre = ...` dentro de `__init__`.

### 4.3. `__repr__` y `__str__`: hacer la clase imprimible

Por defecto, imprimir una instancia da algo inútil:

```python
print(auriculares)
# <__main__.Producto object at 0x7f8b3c0a1d50>
```

Define `__repr__` para que se vuelva útil:

```python
class Producto:
    # ... __init__ y métodos
    def __repr__(self) -> str:
        return f"Producto(nombre={self.nombre!r}, precio={self.precio}, stock={self.stock})"
```

Ahora:

```python
print(auriculares)
# Producto(nombre='Auriculares', precio=89.99, stock=5)
```

**Convención:**

- `__repr__` debe devolver una representación **inequívoca** del objeto, idealmente que pudiera usarse para reconstruirlo. Lo ven los desarrolladores.
- `__str__` (opcional) devuelve la representación **legible para usuarios finales**. Si no lo defines, `str(obj)` cae a `__repr__`.

Para los proyectos del curso, definir solo `__repr__` alcanza el 90% de las veces.

### 4.4. Atributos de instancia vs atributos de clase

```python
class Producto:
    moneda = "USD"                  # ← atributo de CLASE (compartido por todas las instancias)

    def __init__(self, nombre, precio, stock):
        self.nombre = nombre        # ← atributo de INSTANCIA
        self.precio = precio
        self.stock = stock
```

```python
a = Producto("A", 10, 1)
b = Producto("B", 20, 2)

a.moneda            # → "USD"
b.moneda            # → "USD"
Producto.moneda     # → "USD"   (también accesible por la clase)

a.nombre            # → "A"
b.nombre            # → "B"
```

**Trampa clásica**: si el atributo de clase es **mutable** (una lista, un dict), todas las instancias comparten el mismo objeto:

```python
class Carrito:
    items = []                     # ❌ TODAS las instancias comparten esta lista

    def agregar(self, item):
        self.items.append(item)


a = Carrito()
b = Carrito()
a.agregar("manzana")
print(b.items)                     # → ["manzana"]   😱
```

**Regla:** los atributos de clase solo deberían usarse para **constantes** (inmutables). Cualquier dato propio de cada instancia se inicializa en `__init__`.

### 4.5. `@dataclass`: el atajo idiomático para clases-de-datos

Una **clase-de-datos** es una clase cuyo trabajo principal es **agrupar datos**. Si tu `__init__` solo asigna atributos uno a uno, estás en este caso.

Sin dataclass:

```python
class Producto:
    def __init__(self, nombre: str, precio: float, stock: int) -> None:
        self.nombre = nombre
        self.precio = precio
        self.stock = stock

    def __repr__(self) -> str:
        return f"Producto(nombre={self.nombre!r}, precio={self.precio}, stock={self.stock})"

    def __eq__(self, otro: object) -> bool:
        if not isinstance(otro, Producto):
            return NotImplemented
        return (self.nombre, self.precio, self.stock) == (otro.nombre, otro.precio, otro.stock)
```

Con dataclass:

```python
from dataclasses import dataclass

@dataclass
class Producto:
    nombre: str
    precio: float
    stock: int
```

**Eso es todo.** El decorador genera `__init__`, `__repr__` y `__eq__` automáticamente a partir de las anotaciones de tipo.

**Cuándo usarla:** siempre que tu clase sea principalmente datos. Es el patrón por defecto en Python moderno para modelos de dominio.

**Métodos extra siguen funcionando:**

```python
@dataclass
class Producto:
    nombre: str
    precio: float
    stock: int

    def valor_total(self) -> float:
        return self.precio * self.stock

    def disponible(self) -> bool:
        return self.stock > 0
```

**Defaults:**

```python
@dataclass
class Producto:
    nombre: str
    precio: float
    stock: int = 0
    moneda: str = "USD"
```

**Cuidado con defaults mutables:** misma trampa que con atributos de clase. La forma correcta es `field(default_factory=...)`:

```python
from dataclasses import dataclass, field

@dataclass
class Carrito:
    items: list[str] = field(default_factory=list)    # ✅
```

### 4.6. Herencia: lo justo y necesario

Herencia es decir "B es-un tipo de A":

```python
@dataclass
class Producto:
    nombre: str
    precio: float
    stock: int


@dataclass
class ProductoDigital(Producto):
    url_descarga: str
    stock: int = 99999    # los digitales no tienen "stock" físico
```

`ProductoDigital` hereda los tres atributos de `Producto` y agrega `url_descarga`.

**Sobreescribir métodos:**

```python
@dataclass
class ProductoDigital(Producto):
    url_descarga: str

    def disponible(self) -> bool:
        return True       # los digitales siempre están disponibles
```

`super()` invoca al método de la clase padre:

```python
class ProductoDigital(Producto):
    def __repr__(self) -> str:
        base = super().__repr__()
        return f"{base} con url={self.url_descarga!r}"
```

**Reglas para no destruir tu código con herencia:**

1. **Prefiere composición sobre herencia.** Si una clase puede tener un atributo del tipo en lugar de heredar, hazlo. Es más flexible y más fácil de testear.
2. **Una sola jerarquía por concepto.** Que `Producto → ProductoDigital` exista no significa que tengas que crear `ProductoConDescuento → ProductoConDescuentoNavidad`. Es un olor a problema.
3. **Profundidad máxima razonable: 2.** Si la jerarquía tiene tres o más niveles, casi siempre el diseño es incorrecto.
4. **No uses herencia para reutilizar código.** Úsala para modelar relaciones "es-un" reales del dominio.

### 4.7. Métodos especiales útiles

Python expone su comportamiento mediante "dunder methods" (double-underscore). Los más usados después de `__init__` y `__repr__`:

| Método | Para qué |
|---|---|
| `__eq__(self, otro)` | Igualdad: `a == b`. Dataclass lo genera. |
| `__hash__(self)` | Permite usar la instancia como clave de dict o elemento de set. Dataclass lo genera si declaras `frozen=True`. |
| `__lt__(self, otro)` | "Menor que": permite ordenar con `sorted()`. |
| `__len__(self)` | Lo que devuelve `len(obj)`. Útil en colecciones propias. |

**Ejemplo: ordenar productos por precio.**

Sin definir `__lt__`:

```python
sorted(productos, key=lambda p: p.precio)    # ✅ sigue siendo lo más limpio
```

Con `__lt__`:

```python
@dataclass(order=True)         # genera __lt__, __le__, __gt__, __ge__
class Producto:
    precio: float              # primer campo declarado = primer criterio de orden
    nombre: str
    stock: int
```

```python
sorted(productos)              # ya ordena por precio sin lambda
```

Para el integrador del curso, `key=lambda` es suficiente y más explícito. Las clases ordenables son útiles en colecciones internas grandes.

### 4.8. Inmutabilidad: `frozen=True`

```python
@dataclass(frozen=True)
class Punto:
    x: float
    y: float

p = Punto(1.0, 2.0)
p.x = 99             # ❌ FrozenInstanceError
```

**Cuándo usarla:**

- Modelos de **valor** (algo definido por sus campos: una `Direccion`, una `Moneda`, un `Punto`). Si dos instancias tienen los mismos datos, deberían ser intercambiables.
- Cuando quieras usar la instancia como **clave de dict** o elemento de **set** (la inmutabilidad permite que sea hasheable).
- En todo lo que cruza fronteras concurrentes (threading, async) — sin mutación, no hay carreras.

### 4.9. Cuándo NO usar OOP (la sección que la mayoría de cursos omite)

**Antipatrón #1: la clase utility con métodos estáticos.**

```python
class StringUtils:
    @staticmethod
    def normalizar(s: str) -> str: ...
    @staticmethod
    def es_email(s: str) -> bool: ...
```

Eso no es OOP. Es un módulo disfrazado. Borra la clase y déjalas como funciones en `string_utils.py`. Más legible, más Pythonic.

**Antipatrón #2: la clase que es solo datos (sin comportamiento).**

```python
class Direccion:
    def __init__(self, calle, ciudad, codigo_postal):
        self.calle = calle
        self.ciudad = ciudad
        self.codigo_postal = codigo_postal
```

Si no hay métodos, usa `@dataclass`. Si ni siquiera vas a usar igualdad o repr, considera `dict` o `tuple`.

**Antipatrón #3: la jerarquía profunda que modela "tipos de cosas".**

```python
Animal
 ├── Mamifero
 │    ├── Perro
 │    │    ├── PerroGrande
 │    │    └── PerroPequeño
```

Los ejemplos canónicos de OOP son tóxicos. Modelar "tipos de cosas" con herencia profunda casi siempre se rompe ante el primer cambio de requisitos. **Prefiere composición**: un `Animal` que tiene un `tipo`, un `tamaño`, un `comportamiento`.

**Antipatrón #4: god class.**

Una clase con 30 atributos y 50 métodos que "maneja todo". Eso no es OOP — es un archivo monolítico mal disfrazado. Cuando sientas que tu clase crece sin parar, **divídela**: probablemente representa dos o tres conceptos distintos.

## 5. Patrones y antipatrones

| ✅ Patrón | ❌ Antipatrón |
|---|---|
| `@dataclass` para clases-de-datos | `__init__` manual con 7 asignaciones idénticas |
| `frozen=True` para tipos de valor | Modelos de valor mutables que viven en sets/dicts |
| Función pura cuando alcanza | Convertir todo a clase "porque OOP" |
| Composición (atributo del tipo) | Herencia para "reutilizar" código |
| Profundidad máxima 2 niveles | Jerarquías de 4+ niveles |
| `key=lambda` para ordenar | `@dataclass(order=True)` cuando solo ordenas en un lugar |
| Lanzar excepción de dominio en setters/métodos | Asignaciones silenciosas que dejan el objeto en estado inválido |
| `@staticmethod` solo si está semánticamente atado a la clase | "Utility class" como reemplazo de un módulo |

## 6. Conexión con el proyecto integrador — Camino al hito M2

Hasta ahora el integrador maneja productos como `dict[str, Any]`. Hoy migra a:

```python
@dataclass(frozen=True)
class Producto:
    sku: str
    nombre: str
    precio: float
    stock: int
    moneda: str = "USD"

    def disponible(self) -> bool:
        return self.stock > 0
```

`catalogo.py` cambia el tipo: ahora trabaja con `list[Producto]`. La validación que hace al cargar el JSON construye `Producto` y lanza `CatalogoInvalido` si los datos no encajan. `presentacion.py` recibe `list[Producto]` y usa los atributos tipados.

`Cliente` también pasa a ser un `@dataclass`, aunque por ahora es solo un placeholder — en M4 se conecta con la base de datos.

Esto NO cierra el hito M2 todavía. La S09 agrega context managers y generadores, y al final de S09 hacemos el commit final + tag.

## 7. Resumen

1. **OOP es para datos + comportamiento que viven juntos.** Si no hay invariantes, ni varias funciones operando sobre lo mismo, ni "tipos" del concepto, una función pura suele ser mejor.
2. **`@dataclass` es el constructor idiomático.** No escribas `__init__` a mano para clases que solo agrupan datos.
3. **`__repr__` siempre vale la pena.** Hace tu código depurable.
4. **Atributos mutables van en `__init__` o con `field(default_factory=...)`.** Nunca como defaults sueltos.
5. **Herencia es-un, no para-reutilizar.** Profundidad máxima 2. Prefiere composición.
6. **`frozen=True` para tipos de valor.** Inmutabilidad simplifica todo.
7. **Las "utility classes" no son OOP.** Son módulos disfrazados.

## 8. Preguntas de auto-evaluación

1. ¿Qué hace exactamente `__init__` y por qué nunca lo llamas tú directamente?
2. ¿Qué es `self` y por qué siempre se pone como primer parámetro de los métodos?
3. Diferencia entre **atributo de instancia** y **atributo de clase**. Da un ejemplo de cuándo el segundo se vuelve un bug.
4. ¿Qué tres dunder methods escribe `@dataclass` por ti? ¿Cuál de ellos es el que te ahorra más trabajo en la práctica?
5. Tienes `@dataclass class Pedido: items: list = []`. ¿Por qué es un bug? ¿Cómo se arregla?
6. ¿Cuál es la diferencia entre `__repr__` y `__str__`? Si solo vas a definir uno, ¿cuál?
7. ¿Cuándo usarías `frozen=True`? Da dos casos concretos.
8. Da un ejemplo de "clase que no debería ser clase" (los antipatrones de la sección 4.9).
9. Tienes tres clases: `Producto`, `ProductoDigital(Producto)`, `Libro(ProductoDigital)`. ¿Es razonable esa jerarquía? ¿Qué señal te hace dudar?
10. Diseña con dataclasses un modelo mínimo para una **Reserva de hotel**: con qué campos, cuáles son inmutables, qué método incluirías.

Cuando puedas responder todas, pasa a [`ejercicios.md`](ejercicios.md).

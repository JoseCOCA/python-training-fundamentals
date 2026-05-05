# S03 — Estructuras de datos: list, tuple, dict, set

> **Sesión 2h.** ~50 min lectura + ~70 min ejercicios. Las cuatro estructuras de datos que vas a usar todos los días el resto de tu carrera.

---

## 1. Objetivos de aprendizaje

Al terminar esta sesión vas a:

- Conocer las **cuatro estructuras de datos primarias** de Python: `list`, `tuple`, `dict`, `set`.
- Saber cuándo usar cada una — la decisión entre ellas casi nunca es de gusto.
- Entender la **mutabilidad** y por qué dos variables pueden modificarse "mágicamente" la una a la otra.
- Conocer las operaciones comunes (indexar, insertar, borrar, ordenar, buscar, contar).
- Internalizar la complejidad: por qué buscar en un `set` es 1000x más rápido que buscar en una `list` cuando la lista es grande.

## 2. Prerequisitos

- [S01](../sesion-01-variables-tipos/README.md) y [S02](../sesion-02-control-flujo/README.md) completas.
- En particular, dominio de `for` y comprensiones.

## 3. Conceptos clave

1. **Mutable vs inmutable.** Mutable = se puede modificar después de crearlo (`list`, `dict`, `set`). Inmutable = no se puede modificar (`tuple`, `str`, `int`, `float`, `bool`). Saber cuál es cuál te evita los bugs más frustrantes del lenguaje.
2. **Referencia vs valor.** Cuando asignas `b = a` y `a` es mutable, **`b` y `a` apuntan al mismo objeto**. Modificar uno modifica el otro. Es el modelo correcto de variables que vimos en S01 — ahora se vuelve crítico.
3. **Hashable.** Un objeto es hashable si Python puede calcularle un "número identificador" estable. **Solo los hashables pueden ser claves de un dict o elementos de un set.** Los inmutables son hashables; los mutables no.
4. **Ordenado vs no ordenado.** `list` y `tuple` mantienen orden. `dict` mantiene orden de inserción desde Python 3.7+. `set` NO tiene orden — no esperes que `print(set)` te dé los elementos en el orden que los pusiste.
5. **Complejidad.** Buscar un elemento en una `list` de 1 millón toma ~1 millón de operaciones. En un `set` o `dict`, toma ~1. La estructura que eliges importa al rendimiento.

## 4. Teoría

### 4.1. `list` — colección ordenada y mutable

```python
productos = ["auriculares", "teclado", "monitor"]

# Indexar
productos[0]              # → "auriculares"
productos[-1]             # → "monitor" (último, índice negativo)

# Slicing
productos[0:2]            # → ["auriculares", "teclado"]
productos[:2]             # → ["auriculares", "teclado"]
productos[1:]             # → ["teclado", "monitor"]

# Modificar
productos[1] = "ratón"
productos                 # → ["auriculares", "ratón", "monitor"]

# Agregar y quitar
productos.append("tablet")        # al final
productos.insert(0, "monitor 2")  # en posición específica
productos.pop()                   # quita el último y lo devuelve
productos.pop(0)                  # quita el de índice 0 y lo devuelve
productos.remove("ratón")         # quita la primera ocurrencia
del productos[0]                  # quita por índice

# Búsqueda y conteo
"teclado" in productos    # → True/False
productos.index("monitor")  # → posición (lanza ValueError si no está)
productos.count("teclado")  # → cuántas veces aparece

# Longitud
len(productos)            # → 3

# Ordenar
productos.sort()                       # in-place, alfabético
sorted(productos)                       # devuelve nueva lista, no modifica
sorted(productos, reverse=True)         # descendente
sorted(productos, key=len)              # por longitud
```

**Cuándo usar `list`:** secuencia ordenada de elementos donde el orden importa y vas a modificar la colección.

### 4.2. `tuple` — colección ordenada e inmutable

```python
coordenadas = (10.5, 20.3)
producto = ("auriculares", 89.99, 5)

coordenadas[0]            # → 10.5

# Esto FALLA
# coordenadas[0] = 99    → TypeError: 'tuple' object does not support item assignment

# Tuplas se pueden desempaquetar
nombre, precio, stock = producto
print(nombre)             # → "auriculares"
```

**Cuándo usar `tuple`:**

- Cuando los datos son **fijos** (no se modifican): coordenadas, fecha (año, mes, día), config inmutable.
- Cuando necesitas usarlo como **clave de dict** o elemento de **set** (las listas no son hashables, las tuplas sí).
- Cuando una función devuelve **múltiples valores** (es la convención).

```python
def dimensiones():
    return 1920, 1080      # técnicamente devuelve una tupla

ancho, alto = dimensiones()
```

### 4.3. `dict` — pares clave-valor, mutable

```python
producto = {
    "nombre": "auriculares",
    "precio": 89.99,
    "stock": 5,
    "categoria": "audio",
}

# Acceder por clave
producto["nombre"]        # → "auriculares"
producto["sin_clave"]     # → KeyError

# Forma segura
producto.get("sin_clave")              # → None (no error)
producto.get("sin_clave", "default")   # → "default" si no existe

# Modificar
producto["stock"] = 4                  # actualizar
producto["disponible"] = True          # agregar nueva clave

# Quitar
del producto["categoria"]
producto.pop("disponible")

# Iterar
for clave in producto:                 # itera sobre las claves
    print(clave, producto[clave])

for clave, valor in producto.items():  # idiomático: clave y valor a la vez
    print(f"{clave}: {valor}")

for valor in producto.values():        # solo valores
    print(valor)

# Verificar existencia
"precio" in producto                   # → True

# Longitud
len(producto)                          # → cuántas claves
```

**Cuándo usar `dict`:**

- Mapeo nombre → valor: catálogo de productos por código, configuración, conteos.
- Cuando necesitas **acceso rápido por clave** (~O(1) sin importar cuántos elementos).
- Cuando los datos tienen estructura fija: el "objeto" del lenguaje hasta que lleguemos a clases en M2.

### 4.4. `set` — colección sin duplicados, sin orden

```python
categorias = {"audio", "video", "computación", "audio"}
print(categorias)         # → {"audio", "video", "computación"}  (sin duplicados)

# Operaciones
categorias.add("oficina")
categorias.remove("audio")            # error si no está
categorias.discard("ausente")         # silencioso si no está

# Pertenencia (la más importante — muy rápida)
"audio" in categorias                 # → True/False (~O(1))

# Operaciones de conjunto
a = {1, 2, 3}
b = {2, 3, 4}
a | b                     # unión: {1, 2, 3, 4}
a & b                     # intersección: {2, 3}
a - b                     # diferencia: {1}
a ^ b                     # diferencia simétrica: {1, 4}
```

**Cuándo usar `set`:**

- Quitar duplicados: `set(lista)` te deja solo elementos únicos.
- Verificar pertenencia rápidamente: `if elemento in set` es ~1000x más rápido que `if elemento in lista` cuando la colección es grande.
- Operaciones de conjunto matemáticas (unión, intersección).

### 4.5. Mutabilidad: el gotcha que más bugs genera en Python

Volvamos al modelo de "variable como vínculo" que vimos en S01.

```python
a = [1, 2, 3]
b = a                # b apunta al MISMO objeto que a

b.append(4)
print(a)             # → [1, 2, 3, 4]   ← ¡a también cambió!
print(b)             # → [1, 2, 3, 4]
```

**¿Por qué?** Porque `b = a` no copia la lista. Solo crea otro nombre que apunta al mismo objeto en memoria. Cuando modificas vía `b`, también modificas vía `a` — son **el mismo objeto**.

**Cómo copiar de verdad:**

```python
b = a.copy()                  # copia "shallow" — funciona si la lista es de inmutables
b = list(a)                   # equivalente
b = a[:]                      # también, slice completo

import copy
b = copy.deepcopy(a)          # copia "deep" — copia también objetos anidados
```

Esto NO pasa con inmutables. Como no se pueden modificar:

```python
a = 5
b = a
b = 10                # solo cambia a qué apunta b, no toca el 5 original
print(a)              # → 5
```

Por eso preferimos inmutables cuando podemos — son inmunes a este bug.

### 4.6. Hashable y por qué importa

Los `dict` y `set` necesitan calcular un "hash" de cada elemento (un número identificador) para guardarlos. Solo los **inmutables son hashables**.

```python
# Funciona
config = {("usuario", "rol"): "admin"}

# FALLA
# config = {["usuario", "rol"]: "admin"}    # TypeError: unhashable type: 'list'
```

Esto explica por qué las claves de un `dict` suelen ser `str`, `int`, `tuple` (todos inmutables). No puedes usar una `list` o un `dict` como clave.

### 4.7. Cuándo usar cada una — guía rápida

| Necesidad | Estructura | Por qué |
|---|---|---|
| Lista de cosas que vas a modificar | `list` | mutable, ordenada |
| Lista de cosas fijas | `tuple` | inmutable, hashable |
| Mapeo nombre → valor con búsqueda rápida | `dict` | O(1) por clave |
| Solo te interesa "está o no está" | `set` | O(1) en pertenencia, sin duplicados |
| Coordenadas, fechas, config | `tuple` | el agrupamiento natural de cosas que van juntas y no cambian |
| Conteo de ocurrencias | `dict` | clave = elemento, valor = cuenta. (También existe `collections.Counter`.) |
| Quitar duplicados de una lista | `set` | conversión `set(lista)` |

## 5. Patrones y antipatrones

| ✅ Patrón | ❌ Antipatrón |
|---|---|
| `for clave, valor in d.items():` | `for clave in d: ...d[clave]...` (más lento, menos legible) |
| `if x in set:` cuando vas a buscar muchas veces | `if x in lista:` con lista grande |
| `d.get("clave", default)` | `d["clave"]` con `try/except KeyError` |
| `tuple` para datos fijos | `list` que nadie debería modificar |
| `[item.copy() for item in lista]` (cuando hace falta) | `b = a` y luego sorprenderte cuando ambos cambian |
| `set(lista)` para quitar duplicados | bucle con `if x not in resultado: resultado.append(x)` |
| `sorted(items, key=...)` | escribir tu propio bubble sort |

## 6. Conexión con el proyecto integrador

El catálogo de TiendaPro Lite va a ser una **lista de diccionarios**:

```python
catalogo = [
    {"nombre": "auriculares", "precio": 89.99, "stock": 5, "categoria": "audio"},
    {"nombre": "teclado", "precio": 49.50, "stock": 12, "categoria": "computación"},
    ...
]
```

Vas a recorrerlo, filtrarlo, ordenarlo. Cada producto es un `dict`; la colección entera es una `list`. En M3 vamos a tipar estos diccionarios con pydantic, pero por ahora — esta es la forma natural en Python.

## 7. Resumen

1. **Cuatro estructuras, cuatro casos de uso.** `list` para secuencias mutables, `tuple` para fijas, `dict` para mapeos, `set` para pertenencia rápida y unicidad.
2. **Mutabilidad importa.** Mutables (`list`, `dict`, `set`) pueden modificarse y comparten identidad cuando asignas. Inmutables (`tuple`, `str`, `int`) son seguros pero requieren crear nuevos objetos para "modificar".
3. **`set` y `dict` buscan en O(1).** `list` busca en O(n). Si vas a hacer muchas búsquedas, usa la estructura correcta.

## 8. Preguntas de auto-evaluación

1. Tienes `a = [1, 2, 3]` y `b = a`. Ejecutas `b.append(4)`. ¿Cuál es el contenido de `a`? ¿Por qué?
2. ¿Por qué no puedes usar una `list` como clave de un `dict` pero sí una `tuple`?
3. Tienes una lista de 1 millón de strings y necesitas verificar si una palabra está. ¿Mejor usar `list` o `set`? ¿Cuánto cambia el tiempo?
4. Explica la diferencia entre `d["clave"]` y `d.get("clave")`.
5. ¿Cómo quitas duplicados de una lista preservando el tipo `list`? Da una línea de código.
6. Una función devuelve `(precio, stock)`. ¿Qué tipo es eso? ¿Cómo desempaquetas el resultado en dos variables?

Cuando puedas responder todas, pasa a [`ejercicios.md`](ejercicios.md).

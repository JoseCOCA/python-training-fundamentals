# S02 — Control de flujo: if, while, for y comprensiones

> **Sesión 2h.** ~45 min lectura + ~75 min ejercicios. La sesión donde tu código deja de ser una secuencia lineal y empieza a **decidir** y **repetir**.

---

## 1. Objetivos de aprendizaje

Al terminar esta sesión vas a:

- Escribir condicionales correctamente — `if`, `elif`, `else`.
- Conocer las dos formas de iterar: `while` (mientras se cumpla algo) y `for` (sobre una colección).
- Saber cuándo usar `break`, `continue`, y la cláusula `else` de los bucles (sí, los bucles tienen `else`).
- Entender el concepto de **truthiness** y por qué `if cantidad:` es preferible a `if cantidad > 0:` en muchos casos.
- Escribir tu primera **list comprehension** y entender cuándo usarla y cuándo NO.

## 2. Prerequisitos

- [S01 — Variables, tipos primitivos y expresiones](../sesion-01-variables-tipos/README.md) completa, incluidos los ejercicios.
- En particular, dominio de operadores de comparación (`<`, `==`, etc.) y booleanos (`and`, `or`, `not`).

## 3. Conceptos clave

1. **Indentación como sintaxis.** En Python, los bloques se delimitan con sangría, no con llaves `{}`. Cuatro espacios es la convención. Mezclar tabs y espacios es ilegal.
2. **Truthiness.** En un contexto booleano, casi cualquier valor cuenta como `True` o `False`. Saber qué valores son "falsy" te ahorra mucho código.
3. **`while` vs `for`.** `while` repite mientras una condición sea verdadera (puede ser infinito). `for` recorre una colección finita. **Por defecto siempre usa `for`** — es más seguro.
4. **`break` y `continue`.** `break` sale del bucle. `continue` salta a la siguiente iteración. Ambos son señales de que tu lógica tal vez necesita revisión, pero son útiles cuando se usan bien.
5. **Comprensiones.** Forma idiomática de Python para construir listas, diccionarios y sets a partir de iteraciones. Cuando se usa bien, es más legible que un `for` tradicional. Cuando se abusa, es ilegible.

## 4. Teoría

### 4.1. Indentación: la sintaxis del control de flujo

En Python, los bloques de código se definen por **sangría**, no por llaves `{}`. Esto:

```python
if precio > 100:
    print("caro")
    print("descuento del 10%")
print("siempre se imprime")
```

Las dos líneas indentadas pertenecen al `if`. La tercera no — está fuera del bloque.

**Convención:** 4 espacios por nivel. **Nunca mezcles tabs y espacios** — Python te da error. VS Code con la extensión Python configurada respeta esto automáticamente.

### 4.2. `if`, `elif`, `else`

```python
edad = 18

if edad < 13:
    categoria = "niño"
elif edad < 18:
    categoria = "adolescente"
elif edad < 65:
    categoria = "adulto"
else:
    categoria = "adulto mayor"

print(categoria)  # → adulto
```

- `if` empieza la cadena.
- `elif` ("else if") es opcional, puedes tener cero, uno o muchos.
- `else` es opcional. Solo uno al final.
- Python evalúa **de arriba hacia abajo** y entra en el primer bloque cuya condición sea verdadera.

**Anti-patrón clásico:** `if` anidados profundos. Si tienes 4 niveles de `if` adentro de `if`, casi siempre lo puedes aplanar:

```python
# ❌ Mal
if usuario is not None:
    if usuario.es_premium:
        if usuario.saldo > 0:
            procesar_pago(usuario)

# ✅ Mejor (early return)
if usuario is None:
    return
if not usuario.es_premium:
    return
if usuario.saldo <= 0:
    return
procesar_pago(usuario)
```

(El `return` lo vemos en S04 — por ahora basta con que entiendas el patrón.)

### 4.3. Truthiness — qué cuenta como `True` y como `False`

Cuando Python evalúa un valor en un contexto booleano (dentro de `if`, `while`, etc.), aplica reglas de **truthiness**.

**Valores "falsy" (cuentan como `False`):**

```python
False
None
0           # int cero
0.0         # float cero
""          # str vacío
[]          # lista vacía (S03)
{}          # dict vacío (S03)
set()       # set vacío (S03)
```

**Todo lo demás es "truthy".**

Esto te permite escribir más conciso:

```python
nombre = ""

# ❌ Verboso
if nombre == "":
    print("nombre vacío")

# ✅ Idiomático
if not nombre:
    print("nombre vacío")
```

```python
items_carrito = []

# ❌ Verboso
if len(items_carrito) == 0:
    print("carrito vacío")

# ✅ Idiomático
if not items_carrito:
    print("carrito vacío")
```

**Cuidado** — el corolario de truthiness es que `if cantidad:` es `False` cuando `cantidad == 0`. Si necesitas distinguir "no hay valor" (`None`) de "valor cero" (`0`), usa `is None` explícito:

```python
descuento = 0

if descuento:                # ❌ entra solo si descuento != 0
    aplicar(descuento)

if descuento is not None:    # ✅ entra incluso si descuento == 0
    aplicar(descuento)
```

### 4.4. `while`

Repite mientras la condición sea verdadera.

```python
contador = 0
while contador < 3:
    print(f"iteración {contador}")
    contador += 1
```

**Riesgo:** si la condición nunca se vuelve `False`, tienes un bucle infinito. Ctrl+C te salva.

**Cuándo usar `while`:** cuando no sabes de antemano cuántas iteraciones vas a hacer. Por ejemplo: "leer del usuario hasta que escriba 'salir'".

```python
respuesta = ""
while respuesta != "salir":
    respuesta = input("¿qué haces? ")
```

**Cuándo NO usar `while`:** cuando quieres iterar sobre una colección. Para eso está `for`.

### 4.5. `for` con `range()`

`range(n)` genera números de 0 a n-1.

```python
for i in range(5):
    print(i)
# 0
# 1
# 2
# 3
# 4
```

Variantes:

```python
range(2, 5)         # 2, 3, 4
range(0, 10, 2)     # 0, 2, 4, 6, 8 (saltos de 2)
range(10, 0, -1)    # 10, 9, 8, ... 1 (al revés)
```

### 4.6. `for` sobre cualquier iterable

Esta es la forma más común de `for` en Python — recorrer los elementos de una colección.

```python
productos = ["auriculares", "teclado", "monitor"]

for producto in productos:
    print(f"- {producto}")
```

Funciona sobre listas, tuplas, strings, diccionarios, sets, archivos, generadores. Todo lo que sea **iterable**.

**Iterar con índice (`enumerate`):**

```python
for i, producto in enumerate(productos):
    print(f"{i}: {producto}")
# 0: auriculares
# 1: teclado
# 2: monitor
```

**Iterar dos colecciones a la vez (`zip`):**

```python
nombres = ["Carolina", "Marco"]
edades = [28, 34]

for nombre, edad in zip(nombres, edades):
    print(f"{nombre} tiene {edad} años")
```

### 4.7. `break`, `continue` y `else` en bucles

```python
for numero in range(10):
    if numero == 5:
        break              # sale del bucle
    print(numero)
# 0, 1, 2, 3, 4
```

```python
for numero in range(10):
    if numero % 2 == 0:
        continue           # salta a la siguiente iteración
    print(numero)
# 1, 3, 5, 7, 9
```

**`else` en bucles** (poco conocido pero útil): se ejecuta si el bucle terminó **sin** un `break`.

```python
for producto in productos:
    if producto == "auriculares":
        print("¡encontrado!")
        break
else:
    print("no se encontró")
```

Si el bucle encuentra "auriculares", hace `break` y NO entra en el `else`. Si recorre toda la lista sin `break`, sí entra en el `else`. Útil para búsquedas.

### 4.8. Comprensiones de lista

Una de las formas más Pythónicas de construir colecciones.

**Versión `for` tradicional:**

```python
precios = [10, 20, 30]
con_iva = []
for precio in precios:
    con_iva.append(precio * 1.21)
# con_iva == [12.1, 24.2, 36.3]
```

**Versión comprensión:**

```python
con_iva = [precio * 1.21 for precio in precios]
# con_iva == [12.1, 24.2, 36.3]
```

Más corto, más declarativo. Lees: "una lista de `precio * 1.21` para cada `precio` en `precios`".

**Con filtro:**

```python
caros = [p for p in precios if p > 15]
# caros == [20, 30]
```

**Comprensión de dict:**

```python
productos = ["auriculares", "teclado"]
precios = [89.99, 49.50]

catalogo = {nombre: precio for nombre, precio in zip(productos, precios)}
# catalogo == {"auriculares": 89.99, "teclado": 49.50}
```

**Cuándo NO usar comprensiones:**

- Cuando el cuerpo es complejo (varias líneas).
- Cuando necesitas efectos secundarios (`print`, escribir a archivo).
- Cuando hay condicionales anidados que vuelven la línea ilegible.

Regla: si tu compañero no la entiende en 5 segundos, escríbela como `for` normal.

## 5. Patrones y antipatrones

| ✅ Patrón | ❌ Antipatrón |
|---|---|
| `for` sobre colección directamente | `for i in range(len(lista)):` (cuando puedes usar `for x in lista`) |
| `enumerate(lista)` para índice + valor | Llevar un contador manual |
| `if not lista:` para "lista vacía" | `if len(lista) == 0:` |
| Early return / aplanar `if` anidados | 4 niveles de `if` indentados |
| Comprensión simple para transformar/filtrar | Comprensión de 3 líneas con condicionales anidados |
| `while True:` con `break` cuando lo veas claro | `while True:` infinito sin condición de salida |
| `is None` / `is not None` | `== None` / `!= None` |

## 6. Conexión con el proyecto integrador

Al cerrar M1 (en S05) vas a leer un JSON con productos y mostrarlos. Para eso necesitas:

- Recorrer la lista de productos (`for producto in productos`).
- Decidir qué mostrar y qué filtrar (`if producto["stock"] > 0`).
- Ordenar por precio (vamos a usar `sorted()` con `key`, lo veremos en S03).

Toda la lógica de "iterar y decidir" la cubre esta sesión.

## 7. Resumen

1. **Indentación es sintaxis.** 4 espacios. No mezcles con tabs.
2. **Por defecto usa `for`, no `while`.** `for` itera sobre algo finito; `while` puede colgarse.
3. **Truthiness** te deja escribir condiciones más cortas y declarativas. Pero `0` es falsy — usa `is None` cuando necesites distinguir "ausente" de "cero".
4. **Comprensiones** son la forma idiomática de transformar/filtrar colecciones. Una línea, declarativa, legible — si no, vuelve al `for` tradicional.

## 8. Preguntas de auto-evaluación

1. ¿Cuál es la diferencia entre `if x:` y `if x is not None:` cuando `x` puede ser `0`?
2. Lista los 7 valores "falsy" en Python.
3. ¿Cuándo usarías `while` en lugar de `for`?
4. ¿Qué hace la cláusula `else` de un `for`? Da un ejemplo donde sea útil.
5. Escribe una comprensión que tome una lista de precios y devuelva otra solo con los precios mayores a 50.
6. ¿Por qué es preferible `for x in lista:` a `for i in range(len(lista)):`?

Cuando puedas responder todas, pasa a [`ejercicios.md`](ejercicios.md).

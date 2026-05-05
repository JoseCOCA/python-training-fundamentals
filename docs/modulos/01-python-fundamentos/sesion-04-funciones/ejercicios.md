# S04 — Ejercicios

Practica creando y llamando funciones. Crea un archivo `.py` por ejercicio o agrupa varios.

---

## Ejercicio 1 — Tu primera función (5 min)

```python
def saludar(nombre):
    return f"Hola, {nombre}!"

print(saludar("Carolina"))
print(saludar("Marco"))
```

**Modificación:** que la función acepte un segundo parámetro `idioma` (default `"es"`) y devuelva el saludo en español o inglés según el valor.

```python
saludar("Carolina")              # → "Hola, Carolina!"
saludar("Marco", idioma="en")    # → "Hello, Marco!"
```

---

## Ejercicio 2 — Refactorizar a función pura (10 min)

Aquí tienes un script con todo en línea recta. Refactorízalo en al menos 3 funciones:

```python
precio = 89.99
cantidad = 3
descuento = 0.15

subtotal = precio * cantidad
descuento_total = subtotal * descuento
total = subtotal - descuento_total

print(f"Subtotal: ${subtotal:.2f}")
print(f"Descuento: -${descuento_total:.2f}")
print(f"Total: ${total:.2f}")
```

Sugerencias de funciones:
- `calcular_subtotal(precio, cantidad) -> float`
- `aplicar_descuento(subtotal, porcentaje) -> float`
- `imprimir_resumen(subtotal, descuento, total) -> None`

Después usa esas funciones en el bloque principal del script.

---

## Ejercicio 3 — Múltiples retornos con tupla (10 min)

Escribe `dividir_con_resto(dividendo, divisor)` que devuelva una tupla `(cociente, resto)`.

```python
def dividir_con_resto(dividendo, divisor):
    # tu código
    ...

c, r = dividir_con_resto(17, 5)
print(f"17 / 5 = {c} con resto {r}")    # 17 / 5 = 3 con resto 2
```

**Pista:** los operadores `//` y `%` que vimos en S01.

---

## Ejercicio 4 — El gotcha de mutable default (10 min)

Ejecuta tal cual y observa:

```python
def agregar_a_lista(item, lista=[]):
    lista.append(item)
    return lista

print(agregar_a_lista("a"))
print(agregar_a_lista("b"))
print(agregar_a_lista("c"))
```

**Pregunta:** ¿qué imprime la tercera llamada? ¿Por qué?

Ahora arregla la función con el patrón `default=None`:

```python
def agregar_a_lista(item, lista=None):
    # tu código
    ...

print(agregar_a_lista("a"))
print(agregar_a_lista("b"))
print(agregar_a_lista("c"))
```

Verifica que ahora cada llamada empieza con una lista vacía nueva.

---

## Ejercicio 5 — Argumentos por nombre y default (10 min)

Escribe `crear_producto(nombre, precio, stock=0, categoria="general", disponible=True)`. Llámala de tres formas distintas:

1. Solo con los obligatorios.
2. Mezclando posicionales y por nombre.
3. Cambiando solo `disponible` sin tocar los del medio.

```python
def crear_producto(nombre, precio, stock=0, categoria="general", disponible=True):
    return {
        "nombre": nombre,
        "precio": precio,
        "stock": stock,
        "categoria": categoria,
        "disponible": disponible,
    }

# 1
crear_producto("auriculares", 89.99)

# 2
crear_producto("teclado", 49.50, categoria="computación")

# 3
crear_producto("monitor", 320.00, disponible=False)

# imprime los tres
```

---

## Ejercicio 6 — `*args` para promedio (5 min)

```python
def promedio(*numeros):
    if not numeros:
        return 0.0
    return sum(numeros) / len(numeros)

print(promedio(10, 20, 30))            # → 20.0
print(promedio(5))                      # → 5.0
print(promedio())                       # → 0.0
```

**Modificación:** que también acepte una lista directamente:

```python
print(promedio(10, 20, 30))             # con argumentos sueltos
print(promedio(*[10, 20, 30]))          # con lista expandida (operador *)
```

(`*lista` "desempaqueta" la lista en argumentos sueltos al llamar.)

---

## Ejercicio 7 — Scope y `global` (10 min)

Predice qué imprime cada caso ANTES de ejecutar. Después, ejecuta y verifica:

```python
contador = 0

def incrementar_sin_global():
    contador = contador + 1     # ¿qué pasa aquí?

# ¿qué pasa al llamar?
# incrementar_sin_global()
```

Después prueba la versión correcta:

```python
contador = 0

def incrementar_con_global():
    global contador
    contador += 1

incrementar_con_global()
incrementar_con_global()
print(contador)      # ¿qué imprime?
```

**Pregunta para reflexionar:** ¿por qué `global` está mal visto como práctica? ¿Cómo lo evitarías?

---

## Reto opcional — Mini gestor de catálogo (20 min)

Escribe un script con estas cuatro funciones puras:

```python
def crear_producto(nombre, precio, stock=0):
    """Devuelve un dict con los datos del producto."""
    ...

def aplicar_descuento(producto, porcentaje):
    """Devuelve una COPIA del producto con el precio descontado.
    NO modifica el producto original.
    """
    ...

def filtrar_en_stock(catalogo):
    """Devuelve nueva lista solo con productos con stock > 0."""
    ...

def total_inventario(catalogo):
    """Suma precio*stock de todos los productos. Devuelve float."""
    ...

# usa las cuatro funciones para construir un catálogo, aplicar descuentos
# a algunos, filtrar y calcular el inventario total. Imprime cada paso.
```

**Restricciones:**
- Las funciones tienen que ser puras (no modificar nada externo, no modificar el catálogo recibido).
- Usa docstrings.
- Verifica que el catálogo original no cambia después de aplicar descuentos.

---

## Aporte al proyecto integrador

S04 todavía no agrega código directamente al integrador. El hito M1 viene en S05.

---

## Antes de pasar a S05

- ✅ Hiciste los ejercicios 1-7.
- ✅ Entiendes el gotcha de mutable defaults y la solución `None` + sentinel.
- ✅ Sabes la diferencia entre función pura y con efectos secundarios.

Si los tres están listos, sigue con [S05 — Strings](../sesion-05-strings/README.md).

# S03 — Ejercicios

Practica en tu computadora. Para todos los ejercicios crea archivos `.py` y ejecútalos con `uv run python archivo.py`, o usa el REPL.

---

## Ejercicio 1 — list operations (10 min)

Crea `lista_productos.py` y replica esta secuencia exactamente:

```python
productos = ["auriculares", "teclado", "monitor"]

print(productos)
productos.append("ratón")
print(productos)
productos.insert(0, "tablet")
print(productos)
ultimo = productos.pop()
print(f"quité: {ultimo}")
print(productos)
productos[1] = "cámara"
print(productos)
productos.sort()
print(productos)
```

**Pregunta:** ¿qué pasaría si en vez de `productos.sort()` escribieras `nueva = sorted(productos)`?

---

## Ejercicio 2 — La trampa de la asignación (10 min)

Ejecuta este código y predice qué imprime ANTES de ejecutar:

```python
original = [1, 2, 3]
copia = original
copia.append(4)

print("original:", original)
print("copia:   ", copia)
```

¿Te sorprende? Ahora intenta hacerlo con copia real:

```python
original = [1, 2, 3]
copia = original.copy()
copia.append(4)

print("original:", original)
print("copia:   ", copia)
```

**Pregunta:** explica con tus palabras la diferencia entre `copia = original` y `copia = original.copy()`.

---

## Ejercicio 3 — Tuplas inmutables (5 min)

```python
producto = ("auriculares", 89.99, 5)

# desempaquetar
nombre, precio, stock = producto
print(f"{nombre} cuesta ${precio}, hay {stock} unidades")

# intenta modificar
try:
    producto[0] = "monitor"
except TypeError as e:
    print(f"error esperado: {e}")
```

Después intenta lo mismo con una lista:

```python
producto_lista = ["auriculares", 89.99, 5]
producto_lista[0] = "monitor"
print(producto_lista)        # ¿qué pasa aquí?
```

**Reflexiona:** ¿en qué situación preferirías tupla sobre lista?

---

## Ejercicio 4 — dict para catálogo (15 min)

Crea `catalogo.py`:

```python
producto = {
    "nombre": "auriculares",
    "precio": 89.99,
    "stock": 5,
    "categoria": "audio",
}

# 1. Imprime el nombre y el precio
print(f"{producto['nombre']}: ${producto['precio']}")

# 2. Cambia el stock a 3
producto["stock"] = 3

# 3. Agrega una clave nueva: "disponible" = True
producto["disponible"] = True

# 4. Itera sobre todas las claves y valores
for clave, valor in producto.items():
    print(f"  {clave}: {valor}")

# 5. Intenta acceder a una clave inexistente con .get()
descripcion = producto.get("descripcion", "(sin descripción)")
print(f"Descripción: {descripcion}")

# 6. Quita la clave "categoria"
del producto["categoria"]
print(producto)
```

**Reto:** modifica el script para que en vez de un solo producto, tengas una lista de 5 productos (cada uno un dict) y los imprimas todos en formato tabla.

---

## Ejercicio 5 — set para deduplicar (10 min)

```python
# 1. Quitar duplicados
emails = [
    "ana@correo.com",
    "carlos@correo.com",
    "ana@correo.com",
    "luis@correo.com",
    "carlos@correo.com",
]

unicos = set(emails)
print(f"originales: {len(emails)}")
print(f"únicos: {len(unicos)}")
print(unicos)

# 2. Operaciones de conjunto
clientes_premium = {"ana@correo.com", "carlos@correo.com"}
clientes_activos = {"carlos@correo.com", "luis@correo.com"}

print("Premium Y activos:", clientes_premium & clientes_activos)
print("Premium O activos:", clientes_premium | clientes_activos)
print("Premium pero no activos:", clientes_premium - clientes_activos)
```

**Pregunta:** ¿por qué el set imprime los emails en un orden distinto cada vez que ejecutas? ¿Puedes confiar en el orden?

---

## Ejercicio 6 — Conteo con dict (10 min)

Dada una lista de categorías, cuenta cuántas veces aparece cada una:

```python
categorias = [
    "audio", "video", "audio", "computación",
    "audio", "video", "computación", "computación",
    "audio", "oficina",
]

conteo = {}
for cat in categorias:
    if cat in conteo:
        conteo[cat] += 1
    else:
        conteo[cat] = 1

print(conteo)
# ¿qué imprime?
```

Luego haz la versión idiomática con `dict.get()`:

```python
conteo = {}
for cat in categorias:
    conteo[cat] = conteo.get(cat, 0) + 1

print(conteo)
```

**Reflexiona:** ¿cuál te parece más legible?

(Spoiler para el futuro: `from collections import Counter; Counter(categorias)` hace lo mismo en una línea.)

---

## Ejercicio 7 — Ordenar productos (10 min)

Tienes una lista de productos como dicts. Ordénalos:

```python
catalogo = [
    {"nombre": "auriculares", "precio": 89.99, "stock": 5},
    {"nombre": "teclado", "precio": 49.50, "stock": 12},
    {"nombre": "monitor", "precio": 320.00, "stock": 0},
    {"nombre": "ratón", "precio": 19.99, "stock": 30},
    {"nombre": "tablet", "precio": 450.00, "stock": 3},
]

# Por precio ascendente
por_precio = sorted(catalogo, key=lambda p: p["precio"])
for p in por_precio:
    print(f"{p['nombre']:15} ${p['precio']:>7.2f}")
```

(`lambda` es una función anónima — la cubrimos en S04. Por ahora, lee `lambda p: p["precio"]` como "una función que toma `p` y devuelve `p['precio']`".)

**Tu turno:**

1. Ordénalos por nombre alfabéticamente.
2. Ordénalos por stock descendente.
3. Filtra solo los que tienen `stock > 0` (usando comprensión).

---

## Reto opcional — Mini buscador en catálogo (15 min)

Implementa un script `buscar.py` que:

1. Tenga un catálogo de 10 productos como lista de dicts.
2. Pregunte al usuario un nombre de producto.
3. Si lo encuentra, imprima sus datos. Si no, imprima "no encontrado".
4. Pregunte al usuario una categoría.
5. Imprima TODOS los productos de esa categoría (puede haber varios).

Usa lo que aprendiste: `for`, `if`, indexar `dict`, comprensiones de lista.

---

## Aporte al proyecto integrador

S03 todavía no agrega código al integrador. El cierre de M1 viene en S05.

---

## Antes de pasar a S04

- ✅ Hiciste los ejercicios 1-7.
- ✅ Tienes el modelo correcto de mutabilidad (referencia compartida).
- ✅ Sabes cuándo elegir `list`, `tuple`, `dict`, `set`.

Si los tres están listos, sigue con [S04 — Funciones](../sesion-04-funciones/README.md).

# S02 — Ejercicios

Practica en tu computadora. Crea un archivo `.py` por ejercicio (o agrégalos al mismo) y ejecútalos con `uv run python archivo.py`.

---

## Ejercicio 1 — Categorizar precios (10 min)

Crea `categorizar.py`:

```python
precios = [10, 50, 120, 199, 350, 800]

for precio in precios:
    if precio < 50:
        categoria = "barato"
    elif precio < 200:
        categoria = "medio"
    elif precio < 500:
        categoria = "caro"
    else:
        categoria = "premium"
    print(f"${precio} → {categoria}")
```

Ejecuta y observa la salida. Después modifícalo:

1. Agrega una categoría nueva: "regalo" para precios menores a 10.
2. Cambia los rangos para que se ajusten mejor a tu intuición.
3. Pregunta para reflexionar: ¿qué pasa si dos `elif` se solapan? Prueba poner `elif precio < 100` después de `elif precio < 200`.

---

## Ejercicio 2 — Truthiness en práctica (5 min)

Predice la salida de cada `print` antes de ejecutar:

```python
valores = [0, 0.0, "", None, False, [], "0", "False", 1, "hola"]

for valor in valores:
    if valor:
        print(f"{valor!r:10} → truthy")
    else:
        print(f"{valor!r:10} → falsy")
```

¿Te sorprendió alguno? En particular, fíjate en `"0"` y `"False"` — ambos son strings no vacíos, así que ambos son truthy.

---

## Ejercicio 3 — Bucle de input con `while` (10 min)

Crea `menu_input.py`:

```python
opcion = ""

while opcion != "salir":
    print("\n--- Menú TiendaPro ---")
    print("1. Ver catálogo")
    print("2. Agregar producto")
    print("3. Salir (escribe 'salir')")
    opcion = input("Tu opción: ")

    if opcion == "1":
        print("Catálogo: auriculares, teclado, monitor")
    elif opcion == "2":
        print("(funcionalidad pendiente)")
    elif opcion == "salir":
        print("Hasta luego.")
    else:
        print("Opción no válida")
```

Ejecuta y prueba todas las ramas.

**Pregunta para reflexionar:** ¿qué pasa si el usuario nunca escribe "salir"? ¿Y si escribe `Ctrl+C`?

---

## Ejercicio 4 — `for` con `enumerate` y `zip` (10 min)

Crea `lista_compras.py`:

```python
productos = ["auriculares", "teclado", "monitor", "ratón"]
precios = [89.99, 49.50, 320.00, 19.99]
stocks = [5, 12, 0, 30]

# Versión 1 — solo enumerar
print("=== Catálogo (con índice) ===")
for i, producto in enumerate(productos):
    print(f"{i + 1}. {producto}")

# Versión 2 — combinar tres listas con zip
print("\n=== Catálogo completo ===")
for nombre, precio, stock in zip(productos, precios, stocks):
    estado = "DISPONIBLE" if stock > 0 else "AGOTADO"
    print(f"{nombre:15} ${precio:>7.2f}  stock: {stock:>3}  [{estado}]")
```

Observa la salida. La sintaxis `if/else` en una línea es un **operador ternario** — útil para asignaciones cortas, no abuses.

---

## Ejercicio 5 — `break` y `continue` (10 min)

Modifica el siguiente script para que:

1. Solo procese productos con `stock > 0` (usando `continue`).
2. Pare de procesar al encontrar el primer producto con precio mayor a 200 (usando `break`).

```python
productos = [
    {"nombre": "auriculares", "precio": 89.99, "stock": 5},
    {"nombre": "teclado", "precio": 49.50, "stock": 12},
    {"nombre": "monitor", "precio": 320.00, "stock": 3},
    {"nombre": "ratón", "precio": 19.99, "stock": 0},
    {"nombre": "tablet", "precio": 450.00, "stock": 8},
]

for p in productos:
    # ... tu código aquí
    print(f"procesando {p['nombre']} (${p['precio']})")
```

(Los diccionarios los formalizamos en S03 — por ahora basta con que veas que `p["nombre"]` te da el valor asociado a la clave `"nombre"`.)

---

## Ejercicio 6 — Tu primera comprensión (10 min)

Reescribe los siguientes bucles `for` como comprensiones de lista o diccionario.

**Caso 1 — duplicar valores:**

```python
numeros = [1, 2, 3, 4, 5]

# for tradicional
duplicados = []
for n in numeros:
    duplicados.append(n * 2)

# tu versión con comprensión:
# duplicados = ...
```

**Caso 2 — filtrar pares:**

```python
numeros = [1, 2, 3, 4, 5, 6, 7, 8]

# for tradicional
pares = []
for n in numeros:
    if n % 2 == 0:
        pares.append(n)

# tu versión:
# pares = ...
```

**Caso 3 — diccionario nombre → longitud:**

```python
nombres = ["Carolina", "Marco", "Sofia"]

# for tradicional
longitudes = {}
for nombre in nombres:
    longitudes[nombre] = len(nombre)

# tu versión con comprensión de dict:
# longitudes = ...
```

---

## Ejercicio 7 — Búsqueda con `for/else` (5 min)

Escribe un script que busque un producto por nombre en una lista. Si lo encuentra, imprime "encontrado: <precio>". Si no, imprime "no encontrado".

```python
productos = [
    ("auriculares", 89.99),
    ("teclado", 49.50),
    ("monitor", 320.00),
]
buscar = "monitor"

# usa un for sobre productos con un break cuando lo encuentres
# y un else en el bucle para el caso "no encontrado"
```

---

## Reto opcional — Validación de input (15 min)

Escribe `pedir_edad.py` que pida la edad al usuario y valide:

- Que sea un número (si no, muestra error y pide de nuevo).
- Que esté entre 0 y 130 (si no, error y pide de nuevo).
- Cuando recibe un valor válido, imprime "edad registrada: X".

Usa `while True:` con `break` cuando recibas un valor válido. Para convertir el input usa `int()` dentro de un `try/except` — si bien `try/except` lo cubrimos formalmente en S07, aquí lo introducimos.

```python
while True:
    entrada = input("Tu edad: ")
    try:
        edad = int(entrada)
    except ValueError:
        print("No es un número válido. Intenta de nuevo.")
        continue
    if not (0 <= edad <= 130):
        print("Edad fuera de rango. Intenta de nuevo.")
        continue
    print(f"Edad registrada: {edad}")
    break
```

Léelo, ejecútalo, prueba inputs raros (letras, números muy grandes, números negativos, vacío). Observa qué pasa en cada caso.

---

## Aporte al proyecto integrador

S02 todavía no agrega código al integrador. Cierre del M1 viene en S05.

---

## Antes de pasar a S03

- ✅ Hiciste los ejercicios 1-7.
- ✅ Te resultan claras las comprensiones simples (transformar y filtrar).
- ✅ Sabes cuándo usar `for` vs `while`.

Si los tres están listos, sigue con [S03 — Estructuras de datos](../sesion-03-estructuras-datos/README.md).

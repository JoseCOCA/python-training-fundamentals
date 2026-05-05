# S04 — Funciones, scope y argumentos

> **Sesión 2h.** ~50 min lectura + ~70 min ejercicios. Las **funciones** son la primera abstracción real del lenguaje. Esta sesión es donde tu código deja de ser un script lineal y empieza a tener piezas reutilizables.

---

## 1. Objetivos de aprendizaje

Al terminar esta sesión vas a:

- Definir y llamar funciones con la sintaxis correcta.
- Conocer las cuatro formas de pasar argumentos: posicional, por nombre, con default, y variádicos (`*args`, `**kwargs`).
- Entender **scope** (alcance de variables) y la regla LEGB.
- Distinguir una función **pura** de una con efectos secundarios, y por qué importa.
- Evitar el gotcha más famoso de Python: **mutable default arguments**.

## 2. Prerequisitos

- [S01](../sesion-01-variables-tipos/README.md), [S02](../sesion-02-control-flujo/README.md) y [S03](../sesion-03-estructuras-datos/README.md) completas.

## 3. Conceptos clave

1. **Función como caja negra.** Recibe entradas (parámetros), devuelve una salida (return). Lo que pasa adentro no debería tener que importarte cuando la usas.
2. **Parámetro vs argumento.** Parámetros son los nombres que declaras; argumentos son los valores que pasas. `def f(x):` — `x` es parámetro. `f(5)` — `5` es argumento.
3. **Posicional vs por nombre.** `f(5, 10)` pasa por orden. `f(a=5, b=10)` pasa por nombre. La segunda forma es más legible cuando hay muchos parámetros.
4. **Scope LEGB.** Python busca un nombre en este orden: **L**ocal → **E**nclosing → **G**lobal → **B**uilt-in. Saber este orden te explica todos los "por qué no encuentra esta variable".
5. **Pura vs efecto secundario.** Una función pura solo depende de sus argumentos y devuelve un valor. Una con efectos secundarios modifica algo externo (variable global, archivo, BD, lista mutable). Las puras son más fáciles de testear y razonar.

## 4. Teoría

### 4.1. Definir y llamar una función

```python
def saludar(nombre):
    return f"Hola, {nombre}!"

mensaje = saludar("Carolina")
print(mensaje)        # → Hola, Carolina!
```

- `def` es la palabra clave.
- `saludar` es el nombre. Convención: `snake_case`.
- `nombre` es el parámetro.
- El cuerpo va indentado.
- `return` devuelve un valor. Si no escribes `return`, la función devuelve `None` implícitamente.

### 4.2. Múltiples parámetros y valores de retorno

```python
def calcular_total(precio, cantidad, descuento):
    subtotal = precio * cantidad
    descuento_total = subtotal * descuento
    total = subtotal - descuento_total
    return total

print(calcular_total(89.99, 3, 0.15))    # → 229.4745
```

**Múltiples retornos** vía tupla:

```python
def calcular_subtotal_y_descuento(precio, cantidad, descuento):
    subtotal = precio * cantidad
    descuento_total = subtotal * descuento
    return subtotal, descuento_total      # devuelve una tupla

sub, desc = calcular_subtotal_y_descuento(89.99, 3, 0.15)
```

Esto es **convención** en Python — devolver tupla y desempaquetar al recibir.

### 4.3. Argumentos posicionales vs por nombre

**Posicional** — Python asigna por orden:

```python
def crear_producto(nombre, precio, stock):
    return {"nombre": nombre, "precio": precio, "stock": stock}

crear_producto("auriculares", 89.99, 5)
```

**Por nombre (keyword)** — explícito:

```python
crear_producto(nombre="auriculares", precio=89.99, stock=5)
```

**Mezclado** — posicionales primero, después keyword:

```python
crear_producto("auriculares", precio=89.99, stock=5)        # ✅
crear_producto(precio=89.99, "auriculares", stock=5)        # ❌ SyntaxError
```

**Cuándo usar cuál:**

- 1-2 parámetros simples: posicional.
- 3+ parámetros, o cuando el nombre añade claridad (`descuento=0.15`): por nombre.
- Booleanos: **siempre** por nombre. `procesar(True)` no le dice nada al lector. `procesar(con_validacion=True)` sí.

### 4.4. Valores por defecto

```python
def crear_producto(nombre, precio, stock=0, categoria="general"):
    return {
        "nombre": nombre,
        "precio": precio,
        "stock": stock,
        "categoria": categoria,
    }

crear_producto("auriculares", 89.99)
# → {"nombre": "auriculares", "precio": 89.99, "stock": 0, "categoria": "general"}

crear_producto("auriculares", 89.99, stock=5)
# → {"nombre": "auriculares", "precio": 89.99, "stock": 5, "categoria": "general"}
```

Los parámetros con default deben ir **después** de los sin default. `def f(a, b=2, c)` es SyntaxError.

### 4.5. **Mutable default arguments — el gotcha más famoso de Python**

```python
def agregar_a_carrito(item, carrito=[]):       # ❌ NO HAGAS ESTO
    carrito.append(item)
    return carrito

print(agregar_a_carrito("manzana"))           # → ["manzana"]
print(agregar_a_carrito("pera"))              # → ["manzana", "pera"]   ← ¡!
print(agregar_a_carrito("uva"))               # → ["manzana", "pera", "uva"]
```

**Por qué pasa:** los defaults se evalúan **una sola vez**, cuando se define la función. Esa lista vacía es un único objeto que se reutiliza entre todas las llamadas.

**Forma correcta:** usar `None` como sentinel y crear adentro:

```python
def agregar_a_carrito(item, carrito=None):
    if carrito is None:
        carrito = []
    carrito.append(item)
    return carrito
```

Este patrón es **estándar** en Python. Si te lo encuentras en código de terceros, ya sabes por qué.

### 4.6. `*args` y `**kwargs`

Aceptar un número variable de argumentos.

**`*args`** — recolecta argumentos posicionales sobrantes en una **tupla**:

```python
def total(*precios):
    return sum(precios)

total(10, 20, 30)               # → 60
total(10, 20, 30, 40, 50)       # → 150
```

**`**kwargs`** — recolecta argumentos por nombre sobrantes en un **dict**:

```python
def crear_producto(nombre, **extras):
    return {"nombre": nombre, **extras}

crear_producto("auriculares", precio=89.99, stock=5, color="negro")
# → {"nombre": "auriculares", "precio": 89.99, "stock": 5, "color": "negro"}
```

Los nombres `args` y `kwargs` son convención — lo importante son los `*` y `**`. **No abuses de estos** — solo úsalos cuando realmente necesites flexibilidad. La mayor parte del código del curso 2 va a tener parámetros explícitos.

### 4.7. Scope (LEGB)

Cuando Python busca el valor de una variable, busca en este orden:

1. **L** — Local: dentro de la función.
2. **E** — Enclosing: en funciones contenedoras (caso de funciones anidadas).
3. **G** — Global: en el archivo (módulo).
4. **B** — Built-in: nombres del propio Python (`print`, `len`, `range`...).

```python
mensaje = "global"

def fuera():
    mensaje = "enclosing"

    def dentro():
        mensaje = "local"
        print(mensaje)         # → "local"

    dentro()
    print(mensaje)             # → "enclosing"

fuera()
print(mensaje)                 # → "global"
```

**Asignar dentro de una función crea una variable LOCAL nueva.** No modifica la global. Para modificar la global, necesitas la palabra clave `global`:

```python
contador = 0

def incrementar():
    global contador            # explícito: vamos a tocar la variable global
    contador += 1

incrementar()
print(contador)                # → 1
```

**Anti-patrón:** abusar de `global`. Si te encuentras usándolo seguido, casi siempre tu lógica está mal estructurada — pasa los datos como argumentos y devuelve el resultado.

### 4.8. Funciones puras vs efectos secundarios

**Función pura:**

- Su resultado depende **solo** de sus argumentos.
- **No modifica** nada fuera de sí misma (ni globals, ni listas/dicts pasados, ni archivos, ni BD).
- Llamarla con los mismos argumentos siempre da el mismo resultado.

```python
def calcular_total(precio, cantidad):
    return precio * cantidad           # pura
```

**Función con efectos secundarios:**

```python
def agregar_log(mensaje, registro):
    registro.append(mensaje)           # ← modifica el argumento (efecto secundario)
    print(f"LOG: {mensaje}")           # ← I/O (efecto secundario)
```

**Por qué importa:** las funciones puras son **trivialmente testeables** (pasas argumentos, verificas el retorno) y **trivialmente componibles** (las puedes llamar en cualquier orden). Las que tienen efectos requieren más cuidado.

**Regla práctica:** prefiere puras. Cuando necesites efectos secundarios (escribir a BD, llamar a una API), aíslalos en funciones específicas y mantén la lógica de negocio pura.

### 4.9. Docstrings

```python
def calcular_total(precio, cantidad, descuento=0.0):
    """Calcula el total de una compra aplicando descuento.

    Args:
        precio: precio unitario en dólares.
        cantidad: número de unidades.
        descuento: fracción a descontar (0.15 = 15%). Default: 0 (sin descuento).

    Returns:
        Total final en dólares.
    """
    subtotal = precio * cantidad
    return subtotal * (1 - descuento)
```

El **docstring** es el primer string de la función. Es lo que aparece cuando llamas `help(calcular_total)` o cuando el editor te muestra el tooltip. **No** es comentario — es metadato accesible en runtime.

Convención: docstring de una línea para funciones simples; multilínea (con Args/Returns) para las complejas.

## 5. Patrones y antipatrones

| ✅ Patrón | ❌ Antipatrón |
|---|---|
| Funciones cortas, una responsabilidad | Funciones de 100 líneas que hacen 5 cosas |
| Argumentos por nombre cuando son booleanos o numerosos | `procesar(True, False, 5)` (ilegible) |
| `default=None` y crear adentro para mutables | `default=[]` o `default={}` |
| Funciones puras cuando puedas | Funciones que modifican variables globales |
| Devolver explícitamente, aunque sea `None` | Funciones largas con `return` solo en algunos paths |
| Docstring que explica intent y contrato | Sin docstring o solo comentarios sueltos |
| Pasar datos como argumentos, devolver resultados | Modificar variables globales con `global` |

## 6. Conexión con el proyecto integrador

En el hito M1 vas a tener funciones como `cargar_catalogo(ruta)`, `ordenar_por_precio(catalogo)`, `formatear_producto(producto)`. Cada una con una responsabilidad clara. Las habilidades de esta sesión:

- Diseñar la firma de cada función (qué entra, qué sale).
- Mantenerlas puras donde puedas.
- Documentar con docstrings.

## 7. Resumen

1. **Función = caja negra** que recibe argumentos y devuelve un valor. `def`, parámetros indentados, `return`.
2. **Cuatro formas de argumentos:** posicional, por nombre, default, variádicos (`*args`, `**kwargs`). Para mutables como default, usa siempre `None` y crea adentro.
3. **LEGB** te explica dónde Python busca cada nombre. **Asignar dentro crea local** salvo que uses `global`.
4. **Prefiere funciones puras.** Aíslalas las impuras. Tu yo del futuro te lo va a agradecer cuando estés escribiendo tests en M6.

## 8. Preguntas de auto-evaluación

1. ¿Cuál es la diferencia entre parámetro y argumento? Da un ejemplo de cada uno en una línea de código.
2. Predice qué imprime:
   ```python
   def f(items=[]):
       items.append(1)
       return items

   print(f())
   print(f())
   ```
   ¿Por qué? ¿Cómo lo arreglarías?
3. Explica LEGB con un ejemplo de cada nivel.
4. Una función con `return None` explícito y una sin `return`. ¿Devuelven lo mismo?
5. ¿Cuándo usarías `*args` vs declarar parámetros explícitos?
6. Diferencia entre función pura y con efectos secundarios. Da un ejemplo de cada una.

Cuando puedas responder todas, pasa a [`ejercicios.md`](ejercicios.md).

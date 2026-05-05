# S01 — Variables, tipos primitivos y expresiones

> **Sesión 2h.** ~50 min de lectura + ~70 min de práctica guiada en `ejercicios.md`. Es la **primera sesión con código Python real** del curso. Si M0 te dio el taller y las herramientas, esta sesión te da las primeras piezas para construir.

---

## 1. Objetivos de aprendizaje

Al terminar esta sesión vas a:

- Entender qué es **realmente** una variable en Python (spoiler: no es una caja).
- Conocer los cinco **tipos primitivos** que vas a usar el 95% del tiempo: `int`, `float`, `str`, `bool` y `None`.
- Saber cuándo y cómo **convertir** entre tipos sin perder información.
- Usar todos los **operadores aritméticos, de comparación y booleanos** sin sorprenderte por los gotchas clásicos (división, precisión de float, short-circuit).
- Tener internalizada la diferencia entre **expresión** y **sentencia** — una distinción que no parece importante hasta que importa muchísimo.

## 2. Prerequisitos

- Módulo 0 completo. Específicamente: tienes Python 3.12, uv y VS Code instalados, y has ejecutado al menos una vez `uv run python main.py`.
- Sabes navegar a un directorio en la terminal y crear archivos.

## 3. Conceptos clave

1. **Variable como vínculo (binding), no como caja.** En Python una variable es un nombre que apunta a un valor en memoria. Esa diferencia con "una caja que contiene" se vuelve crítica cuando lleguemos a estructuras de datos en S03.
2. **Tipado dinámico.** Python no te obliga a declarar el tipo de una variable. Lo deduce del valor que le asignas. Esto es cómodo pero tiene consecuencias — vas a aprender a domesticar esa flexibilidad cuando lleguemos al Módulo 3 (tipado).
3. **Tipos primitivos.** Bloques mínimos del lenguaje: `int` (enteros), `float` (decimales), `str` (texto), `bool` (verdadero/falso), `None` (ausencia de valor).
4. **Expresión vs sentencia.** Una expresión **devuelve un valor** (`2 + 3` devuelve `5`). Una sentencia **hace algo** (`x = 5` asigna). Confundirlas es la fuente de muchos errores de novato.
5. **Short-circuit evaluation.** Los operadores `and` y `or` no siempre evalúan ambos lados. Lo entiendes una vez y te ahorras horas de bugs.

## 4. Teoría

### 4.1. Qué es una variable (de verdad)

La forma común de explicar variables — *"una caja con un nombre donde guardas un valor"* — está mal. Es una mentira pedagógica que después tienes que desaprender. Vamos a empezar por el modelo correcto desde el principio.

En Python, una variable es un **nombre** que está vinculado a un **valor en memoria**. La asignación `x = 5` no mete el `5` "dentro" de `x`. Lo que hace es:

1. Crea (o reutiliza) un objeto `5` en memoria.
2. Hace que el nombre `x` apunte a ese objeto.

Visualmente:

```
x  ────────►  [ 5 ]
nombre        objeto en memoria
```

Cuando ejecutas `x = 10` después, no estás "cambiando lo que hay en la caja". Estás moviendo la flecha:

```
x  ────────►  [ 10 ]    ← x ahora apunta a otro objeto
              [ 5 ]     ← el 5 sigue en memoria hasta que el recolector lo limpie
```

Esta distinción no importa todavía — pero va a importar en S03 cuando dos variables apunten al mismo objeto y modifiques uno "por accidente". Ten el modelo mental correcto desde ahora.

### 4.2. Asignación e identificadores

```python
edad = 25
nombre = "Sofia"
es_cliente = True
```

**Reglas para nombres de variables (identificadores):**

- Pueden contener letras, dígitos y guion bajo (`_`).
- **No** pueden empezar con un dígito.
- Distinguen mayúsculas: `edad` y `Edad` son variables distintas.
- No pueden usar palabras reservadas del lenguaje (`if`, `for`, `class`, `True`, etc.).

**Convenciones (no obligatorias pero universales en Python — PEP 8):**

- `snake_case` para variables y funciones: `precio_producto`, `nombre_cliente`.
- `UPPER_SNAKE_CASE` para constantes: `IVA = 0.21`.
- `_nombre` (con guion bajo al inicio) sugiere "uso interno" (lo veremos en M2).
- Evita nombres de una letra (`x`, `n`) salvo en contadores o casos triviales.
- Nombra con la **intención** del valor, no con el tipo: `clientes` mejor que `lista_clientes`.

### 4.3. Tipos primitivos

Python tiene cinco tipos primitivos que vas a usar el 95% del tiempo. Los demás (listas, diccionarios, etc.) son **estructuras de datos** y los vemos en S03.

**`int` — enteros**

```python
edad = 25
ano = 2026
saldo = -150
unidades_disponibles = 0
```

A diferencia de muchos lenguajes, Python **no tiene límite de tamaño** para enteros. `2 ** 1000` funciona y te devuelve un número de 300 dígitos sin desbordarse.

**`float` — números con decimales**

```python
precio = 19.99
porcentaje_descuento = 0.15
pi = 3.14159
```

Internamente usan IEEE 754 (estándar de la industria). Esto trae un gotcha clásico que vamos a ver en §4.10.

**`str` — texto (cadenas de caracteres)**

```python
nombre = "Carolina"
direccion = 'Calle 13 #45-67'
mensaje = """Esto es un texto
que puede ocupar
varias líneas."""
```

Comillas simples y dobles son intercambiables. Triples (`"""`) permiten texto multilínea. Las cadenas son **inmutables** — concepto importante que profundizamos en S05.

**`bool` — verdadero o falso**

```python
es_premium = True
esta_activo = False
```

Solo dos valores: `True` y `False`. Importante: empiezan con mayúscula. `true` (en minúsculas) **no existe** en Python y te tirará un error.

**`None` — ausencia de valor**

```python
direccion_envio = None
respuesta_servidor = None
```

`None` representa "no hay valor" o "todavía no se asignó". Es el tipo de retorno por defecto de funciones que no retornan nada explícitamente. **No es lo mismo que `0`, `""` o `False`** — es su propia cosa, con su propio tipo (`NoneType`).

### 4.4. Tipado dinámico (y por qué eso importa)

Python no te obliga a declarar el tipo de una variable. Esto compila:

```python
x = 5            # x es int
x = "hola"       # ahora x es str
x = [1, 2, 3]    # ahora x es list
```

La variable `x` puede apuntar a cualquier tipo, en cualquier momento. Esto es **tipado dinámico**.

**Pro:** flexible, expresivo, rápido para prototipar.
**Contra:** te puedes equivocar y pasar el tipo incorrecto sin que nadie te avise hasta que el programa falle en runtime.

A partir del Módulo 3 vamos a usar **type hints** para domesticar esta flexibilidad — escribir el tipo "esperado" para que herramientas como `mypy` te avisen antes de ejecutar. Pero por ahora, simplemente sé consciente de que Python te da libertad y la libertad implica responsabilidad.

Para inspeccionar el tipo de un valor:

```python
type(25)            # → <class 'int'>
type(19.99)         # → <class 'float'>
type("Carolina")    # → <class 'str'>
type(True)          # → <class 'bool'>
type(None)          # → <class 'NoneType'>
```

### 4.5. Conversión de tipos

A veces necesitas convertir un valor de un tipo a otro. Python te lo permite con funciones explícitas:

```python
int("25")        # → 25         (str a int)
float("19.99")   # → 19.99      (str a float)
str(25)          # → "25"       (int a str)
bool(0)          # → False      (cualquier "vacío" es False)
bool(1)          # → True       (todo lo demás es True)
```

**Cuidado** — algunas conversiones pierden información o fallan:

```python
int(19.99)       # → 19         (TRUNCA, no redondea)
int("hola")      # → ValueError ("hola" no es un número)
float("3,14")    # → ValueError (Python usa . como decimal, no ,)
```

Regla general: si una conversión puede fallar, valida el input antes (en M3 vamos a ver pydantic, que automatiza esto).

### 4.6. Expresiones vs sentencias

Una distinción que parece pedante pero ahorra muchos bugs.

**Expresión:** un fragmento de código que **devuelve un valor**. Puedes ponerlo del lado derecho de un `=`.

```python
2 + 3              # expresión, devuelve 5
"hola" + " mundo"  # expresión, devuelve "hola mundo"
edad >= 18         # expresión, devuelve True o False
```

**Sentencia:** un fragmento de código que **hace algo** pero no devuelve un valor utilizable.

```python
x = 5              # sentencia (asignación)
print("hola")      # llamada a función — técnicamente expresión, pero su valor (None) rara vez se usa
if edad >= 18:     # sentencia (estructura de control)
    ...
```

La forma rápida de saber: ¿puedes ponerlo del lado derecho de un `=`? Si sí, es expresión. Si no, es sentencia.

```python
x = (y = 5)        # ¡error! "y = 5" es sentencia, no expresión
x = (5 + 3)        # ok, "5 + 3" es expresión
```

### 4.7. Operadores aritméticos

```python
2 + 3       # 5      suma
10 - 4      # 6      resta
3 * 4       # 12     multiplicación
10 / 3      # 3.333… división (siempre devuelve float)
10 // 3     # 3      división entera (TRUNCA hacia abajo)
10 % 3      # 1      módulo (resto de la división)
2 ** 8      # 256    potencia
```

**Gotcha clásico:** en Python 3, `/` siempre devuelve `float`, incluso si divides dos enteros que dan un resultado entero:

```python
10 / 5      # → 2.0 (no 2)
```

Si necesitas el resultado entero, usa `//`:

```python
10 // 5     # → 2
```

Esto es **distinto** de C, Java, JavaScript y otros lenguajes donde `/` entre enteros da entero. Python eligió ser explícito: si quieres división entera, pídela.

### 4.8. Operadores de comparación

Devuelven `bool`.

```python
5 == 5      # True   igualdad (¡dos signos =!)
5 != 5      # False  desigualdad
5 < 10      # True   menor que
5 > 10      # False  mayor que
5 <= 5      # True   menor o igual
5 >= 6      # False  mayor o igual
```

**Gotcha clásico:** confundir `=` (asignación) con `==` (comparación). Python te da un error claro si pones `=` donde va `==`, así que no es un bug silencioso — pero acostúmbrate al doble signo desde ahora.

### 4.9. Operadores booleanos

```python
True and False     # False
True or False      # True
not True           # False
```

**Short-circuit evaluation** (cortocircuito):

- `and`: si el primer operando es `False`, no evalúa el segundo (porque ya sabe que el resultado será `False`).
- `or`: si el primer operando es `True`, no evalúa el segundo.

```python
def es_caro():
    print("evaluando precio…")
    return True

False and es_caro()    # imprime nada — no se evalúa es_caro()
True or es_caro()      # imprime nada — no se evalúa es_caro()
True and es_caro()     # imprime "evaluando precio…" → True
```

Esto se usa para escribir validaciones seguras:

```python
if usuario is not None and usuario.es_premium:
    ...
```

Sin short-circuit, accediendo `usuario.es_premium` cuando `usuario` es `None` lanzaría un error. Con short-circuit, el `and` corta antes de llegar al segundo lado.

### 4.10. Precisión de los float (importante)

Los `float` en Python (y en casi todos los lenguajes) usan IEEE 754 — una forma binaria de representar decimales. Algunos números no se pueden representar con exactitud:

```python
0.1 + 0.2       # → 0.30000000000000004
```

No es un bug de Python — es matemática binaria. `0.1` en binario es una fracción periódica infinita.

**Reglas prácticas:**

- **Nunca uses `==` para comparar floats.** Usa una tolerancia: `abs(a - b) < 1e-9`.
- **Para dinero**, no uses `float`. Usa `Decimal` (lo veremos cuando lleguemos a TiendaPro Lite serio en M5) o trabajá en céntimos enteros.
- Para precios visuales en TiendaPro durante el M1 está bien usar `float`. La advertencia es para que lo tengas en mente cuando construyamos el integrador de verdad.

## 5. Patrones y antipatrones

| ✅ Patrón | ❌ Antipatrón |
|---|---|
| Nombrar con la **intención** (`precio_unitario`) | Nombrar con el tipo (`float_precio`) o con una letra (`p`) |
| Usar `snake_case` para variables | Mezclar `camelCase`, `PascalCase` y `snake_case` en el mismo archivo |
| Convertir tipos explícitamente cuando hace falta | Asumir que Python "se da cuenta solo" |
| Usar `//` para división entera | Usar `int(a / b)` (funciona pero es más confuso) |
| Comparar floats con tolerancia | `if precio_calculado == 10.0:` |
| Aprovechar short-circuit para validar antes de acceder | Anidar `if` cuando un `and` con cortocircuito sería suficiente |

## 6. Conexión con el proyecto integrador

En el hito M1 de TiendaPro Lite vas a escribir un script que lee un archivo JSON con productos y los imprime ordenados por precio. Para eso necesitas:

- Variables que guarden datos de productos (`nombre`, `precio`, `stock`).
- Tipos correctos: `str` para nombre, `float` para precio, `int` para stock, `bool` para `disponible`.
- Conversión de tipos cuando lees el JSON.
- Comparación de precios (operador `<`).

Todo esto lo cubre esta sesión.

## 7. Resumen

Los tres puntos que te tienes que llevar:

1. **Una variable es un nombre que apunta a un valor**, no una caja que lo contiene. Ten el modelo correcto desde el día 1 — en S03 vas a agradecerlo.
2. **Los cinco tipos primitivos** (`int`, `float`, `str`, `bool`, `None`) cubren el 95% de tu vida diaria. Conoce sus conversiones (`int()`, `str()`, etc.) y sus gotchas (división de int en Python 3 da float, comparar floats con `==` es trampa).
3. **Expresión devuelve un valor; sentencia hace algo.** Si puedes ponerlo del lado derecho de un `=`, es expresión.

## 8. Preguntas de auto-evaluación

Si no puedes responderlas sin volver a leer, vuelve a leer.

1. ¿Cuál es la diferencia entre el modelo "variable como caja" y "variable como vínculo"? ¿Por qué importa?
2. Tienes `x = 5` y luego `x = "hola"`. ¿Qué pasó con el `5`? ¿Está prohibido en Python?
3. ¿Cuál es la diferencia entre `10 / 3` y `10 // 3` en Python 3? ¿Por qué `10 / 5` devuelve `2.0` y no `2`?
4. Da un ejemplo concreto donde `0.1 + 0.2 == 0.3` falle. ¿Por qué pasa? ¿Cómo se compara correctamente?
5. ¿Qué imprime el siguiente código? ¿Por qué?
   ```python
   def costoso():
       print("calculando…")
       return True
   resultado = False and costoso()
   print(resultado)
   ```
6. ¿Cuál es la diferencia entre `None`, `0`, `False` y `""`? Da una situación donde uses cada uno.
7. ¿Por qué `int("hola")` falla? ¿Y `int("19.99")`? ¿Cómo conviertes correctamente `"19.99"` a un número entero?

Cuando puedas responder todas, pasa a [`ejercicios.md`](ejercicios.md).

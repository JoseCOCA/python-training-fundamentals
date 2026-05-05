# S09 — Decoradores, generadores y context managers (lo justo y necesario)

> **Sesión 2h.** ~45 min lectura + ~75 min ejercicios. **Cierra el Módulo 2** con el segundo hito del proyecto integrador (`proyecto-m2`). Esta sesión cubre tres herramientas que vas a **reconocer y usar a diario** en código Python real, sin caer en la trampa de "construir frameworks". El objetivo: que cuando veas `@retry`, `yield` o `with open(...)` en código ajeno, sepas exactamente qué hace y por qué.

---

## 1. Objetivos de aprendizaje

Al terminar esta sesión vas a poder:

- Explicar qué es un **decorador** y leerlo correctamente en código ajeno.
- Escribir un decorador simple usando `functools.wraps`.
- Entender qué es un **generador** y por qué `yield` cambia la naturaleza de la función.
- Distinguir cuándo un generador es la herramienta correcta (lazy iteration, streams, pipelines).
- Usar context managers con `with` y entender el protocolo `__enter__` / `__exit__`.
- Crear un context manager simple con `contextlib.contextmanager`.

## 2. Prerequisitos

- [S04 — Funciones](../../01-python-fundamentos/sesion-04-funciones/README.md) firme. Vas a tratar funciones como datos.
- [S07 — Errores](../sesion-07-errores/README.md). Los context managers brillan en el manejo correcto de recursos cuando hay excepciones.
- [S08 — OOP](../sesion-08-oop-dataclasses/README.md). Vas a entender el protocolo `__enter__`/`__exit__`.

## 3. Conceptos clave

1. **Función de primera clase.** En Python, una función es un objeto: se asigna a variables, se pasa como argumento, se devuelve. Esto es la base de los decoradores.
2. **Decorador.** Una función que **toma una función y devuelve otra función**, generalmente con comportamiento adicional (logging, cache, autenticación, retry). La sintaxis `@decorador` arriba de una `def` es solo azúcar para `funcion = decorador(funcion)`.
3. **Generador.** Una función que en lugar de `return` usa `yield`. Cuando se llama, **no ejecuta el cuerpo** — devuelve un objeto iterable que produce valores uno a uno bajo demanda.
4. **Context manager.** Un objeto que define `__enter__` y `__exit__`. Se usa con `with` para garantizar que un recurso se libera correctamente, **incluso si hay excepción**.
5. **`with` statement.** La forma correcta de manejar archivos, conexiones, locks y cualquier recurso que requiera limpieza.

## 4. Teoría

### 4.1. Funciones como objetos: el cimiento de los decoradores

```python
def saludar(nombre: str) -> str:
    return f"Hola, {nombre}"

# Las funciones son objetos:
otra = saludar                          # asignación
print(otra("Ana"))                      # → "Hola, Ana"

def aplicar(f, valor):                  # pasar como argumento
    return f(valor)

print(aplicar(saludar, "Bruno"))        # → "Hola, Bruno"

def fabricar() -> callable:             # devolver desde otra función
    def decir_hola():
        return "hola"
    return decir_hola

f = fabricar()
print(f())                              # → "hola"
```

Si entendiste lo de arriba, los decoradores te van a parecer obvios.

### 4.2. Decorador básico

Un decorador es una **función que toma una función y devuelve otra**. Ejemplo: un decorador que loggea cada llamada.

```python
def log(funcion):
    def envoltorio(*args, **kwargs):
        print(f"→ llamando {funcion.__name__}({args}, {kwargs})")
        resultado = funcion(*args, **kwargs)
        print(f"← {funcion.__name__} devolvió {resultado!r}")
        return resultado
    return envoltorio


def sumar(a, b):
    return a + b


sumar = log(sumar)        # ← reemplazamos sumar por su versión decorada
sumar(2, 3)
# → llamando sumar((2, 3), {})
# ← sumar devolvió 5
```

La sintaxis `@decorador` es **exactamente** azúcar para esa última línea:

```python
@log
def sumar(a, b):
    return a + b

# Equivalente a:
# def sumar(a, b): ...
# sumar = log(sumar)
```

### 4.3. `functools.wraps`: preservar la identidad de la función

Sin precaución, el decorador "esconde" la función original:

```python
@log
def sumar(a, b):
    return a + b

print(sumar.__name__)        # → "envoltorio"   ❌ debería ser "sumar"
```

`functools.wraps` lo arregla:

```python
import functools

def log(funcion):
    @functools.wraps(funcion)        # ← copia nombre, docstring y metadatos
    def envoltorio(*args, **kwargs):
        # ...
    return envoltorio
```

**Regla:** todo decorador serio usa `@functools.wraps`. Sin él, los tracebacks mienten, los tests con `__name__` se rompen y mypy se confunde.

### 4.4. Decoradores útiles de la librería estándar

Los más usados en código Python real:

```python
import functools


@functools.cache                  # memoiza con cache infinito
def fibonacci(n: int) -> int:
    if n < 2:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)


@functools.lru_cache(maxsize=128) # memoiza con cache acotado
def consulta_costosa(clave: str) -> dict:
    ...
```

`@dataclass`, `@staticmethod`, `@classmethod`, `@property` son decoradores también. La sintaxis es la misma.

### 4.5. Cuándo escribir tu propio decorador (y cuándo no)

**Casos legítimos:**

- Comportamiento transversal: logging, métricas, autenticación, cache, retry, timing.
- Algo que se repite en 3+ funciones y tiene una forma genérica clara.

**Antipatrones:**

- Decoradores con cinco parámetros y tres niveles de funciones anidadas. Si tu decorador es más difícil de leer que la función que decora, **mata el decorador**.
- Decoradores que cambian profundamente el comportamiento de la función (no solo la envuelven). El que los lea va a sufrir.

**Heurística:** un decorador debería caber en menos de 30 líneas, hacer **una** cosa, y no requerir doc para entenderlo.

### 4.6. Generadores: funciones que pausan

Una función normal:

```python
def numeros():
    return [1, 2, 3]
```

Un generador:

```python
def numeros():
    yield 1
    yield 2
    yield 3
```

La diferencia: cuando llamas `numeros()`, **no se ejecuta el cuerpo**. Devuelve un objeto generador que produce valores uno a uno.

```python
gen = numeros()
print(gen)                # <generator object numeros at 0x...>
print(next(gen))          # → 1   (ahora corre hasta el primer yield)
print(next(gen))          # → 2   (sigue desde donde se pausó)
print(next(gen))          # → 3
print(next(gen))          # → StopIteration   (el generador terminó)
```

Lo más común no es usar `next()` a mano — es iterarlo:

```python
for n in numeros():
    print(n)
```

El `for` llama `next()` en silencio hasta que el generador se acabe.

### 4.7. ¿Para qué sirven los generadores en la práctica?

**Caso 1: archivos grandes que no caben en memoria.**

```python
def lineas_que_contienen(ruta: str, palabra: str):
    with open(ruta, encoding="utf-8") as f:
        for linea in f:
            if palabra in linea:
                yield linea.rstrip()


# Itera sin cargar el archivo entero:
for linea in lineas_que_contienen("logs.txt", "ERROR"):
    print(linea)
```

`for linea in f` ya es un generador interno que entrega línea a línea. Tu generador filtra encima sin acumular memoria.

**Caso 2: pipelines.**

```python
def leer(ruta):
    with open(ruta) as f:
        for linea in f:
            yield linea.rstrip()

def filtrar(lineas, palabra):
    for linea in lineas:
        if palabra in linea:
            yield linea

def normalizar(lineas):
    for linea in lineas:
        yield linea.lower().strip()


lineas_finales = normalizar(filtrar(leer("logs.txt"), "ERROR"))
for linea in lineas_finales:
    print(linea)
```

Cada paso procesa un elemento a la vez. Memoria constante, código legible.

**Caso 3: secuencias infinitas.**

```python
def naturales():
    n = 1
    while True:
        yield n
        n += 1
```

Imposible con una lista (sería infinita). Con generador, totalmente normal — solo "tiras" los valores que necesitas.

### 4.8. Generator expression: el atajo

Igual que las comprensiones de lista, pero con paréntesis:

```python
cuadrados = [x * x for x in range(10)]      # lista (todos los valores en memoria)
cuadrados = (x * x for x in range(10))      # generator (lazy, uno a la vez)

sum(x * x for x in range(10))               # paréntesis "implícitos" dentro de un call
```

**Regla:** si vas a iterar **una sola vez** y el dato puede ser grande, usa generator expression. Si vas a iterar varias veces o necesitas indexar, usa lista.

### 4.9. Context managers: el patrón `with`

El problema clásico:

```python
archivo = open("datos.txt")
contenido = archivo.read()
archivo.close()                  # ¿qué pasa si .read() lanza una excepción?
```

Si `read()` falla, `close()` nunca se ejecuta. El descriptor de archivo queda abierto. En un servidor con miles de requests, esto te lleva a `Too many open files` en horas.

El patrón con `try / finally`:

```python
archivo = open("datos.txt")
try:
    contenido = archivo.read()
finally:
    archivo.close()
```

Funciona pero es verboso. La forma idiomática:

```python
with open("datos.txt") as archivo:
    contenido = archivo.read()
# aquí el archivo ya está cerrado, haya excepción o no
```

`with` es **el patrón correcto** para cualquier recurso que requiera limpieza.

### 4.10. ¿Cómo funciona `with` por dentro?

`with X as y:` requiere que `X` sea un **context manager** — un objeto con dos métodos:

```python
class MiCM:
    def __enter__(self):
        # se ejecuta al entrar al with
        # devuelve lo que va al `as`
        return self.recurso

    def __exit__(self, exc_type, exc_value, traceback):
        # se ejecuta al salir, haya o no excepción
        # devuelve True para suprimir la excepción (rara vez es lo que quieres)
        self.recurso.close()
```

`open()` ya implementa este protocolo por ti. Lo mismo para conexiones de DB, locks de threading, etc.

### 4.11. `contextlib.contextmanager`: hacer un context manager con un generador

A veces necesitas un context manager propio pero la clase con `__enter__`/`__exit__` es demasiado para un caso simple. `contextlib` te deja escribirlo como generador:

```python
from contextlib import contextmanager
import time


@contextmanager
def cronometro(nombre: str):
    inicio = time.perf_counter()
    yield                                     # aquí corre el cuerpo del with
    duracion = time.perf_counter() - inicio
    print(f"{nombre}: {duracion:.3f}s")


# Uso:
with cronometro("carga del catalogo"):
    productos = cargar_catalogo("data/productos.json")
# imprime: "carga del catalogo: 0.012s"
```

**Mecánica:**

1. Todo lo que está antes de `yield` es el `__enter__`.
2. El valor del `yield` (si hay) es lo que va al `as`.
3. Todo lo que está después es el `__exit__`.
4. Si necesitas manejar excepciones del cuerpo, envuelve el `yield` con `try/finally`.

### 4.12. Los context managers en el día a día

Los vas a ver en:

- **Archivos.** `with open(...)` siempre.
- **Conexiones de base de datos.** `with sqlite3.connect(...)`, `with engine.begin()`.
- **Locks de threading.** `with lock:`.
- **Mocks en tests.** `with patch(...)`.
- **Sesiones HTTP.** `with httpx.Client() as cliente:`.

**Si una librería tiene un objeto que se "abre" y se "cierra", casi siempre tiene soporte de context manager.** Acostúmbrate a buscarlo en la doc — es lo idiomático.

## 5. Patrones y antipatrones

| ✅ Patrón | ❌ Antipatrón |
|---|---|
| `with open(...) as f:` | `f = open(...)` sin cerrar |
| Decorador con `@functools.wraps` | Decorador que rompe `__name__` y `__doc__` |
| Generator expression para una sola pasada | Lista intermedia gigante en memoria |
| `@contextmanager` para CMs simples | Clase con `__enter__/__exit__` para algo trivial |
| Decorador que envuelve sin transformar la API | Decorador con cinco capas de funciones anidadas |
| `for x in generador` (consumir lazy) | `list(generador)` "por las dudas" |
| Generador para streams y pipelines | Acumular todo en una lista antes de procesar |
| Pipeline = composición de generadores | Hacer todo en un solo bucle gigante |

## 6. Conexión con el proyecto integrador — Hito M2

**Llegamos al final del módulo.** Hoy se cierra TiendaPro Lite versión M2 con tag `proyecto-m2`.

Cambios concretos sobre el integrador:

1. **`with open(...)`** al cargar el JSON. Manejo correcto de archivos.
2. **Generador** opcional para iterar productos sin materializar la lista completa (útil cuando el catálogo crece).
3. **Decorador `@log` simple** (opcional) sobre la función principal de carga, para ver el tiempo de operación. No es obligatorio.

Estructura final del integrador al cerrar M2:

```
proyecto-integrador/
├── README.md
├── pyproject.toml
├── data/
│   └── catalogo.json
├── main.py                              ← if __name__ + manejo de errores
└── src/
    └── tiendapro/
        ├── __init__.py
        ├── modelos.py                   ← Producto, Cliente (S08)
        ├── errores.py                   ← TiendaProError + sub-clases (S07)
        ├── catalogo.py                  ← carga con `with`, generadores (S09)
        └── presentacion.py              ← imprimir tabla
```

Al verificar que todo corre, hacemos:

```bash
git add code/proyecto-integrador
git commit -m "feat(proyecto-integrador): cierra M2 con paquete real (proyecto-m2)"
git tag proyecto-m2
```

## 7. Resumen

1. **Funciones son objetos.** Esto es el pilar de los decoradores.
2. **Decorador = función que toma función y devuelve función.** `@decorador` es solo azúcar. Siempre con `functools.wraps`.
3. **Generador = función con `yield`.** Lazy. Para archivos grandes, pipelines, secuencias infinitas, memoria constante.
4. **Context manager = `__enter__` + `__exit__`.** Se usa con `with`. La forma correcta de manejar recursos. `@contextmanager` para casos simples.
5. **El `with` reemplaza el 99% de los `try/finally` de S07.**
6. **Si lo ves en código ajeno, ahora lo entiendes.** Eso es lo que separaba a un programador junior de uno que puede leer una librería real.

## 8. Preguntas de auto-evaluación

1. ¿Qué hace `@decorador` arriba de una `def`? Reescríbelo sin la sintaxis `@`.
2. ¿Por qué `@functools.wraps(func)` es importante? ¿Qué se rompe sin él?
3. Diferencia entre una función con `return` y una con `yield`. Da un ejemplo de cada una.
4. Tienes un archivo de 10 GB. Escribe en pseudocódigo cómo procesarlo línea a línea sin agotar la memoria.
5. ¿Cuál es la diferencia entre `[x * x for x in range(N)]` y `(x * x for x in range(N))`?
6. ¿Qué problema resuelve `with` que el código `open()` + `close()` no resuelve?
7. Define `__enter__` y `__exit__` con tus palabras. ¿Qué recibe `__exit__` cuando el bloque termina sin excepción?
8. ¿Cuándo usarías `@contextmanager` en vez de una clase con `__enter__`/`__exit__`?
9. Escribe un decorador `@cronometro` que mida el tiempo de ejecución de la función decorada e imprima el resultado.
10. Escribe un generador `pares(n)` que produzca los primeros `n` pares positivos.

Cuando puedas responder todas, pasa a [`ejercicios.md`](ejercicios.md).

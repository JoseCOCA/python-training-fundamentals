# S07 — Manejo de errores: try/except, raise y excepciones de dominio

> **Sesión 2h.** ~45 min lectura + ~75 min ejercicios. Esta sesión cambia tu mentalidad: dejas de ver los errores como "código que falla" y empiezas a verlos como **información que el programa te entrega**. Un programa robusto no es uno que no falla — es uno que falla **en el lugar correcto, con el mensaje correcto, en el momento correcto**.

---

## 1. Objetivos de aprendizaje

Al terminar esta sesión vas a poder:

- Explicar qué es una excepción en Python y cómo rompe el flujo normal del programa.
- Usar `try` / `except` / `else` / `finally` con criterio.
- Capturar excepciones **específicas** y nunca `except Exception:` salvo razón fuerte.
- Usar `raise` para propagar errores y `raise from` para encadenar contexto.
- Crear **excepciones de dominio** (clases que heredan de `Exception`) y entender por qué importan.
- Aplicar el principio EAFP — _easier to ask forgiveness than permission_ — y reconocer cuándo `if` defensivo es peor que `try`.
- Identificar antipatrones: `except: pass`, capturar genérico, perder el traceback.

## 2. Prerequisitos

- [S06](../sesion-06-modulos-paquetes/README.md) completa: módulos, paquetes y uv.
- Funciones (S04) — vas a definir funciones que lanzan errores.
- Estructuras (S03) — vas a manejar diccionarios que pueden no tener una clave.

## 3. Conceptos clave

1. **Excepción.** Un objeto que representa una condición anómala. Cuando se lanza, **interrumpe** el flujo del programa y propaga hacia arriba en la pila de llamadas hasta que algo la capture o el programa termine.
2. **Jerarquía.** Todas las excepciones heredan de `BaseException`. Las que tu código maneja heredan de `Exception`. Hay sub-jerarquías: `ValueError`, `TypeError`, `KeyError`, `FileNotFoundError`, etc.
3. **`raise`.** Lanzar una excepción. Puedes lanzar una nueva o re-lanzar la actual.
4. **Excepción de dominio.** Una clase que hereda de `Exception` para representar un error específico de **tu** aplicación: `ProductoNoEncontrado`, `PrecioInvalido`. Hace tu código mucho más legible y robusto.
5. **EAFP vs LBYL.** Dos filosofías. EAFP: intenta y captura si falla. LBYL: chequea antes de actuar. Python prefiere EAFP en la mayoría de casos.

## 4. Teoría

### 4.1. El modelo: una excepción es un objeto que viaja hacia arriba

Cuando una línea de Python falla, no devuelve un código de error. Crea un **objeto excepción** y lo lanza. Ese objeto viaja hacia arriba por las funciones que están corriendo, una por una, hasta que algo lo atrape.

```python
def dividir(a, b):
    return a / b              # ZeroDivisionError si b == 0

def calcular():
    return dividir(10, 0)     # la excepción pasa de aquí hacia arriba

def main():
    print(calcular())          # y de aquí hacia arriba

main()
# ZeroDivisionError: division by zero
```

Si nadie la captura, **el programa termina** y Python imprime el _traceback_: la lista completa de funciones por las que pasó la excepción. **Aprende a leer el traceback de abajo hacia arriba** — la última línea te dice el tipo de error y el mensaje; las anteriores te dicen dónde se originó.

### 4.2. `try` / `except`: capturar la excepción

```python
try:
    resultado = dividir(10, 0)
except ZeroDivisionError:
    resultado = 0
    print("No se puede dividir por cero. Uso 0 como fallback.")
```

**Captura siempre el tipo más específico que conoces.** No esto:

```python
try:
    resultado = dividir(10, 0)
except Exception:               # ❌ atrapa TODO, incluso bugs en tu código
    resultado = 0
```

`except Exception` esconde errores de programación (un typo en un nombre de variable, un `None` donde no debería haberlo) y los confunde con errores de runtime esperados. Resultado: bugs invisibles que el código "absorbe" silenciosamente.

### 4.3. Capturar varios tipos a la vez

```python
try:
    valor = int(entrada_usuario)
except (ValueError, TypeError) as e:
    print(f"Entrada inválida: {e}")
```

`as e` te da acceso al objeto excepción. `e.args`, `str(e)` y los atributos específicos del tipo (por ejemplo `FileNotFoundError.filename`) te dan datos para tomar decisiones o construir mensajes informativos.

### 4.4. `else` y `finally`

```python
try:
    archivo = open("datos.txt")
except FileNotFoundError:
    print("El archivo no existe.")
else:
    # solo corre si NO hubo excepción
    contenido = archivo.read()
finally:
    # corre SIEMPRE (haya excepción o no)
    if "archivo" in dir():
        archivo.close()
```

- **`else`** corre solo si el `try` no lanzó excepción. Útil para separar "lo que puede fallar" de "lo que sigue si todo bien".
- **`finally`** corre siempre. Su uso clásico es liberar recursos (cerrar archivos, conexiones). Veremos en [S09](../sesion-09-decoradores-generadores-context/README.md) que `with` reemplaza el 99% de los `finally` en código moderno.

### 4.5. `raise`: lanzar una excepción

```python
def cobrar(monto: float) -> None:
    if monto <= 0:
        raise ValueError(f"El monto debe ser positivo, recibí {monto}")
    # ... resto del cobro
```

Reglas:

- Lanza el tipo **más específico** que aplique. `ValueError` para valores fuera de rango, `TypeError` para tipos incompatibles, `KeyError` para claves ausentes.
- Pon **información útil** en el mensaje. "Monto inválido" es vago. "El monto debe ser positivo, recibí -50" se debuggea solo.
- No uses `raise Exception("...")` — es como decir "algo salió mal" sin más detalle. Igual de inútil que un `if/else` que solo imprime.

### 4.6. `raise from`: encadenar contexto

A veces capturas una excepción de bajo nivel y quieres lanzar una de tu dominio, sin perder el origen:

```python
class ProductoNoEncontrado(Exception):
    pass

def buscar(catalogo: dict, sku: str) -> dict:
    try:
        return catalogo[sku]
    except KeyError as e:
        raise ProductoNoEncontrado(f"SKU {sku} no existe") from e
```

`raise X from Y` **encadena** las dos excepciones en el traceback. Cuando alguien debuggea, ve tu `ProductoNoEncontrado` y debajo el `KeyError` original. Información completa, sin ocultar nada.

### 4.7. La jerarquía de excepciones de Python

```
BaseException
 ├── SystemExit              ← no la captures (sys.exit)
 ├── KeyboardInterrupt       ← Ctrl+C; no la captures sin razón
 └── Exception               ← raíz de TUS excepciones
      ├── ValueError         ← valor del tipo correcto pero inadecuado
      ├── TypeError          ← tipo equivocado
      ├── LookupError
      │   ├── KeyError       ← clave de dict ausente
      │   └── IndexError     ← índice de lista fuera de rango
      ├── OSError
      │   ├── FileNotFoundError
      │   └── PermissionError
      └── ...
```

**Reglas:**

- Tus excepciones siempre heredan de `Exception` (nunca de `BaseException`).
- `except Exception` atrapa todo lo de "tu" jerarquía. Casi nunca es lo que necesitas — captura específico.
- `KeyboardInterrupt` y `SystemExit` no heredan de `Exception` precisamente para que un `except Exception` no las atrape por accidente.

### 4.8. Excepciones de dominio: clases propias

Una **excepción de dominio** es una clase que hereda de `Exception` para nombrar errores específicos de **tu** aplicación. Compara:

```python
# Versión genérica
def buscar_producto(sku):
    if sku not in catalogo:
        raise ValueError("no encontrado")    # ❌ ¿qué no encontrado?
```

```python
# Versión con dominio
class ProductoNoEncontrado(Exception):
    """Se lanza cuando un SKU no existe en el catálogo."""

def buscar_producto(sku):
    if sku not in catalogo:
        raise ProductoNoEncontrado(f"SKU {sku} no existe en catálogo")
```

**Por qué importa:**

- **Trazabilidad.** Quien lee el código entiende inmediatamente qué error es.
- **Captura específica.** Otros módulos pueden hacer `except ProductoNoEncontrado` sin atrapar errores no relacionados.
- **Documentación viva.** El nombre de la clase _es_ documentación.

**Patrón típico — base de dominio + sub-clases:**

```python
class TiendaProError(Exception):
    """Base de todas las excepciones de TiendaPro."""

class ProductoNoEncontrado(TiendaProError): ...
class CatalogoInvalido(TiendaProError): ...
class StockInsuficiente(TiendaProError): ...
```

Quien quiere atrapar "cualquier cosa del dominio TiendaPro" hace `except TiendaProError`. Quien quiere atrapar lo específico, atrapa la sub-clase. Lo mejor de los dos mundos.

### 4.9. EAFP vs LBYL: la filosofía Python

Dos formas de manejar "puede fallar":

**LBYL — Look Before You Leap (chequea antes):**

```python
if "precio" in producto and isinstance(producto["precio"], (int, float)):
    total = producto["precio"] * cantidad
else:
    total = 0
```

**EAFP — Easier to Ask Forgiveness than Permission (intenta y captura):**

```python
try:
    total = producto["precio"] * cantidad
except (KeyError, TypeError):
    total = 0
```

Python prefiere EAFP por varias razones:

- **Es más legible:** una sola intención (calcular el total) en lugar de tres condiciones encadenadas.
- **Es más correcto:** no hay condiciones de carrera entre el chequeo y el uso. Imagina que `producto` viene de otro hilo o de un archivo que cambió entre el `if` y el cálculo — LBYL falla, EAFP no.
- **Es más rápido en el caso feliz:** el `try` no tiene costo cuando no hay excepción. El `if` siempre evalúa.

**Cuándo LBYL sigue teniendo sentido:** validaciones tempranas en los bordes (input de usuario, datos externos), donde quieres mensajes claros antes de empezar el procesamiento.

### 4.10. El antipatrón de los antipatrones: `except: pass`

```python
try:
    operacion_critica()
except:           # ❌❌❌
    pass
```

Esto:

1. Atrapa **todo**, incluido `KeyboardInterrupt` (no puedes cancelar con Ctrl+C).
2. Descarta el error sin loggearlo, sin levantarlo, sin actuar.
3. Convierte un bug en silencio en silencio.

**Regla absoluta:** un `except` siempre debe hacer **algo** (logear, recuperar, transformar y re-lanzar). Si no sabes qué hacer, no captures. Es mejor que el programa muera con un traceback claro que que siga corriendo en estado corrupto.

## 5. Patrones y antipatrones

| ✅ Patrón | ❌ Antipatrón |
|---|---|
| `except KeyError:` (específico) | `except:` o `except Exception:` |
| Mensaje con datos: `raise ValueError(f"recibí {x}")` | `raise Exception("error")` |
| Excepciones de dominio (`ProductoNoEncontrado`) | Reutilizar `ValueError` para todo |
| `raise X from e` para preservar el origen | Capturar y re-lanzar perdiendo el traceback |
| EAFP cuando el caso feliz es la norma | LBYL con cinco `if` encadenados |
| `try` envolviendo solo lo que puede fallar | `try` envolviendo bloques gigantes "por si acaso" |
| `finally` (o mejor `with`) para liberar recursos | Asumir que el `close()` siempre se ejecuta |
| Logear antes de re-lanzar | `except: pass` |

## 6. Conexión con el proyecto integrador — Camino al hito M2

En [S06](../sesion-06-modulos-paquetes/README.md) refactorizaste `main.py` a un paquete con `catalogo.py` y `presentacion.py`. Hoy vas a **agregarle errores de dominio**:

```
src/tiendapro/
├── __init__.py
├── catalogo.py
├── errores.py            ← NUEVO
└── presentacion.py
```

`errores.py` va a tener al menos:

```python
class TiendaProError(Exception):
    """Base de todas las excepciones del dominio TiendaPro."""

class CatalogoInvalido(TiendaProError):
    """Se lanza cuando el archivo de catálogo no se puede leer o parsear."""

class ProductoNoEncontrado(TiendaProError):
    """Se lanza cuando se busca un producto que no existe."""
```

`catalogo.py` deja de devolver `None` o lista vacía cuando algo falla — **lanza** `CatalogoInvalido` con un mensaje útil. `main.py` envuelve la operación principal en un `try` y muestra un mensaje legible al usuario en lugar de un traceback.

Esto NO es el hito M2 todavía. El hito cierra al final de S09, cuando el paquete tenga clases (S08) y use generadores/`with` (S09).

## 7. Resumen

1. **Una excepción es un objeto que rompe el flujo y viaja hacia arriba.** Hasta que algo la atrape o el programa muera con traceback.
2. **Captura específico, nunca genérico.** `except KeyError:`, no `except Exception:`. Los errores genéricos esconden bugs.
3. **`raise from` preserva el origen.** Cuando traduces un error de bajo nivel a uno de tu dominio, encadena con `from`.
4. **Excepciones de dominio = código legible.** Hereda de `Exception`. Crea una base por proyecto y sub-clases por caso.
5. **EAFP es la filosofía Python.** Intenta, captura específico, recupera. Mejor que cinco `if` defensivos.
6. **`except: pass` es la línea más peligrosa que vas a escribir.** Nunca silencies un error sin razón fuerte y documentada.

## 8. Preguntas de auto-evaluación

1. ¿Cuál es la diferencia entre `BaseException` y `Exception` y por qué tus clases siempre deberían heredar de `Exception`?
2. ¿Qué problema tiene `except Exception:` como captura por defecto?
3. Tu función llama a `dict[clave]` y la clave no existe. ¿Qué tipo concreto de excepción se lanza?
4. Diferencia entre `else` y `finally` en un `try`. Da un ejemplo de cuándo usarías cada uno.
5. ¿Qué hace `raise NuevoError(...) from e`? ¿Por qué es mejor que `raise NuevoError(...)` sin más?
6. Define EAFP con tus palabras y muestra un ejemplo donde EAFP es más limpio que LBYL.
7. ¿Qué hace exactamente `except: pass` y por qué es peligroso?
8. Estás escribiendo una librería de pagos. Diseña tres excepciones de dominio sensatas para ella, con su jerarquía.
9. ¿Por qué `KeyboardInterrupt` no hereda de `Exception`?
10. Tienes este código:
    ```python
    try:
        valor = lista[5]
    except (IndexError, KeyError):
        valor = None
    ```
    ¿Está mal? ¿Por qué?

Cuando puedas responder todas, pasa a [`ejercicios.md`](ejercicios.md).

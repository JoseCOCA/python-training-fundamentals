# S09 — Ejercicios

> **Tiempo estimado:** ~75 min. Tres bloques: ejercicio guiado armando un mini pipeline de logs con generadores + context manager + decorador, libres para entrenar reflejos, reto, y cierre del hito M2.

---

## 0. Antes de empezar

Tu sandbox vive en `code/m02-python-intermedio/sesion-09/`. Si todavía no lo corriste:

```bash
cd code/m02-python-intermedio/sesion-09
uv run python main.py
```

Confirma que ves las tres demos. Después regresa a este documento.

## 1. Ejercicio guiado — Mini pipeline de logs

Vas a procesar un archivo de logs combinando:

- un **decorador** `@cronometro` para medir cuánto tarda la operación,
- **generadores** para procesar línea a línea sin cargar todo en memoria,
- un **context manager** para abrir el archivo correctamente.

### Paso 1.1 — Crear el sandbox del ejercicio

```bash
cd code/m02-python-intermedio
uv init --no-readme --bare ejercicio-09
cd ejercicio-09
```

Crea un archivo `app.log` con contenido sintético:

```bash
cat > app.log <<'EOF'
2026-05-04 10:00:00 INFO server started
2026-05-04 10:00:05 DEBUG request /health
2026-05-04 10:00:10 ERROR database connection lost
2026-05-04 10:00:11 INFO retrying
2026-05-04 10:00:12 ERROR connection still failing
2026-05-04 10:00:15 INFO database back online
2026-05-04 10:00:20 WARN slow query detected
2026-05-04 10:00:25 ERROR timeout in /api/orders
2026-05-04 10:00:30 INFO orders cleaned up
EOF
```

### Paso 1.2 — Decorador `@cronometro`

Crea `pipeline.py`:

```python
import functools
import time


def cronometro(funcion):
    @functools.wraps(funcion)
    def envoltorio(*args, **kwargs):
        inicio = time.perf_counter()
        resultado = funcion(*args, **kwargs)
        duracion = time.perf_counter() - inicio
        print(f"[{funcion.__name__}] tardó {duracion:.4f}s")
        return resultado
    return envoltorio
```

### Paso 1.3 — Pipeline de generadores

Sigue en `pipeline.py`:

```python
def leer_lineas(ruta: str):
    """Generador: una línea a la vez, sin cargar el archivo completo."""
    with open(ruta, encoding="utf-8") as f:
        for linea in f:
            yield linea.rstrip()


def filtrar(lineas, nivel: str):
    """Generador: filtra las líneas que tienen el nivel pedido."""
    for linea in lineas:
        if f" {nivel} " in linea:
            yield linea


def extraer_mensaje(lineas):
    """Generador: deja solo el mensaje (lo que viene después del nivel)."""
    for linea in lineas:
        partes = linea.split(maxsplit=3)
        if len(partes) >= 4:
            yield partes[3]
```

### Paso 1.4 — Composición y ejecución

Sigue en `pipeline.py`:

```python
@cronometro
def errores_de(ruta: str) -> list[str]:
    return list(extraer_mensaje(filtrar(leer_lineas(ruta), "ERROR")))


if __name__ == "__main__":
    mensajes = errores_de("app.log")
    print(f"\n{len(mensajes)} errores encontrados:")
    for m in mensajes:
        print(f"  - {m}")
```

Córrelo:

```bash
uv run python pipeline.py
```

Output esperado:

```
[errores_de] tardó 0.0001s

3 errores encontrados:
  - database connection lost
  - connection still failing
  - timeout in /api/orders
```

### Paso 1.5 — Reflexionar

- **¿Cuándo se abre y cuándo se cierra el archivo?** El `with open(...)` se abre cuando el generador se itera por primera vez y se cierra cuando se agota. Esto pasa **dentro** de `list(...)`. Si interrumpieras el bucle a mitad, el archivo seguiría abierto hasta que el generador fuera recolectado por el GC. Para casos críticos, se materializa con `list()` lo antes posible o se itera dentro del `with` directamente.
- **¿Por qué el pipeline es más legible que un solo bucle gigante?** Cada generador hace **una cosa**. Compón las que necesites para cada caso de uso. Reusable, testeable, sin estado escondido.
- **¿Por qué `@cronometro` está solo arriba de `errores_de`?** Porque mide la operación **completa**, no cada paso intermedio. Decorar cada generador no daría más información — todo el trabajo pasa cuando consumes el resultado final.

## 2. Ejercicios libres

### 2.1. Decorador `@retry`

Escribe un decorador `retry(intentos=3, espera=1.0)` que:

- Reintente la función decorada hasta `intentos` veces si lanza una excepción.
- Espere `espera` segundos entre intentos (`time.sleep`).
- Loguee cada reintento (`print(f"intento {n} falló: {e}")`).
- Si después de `intentos` sigue fallando, **re-lanza la última excepción**.

Pista: este decorador toma argumentos, así que es una **fábrica de decoradores** — una función que devuelve un decorador que devuelve un envoltorio. Tres niveles. Si te trabas, busca "Python decorator with arguments" y entiéndelo antes de copiar.

### 2.2. Context manager con `@contextmanager`

Escribe `cwd_temporal(ruta)` que:

- Recuerda el directorio actual (`os.getcwd()`).
- Cambia al `ruta` que recibe (`os.chdir`).
- Cuando se sale del `with`, vuelve al directorio original — incluso si hubo excepción.

Uso:

```python
with cwd_temporal("/tmp"):
    print(os.getcwd())   # /tmp
print(os.getcwd())       # vuelve al original
```

Pista: usa `try/finally` alrededor del `yield`.

### 2.3. Generador para Fibonacci infinito

Escribe `fibonacci()` (sin argumentos) que produzca **infinitos** números Fibonacci. Después usa `itertools.islice` para tomar solo los primeros 10:

```python
import itertools
print(list(itertools.islice(fibonacci(), 10)))
# → [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
```

Reflexiona: ¿podrías hacerlo con una lista? ¿Por qué un generador es la herramienta correcta?

### 2.4. `with` que no es archivo

Lee la doc de `unittest.mock.patch` y experimenta:

```python
from unittest.mock import patch

with patch("module.func") as mock_func:
    mock_func.return_value = "fake"
    # aquí `module.func()` devuelve "fake"
# afuera del with, vuelve a su comportamiento original
```

¿Qué context manager está pasando ahí? ¿Qué hace su `__enter__`? ¿Y su `__exit__`? No es código de archivos — es un buen ejemplo del patrón aplicado a otra cosa.

### 2.5. Decorador con cache

Define una función `factorial(n)` recursiva. Decórala con `@functools.cache`. Mide con `time.perf_counter` la diferencia entre `factorial(500)` la primera vez y la segunda vez. Explica con tus palabras qué pasó.

## 3. Reto

Construye una mini-librería de **observabilidad** con tres herramientas:

1. **Decorador `@log_args`** que imprime los argumentos con que se llamó la función y el resultado. Usa `functools.wraps`.
2. **Decorador `@medir(unidad="ms")`** que mide tiempo de ejecución en milisegundos o segundos según la unidad. Es una fábrica de decoradores.
3. **Context manager `bloque(nombre)`** (con `@contextmanager`) que mide y loguea el tiempo de un bloque de código:
   ```python
   with bloque("carga de catalogo"):
       cargar(...)
       procesar(...)
   ```

Apílalos:

```python
@log_args
@medir(unidad="ms")
def operacion_costosa(x, y):
    return x ** y
```

Cuando termines, ejecuta `operacion_costosa(2, 30)` y observa el orden de los logs. ¿En qué orden se aplican los decoradores? ¿Por qué?

## 4. Aporte al proyecto integrador — Cierre del hito M2

**Ahora cerramos M2.** El integrador queda como paquete real con clases, errores, manejo correcto de archivos.

### 4.1. Estado al iniciar

Si seguiste los aportes de S06, S07 y S08, el integrador ya tiene:

- `src/tiendapro/{__init__.py, modelos.py, errores.py, catalogo.py, presentacion.py}`
- `main.py` con `if __name__ == "__main__":`
- Modelos como `@dataclass(frozen=True)`.
- Excepciones de dominio (`TiendaProError`, `CatalogoInvalido`, `ProductoNoEncontrado`).

Si no completaste los aportes anteriores, dedica los primeros minutos a ponerte al día. M2 cierra con todo eso integrado.

### 4.2. Cambios de S09

**a) `with` al cargar el JSON.** En `src/tiendapro/catalogo.py`:

```python
import json
from pathlib import Path

from tiendapro.errores import CatalogoInvalido
from tiendapro.modelos import Producto


def cargar(ruta: Path) -> list[Producto]:
    try:
        with ruta.open(encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError as e:
        raise CatalogoInvalido(f"Archivo de catálogo no encontrado: {ruta}") from e
    except json.JSONDecodeError as e:
        raise CatalogoInvalido(f"JSON inválido en {ruta}: {e.msg}") from e

    if not isinstance(data, list):
        raise CatalogoInvalido(
            f"El catálogo debe ser una lista, recibí {type(data).__name__}"
        )

    productos = []
    for i, item in enumerate(data):
        try:
            productos.append(
                Producto(
                    sku=item["sku"],
                    nombre=item["nombre"],
                    precio=float(item["precio"]),
                    stock=int(item["stock"]),
                )
            )
        except (KeyError, TypeError, ValueError) as e:
            raise CatalogoInvalido(
                f"Producto inválido en posición {i}: {e}"
            ) from e

    return productos
```

**b) Generador para iterar disponibles.** En el mismo archivo:

```python
from collections.abc import Iterable, Iterator


def disponibles(productos: Iterable[Producto]) -> Iterator[Producto]:
    """Generador: produce productos disponibles, uno a la vez."""
    for p in productos:
        if p.disponible():
            yield p
```

**c) Decorador opcional para timing en `main.py`.** Si lo agregas, mantenlo simple:

```python
import functools
import time


def cronometro(funcion):
    @functools.wraps(funcion)
    def envoltorio(*args, **kwargs):
        inicio = time.perf_counter()
        try:
            return funcion(*args, **kwargs)
        finally:
            print(f"[{funcion.__name__}] {time.perf_counter() - inicio:.4f}s",
                  flush=True)
    return envoltorio
```

Decora tu `main()` con `@cronometro` para ver cuánto tarda la operación completa.

**d) `main.py` final.**

```python
import sys
from pathlib import Path

from tiendapro import (
    CatalogoInvalido,
    TiendaProError,
    catalogo,
    presentacion,
)


def main() -> int:
    ruta = Path(__file__).parent / "data" / "catalogo.json"
    try:
        productos = catalogo.cargar(ruta)
        disponibles = list(catalogo.disponibles(productos))
        ordenados = sorted(disponibles, key=lambda p: p.precio)
        presentacion.imprimir_tabla(ordenados)
        total = sum(p.valor_total() for p in ordenados)
        print(f"\nValor total del inventario disponible: ${total:.2f}")
    except TiendaProError as e:
        print(f"Error en TiendaPro: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

### 4.3. Verificar

```bash
cd code/proyecto-integrador
uv run python main.py
```

El output debe ser equivalente al hito M1 (la tabla y el total). Si algo se rompe, **léelo con calma**: probablemente sea un import o una clave que cambió de nombre.

### 4.4. Commit y tag

```bash
git add code/proyecto-integrador
git commit -m "feat(proyecto-integrador): cierra M2 con paquete real (proyecto-m2)"
git tag proyecto-m2
git push origin main
git push origin proyecto-m2
```

**Felicitaciones — terminaste el Módulo 2.** El integrador ahora es un paquete real con dominio modelado, errores explícitos, archivos manejados correctamente y estructura escalable. La siguiente parada (M3) le agrega tipado estricto, validación con pydantic y herramientas de calidad de código (ruff, mypy).

---

Cuando termines, vuelve al README y responde las preguntas de auto-evaluación. Si todas se contestan sin dudar, M2 está consolidado y puedes pasar a [M3 — Tipado y calidad de código](../../03-tipado-calidad/) (cuando esté publicado).

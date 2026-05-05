# S07 — Ejercicios

> **Tiempo estimado:** ~75 min. Tres bloques: (1) ejercicio guiado donde construyes una mini-API que falla bien, (2) ejercicios libres para entrenar reflejos, (3) reto, (4) aporte al integrador agregando errores de dominio.

---

## 0. Antes de empezar

Tu sandbox vive en `code/m02-python-intermedio/sesion-07/`. Si todavía no lo corriste:

```bash
cd code/m02-python-intermedio/sesion-07
uv run python main.py
```

Confirma que ves cinco demos numeradas. Después regresa a este documento.

## 1. Ejercicio guiado — Una mini-API de inventario que falla bien

Vamos a construir una pequeña función `obtener_precio(catalogo, sku)` y a hacer que falle de forma **útil** en cada caso.

### Paso 1.1 — Versión ingenua (la que NO debes escribir)

```python
def obtener_precio(catalogo, sku):
    return catalogo[sku]["precio"]
```

¿Qué pasa si:

- el `sku` no existe?
- el producto existe pero no tiene la clave `precio`?
- `catalogo` es `None`?

Pruébalo en una sesión Python:

```python
catalogo = {"A001": {"nombre": "Auriculares", "precio": 89.99}}
print(obtener_precio(catalogo, "Z999"))    # KeyError genérico
```

El traceback te dice "KeyError: 'Z999'", pero **no dice si el problema fue el SKU o la clave 'precio'**. Para quien usa tu librería, esto es información incompleta.

### Paso 1.2 — Versión con excepciones de dominio

```python
class CatalogoError(Exception):
    """Base de los errores del catálogo."""

class ProductoNoEncontrado(CatalogoError):
    """Se lanza cuando el SKU no existe."""

class ProductoIncompleto(CatalogoError):
    """Se lanza cuando un producto existe pero le falta información."""


def obtener_precio(catalogo: dict, sku: str) -> float:
    if catalogo is None:
        raise ValueError("catalogo no puede ser None")

    try:
        producto = catalogo[sku]
    except KeyError as e:
        raise ProductoNoEncontrado(f"SKU {sku!r} no existe en el catálogo") from e

    try:
        return float(producto["precio"])
    except KeyError as e:
        raise ProductoIncompleto(
            f"El producto {sku!r} no tiene precio definido"
        ) from e
    except (TypeError, ValueError) as e:
        raise ProductoIncompleto(
            f"El precio del producto {sku!r} no es un número: {producto.get('precio')!r}"
        ) from e
```

Prueba los tres casos:

```python
catalogo = {
    "A001": {"nombre": "Auriculares", "precio": 89.99},
    "A002": {"nombre": "Cable USB"},               # falta precio
    "A003": {"nombre": "Cargador", "precio": "doce"},  # precio inválido
}

obtener_precio(catalogo, "A001")   # → 89.99
obtener_precio(catalogo, "Z999")   # → ProductoNoEncontrado: SKU 'Z999' no existe ...
obtener_precio(catalogo, "A002")   # → ProductoIncompleto: ... no tiene precio definido
obtener_precio(catalogo, "A003")   # → ProductoIncompleto: ... no es un número: 'doce'
```

### Paso 1.3 — Reflexionar

Compara las dos versiones desde el punto de vista de un consumidor:

| | Versión ingenua | Versión con dominio |
|---|---|---|
| Mensaje al fallar | `KeyError: 'Z999'` | `ProductoNoEncontrado: SKU 'Z999' no existe...` |
| ¿Puedo capturar solo "no encontrado"? | difícil — `except KeyError` también atrapa el `precio` ausente | sí — `except ProductoNoEncontrado` |
| ¿El traceback original se preserva? | sí (no hay encadenamiento) | sí (gracias a `raise from`) |
| Líneas de código | 2 | ~25 |

Las 25 líneas no son "más complejidad" — son **información estructurada** que el código mismo es. Cuando un compañero o tu yo de seis meses lea esa función, entiende todos los modos de falla solo leyendo los tipos de excepción.

## 2. Ejercicios libres

### 2.1. EAFP vs LBYL

Reescribe esta función LBYL en estilo EAFP:

```python
def imprimir_total(carrito: list[dict]) -> None:
    total = 0
    for item in carrito:
        if isinstance(item, dict) and "precio" in item and "cantidad" in item:
            if isinstance(item["precio"], (int, float)) and isinstance(item["cantidad"], int):
                total += item["precio"] * item["cantidad"]
            else:
                print(f"Item con tipos inválidos: {item}")
        else:
            print(f"Item incompleto: {item}")
    print(f"Total: ${total:.2f}")
```

La versión EAFP debería tener menos líneas y leerse "naturalmente": calcular el total; si un item falla, reportar y seguir.

### 2.2. Encadenar excepciones correctamente

Tienes esta función:

```python
def cargar_config(ruta: str) -> dict:
    import json
    with open(ruta) as f:
        return json.load(f)
```

Reescríbela de forma que:

- Si el archivo no existe, lance `ConfigError("Archivo de config no encontrado: <ruta>")`.
- Si el archivo existe pero tiene JSON mal formado, lance `ConfigError("Config con JSON inválido: <ruta>")`.
- En ambos casos, el traceback debe **encadenar** la excepción original con `from`.

### 2.3. La trampa del `except: pass`

Lee este código y explica con tus palabras qué tres problemas concretos tiene:

```python
def procesar_archivos(rutas):
    resultados = []
    for ruta in rutas:
        try:
            with open(ruta) as f:
                resultados.append(f.read())
        except:
            pass
    return resultados
```

(Pista: piensa en Ctrl+C, en bugs de tipeo y en debugging.)

### 2.4. Jerarquía de dominio

Diseña una jerarquía de excepciones para una librería de **autenticación**. Mínimo:

- una clase base
- al menos tres sub-clases para casos distintos (credenciales inválidas, usuario bloqueado, token expirado, por ejemplo)

Documenta cada una con un docstring de una línea. Después escribe una función que las use y un consumidor que capture la base **y** una sub-clase específica para mostrar mensajes diferentes al usuario.

### 2.5. `else` y `finally` en práctica

Escribe una función `leer_lineas(ruta)` que:

- abra el archivo
- si el `open` falla, lance una excepción de dominio `ArchivoInaccesible`
- si la lectura tuvo éxito, devuelva la lista de líneas
- en cualquier caso, imprima `"Operación finalizada para <ruta>"` antes de devolver o lanzar

Resuelve con `try / except / else / finally`. Después reescríbela usando `with` (vas a ver context managers en S09; intenta intuir la diferencia).

## 3. Reto

Toma el sandbox de S06 (`code/m02-python-intermedio/sesion-06/`), específicamente el paquete `tienda/`, y agrega un módulo `tienda/errores.py` con una jerarquía de dominio:

- `TiendaError` (base)
- `ProductoNoEncontrado`
- `ClienteNoEncontrado`
- `EmailInvalido`

Modifica `tienda/productos.py` y `tienda/clientes.py` para usarlas:

- `crear` cliente debe validar el formato del email (mínimo: contiene `@` y al menos un `.` después). Si no, lanza `EmailInvalido`.
- Agrega una función `obtener(sku)` en `productos.py` que devuelva un producto por SKU o lance `ProductoNoEncontrado`.
- En `main.py`, captura las excepciones específicas y muestra mensajes diferenciados al usuario.

Cuando termines, lee tu propio código:

- ¿Las excepciones se llaman como el problema, no como la solución? (Bien: `ProductoNoEncontrado`. Mal: `ErrorDeProducto`.)
- ¿Los mensajes incluyen los datos relevantes (qué SKU, qué email)?
- ¿Usaste `raise from` cuando traduciste un error de bajo nivel?

## 4. Aporte al proyecto integrador

En S06 dejaste el integrador con `src/tiendapro/catalogo.py` y `src/tiendapro/presentacion.py`. Hoy le agregas el módulo de errores y los conecta.

### 4.1. Crear `src/tiendapro/errores.py`

```python
"""Excepciones de dominio de TiendaPro."""


class TiendaProError(Exception):
    """Base de todas las excepciones del dominio TiendaPro."""


class CatalogoInvalido(TiendaProError):
    """El archivo de catálogo no se puede leer o parsear."""


class ProductoNoEncontrado(TiendaProError):
    """No existe un producto con el identificador buscado."""
```

### 4.2. Conectar en `catalogo.py`

La función que carga el JSON deja de devolver `None` o lista vacía cuando algo falla. Ahora:

- Si el archivo no existe → `CatalogoInvalido(f"Archivo no encontrado: {ruta}")`.
- Si el JSON está mal formado → `CatalogoInvalido(f"JSON inválido en {ruta}")`.
- Si la estructura no tiene la lista esperada → `CatalogoInvalido(...)`.

Usa `raise X from e` en cada `try/except` para preservar el traceback original.

### 4.3. Conectar en `main.py`

El punto de entrada captura el `TiendaProError` base y muestra un mensaje legible al usuario:

```python
def main() -> None:
    try:
        productos = catalogo.cargar(Path("data/catalogo.json"))
        productos_disponibles = catalogo.filtrar_disponibles(productos)
        productos_ordenados = catalogo.ordenar_por_precio(productos_disponibles)
        presentacion.imprimir_tabla(productos_ordenados)
    except TiendaProError as e:
        print(f"Error en TiendaPro: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
```

### 4.4. Probar los modos de falla

Crea (temporalmente, no commitees) los siguientes casos y confirma que cada uno produce un mensaje claro:

1. Renombra `data/catalogo.json` a `catalogo.bak` → debería decir "Archivo no encontrado".
2. Modifica `catalogo.json` borrando una llave `}` final → debería decir "JSON inválido".
3. Reemplaza el contenido por `{"productos": "esto no es una lista"}` → debería decir que la estructura es inválida.

Después restaura el JSON correcto antes de commitear.

### 4.5. Commit

```bash
git add code/proyecto-integrador
git commit -m "feat(proyecto-integrador): agrega errores de dominio TiendaProError"
```

> **Importante:** sigue siendo trabajo intermedio. El hito M2 cierra al final de S09 con el commit final + tag `proyecto-m2`.

---

Cuando termines, vuelve al README y responde las preguntas de auto-evaluación. Si todas se contestan sin dudar, pasa a [S08 — OOP, clases y dataclasses](../sesion-08-oop-dataclasses/README.md).

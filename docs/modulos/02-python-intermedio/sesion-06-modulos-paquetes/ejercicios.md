# S06 — Ejercicios

> **Tiempo estimado:** ~75 min. El ejercicio guiado te lleva de un script monolítico a un paquete real. Los ejercicios libres te entrenan los reflejos. El reto consolida lo aprendido. Y el aporte al integrador deja a TiendaPro Lite preparada para el resto de M2.

---

## 0. Antes de empezar

Tu sandbox vive en `code/m02-python-intermedio/sesion-06/`. Si todavía no lo corriste:

```bash
cd code/m02-python-intermedio/sesion-06
uv run python main.py
```

Confirma que ves las cuatro secciones de demo. Después regresa a este documento.

## 1. Ejercicio guiado — De script a paquete

Vamos a tomar un único `main.py` que hace varias cosas y partirlo en módulos. Es el camino que vas a recorrer en el integrador la próxima sesión.

### Paso 1.1 — Crear el proyecto

```bash
cd code/m02-python-intermedio
uv init --no-readme --bare ejercicio-06
cd ejercicio-06
```

Verifica que se creó `pyproject.toml` y nada más:

```bash
ls -la
```

### Paso 1.2 — Escribir el monolito

Crea `monolito.py`:

```python
# monolito.py

PRODUCTOS = [
    {"nombre": "Auriculares", "precio": 89.99, "stock": 5},
    {"nombre": "Cable USB", "precio": 12.50, "stock": 0},
    {"nombre": "Cargador", "precio": 24.00, "stock": 12},
]


def disponibles(productos: list[dict]) -> list[dict]:
    return [p for p in productos if p["stock"] > 0]


def por_precio(productos: list[dict]) -> list[dict]:
    return sorted(productos, key=lambda p: p["precio"])


def imprimir(productos: list[dict]) -> None:
    print(f"{'Producto':<15} {'Precio':>8} {'Stock':>6}")
    print("-" * 31)
    for p in productos:
        print(f"{p['nombre']:<15} ${p['precio']:>7.2f} {p['stock']:>6}")


if __name__ == "__main__":
    imprimir(por_precio(disponibles(PRODUCTOS)))
```

Córrelo:

```bash
uv run python monolito.py
```

Funciona, pero **mete tres responsabilidades en un mismo archivo**: datos, lógica de negocio y presentación. Vamos a separarlas.

### Paso 1.3 — Crear el paquete

Crea esta estructura:

```
ejercicio-06/
├── monolito.py               (lo dejamos como referencia)
├── pyproject.toml
├── main.py                   (nuevo punto de entrada)
└── catalogo/
    ├── __init__.py
    ├── datos.py
    ├── filtros.py
    └── vista.py
```

Comandos:

```bash
mkdir catalogo
touch catalogo/__init__.py catalogo/datos.py catalogo/filtros.py catalogo/vista.py
touch main.py
```

### Paso 1.4 — Repartir el código

`catalogo/datos.py` — solo los datos:

```python
PRODUCTOS = [
    {"nombre": "Auriculares", "precio": 89.99, "stock": 5},
    {"nombre": "Cable USB", "precio": 12.50, "stock": 0},
    {"nombre": "Cargador", "precio": 24.00, "stock": 12},
]
```

`catalogo/filtros.py` — solo la lógica de negocio:

```python
def disponibles(productos: list[dict]) -> list[dict]:
    return [p for p in productos if p["stock"] > 0]


def por_precio(productos: list[dict]) -> list[dict]:
    return sorted(productos, key=lambda p: p["precio"])
```

`catalogo/vista.py` — solo presentación:

```python
def imprimir(productos: list[dict]) -> None:
    print(f"{'Producto':<15} {'Precio':>8} {'Stock':>6}")
    print("-" * 31)
    for p in productos:
        print(f"{p['nombre']:<15} ${p['precio']:>7.2f} {p['stock']:>6}")
```

`catalogo/__init__.py` — re-exporta lo que el consumidor va a usar:

```python
from catalogo.datos import PRODUCTOS
from catalogo.filtros import disponibles, por_precio
from catalogo.vista import imprimir

__all__ = ["PRODUCTOS", "disponibles", "por_precio", "imprimir"]
```

`main.py` — el orquestador:

```python
from catalogo import PRODUCTOS, disponibles, imprimir, por_precio


def main() -> None:
    productos = por_precio(disponibles(PRODUCTOS))
    imprimir(productos)


if __name__ == "__main__":
    main()
```

### Paso 1.5 — Correr y comparar

```bash
uv run python main.py
```

El output debería ser idéntico al de `monolito.py`. Si no lo es, **ese es el momento de aprender**: lee el error, identifica si es un import roto, un nombre mal escrito o un orden de funciones incorrecto.

### Paso 1.6 — Reflexionar

Comparando los dos enfoques:

| | `monolito.py` | `main.py` + paquete `catalogo/` |
|---|---|---|
| Líneas en el archivo principal | ~25 | ~7 |
| Cuesta cambiar la presentación | tienes que tocar el archivo grande | editas solo `vista.py` |
| Cuesta agregar una fuente de datos nueva | mezclas datos con lógica | agregas un módulo en `catalogo/` |
| Tests | difícil (todo está pegado) | fácil (cada módulo prueba algo concreto) |

Esa diferencia se nota poco con 25 líneas. Con 2.500 te salva la vida.

## 2. Ejercicios libres

### 2.1. El guard en práctica

Agrega al final de `catalogo/vista.py` un `if __name__ == "__main__":` que llame a `imprimir([{"nombre": "demo", "precio": 1.0, "stock": 1}])`.

Pruébalo de dos formas:

```bash
uv run python -m catalogo.vista     # debería imprimir la demo
uv run python main.py                # NO debería imprimir la demo
```

Explica con tus palabras por qué pasa cada cosa.

### 2.2. Las tres formas de importar

Cambia `main.py` para usar las tres formas que viste en la sesión y comprueba que sigue funcionando:

```python
# Forma 1
import catalogo
catalogo.imprimir(catalogo.por_precio(catalogo.disponibles(catalogo.PRODUCTOS)))

# Forma 2
from catalogo import PRODUCTOS, imprimir
# ...

# Forma 3
from catalogo import filtros as f
# ...
```

Decide cuál te resulta más legible **para este caso concreto**. No hay una respuesta universal — escribe en un comentario por qué eligiste esa.

### 2.3. Detectar imports problemáticos

En `catalogo/vista.py` agrega arriba:

```python
from catalogo import *
```

Corre `uv run python main.py`. Vas a obtener un `ImportError` o una recursión circular. Diagnóstica el problema, explícalo con tus palabras y revierte el cambio. **Esa es la razón por la que `import *` es un antipatrón.**

### 2.4. Dependencias declaradas

Sin instalar nada, abre `pyproject.toml` y agrega manualmente:

```toml
dependencies = [
    "httpx>=0.27",
]
```

Ahora corre:

```bash
uv sync
```

Observa que `uv` instala `httpx` y crea/actualiza `uv.lock`. Después, abre Python y comprueba:

```bash
uv run python -c "import httpx; print(httpx.__version__)"
```

Quita `httpx` con `uv remove httpx` y observa que el lockfile se actualiza solo. **Nunca mantengas dependencias a mano cuando uv puede hacerlo por ti.**

### 2.5. Dependencias de desarrollo

Agrega `pytest` solo para desarrollo:

```bash
uv add --dev pytest
```

Mira el `pyproject.toml`: aparece bajo `[dependency-groups].dev`, separada de las dependencias de producción. Esa separación importa cuando despliegas: en producción no instalas tests.

## 3. Reto

Toma el sandbox de `code/m01-python-fundamentos/sesion-04/` (donde practicaste funciones) y refactorízalo a un paquete. Reglas:

- Un módulo por responsabilidad clara (no por función).
- `main.py` con `if __name__ == "__main__":` que llame a una sola función `main()`.
- `__init__.py` re-exportando solo lo que un consumidor externo necesitaría.
- Decide si algunas funciones son **internas** del paquete (privadas, con `_` adelante) y no deberían re-exportarse.
- Documenta cada módulo con un docstring de una línea explicando su responsabilidad.

Cuando termines, abre el `__init__.py` y léelo. Si esa lista de re-exports no le dice a un lector externo qué hace tu paquete, está mal pensado: itera.

## 4. Aporte al proyecto integrador

Este es el primer paso de M2 sobre TiendaPro Lite. **No agregamos lógica nueva** — preparamos la estructura para que las próximas sesiones (errores en S07, OOP en S08) tengan dónde caer.

### 4.1. Mover el código a un paquete

Hoy `code/proyecto-integrador/` se ve así:

```
proyecto-integrador/
├── README.md
├── pyproject.toml
├── data/
│   └── catalogo.json
└── main.py
```

Lo dejamos así:

```
proyecto-integrador/
├── README.md
├── pyproject.toml
├── data/
│   └── catalogo.json
├── main.py                    ← solo punto de entrada
└── src/
    └── tiendapro/
        ├── __init__.py
        ├── catalogo.py        ← carga del JSON, filtrado, ordenado
        └── presentacion.py    ← imprimir la tabla
```

### 4.2. Pasos

1. Crea `src/tiendapro/__init__.py`, `src/tiendapro/catalogo.py`, `src/tiendapro/presentacion.py`.
2. Mueve la lógica de carga y procesamiento del JSON a `catalogo.py`.
3. Mueve la impresión de la tabla a `presentacion.py`.
4. Deja `main.py` con un único `main()` que orquesta y un `if __name__ == "__main__":`.
5. Re-exporta desde `__init__.py` solo lo que `main.py` consume.
6. Para que `src/tiendapro` sea importable, edita `pyproject.toml` agregando:

   ```toml
   [tool.uv]
   package = true

   [build-system]
   requires = ["hatchling"]
   build-backend = "hatchling.build"

   [tool.hatch.build.targets.wheel]
   packages = ["src/tiendapro"]
   ```

   Después corre `uv sync` para que tome la nueva configuración.
7. Verifica que `uv run python main.py` produce el mismo output que antes del refactor. **El test es: el comportamiento no cambia, solo la estructura.**

### 4.3. Commit

```bash
git add code/proyecto-integrador
git commit -m "refactor(proyecto-integrador): convierte main.py monolítico en paquete tiendapro"
```

> **Importante.** Esto NO es el hito M2. El hito M2 cierra al final de la S09, cuando el paquete tenga clases, errores y los demás módulos del integrador. Por ahora, el commit es solo un `refactor(...)` — la convención lo deja claro.

---

Cuando termines los ejercicios libres y el aporte al integrador, valida que entendiste devolviéndote a las **preguntas de auto-evaluación** del README. Si todas se responden sin dudar, estás listo para [S07 — Manejo de errores](../sesion-07-errores/README.md) (próxima sesión del módulo).

# S06 — Módulos, paquetes, imports y virtualenvs con uv

> **Sesión 2h.** ~45 min lectura + ~75 min ejercicios. **Abre el Módulo 2.** Hasta aquí todo el código vivió en un solo archivo. A partir de esta sesión, tu código deja de ser un archivo y empieza a ser un **proyecto**: varios archivos que se importan entre sí, dependencias externas declaradas y un entorno aislado por proyecto. Dominar esto separa al que escribe scripts del que construye software.

---

## 1. Objetivos de aprendizaje

Al terminar esta sesión vas a poder:

- Distinguir un **módulo** de un **paquete** y explicar la diferencia con tus palabras.
- Importar código con las tres formas (`import x`, `from x import y`, `import x as y`) y elegir la correcta según el caso.
- Estructurar un proyecto en varios archivos sin caer en imports circulares.
- Usar el guard `if __name__ == "__main__":` y entender por qué existe.
- Explicar **qué resuelve un virtualenv** y por qué instalar con `pip` a nivel sistema es un antipatrón.
- Manejar un proyecto con **uv**: `uv init`, `uv add`, `uv run`, `uv sync`, `uv lock`.
- Leer y editar un `pyproject.toml` básico.

## 2. Prerequisitos

- Módulo 1 completo: [S01](../../01-python-fundamentos/sesion-01-variables-tipos/README.md) a [S05](../../01-python-fundamentos/sesion-05-strings/README.md).
- En particular: funciones (S04) y estructuras de datos (S03).
- Tener `uv` instalado y haber corrido al menos un proyecto en M1. Si tu setup no está listo, vuelve a [`docs/01-setup.md`](../../../01-setup.md).

## 3. Conceptos clave

1. **Módulo.** Un archivo `.py` cualquiera. Si tienes `utils.py`, eso es un módulo llamado `utils`.
2. **Paquete.** Un directorio que Python trata como una unidad importable. Tradicionalmente contiene un archivo `__init__.py`.
3. **Import.** La instrucción que ejecuta otro módulo y deja sus nombres disponibles para usar.
4. **Virtualenv (entorno virtual).** Una carpeta aislada con su propia copia de Python y sus propias dependencias. Cada proyecto tiene la suya, sin contaminarse entre sí.
5. **uv.** Herramienta única que cubre: instalar versiones de Python, crear virtualenvs, instalar dependencias, mantener un lockfile reproducible y ejecutar tu código dentro del entorno correcto.

## 4. Teoría

### 4.1. Un módulo no es un concepto: es un archivo

Cualquier archivo `.py` es un módulo. No tienes que hacer nada para "convertirlo" en módulo — ya lo es. Lo que necesitas para usarlo desde otro archivo es **importarlo**.

```
proyecto/
├── main.py
└── utils.py
```

Si `utils.py` contiene:

```python
# utils.py
PI = 3.1416

def saludar(nombre: str) -> str:
    return f"Hola, {nombre}"
```

Desde `main.py`, en el mismo directorio:

```python
# main.py
import utils

print(utils.PI)               # → 3.1416
print(utils.saludar("Ana"))   # → "Hola, Ana"
```

El nombre del módulo es **el nombre del archivo sin la extensión**. `utils.py` se importa como `utils`.

### 4.2. Las tres formas de importar (y cuándo usar cada una)

**Forma 1 — `import módulo`** (recomendada por defecto):

```python
import utils

utils.saludar("Ana")
```

**Ventaja:** queda claro de dónde sale `saludar`. Cuando lees el código un mes después, no tienes que adivinar.

**Forma 2 — `from módulo import nombre`** (cuando el origen es obvio o lo usas mucho):

```python
from utils import saludar

saludar("Ana")
```

**Ventaja:** menos verboso. **Riesgo:** si tienes diez `from x import y` arriba del archivo, leer una función deja de ser obvio: ¿`saludar` viene de qué?

**Forma 3 — `import módulo as alias`** (cuando el nombre es largo o hay convención):

```python
import numpy as np
import pandas as pd
```

`np` y `pd` son convenciones del ecosistema científico. Fuera de convenciones establecidas, los alias arbitrarios confunden.

**Antipatrón clásico:**

```python
from utils import *    # ❌ trae TODO lo público de utils, sin que sepas qué
```

`import *` rompe la trazabilidad: una variable `PI` aparece en el archivo y no se sabe de dónde salió. **Nunca lo uses en código tuyo.**

### 4.3. De módulo a paquete: el directorio importable

Un **paquete** es un directorio que Python puede importar como si fuera un módulo. La forma tradicional es agregar un archivo vacío llamado `__init__.py`:

```
proyecto/
├── main.py
└── tienda/
    ├── __init__.py
    ├── productos.py
    └── clientes.py
```

Ahora `tienda` es un paquete. Desde `main.py`:

```python
from tienda import productos, clientes

productos.listar()
clientes.crear("Ana")
```

O bien:

```python
from tienda.productos import listar
from tienda.clientes import crear
```

**Qué hace `__init__.py`:**

- Marca al directorio como paquete (en el modelo tradicional).
- Se ejecuta una vez la primera vez que se importa el paquete.
- Si está vacío, está bien — su sola presencia es suficiente.
- Si pones código adentro, ese código corre al primer import. Útil para **re-exportar** nombres:

```python
# tienda/__init__.py
from tienda.productos import listar
from tienda.clientes import crear
```

Con eso, desde fuera puedes hacer `from tienda import listar, crear` directamente.

> **Nota técnica.** Python 3 acepta también **namespace packages** sin `__init__.py`. Funciona, pero para empezar quédate con la regla simple: **directorio importable → mete un `__init__.py`, aunque esté vacío**. Te ahorra ambigüedades hasta que sepas para qué sirven los namespace packages.

### 4.4. Imports absolutos y relativos

**Absoluto** — escribes la ruta completa desde la raíz del proyecto:

```python
from tienda.productos import listar
```

**Relativo** — escribes la ruta desde el archivo actual con puntos:

```python
# desde dentro de tienda/clientes.py
from .productos import listar           # . = mismo paquete
from ..otro_paquete import algo         # .. = paquete padre
```

**Regla práctica:** **usa imports absolutos**. Son más fáciles de leer, no rompen cuando mueves archivos, y la convención moderna (PEP 8) los recomienda. Los relativos solo tienen sentido dentro de paquetes grandes y profundos, y no es nuestro caso todavía.

### 4.5. El guard `if __name__ == "__main__":`

Cuando Python ejecuta un archivo, le asigna a la variable `__name__` uno de dos valores:

- `"__main__"` si el archivo se está corriendo directamente (`python main.py`).
- el nombre del módulo si se está importando (`import main` lo pone en `"main"`).

Esto permite escribir un módulo que **funciona como librería** y **a la vez como script ejecutable**:

```python
# saludador.py

def saludar(nombre: str) -> str:
    return f"Hola, {nombre}"

if __name__ == "__main__":
    # Esto solo corre si ejecutas: python saludador.py
    # NO corre si haces: from saludador import saludar
    print(saludar("Mundo"))
```

**Por qué importa:** sin el guard, el `print(saludar("Mundo"))` se ejecutaría también cuando otro archivo hiciera `import saludador`. Resultado: efectos secundarios al importar — un dolor de cabeza para depurar.

**Convención:** todo script que tenga un punto de entrada usa el guard. Es uno de los hábitos más reconocibles de código Python profesional.

### 4.6. Cómo encuentra Python los módulos

Cuando escribes `import requests`, Python busca el módulo en una lista ordenada de directorios: `sys.path`. Es esencialmente:

1. El directorio del script que se está ejecutando.
2. Los directorios listados en la variable de entorno `PYTHONPATH` (rara vez usada).
3. Los directorios del **virtualenv activo** (si hay uno).
4. La librería estándar.
5. Los `site-packages` del sistema (paquetes instalados con `pip` global).

```python
import sys
print(sys.path)    # imprime la lista en orden
```

**Consecuencia:** si dos directorios distintos tienen un módulo con el mismo nombre, **gana el primero** de la lista. Por eso un virtualenv aísla: empuja sus directorios al frente y oculta los del sistema.

**Archivos `.pyc` y `__pycache__`:** la primera vez que importas un módulo, Python lo compila a bytecode y lo cachea en `__pycache__/módulo.cpython-312.pyc`. No hace falta tocarlo. Está en `.gitignore` por defecto.

### 4.7. Virtualenvs: el problema que resuelven

Imagina dos proyectos en tu computadora:

- `app-vieja` necesita `requests==2.20`.
- `app-nueva` necesita `requests==2.31` con cambios incompatibles.

Si instalas `requests` con `pip install requests` a nivel de sistema, **solo puede haber una versión a la vez**. Una de las dos apps se rompe.

Un **virtualenv** resuelve esto creando una carpeta (típicamente `.venv/`) con su propia copia de Python y su propio `site-packages/`. Cada proyecto tiene la suya:

```
app-vieja/
├── .venv/        ← su Python + requests 2.20
└── ...

app-nueva/
├── .venv/        ← su Python + requests 2.31
└── ...
```

**Reglas inviolables:**

1. **Nunca instales paquetes con `pip` global.** Solo dentro de un virtualenv.
2. **Cada proyecto tiene su propio virtualenv.** No compartas entornos.
3. **El virtualenv NO va al repo.** Está en `.gitignore`. Lo que va al repo es la lista de dependencias (`pyproject.toml` + lockfile).

### 4.8. uv: una sola herramienta para todo

Históricamente Python necesitaba cuatro herramientas distintas:

- `pyenv` para instalar versiones de Python.
- `venv` o `virtualenv` para crear entornos.
- `pip` para instalar paquetes.
- `pip-tools` o `poetry` para mantener un lockfile reproducible.

**uv reemplaza las cuatro.** Es la herramienta que se usa en este curso porque es lo más cercano a "no pienses en el tooling, escribe código".

**Comandos esenciales** (los que vas a usar todos los días):

| Comando | Qué hace |
|---|---|
| `uv init mi-proyecto` | Crea un proyecto nuevo con `pyproject.toml` y estructura básica |
| `uv add httpx` | Agrega `httpx` a las dependencias e instala |
| `uv add --dev pytest` | Agrega `pytest` solo para desarrollo (no producción) |
| `uv remove httpx` | Quita una dependencia |
| `uv sync` | Instala todas las dependencias declaradas, exactamente como están en el lockfile |
| `uv lock` | Regenera el lockfile (`uv.lock`) |
| `uv run python script.py` | Corre `script.py` dentro del virtualenv del proyecto |
| `uv run pytest` | Igual, para cualquier comando: lo ejecuta en el entorno correcto |

**Detalle clave:** `uv run` se encarga del virtualenv por ti. **No tienes que activar nada manualmente.** Cero `source .venv/bin/activate`. Esto elimina la clase entera de errores "olvidé activar el entorno".

### 4.9. pyproject.toml: la fuente de verdad

`pyproject.toml` es el archivo que describe tu proyecto Python moderno. Reemplaza al viejo `setup.py` y al `requirements.txt`. Ejemplo mínimo:

```toml
[project]
name = "tiendapro"
version = "0.1.0"
description = "TiendaPro Lite: catálogo, clientes, pedidos"
requires-python = ">=3.12"
dependencies = [
    "httpx>=0.27",
    "pydantic>=2.6",
]

[dependency-groups]
dev = [
    "pytest>=8.0",
    "ruff>=0.5",
    "mypy>=1.10",
]
```

**Lo que tienes que entender:**

- `[project]` es estándar (PEP 621). Cualquier herramienta moderna lo lee.
- `dependencies` lista lo que tu app necesita en producción.
- `[dependency-groups].dev` lista lo que solo necesitas mientras desarrollas (tests, linters, type checkers).
- `requires-python` fija un rango de versiones aceptables.
- **Nunca edites a mano las versiones de dependencias** si puedes evitarlo: usa `uv add paquete` y deja que uv resuelva la versión y actualice el lockfile.

**`uv.lock`:** es el archivo que congela las versiones exactas de cada dependencia (y sus dependencias transitivas). Garantiza que tu compañero, tu CI y tu producción instalen **exactamente lo mismo** que tú. Ese archivo **sí va al repo**.

## 5. Patrones y antipatrones

| ✅ Patrón | ❌ Antipatrón |
|---|---|
| `import módulo` y usar `módulo.nombre` | `from módulo import *` |
| Imports absolutos (`from tienda.productos import listar`) | Imports relativos profundos (`from ...otro import x`) |
| `if __name__ == "__main__":` para puntos de entrada | Código suelto en el cuerpo del módulo que corre al importar |
| Un virtualenv por proyecto | Un solo entorno global compartido |
| `uv add paquete` | Editar `pyproject.toml` a mano y olvidar el lockfile |
| `uv run python main.py` | Activar `.venv` manualmente cada vez |
| Commitear `pyproject.toml` y `uv.lock` | Commitear `.venv/` o `__pycache__/` |
| `__init__.py` aunque esté vacío | Asumir que namespace packages "ya funcionan" sin entender el modelo |

## 6. Conexión con el proyecto integrador — Camino al hito M2

En M1 cerraste TiendaPro Lite como **un solo `main.py`** que carga JSON y lista productos. Eso fue suficiente para validar fundamentos.

A lo largo de M2 ese script va a convertirse en un **paquete real** con esta forma:

```
proyecto-integrador/
├── pyproject.toml
├── uv.lock
├── data/
│   └── catalogo.json
├── src/
│   └── tiendapro/
│       ├── __init__.py
│       ├── catalogo.py        ← carga, filtrado, ordenado (S06 + S07)
│       ├── modelos.py         ← clases (S08)
│       └── errores.py         ← excepciones del dominio (S07)
└── main.py                    ← punto de entrada con if __name__ == "__main__"
```

En esta sesión (S06) el aporte concreto al integrador es **partir el `main.py` monolítico en módulos** y dejar la estructura de paquete preparada. No agregamos lógica nueva — refactorizamos. La regla profesional es: **antes de agregar funcionalidad, organiza lo que tienes**.

## 7. Resumen

1. **Módulo es un archivo `.py`. Paquete es un directorio con `__init__.py`.** Las dos cosas se importan igual.
2. **Por defecto, `import módulo` y `módulo.nombre`.** Es el patrón más legible. Evita `from x import *` siempre.
3. **Cada proyecto tiene su propio virtualenv.** Esto no es opcional. `pip install` global es un error.
4. **uv es la única herramienta que necesitas.** `uv init`, `uv add`, `uv run`. Cero activación manual de entornos.

## 8. Preguntas de auto-evaluación

1. ¿Cuál es la diferencia entre un módulo y un paquete?
2. ¿Qué hace `import *` y por qué es un antipatrón?
3. Tienes `tienda/productos.py` con una función `listar()`. Escribe **dos** formas distintas de importar y usar esa función desde `main.py`.
4. ¿Qué imprime un módulo con `print(__name__)` cuando se ejecuta directamente con `python módulo.py`? ¿Y cuando se importa desde otro archivo?
5. ¿Por qué sería un problema poner `print("hola")` directamente en el cuerpo de un módulo (sin guard)?
6. ¿Qué problema concreto resuelve un virtualenv? Da un ejemplo con dos versiones de un paquete.
7. ¿Qué archivo del proyecto **NO** va al repositorio: `pyproject.toml`, `uv.lock`, `.venv/`, `__pycache__/`?
8. ¿Para qué sirve `uv.lock` y por qué tu compañero de equipo tiene que respetarlo?
9. ¿Qué hace `uv run python main.py` que `python main.py` no hace?
10. Tu proyecto necesita `pytest` para correr tests pero NO en producción. ¿Con qué comando lo agregas?

Cuando puedas responder todas sin volver al texto, pasa a [`ejercicios.md`](ejercicios.md).

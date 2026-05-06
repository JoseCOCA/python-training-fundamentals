# S11 — Ejercicios

> **Tiempo estimado:** ~75 min. Tres bloques: ejercicio guiado migrando un `@dataclass` a `BaseModel`, libres para entrenar reflejos sobre validators, ruff y pre-commit; reto, y aporte al integrador que **cierra el hito M3** con tag `proyecto-m3`.

---

## 0. Antes de empezar

Tu sandbox vive en `code/m03-tipado-calidad/sesion-11/`. Si todavía no lo corriste:

```bash
cd code/m03-tipado-calidad/sesion-11
uv sync
uv run python main.py
uv run ruff check .
uv run mypy .
```

Confirma que las cuatro demos imprimen, ruff no reporta nada, mypy pasa limpio. Después regresa a este documento.

## 1. Ejercicio guiado — De `@dataclass` a `BaseModel`

Tomamos el modelo `Producto` que armaste en S08 y lo migramos a pydantic con validación real.

### Paso 1.1 — Versión `@dataclass` (la línea de base)

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class Producto:
    nombre: str
    precio: float
    stock: int


# Esto compila feliz aunque sean datos basura:
p = Producto(nombre="X", precio=-99.0, stock=-5)
print(p)
```

`@dataclass` no cuestiona los valores. `precio = -99` y `stock = -5` no tienen sentido pero Python no lo sabe. mypy tampoco — el tipo es correcto.

### Paso 1.2 — Versión `BaseModel` con validators

```bash
uv add pydantic
```

```python
from pydantic import BaseModel, ConfigDict, field_validator


class Producto(BaseModel):
    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    nombre: str
    precio: float
    stock: int

    @field_validator("nombre")
    @classmethod
    def nombre_no_vacio(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("el nombre no puede estar vacío")
        return v

    @field_validator("precio")
    @classmethod
    def precio_positivo(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("el precio debe ser positivo")
        return v

    @field_validator("stock")
    @classmethod
    def stock_no_negativo(cls, v: int) -> int:
        if v < 0:
            raise ValueError("el stock no puede ser negativo")
        return v


# Caso feliz
print(Producto(nombre="Cable USB", precio=12.5, stock=3))

# Caso de error: pydantic reúne TODOS los problemas en un solo ValidationError
from pydantic import ValidationError
try:
    Producto(nombre="  ", precio=-99.0, stock=-5)
except ValidationError as e:
    print(e)
```

Output esperado del caso de error:

```
3 validation errors for Producto
nombre
  Value error, el nombre no puede estar vacío ...
precio
  Value error, el precio debe ser positivo ...
stock
  Value error, el stock no puede ser negativo ...
```

**Tres bugs detectados de un golpe**, con mensajes que indican el campo exacto y la regla violada. Esa es la diferencia con el `@dataclass`.

### Paso 1.3 — Reflexionar

| | `@dataclass` | `BaseModel` |
|---|---|---|
| ¿Qué hace `Producto(precio=-99)` ? | acepta sin chistar | lanza `ValidationError` |
| ¿Y `Producto(precio="12.5")` con `strict=True`? | acepta y precio queda como `"12.5"` (str) | lanza `ValidationError` |
| Carga desde JSON | hay que parsear y construir a mano | `model_validate_json(raw)` |
| Serializar a JSON | hay que mapear cada campo | `model_dump_json()` |
| Tiempo de construcción | ~más rápido | ~más lento (paga validación) |

**Lección:** `@dataclass` es el modelo interno; `BaseModel` es el modelo de borde. Si tu código va a recibir esos datos del exterior, vale lo que cueste pagar la validación.

## 2. Ejercicios libres

### 2.1. Validator entre campos

Define un `BaseModel` `Reserva` con:

- `huesped: str`
- `entrada: date`
- `salida: date`
- `noches: int`

Usa `@model_validator(mode="after")` para validar:

- `salida > entrada`.
- `noches == (salida - entrada).days`.

Después prueba: `Reserva(huesped="Ana", entrada=date(2026, 5, 10), salida=date(2026, 5, 8), noches=3)`. ¿Cuántos errores reporta?

### 2.2. Cargar desde JSON con manejo de errores

Tienes este JSON:

```json
{"productos": [
  {"nombre": "Cable", "precio": 12.5, "stock": 3},
  {"nombre": "", "precio": -10, "stock": 5},
  {"nombre": "Cargador", "precio": 24.99, "stock": "tres"}
]}
```

Escribe una función `cargar_productos(raw: str) -> list[Producto]` que:

1. Parsea el JSON.
2. Itera la lista de productos.
3. Para cada uno intenta `Producto.model_validate(...)`.
4. Acumula los errores en un dict `{indice: lista_de_errores}` y devuelve los productos que sí validaron.
5. Imprime los errores por consola con el índice del producto y el campo que falló.

Pista: `ValidationError.errors()` te da la lista estructurada.

### 2.3. ruff descubre cosas que mypy no

Crea un archivo `mal_estilo.py`:

```python
from typing import Optional, List

import os
import sys

def f(items: List[Optional[int]] = []):
    for i in range(len(items)):
        if items[i] != None:
            print(items[i])
```

Corre `uv run ruff check .` y léelo. Vas a ver al menos:

- `UP006` (`List` → `list`).
- `UP007` (`Optional[X]` → `X | None`).
- `B006` (default mutable).
- `E711` (`!= None` → `is not None`).
- `F401` (`os`, `sys` no usados).
- `C0200` o equivalente (no usar `range(len(...))`).

Corre `uv run ruff check . --fix` y después `uv run ruff format .`. Compara el archivo antes y después.

### 2.4. Modelos anidados

Define:

```python
class Direccion(BaseModel):
    calle: str
    ciudad: str
    codigo_postal: str


class Cliente(BaseModel):
    nombre: str
    email: str
    direccion: Direccion
```

Prueba:

```python
Cliente.model_validate({
    "nombre": "Ana",
    "email": "ana@example.com",
    "direccion": {"calle": "Calle 1", "ciudad": "Ciudad A", "codigo_postal": "1000"}
})
```

Después intenta pasar `direccion: "no es un dict"`. ¿Qué error reporta? ¿En qué nivel del modelo?

### 2.5. Pre-commit en práctica

En el sandbox del ejercicio:

1. `uv add --dev pre-commit`
2. Crea `.pre-commit-config.yaml` con los hooks de ruff (sin mypy por ahora — mypy en pre-commit suele requerir configuración extra).
3. `uv run pre-commit install`
4. Crea un archivo con `print( "hola"  )` (espacios raros) y commitea.
5. Observa que el hook arregla el formato y rechaza el commit. Vuelve a hacer `git add .` y commitea de nuevo.

## 3. Reto

Construye un mini-validador de configuración para un servicio:

- `BaseModel` `ServerConfig` con: `host: str`, `port: int`, `debug: bool = False`, `allowed_hosts: list[str]`, `database_url: str`.
- Validators:
  - `port` entre 1 y 65535.
  - `host` no puede ser cadena vacía.
  - `database_url` debe empezar con `postgresql://` o `sqlite://`.
  - `allowed_hosts` no puede estar vacío.
- `model_config` con `frozen=True`, `strict=True`, `extra="forbid"`.

Carga la config desde un JSON. Si falla, imprime al usuario los problemas en formato amigable: `[port] valor inválido: 99999 — debe estar entre 1 y 65535`. No imprimas el `ValidationError` crudo.

Si lo terminas, agrega `pydantic-settings` (el módulo hermano) y lee la config también desde variables de entorno como prueba opcional. (Vamos a verlo formalmente en M5.)

## 4. Aporte al proyecto integrador — Cierre del hito M3

**Hoy cierra el Módulo 3.** TiendaPro Lite queda con tipado estricto, validación pydantic y herramientas de calidad pasando limpio.

### 4.1. Configurar dependencias

En `code/proyecto-integrador/pyproject.toml`, agregar pydantic y dev tools:

```toml
[project]
# ...
dependencies = [
    "pydantic>=2.6",
]

[dependency-groups]
dev = [
    "mypy>=1.10",
    "ruff>=0.5",
]

[tool.ruff]
line-length = 100
target-version = "py312"

[tool.ruff.lint]
select = ["E", "W", "F", "I", "B", "UP", "RUF"]

[tool.mypy]
python_version = "3.12"
warn_unused_ignores = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
no_implicit_optional = true
warn_return_any = true
plugins = ["pydantic.mypy"]
```

```bash
cd code/proyecto-integrador
uv sync
```

### 4.2. Migrar `modelos.py` a pydantic

Reemplaza el contenido de `src/tiendapro/modelos.py`:

```python
"""Modelos de dominio de TiendaPro (validación con pydantic)."""

from pydantic import BaseModel, ConfigDict, field_validator


class Producto(BaseModel):
    model_config = ConfigDict(frozen=True, strict=False, extra="forbid")

    nombre: str
    categoria: str
    precio: float
    stock: int
    moneda: str = "USD"

    @field_validator("nombre", "categoria")
    @classmethod
    def texto_no_vacio(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("no puede estar vacío")
        return v

    @field_validator("precio")
    @classmethod
    def precio_positivo(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("el precio debe ser positivo")
        return v

    @field_validator("stock")
    @classmethod
    def stock_no_negativo(cls, v: int) -> int:
        if v < 0:
            raise ValueError("el stock no puede ser negativo")
        return v

    def disponible(self) -> bool:
        return self.stock > 0

    def valor_inventario(self) -> float:
        return self.precio * self.stock


class Cliente(BaseModel):
    model_config = ConfigDict(frozen=True, strict=False, extra="forbid")

    id: int
    nombre: str
    email: str

    @field_validator("email")
    @classmethod
    def email_basico(cls, v: str) -> str:
        v = v.strip()
        if "@" not in v or "." not in v.split("@")[-1]:
            raise ValueError("formato de email inválido")
        return v
```

> **Nota sobre `strict=False`:** lo dejamos en `False` porque el JSON puede tener `precio` como número pero también como string en algunos sistemas. La validación de tipo igual ocurre — pydantic lo convierte cuando puede.

### 4.3. Adaptar `catalogo.py`

```python
"""Carga, filtrado y ordenamiento del catálogo de productos."""

import json
from collections.abc import Iterable, Iterator
from pathlib import Path

from pydantic import ValidationError

from tiendapro.errores import CatalogoInvalido
from tiendapro.modelos import Producto


def cargar(ruta: Path) -> list[Producto]:
    """Lee el JSON y devuelve una lista de Producto validada."""
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

    productos: list[Producto] = []
    for i, item in enumerate(data):
        try:
            productos.append(Producto.model_validate(item))
        except ValidationError as e:
            raise CatalogoInvalido(
                f"Producto inválido en posición {i}: {e}"
            ) from e

    return productos


def disponibles(productos: Iterable[Producto]) -> Iterator[Producto]:
    for p in productos:
        if p.disponible():
            yield p


def ordenar_por_precio(productos: Iterable[Producto]) -> list[Producto]:
    return sorted(productos, key=lambda p: p.precio)
```

### 4.4. Verificar todo

```bash
cd code/proyecto-integrador
uv run python main.py                     # output equivalente al M2
uv run mypy src/ main.py                  # cero errores
uv run ruff check .                       # cero issues
uv run ruff format --check .              # formato correcto
```

Si alguno falla, **arréglalo antes de commitear**. Esa es la disciplina del módulo.

### 4.5. Configurar pre-commit (opcional pero recomendado)

En la **raíz del repo** (no en el integrador), si todavía no existe `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.5.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
```

```bash
uv add --dev pre-commit
uv run pre-commit install
```

A partir de ahora cada commit pasa por ruff automáticamente.

### 4.6. Commit final + tag

```bash
git add code/proyecto-integrador
git commit -m "feat(proyecto-integrador): cierra M3 con pydantic, mypy y ruff (proyecto-m3)"
git tag proyecto-m3
git push origin main
git push origin proyecto-m3
```

**Felicitaciones — terminaste el Módulo 3.** TiendaPro Lite ahora tiene:

- Tipado estático completo (mypy estricto).
- Validación runtime de los datos que entran (pydantic).
- Estilo y reglas del ecosistema garantizadas (ruff).
- Hooks que evitan que código sucio entre al repo (pre-commit).

Es un proyecto que **falla rápido**, **falla con buen mensaje** y **se ve consistente** sin esfuerzo manual. Eso es ingeniería de software, no scripting.

---

Cuando termines, vuelve al README y responde las preguntas de auto-evaluación. Si todas se contestan sin dudar, M3 está consolidado y puedes pasar a [M4 — Async, HTTP y persistencia](../../04-async-http-persistencia/) (cuando esté publicado).

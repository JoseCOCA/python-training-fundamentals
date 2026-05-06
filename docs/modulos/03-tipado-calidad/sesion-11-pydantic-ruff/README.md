# S11 — pydantic v2, ruff y pre-commit hooks

> **Sesión 2h.** ~45 min lectura + ~75 min ejercicios. **Cierra el Módulo 3** con el hito `proyecto-m3` del integrador. En S10 aprendiste que mypy verifica tipos **antes** de correr el programa. En esta sesión cubrimos las dos piezas restantes: **pydantic** verifica los datos que entran **mientras** el programa corre, y **ruff** garantiza que el código que escribes sigue las convenciones del ecosistema. Cuando termines, tendrás un proyecto que falla rápido, falla bien, y se ve bien.

---

## 1. Objetivos de aprendizaje

Al terminar esta sesión vas a poder:

- Distinguir **tipado estático** (mypy, S10) de **validación runtime** (pydantic).
- Definir modelos pydantic con `BaseModel`, campos tipados y defaults.
- Validar entrada con `Model.model_validate(...)` y entender qué pasa cuando los datos no encajan.
- Escribir validadores propios con `@field_validator` y `@model_validator`.
- Capturar y leer `ValidationError`.
- Serializar modelos con `model_dump()` y `model_dump_json()`.
- Configurar **ruff** como linter y formatter, y entender qué reglas comunes te va a marcar.
- Configurar **pre-commit hooks** para que ruff y mypy se ejecuten antes de cada commit.

## 2. Prerequisitos

- [S10 — Type hints y mypy](../sesion-10-type-hints-mypy/README.md) sólida. pydantic se construye encima del sistema de tipos.
- [S08 — dataclasses](../../02-python-intermedio/sesion-08-oop-dataclasses/README.md). Vas a comparar `@dataclass` con `BaseModel`.
- [S07 — Errores](../../02-python-intermedio/sesion-07-errores/README.md). pydantic lanza `ValidationError`; vas a manejarla.

## 3. Conceptos clave

1. **Tipado estático vs validación runtime.** mypy chequea **antes de correr**. pydantic chequea **al recibir datos**. Son complementarios — no son lo mismo.
2. **`BaseModel`.** Clase base de pydantic. Como `@dataclass`, pero con **validación de tipos en runtime** y serialización JSON gratis.
3. **`ValidationError`.** Excepción que pydantic lanza cuando los datos no encajan con el modelo. Trae mensajes muy informativos por campo.
4. **Validator.** Función decorada con `@field_validator(...)` o `@model_validator(...)` que corre como parte de la validación. Permite reglas de negocio (precio > 0, email válido, fechas coherentes).
5. **ruff.** Herramienta moderna escrita en Rust que reemplaza a flake8, isort, pyupgrade, pylint y formatter (reemplaza a black). Es absurdamente rápida.
6. **Pre-commit.** Framework para ejecutar herramientas de calidad antes de cada commit. Si ruff o mypy fallan, el commit no pasa.

## 4. Teoría

### 4.1. Estático vs runtime: la otra mitad del problema

mypy verifica que **el código** sea correcto:

```python
def cobrar(monto: float) -> None: ...

cobrar("90")           # mypy: error — esperaba float, recibió str
```

Pero mypy **no puede saber** qué llega cuando el programa lee un JSON, recibe un request HTTP o lee de la base de datos. Esos datos son `Any` desde la perspectiva del compilador. Y ahí entra pydantic:

```python
import json
from pydantic import BaseModel


class Producto(BaseModel):
    nombre: str
    precio: float


# Datos que vienen del mundo exterior — Any:
crudo = json.loads('{"nombre": "Cable", "precio": "12.5"}')

# Validar al cruzar la frontera:
producto = Producto.model_validate(crudo)
print(producto.precio)        # → 12.5  (str → float automático)
print(type(producto.precio))  # → float
```

**Regla:** mypy en el centro, pydantic en los bordes. Donde llegan datos del exterior — JSON, HTTP, base de datos, archivos — los pasas por un modelo pydantic. Una vez validados, el resto del código vuelve a ser tipado estático.

### 4.2. BaseModel básico

```python
from pydantic import BaseModel


class Producto(BaseModel):
    nombre: str
    precio: float
    stock: int
    moneda: str = "USD"
```

Crear instancias:

```python
p = Producto(nombre="Auriculares", precio=89.99, stock=5)
print(p)
# → nombre='Auriculares' precio=89.99 stock=5 moneda='USD'
```

Si los tipos no encajan, **pydantic intenta convertir** (a menos que se lo prohíbas):

```python
p = Producto(nombre="Cable", precio="12.5", stock="3")  # str → float, str → int
print(p.precio, type(p.precio))   # → 12.5 <class 'float'>
```

Si la conversión es imposible, levanta `ValidationError`:

```python
Producto(nombre="X", precio="no es número", stock=5)
# pydantic_core.ValidationError: 1 validation error for Producto
# precio
#   Input should be a valid number, ...
```

### 4.3. Validar desde JSON / dict

Caso típico: tienes un dict (o un JSON) de fuente externa.

```python
data = {"nombre": "Cable", "precio": 12.5, "stock": 3}
p = Producto.model_validate(data)

raw_json = '{"nombre": "Cable", "precio": 12.5, "stock": 3}'
p = Producto.model_validate_json(raw_json)
```

`model_validate` recibe un `dict` (u objeto compatible). `model_validate_json` recibe un string JSON y hace el parseo + validación en un solo paso.

### 4.4. ValidationError: un mensaje útil

```python
from pydantic import ValidationError

try:
    Producto.model_validate({"nombre": "X", "precio": -10, "stock": "abc"})
except ValidationError as e:
    print(e)
```

```
2 validation errors for Producto
precio
  Input should be greater than 0 ...     ← solo si tienes un validador
stock
  Input should be a valid integer, unable to parse string as an integer ...
```

`ValidationError` reúne **todos** los problemas en un solo mensaje. Eso es enormemente más útil que recibirlos uno a uno.

Para programáticamente extraerlos:

```python
e.errors()
# [{'type': 'int_parsing', 'loc': ('stock',), 'msg': '...', 'input': 'abc'}, ...]
```

### 4.5. Validators: reglas de negocio

`@field_validator` para validar un campo:

```python
from pydantic import BaseModel, field_validator


class Producto(BaseModel):
    nombre: str
    precio: float
    stock: int

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
```

`@model_validator(mode="after")` para reglas que cruzan campos:

```python
from pydantic import BaseModel, model_validator


class Reserva(BaseModel):
    entrada: date
    salida: date

    @model_validator(mode="after")
    def fechas_coherentes(self) -> "Reserva":
        if self.salida <= self.entrada:
            raise ValueError("la salida debe ser posterior a la entrada")
        return self
```

**Regla:** los validators son la frontera entre los tipos (que son universales) y las **reglas de tu dominio** (que no lo son). Aquí codificas "qué es válido en TiendaPro", "qué es válido para una reserva".

### 4.6. ConfigDict: ajustar el comportamiento

```python
from pydantic import BaseModel, ConfigDict


class Producto(BaseModel):
    model_config = ConfigDict(
        frozen=True,                 # inmutable como @dataclass(frozen=True)
        strict=True,                 # NO convierte automáticamente; si llega "5" en lugar de 5, falla
        extra="forbid",              # campos extra en la entrada → error
        str_strip_whitespace=True,   # strings se normalizan (strip)
    )

    nombre: str
    precio: float
```

**Por qué `strict=True` muchas veces es lo que necesitas:** sin él, pydantic acepta `"5"` cuando esperabas `5`. Eso es una conversión silenciosa que puede esconder bugs en datos sucios.

### 4.7. Serialización

```python
p = Producto(nombre="Cable", precio=12.5, stock=3)

p.model_dump()           # → {'nombre': 'Cable', 'precio': 12.5, 'stock': 3, 'moneda': 'USD'}
p.model_dump_json()      # → '{"nombre":"Cable","precio":12.5,...}'
p.model_dump(exclude={"moneda"})        # excluir campos
p.model_dump(include={"nombre", "precio"})
```

`model_dump` devuelve un `dict`. `model_dump_json` un `str`. Ambos respetan los tipos (incluso para `datetime`, `Path`, `UUID`).

### 4.8. pydantic vs `@dataclass`: cuándo cada uno

| Caso | Mejor opción |
|---|---|
| Modelo de **datos internos** sin entrada externa | `@dataclass` |
| Modelo que **valida** datos de JSON/HTTP/DB | `pydantic.BaseModel` |
| Necesitas serializar a JSON con tipos complejos | pydantic |
| Quieres reglas de negocio embebidas (precio > 0) | pydantic con validators |
| Performance crítica con miles de instancias | `@dataclass` (más rápido construyendo) |

**En el integrador del curso:** `Producto` y `Cliente` se vuelven `BaseModel` porque vienen de fuente externa (JSON, en M4 base de datos, en M5 requests HTTP).

### 4.9. ruff: el linter y formatter del ecosistema moderno

Ruff es una sola herramienta que reemplaza:

- **flake8** (linter de estilo)
- **isort** (orden de imports)
- **pyupgrade** (sintaxis moderna)
- **black** (formatter — lo reemplaza desde 2024 con `ruff format`)
- **pylint** (parcialmente, las reglas más comunes)

Y todo en Rust, así que es **decenas de veces más rápido**.

**Comandos esenciales:**

```bash
uv run ruff check .              # linter — reporta problemas
uv run ruff check . --fix        # arregla los autoarreglables
uv run ruff format .              # formatea (reemplazo de black)
```

**Configuración mínima** en `pyproject.toml`:

```toml
[tool.ruff]
line-length = 100
target-version = "py312"

[tool.ruff.lint]
select = [
    "E", "W",   # pycodestyle (estilo)
    "F",        # pyflakes (errores reales)
    "I",        # isort (imports ordenados)
    "B",        # bugbear (bugs comunes)
    "UP",       # pyupgrade (sintaxis moderna)
    "RUF",      # reglas propias de ruff
]
ignore = []
```

**Reglas que vas a ver más seguido:**

- **E501** — línea demasiado larga (>100 chars en nuestra config).
- **F401** — import no usado.
- **F811** — variable redefinida.
- **B008** — `def f(x=Producto())` — defaults mutables como argumento.
- **UP007** — `Optional[X]` cuando podrías usar `X | None`.
- **I001** — imports desordenados.

Acostúmbrate a correr `ruff check . --fix` y `ruff format .` antes de cada commit.

### 4.10. Pre-commit: automatizar la calidad

`pre-commit` es un framework que ejecuta checks antes de cada commit. Si algún check falla, el commit no se crea.

**Setup:**

1. Agregar `pre-commit` a dependencias dev:
   ```bash
   uv add --dev pre-commit
   ```

2. Crear `.pre-commit-config.yaml` en la raíz del repo:
   ```yaml
   repos:
     - repo: https://github.com/astral-sh/ruff-pre-commit
       rev: v0.5.0
       hooks:
         - id: ruff
           args: [--fix]
         - id: ruff-format

     - repo: https://github.com/pre-commit/mirrors-mypy
       rev: v1.10.0
       hooks:
         - id: mypy
           additional_dependencies: [pydantic>=2.6]
   ```

3. Instalar los hooks (una sola vez por clon del repo):
   ```bash
   uv run pre-commit install
   ```

A partir de ahora, cada `git commit` corre ruff (con autofix), ruff format y mypy. Si alguno falla, el commit se cancela. **Es la forma de garantizar que nunca se commitea código que no pasa los checks.**

Para correr manualmente sobre todos los archivos:

```bash
uv run pre-commit run --all-files
```

### 4.11. La filosofía: rápido, automático, ruidoso

La idea de M3 entera:

1. **Rápido al fallar.** mypy y pydantic detectan problemas antes que el cliente.
2. **Automático.** ruff arregla el estilo solo. Pre-commit corre todo antes de que tú lo olvides.
3. **Ruidoso al equivocarse.** No silencies un error porque "ya lo vas a arreglar". Si pre-commit te detiene, es por algo.

Cuando empieces a sentir que las herramientas "estorban", tómalo como señal de que están haciendo bien su trabajo: te están obligando a que el código que entrega esté en el estándar. Esa fricción es valor, no costo.

## 5. Patrones y antipatrones

| ✅ Patrón | ❌ Antipatrón |
|---|---|
| pydantic en bordes (JSON, HTTP, DB) | pydantic en estructuras internas que nunca cruzan frontera |
| `@dataclass` para datos internos sin validación | `BaseModel` para todo "porque es más completo" |
| `model_validate` con `try/except ValidationError` | Asumir que el JSON tiene la forma correcta y dejar que el AttributeError aparezca tres llamadas después |
| `@field_validator` con regla de negocio clara | Validar en el código que usa el modelo, en lugar de en el modelo |
| `strict=True` por defecto | Conversiones implícitas silenciosas (`"5"` → `5`) |
| `ruff check . --fix` antes de cada commit | Ignorar warnings hasta que se acumulan 200 |
| Pre-commit instalado en cada clon | "Ya me acuerdo de correr el linter" (no, no te acuerdas) |
| Reglas de ruff explícitas en `pyproject.toml` | Ruleset por defecto que cambia entre versiones |

## 6. Conexión con el proyecto integrador — Cierre del hito M3

**Hoy cierra el Módulo 3.** Cambios concretos al integrador:

1. **`src/tiendapro/modelos.py`** migra de `@dataclass(frozen=True)` a `pydantic.BaseModel` con `model_config = ConfigDict(frozen=True, strict=True, extra="forbid")`.
2. **`src/tiendapro/catalogo.py`** reemplaza la construcción manual de `Producto(...)` por `Producto.model_validate(item)` y captura `ValidationError` traduciéndola a `CatalogoInvalido`.
3. **Validators**: `precio > 0`, `stock >= 0`, `nombre.strip()` no vacío.
4. **Configuración** en el `pyproject.toml` del integrador: `[tool.ruff]` y `[tool.mypy]` estrictos. `pre-commit` configurado para correr ambos.
5. **Verificación**: `uv run mypy src/ main.py`, `uv run ruff check .`, `uv run python main.py`. Los tres tienen que pasar.
6. **Commit final + tag**:
   ```bash
   git add code/proyecto-integrador
   git commit -m "feat(proyecto-integrador): cierra M3 con pydantic, mypy y ruff (proyecto-m3)"
   git tag proyecto-m3
   ```

## 7. Resumen

1. **mypy en el centro, pydantic en los bordes.** Tipado estático para tu código; validación runtime para datos externos.
2. **`BaseModel` te da validación, conversión, serialización y `ValidationError` informativo.** Cuatro features de un golpe.
3. **`@field_validator` codifica reglas de tu dominio.** Precio positivo, fechas coherentes, emails válidos.
4. **`strict=True` y `extra="forbid"`** son las dos flags que más bugs evitan.
5. **ruff = linter + formatter + isort + pyupgrade**, y todo en Rust. Aprende a leer su output.
6. **Pre-commit te quita la responsabilidad de acordarte.** Instálalo en cada clon del repo.
7. **La fricción de las herramientas es valor.** Si te molestan, están haciendo su trabajo.

## 8. Preguntas de auto-evaluación

1. ¿Qué chequea mypy y qué chequea pydantic? Da un ejemplo donde mypy NO te puede ayudar y pydantic sí.
2. Diferencia entre `@dataclass` y `pydantic.BaseModel`. ¿Cuándo usarías cada uno?
3. Con `strict=True`, ¿qué pasa si tu modelo espera `int` y le pasas `"5"`?
4. Define un `BaseModel` `Reserva` con `entrada: date`, `salida: date`, y un `model_validator` que valide que la salida sea posterior a la entrada.
5. ¿Cómo capturas y procesas un `ValidationError` para mostrarle al usuario los errores por campo?
6. Diferencia entre `model_dump()` y `model_dump_json()`.
7. ¿Qué cinco herramientas reemplaza ruff? Nombra al menos tres.
8. ¿Qué hace `ruff check . --fix` que `ruff check .` no hace?
9. ¿Cuál es la diferencia entre `[tool.ruff.lint] select = ["E"]` y agregar `"F"` a la lista?
10. ¿Por qué `pre-commit` se instala con `pre-commit install` y por qué hay que hacerlo en cada clon del repo?

Cuando puedas responder todas, pasa a [`ejercicios.md`](ejercicios.md).

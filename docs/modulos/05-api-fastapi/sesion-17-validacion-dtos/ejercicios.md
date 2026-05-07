# S17 — Ejercicios

> **Tiempo estimado:** ~75 min. Tres bloques: ejercicio guiado armando la separación Request/Response/ORM en una mini-API, libres para entrenar exception handlers / `Field` / `field_validator`, y **aporte parcial al integrador** que arma `tiendapro.api` con un endpoint y los exception handlers.

---

## 0. Antes de empezar

Tu sandbox vive en `code/m05-api-fastapi/sesion-17/`. Si todavía no lo corriste:

```bash
cd code/m05-api-fastapi/sesion-17
uv sync
uv run uvicorn main:app --reload
uv run mypy .
uv run ruff check .
```

Abrí `http://localhost:8000/docs` y confirmá que las rutas responden. La sesión introduce un mini-dominio "biblioteca" para no contaminarse con TiendaPro hasta el aporte al integrador.

## 1. Ejercicio guiado — Tres modelos para `Libro`

### Paso 1.1 — Modelo "ORM" (simulado en memoria)

```python
from dataclasses import dataclass
from datetime import datetime


@dataclass
class LibroDB:
    id: int
    titulo: str
    autor: str
    paginas: int
    creado_en: datetime
    creado_por: str         # campo INTERNO — no debería filtrarse
```

(Para simplificar, usamos `@dataclass`. En el integrador es un `ProductoORM` con SQLAlchemy.)

### Paso 1.2 — Modelo de Request

```python
from pydantic import BaseModel, ConfigDict, Field, field_validator


class LibroCrear(BaseModel):
    model_config = ConfigDict(extra="forbid")

    titulo: str = Field(min_length=1, max_length=200, examples=["Cien años de soledad"])
    autor: str = Field(min_length=1, max_length=120)
    paginas: int = Field(gt=0, le=10_000)

    @field_validator("titulo", "autor")
    @classmethod
    def normalizar_texto(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("no puede estar vacío")
        return v
```

### Paso 1.3 — Modelo de Response

```python
class LibroOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    titulo: str
    autor: str
    paginas: int
    creado_en: datetime
    # creado_por NO está acá → se filtra en el response.
```

### Paso 1.4 — Handlers que usan los tres

```python
from fastapi import FastAPI, HTTPException, status

app = FastAPI()
LIBROS: dict[int, LibroDB] = {}
_proximo_id = 1


@app.post("/libros", response_model=LibroOut, status_code=status.HTTP_201_CREATED)
def crear(nuevo: LibroCrear) -> LibroDB:
    global _proximo_id
    libro = LibroDB(
        id=_proximo_id,
        titulo=nuevo.titulo,
        autor=nuevo.autor,
        paginas=nuevo.paginas,
        creado_en=datetime.utcnow(),
        creado_por="admin",
    )
    LIBROS[_proximo_id] = libro
    _proximo_id += 1
    return libro                # devuelve LibroDB; FastAPI lo convierte a LibroOut


@app.get("/libros/{libro_id}", response_model=LibroOut)
def obtener(libro_id: int) -> LibroDB:
    if libro_id not in LIBROS:
        raise HTTPException(status_code=404, detail=f"libro {libro_id} no existe")
    return LIBROS[libro_id]
```

### Paso 1.5 — Probar y observar

Levantá el server, andá a `/docs` y:

1. `POST /libros` con `{"titulo": "Test", "autor": "X", "paginas": 100}` → 201, response **sin `creado_por`** aunque el dataclass interno lo tenga.
2. `POST /libros` con `{"titulo": "", "autor": "X", "paginas": 100}` → 422 con detalle del campo.
3. `POST /libros` con `{"titulo": "X", "autor": "Y", "paginas": -1}` → 422.
4. `POST /libros` con un campo extra (`{"titulo": "...", "autor": "...", "paginas": 100, "secreto": "x"}`) → 422 (por `extra="forbid"`).
5. `GET /libros/999` → 404.

**Lección:** cada modelo cumple una frontera. Mismo trabajo, tres formas, sin pisarse.

## 2. Ejercicios libres

### 2.1. Validación que cruza campos con `model_validator`

Agregá un campo opcional `paginas_resumen: int | None = None`. Si está, debe ser **menor** que `paginas`. Implementalo con `model_validator(mode="after")`.

```python
from pydantic import model_validator


class LibroCrear(BaseModel):
    titulo: str
    autor: str
    paginas: int
    paginas_resumen: int | None = None

    @model_validator(mode="after")
    def resumen_consistente(self) -> "LibroCrear":
        if self.paginas_resumen is not None and self.paginas_resumen >= self.paginas:
            raise ValueError("paginas_resumen debe ser menor que paginas")
        return self
```

Probá `{"titulo": "X", "autor": "Y", "paginas": 100, "paginas_resumen": 200}` → 422 con tu mensaje.

### 2.2. Exception handler global

Definí una excepción de dominio:

```python
class LibroNoEncontrado(Exception):
    def __init__(self, libro_id: int):
        super().__init__(f"libro {libro_id} no existe")
        self.libro_id = libro_id
```

Y un handler:

```python
from fastapi import Request
from fastapi.responses import JSONResponse


@app.exception_handler(LibroNoEncontrado)
async def libro_no_encontrado_handler(
    request: Request, exc: LibroNoEncontrado
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": str(exc), "libro_id": exc.libro_id},
    )
```

Cambiá el handler `obtener` para que **lance `LibroNoEncontrado`** en vez de `HTTPException`. Probá `GET /libros/999` → ahora la respuesta tiene tu formato (`detail` + `libro_id`).

**Lo importante:** el handler quedó simple — sin `try/except`, sin `HTTPException`. Cuando agregués `PUT`, `DELETE`, etc., todos comparten el mismo comportamiento gratis.

### 2.3. Personalizar el handler de validación

Reemplazá el response 422 default por uno con tu formato:

```python
from fastapi.exceptions import RequestValidationError


@app.exception_handler(RequestValidationError)
async def validacion_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    errores = [
        {
            "campo": ".".join(str(x) for x in e["loc"][1:]) or "(root)",
            "mensaje": e["msg"],
            "tipo": e["type"],
        }
        for e in exc.errors()
    ]
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "datos inválidos", "errores": errores},
    )
```

Probá un POST con dos errores. Vas a ver tu formato propio en lugar del default de FastAPI.

### 2.4. Listas y `from_attributes` con conversión explícita

Agregá:

```python
@app.get("/libros", response_model=list[LibroOut])
def listar() -> list[LibroDB]:
    return list(LIBROS.values())
```

¿Funciona? Sí — FastAPI itera la lista y convierte cada item con `from_attributes`. Probá agregando varios libros y haciendo `GET /libros`.

### 2.5. POST que devuelve 409 cuando hay conflicto

Si dos libros con el **mismo título** se intentan crear, levantá `LibroDuplicado`:

```python
class LibroDuplicado(Exception): ...


@app.exception_handler(LibroDuplicado)
async def libro_duplicado_handler(request, exc):
    return JSONResponse(status_code=409, content={"detail": str(exc)})
```

Y en `crear`, antes de insertar:

```python
if any(l.titulo == nuevo.titulo for l in LIBROS.values()):
    raise LibroDuplicado(f"ya existe un libro con título {nuevo.titulo!r}")
```

Probá crear el mismo libro dos veces. Segunda vez → 409.

## 3. Aporte al proyecto integrador (parcial) — `tiendapro.api`

> **NO cierra el hito M5 todavía.** Solo armamos la pieza de API y los exception handlers. La S18 agrega config + logging y ahí cerramos.

### 3.1. Agregar dependencias al integrador

En `code/proyecto-integrador/pyproject.toml`:

```toml
dependencies = [
    "pydantic>=2.6",
    "httpx>=0.27",
    "sqlalchemy>=2.0",
    "fastapi>=0.115",
    "uvicorn[standard]>=0.30",
]
```

```bash
cd /home/jose/Proyectos/python-training-fundamentals/code/proyecto-integrador
uv sync --all-groups
```

### 3.2. Crear el sub-paquete `api/`

Estructura objetivo:

```
src/tiendapro/api/
├── __init__.py
├── app.py          ← FastAPI() y exception handlers
├── dtos.py         ← ProductoCrear, ProductoOut
└── rutas.py        ← @router.get/post/...
```

`src/tiendapro/api/__init__.py`:

```python
from tiendapro.api.app import app

__all__ = ["app"]
```

### 3.3. `dtos.py` — modelos request/response

```python
"""DTOs de la API. Separados de los modelos de dominio (modelos.py) y
de los modelos ORM (orm.py). Cada DTO viaja entre cliente ↔ API."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ProductoCrear(BaseModel):
    """Lo que el cliente manda en POST /productos."""

    model_config = ConfigDict(extra="forbid")

    nombre: str = Field(min_length=1, max_length=120)
    categoria: str = Field(min_length=1, max_length=40)
    precio: float = Field(gt=0)
    stock: int = Field(ge=0, default=0)

    @field_validator("nombre", "categoria")
    @classmethod
    def normalizar(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("no puede estar vacío")
        return v


class ProductoOut(BaseModel):
    """Lo que la API devuelve en GET / POST. Mapea desde ProductoORM."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    categoria: str
    precio: float
    stock: int


class HealthOut(BaseModel):
    servicio: str
    estado: str
    productos_en_db: int
```

### 3.4. `rutas.py` — los endpoints

```python
"""Rutas REST de TiendaPro.

Las rutas reciben DTOs (entrada), llaman al repositorio (que devuelve
DTOs pydantic existentes en `tiendapro.modelos`) y devuelven los DTOs
de salida `ProductoOut`. Los exception handlers globales (en `app.py`)
traducen las excepciones de dominio a HTTP.
"""

from fastapi import APIRouter, status

from tiendapro import repositorio
from tiendapro.api.dtos import HealthOut, ProductoCrear, ProductoOut
from tiendapro.modelos import Producto

router = APIRouter()


@router.get("/health", response_model=HealthOut, tags=["meta"])
def health() -> HealthOut:
    productos = repositorio.todos()
    return HealthOut(
        servicio="tiendapro",
        estado="ok",
        productos_en_db=len(productos),
    )


@router.get("/productos", response_model=list[ProductoOut], tags=["productos"])
def listar(categoria: str | None = None) -> list[Producto]:
    if categoria is not None:
        return repositorio.por_categoria(categoria)
    return repositorio.todos()


@router.post(
    "/productos",
    response_model=ProductoOut,
    status_code=status.HTTP_201_CREATED,
    tags=["productos"],
)
def crear(nuevo: ProductoCrear) -> Producto:
    dto = Producto.model_validate(nuevo.model_dump())
    return repositorio.crear(dto)
```

### 3.5. `app.py` — la `FastAPI()` y los exception handlers

```python
"""Construye la `FastAPI()`, registra rutas y exception handlers."""

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from tiendapro.api.rutas import router
from tiendapro.catalogo import inicializar
from tiendapro.errores import (
    CatalogoInvalido,
    IntegracionError,
    ProductoNoEncontrado,
    TiendaProError,
)


def _build_app() -> FastAPI:
    app = FastAPI(
        title="TiendaPro API",
        description="API REST de TiendaPro Lite — proyecto integrador del curso.",
        version="0.5.0",
    )
    app.include_router(router)
    _registrar_handlers(app)

    @app.on_event("startup")
    def startup() -> None:
        # Bootstrap de la DB con el seed JSON la primera vez
        from pathlib import Path

        seed = Path(__file__).resolve().parents[3] / "data" / "catalogo.json"
        inicializar(seed if seed.exists() else None)

    return app


def _registrar_handlers(app: FastAPI) -> None:
    @app.exception_handler(ProductoNoEncontrado)
    async def _producto_no_encontrado(
        request: Request, exc: ProductoNoEncontrado
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": str(exc)},
        )

    @app.exception_handler(IntegracionError)
    async def _integracion(request: Request, exc: IntegracionError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_502_BAD_GATEWAY,
            content={"detail": "servicio externo no disponible", "info": str(exc)},
        )

    @app.exception_handler(CatalogoInvalido)
    async def _catalogo(request: Request, exc: CatalogoInvalido) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": str(exc)},
        )

    @app.exception_handler(TiendaProError)
    async def _tiendapro(request: Request, exc: TiendaProError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": str(exc)},
        )

    @app.exception_handler(RequestValidationError)
    async def _validacion(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        errores = [
            {
                "campo": ".".join(str(x) for x in e["loc"][1:]) or "(root)",
                "mensaje": e["msg"],
                "tipo": e["type"],
            }
            for e in exc.errors()
        ]
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": "datos inválidos", "errores": errores},
        )


app = _build_app()
```

### 3.6. Probar

```bash
cd code/proyecto-integrador
uv run uvicorn tiendapro.api:app --reload
```

Abrí `http://localhost:8000/docs`. Vas a ver:
- `GET /health`
- `GET /productos` con query param `categoria`
- `POST /productos`

Probá:
```bash
curl -s http://localhost:8000/health
curl -s http://localhost:8000/productos | head -c 200
curl -s -X POST http://localhost:8000/productos -H "Content-Type: application/json" \
    -d '{"nombre": "Test API", "categoria": "test", "precio": 9.99, "stock": 5}'
curl -s -X POST http://localhost:8000/productos -H "Content-Type: application/json" \
    -d '{"nombre": "", "categoria": "x", "precio": -1, "stock": 0}'   # debería ser 422
```

### 3.7. Verificar

```bash
uv run mypy src/ main.py
uv run ruff check .
uv run ruff format --check .
```

mypy y ruff deberían pasar. (Si tirás `main.py`, `main.py` está intocado; sigue corriendo en modo CLI.)

### 3.8. Commit (NO el del hito todavía)

```bash
git add code/proyecto-integrador
git commit -m "feat(proyecto-integrador): agrega capa API con FastAPI (S17)"
```

**No taggeás `proyecto-m5` todavía.** Eso ocurre al final de S18.

---

Cuando termines, vuelve al README y responde las preguntas de auto-evaluación. Si todas se contestan sin dudar, S17 está consolidada y puedes pasar a [S18 — pydantic-settings + logging](../sesion-18-config-logging/README.md).

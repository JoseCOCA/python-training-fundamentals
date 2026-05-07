"""Demo de S17 — Validación + DTOs + manejo de errores HTTP.

Levantá el server con:
    uv run uvicorn main:app --reload

Después abrí:
    http://localhost:8000/docs

Verificá tipos y estilo:
    uv run mypy .
    uv run ruff check .
    uv run ruff format --check .

La demo es una mini-API de biblioteca con cuatro patrones reales:

1. Tres modelos por entidad: LibroDB (interno), LibroCrear (entrada),
   LibroOut (salida con from_attributes=True).
2. Validación con Field (constraints) + field_validator (normalización)
   + model_validator (regla que cruza campos).
3. Excepciones de dominio (LibroNoEncontrado, LibroDuplicado) con
   exception handlers globales que las traducen a 404/409.
4. Custom handler de RequestValidationError que cambia el formato del
   422 al estilo de la app.
"""

from dataclasses import dataclass
from datetime import UTC, datetime

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

# ---------------------------------------------------------------------------
# 1. Tres modelos: DB / Crear / Out
# ---------------------------------------------------------------------------


@dataclass
class LibroDB:
    """Modelo INTERNO. En el integrador equivale al ORM (SQLAlchemy)."""

    id: int
    titulo: str
    autor: str
    paginas: int
    paginas_resumen: int | None
    creado_en: datetime
    creado_por: str  # campo INTERNO — no debe filtrarse al cliente


class LibroCrear(BaseModel):
    """Lo que el cliente manda en POST /libros."""

    model_config = ConfigDict(extra="forbid")

    titulo: str = Field(min_length=1, max_length=200, examples=["Cien años de soledad"])
    autor: str = Field(min_length=1, max_length=120, examples=["G. García Márquez"])
    paginas: int = Field(gt=0, le=10_000)
    paginas_resumen: int | None = Field(default=None, ge=1)

    @field_validator("titulo", "autor")
    @classmethod
    def normalizar_texto(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("no puede estar vacío")
        return v

    @model_validator(mode="after")
    def resumen_consistente(self) -> "LibroCrear":
        if self.paginas_resumen is not None and self.paginas_resumen >= self.paginas:
            raise ValueError("paginas_resumen debe ser menor que paginas")
        return self


class LibroOut(BaseModel):
    """Lo que la API devuelve. Mapea desde LibroDB sin exponer creado_por."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    titulo: str
    autor: str
    paginas: int
    paginas_resumen: int | None
    creado_en: datetime


# ---------------------------------------------------------------------------
# 2. Excepciones de dominio
# ---------------------------------------------------------------------------


class BibliotecaError(Exception):
    """Base de las excepciones de dominio."""


class LibroNoEncontrado(BibliotecaError):
    def __init__(self, libro_id: int) -> None:
        super().__init__(f"libro {libro_id} no existe")
        self.libro_id = libro_id


class LibroDuplicado(BibliotecaError):
    def __init__(self, titulo: str) -> None:
        super().__init__(f"ya existe un libro con título {titulo!r}")
        self.titulo = titulo


# ---------------------------------------------------------------------------
# 3. "Repositorio" en memoria (para no contaminar la demo con DB)
# ---------------------------------------------------------------------------


_LIBROS: dict[int, LibroDB] = {}
_proximo_id = 1


def _crear(nuevo: LibroCrear) -> LibroDB:
    global _proximo_id
    if any(libro.titulo == nuevo.titulo for libro in _LIBROS.values()):
        raise LibroDuplicado(nuevo.titulo)
    libro = LibroDB(
        id=_proximo_id,
        titulo=nuevo.titulo,
        autor=nuevo.autor,
        paginas=nuevo.paginas,
        paginas_resumen=nuevo.paginas_resumen,
        creado_en=datetime.now(UTC),
        creado_por="admin",
    )
    _LIBROS[_proximo_id] = libro
    _proximo_id += 1
    return libro


def _obtener(libro_id: int) -> LibroDB:
    if libro_id not in _LIBROS:
        raise LibroNoEncontrado(libro_id)
    return _LIBROS[libro_id]


def _todos() -> list[LibroDB]:
    return list(_LIBROS.values())


# ---------------------------------------------------------------------------
# 4. App + handlers + rutas
# ---------------------------------------------------------------------------


app = FastAPI(
    title="Biblioteca API (demo S17)",
    description="Patrón Request/Response + exception handlers + validación.",
    version="0.1.0",
)


@app.exception_handler(LibroNoEncontrado)
async def _libro_no_encontrado(request: Request, exc: LibroNoEncontrado) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": str(exc), "libro_id": exc.libro_id},
    )


@app.exception_handler(LibroDuplicado)
async def _libro_duplicado(request: Request, exc: LibroDuplicado) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": str(exc), "titulo": exc.titulo},
    )


@app.exception_handler(BibliotecaError)
async def _biblioteca_fallback(request: Request, exc: BibliotecaError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": str(exc)},
    )


@app.exception_handler(RequestValidationError)
async def _validacion(request: Request, exc: RequestValidationError) -> JSONResponse:
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


@app.get("/", tags=["meta"])
def root() -> dict[str, str]:
    return {"servicio": "biblioteca-demo", "version": app.version}


@app.get("/libros", response_model=list[LibroOut], tags=["libros"])
def listar() -> list[LibroDB]:
    return _todos()


@app.get("/libros/{libro_id}", response_model=LibroOut, tags=["libros"])
def obtener(libro_id: int) -> LibroDB:
    # No try/except: si no existe, _obtener lanza LibroNoEncontrado
    # y el exception handler lo traduce a 404.
    return _obtener(libro_id)


@app.post(
    "/libros",
    response_model=LibroOut,
    status_code=status.HTTP_201_CREATED,
    tags=["libros"],
)
def crear(nuevo: LibroCrear) -> LibroDB:
    return _crear(nuevo)

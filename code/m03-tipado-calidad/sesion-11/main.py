"""Demo de S11 — pydantic v2, ruff y pre-commit.

Ejecuta el programa con:
    uv run python main.py

Verifica los tipos con:
    uv run mypy .

Verifica el estilo con:
    uv run ruff check .
    uv run ruff format --check .

Cuatro demos:
1. BaseModel básico con conversión.
2. Validators (@field_validator y @model_validator).
3. ValidationError y manejo de errores.
4. Serialización (model_dump, model_dump_json) y modelos anidados.
"""

from datetime import date

from pydantic import (
    BaseModel,
    ConfigDict,
    ValidationError,
    field_validator,
    model_validator,
)


def seccion(titulo: str) -> None:
    print()
    print("=" * 60)
    print(titulo)
    print("=" * 60)


# ---------------------------------------------------------------------------
# 1. BaseModel básico
# ---------------------------------------------------------------------------


class Producto(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    nombre: str
    precio: float
    stock: int
    moneda: str = "USD"


def demo_basico() -> None:
    seccion("1. BaseModel básico — conversión y construcción")
    p = Producto(nombre="Auriculares", precio=89.99, stock=5)
    print(f"  {p}")
    # pydantic convierte automáticamente cuando puede:
    p2 = Producto.model_validate({"nombre": "Cable USB", "precio": "12.5", "stock": "3"})
    print(f"  desde JSON: {p2} (precio: {type(p2.precio).__name__})")


# ---------------------------------------------------------------------------
# 2. Validators
# ---------------------------------------------------------------------------


class ProductoValidado(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

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


class Reserva(BaseModel):
    model_config = ConfigDict(frozen=True)

    huesped: str
    entrada: date
    salida: date

    @model_validator(mode="after")
    def fechas_coherentes(self) -> "Reserva":
        if self.salida <= self.entrada:
            raise ValueError("la salida debe ser posterior a la entrada")
        return self


def demo_validators() -> None:
    seccion("2. Validators — reglas de negocio en el modelo")
    p = ProductoValidado(nombre="  Cable  ", precio=12.5, stock=3)
    print(f"  nombre normalizado: {p.nombre!r}  (strip aplicado por el validator)")

    r = Reserva(huesped="Ana", entrada=date(2026, 5, 10), salida=date(2026, 5, 15))
    print(f"  reserva válida: {r}")


# ---------------------------------------------------------------------------
# 3. ValidationError
# ---------------------------------------------------------------------------


def demo_validation_error() -> None:
    seccion("3. ValidationError — todos los problemas de un golpe")
    try:
        ProductoValidado.model_validate({"nombre": "  ", "precio": -99.0, "stock": -5})
    except ValidationError as e:
        print(f"  Encontrados {len(e.errors())} errores:")
        for err in e.errors():
            campo = ".".join(str(x) for x in err["loc"])
            print(f"    [{campo}] {err['msg']}")


# ---------------------------------------------------------------------------
# 4. Serialización y modelos anidados
# ---------------------------------------------------------------------------


class Direccion(BaseModel):
    calle: str
    ciudad: str
    codigo_postal: str


class Cliente(BaseModel):
    nombre: str
    email: str
    direccion: Direccion


def demo_serializacion() -> None:
    seccion("4. Serialización y modelos anidados")
    c = Cliente.model_validate(
        {
            "nombre": "Ana",
            "email": "ana@example.com",
            "direccion": {
                "calle": "Calle 1",
                "ciudad": "Ciudad A",
                "codigo_postal": "1000",
            },
        }
    )
    print(f"  modelo: {c}")
    print(f"  model_dump: {c.model_dump()}")
    print(f"  model_dump_json:\n    {c.model_dump_json(indent=2)}")
    print()
    print("  Probando estructura inválida en el sub-modelo:")
    try:
        Cliente.model_validate(
            {
                "nombre": "Bruno",
                "email": "bruno@example.com",
                "direccion": "no es un dict",
            }
        )
    except ValidationError as e:
        for err in e.errors():
            campo = ".".join(str(x) for x in err["loc"])
            print(f"    [{campo}] {err['msg']}")


if __name__ == "__main__":
    demo_basico()
    demo_validators()
    demo_validation_error()
    demo_serializacion()

"""Demo de S10 — Type hints y mypy.

Ejecuta el programa con:
    uv run python main.py

Verifica los tipos con:
    uv run mypy .

Cuatro demos:
1. Genéricos: list[int], dict[str, float], tuple, Callable.
2. Optional / X | None y type narrowing.
3. TypedDict y Literal.
4. Protocol — duck typing tipado.
"""

from collections.abc import Callable, Iterable
from dataclasses import dataclass
from typing import Literal, Protocol, TypedDict


def seccion(titulo: str) -> None:
    print()
    print("=" * 60)
    print(titulo)
    print("=" * 60)


# ---------------------------------------------------------------------------
# 1. Genéricos
# ---------------------------------------------------------------------------

def filtrar_pares(numeros: list[int]) -> list[int]:
    return [n for n in numeros if n % 2 == 0]


def precios_indexados(productos: dict[str, float]) -> list[tuple[str, float]]:
    """Devuelve la lista de (sku, precio) ordenada por sku."""
    return sorted(productos.items())


def aplicar(
    valores: Iterable[int],
    transformacion: Callable[[int], int],
) -> list[int]:
    return [transformacion(v) for v in valores]


def demo_genericos() -> None:
    seccion("1. Genéricos: list[int], dict[str, float], Callable")
    print(f"pares: {filtrar_pares([1, 2, 3, 4, 5, 6])}")
    print(f"precios: {precios_indexados({'B': 5.0, 'A': 10.0, 'C': 2.5})}")
    print(f"al cuadrado: {aplicar([1, 2, 3, 4], lambda x: x * x)}")


# ---------------------------------------------------------------------------
# 2. Optional / X | None y narrowing
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Usuario:
    nombre: str
    email: str


_USUARIOS: list[Usuario] = [
    Usuario("Ana", "ana@example.com"),
    Usuario("Bruno", "bruno@example.com"),
]


def buscar_por_email(email: str) -> Usuario | None:
    for u in _USUARIOS:
        if u.email == email:
            return u
    return None


def saludar_si_existe(email: str) -> str:
    u = buscar_por_email(email)
    if u is None:
        return f"No hay usuario con email {email}"
    # En esta rama mypy sabe que u es Usuario, no Usuario | None.
    return f"Hola, {u.nombre}"


def demo_narrowing() -> None:
    seccion("2. Optional / X | None y type narrowing")
    print(saludar_si_existe("ana@example.com"))
    print(saludar_si_existe("nadie@example.com"))


# ---------------------------------------------------------------------------
# 3. TypedDict y Literal
# ---------------------------------------------------------------------------

class ProductoJSON(TypedDict):
    sku: str
    precio: float
    stock: int


Criterio = Literal["sku", "precio", "stock"]


def ranking(productos: list[ProductoJSON], criterio: Criterio) -> list[ProductoJSON]:
    return sorted(productos, key=lambda p: p[criterio])


def demo_typeddict() -> None:
    seccion("3. TypedDict y Literal")
    productos: list[ProductoJSON] = [
        {"sku": "A", "precio": 10.0, "stock": 3},
        {"sku": "B", "precio": 5.0, "stock": 8},
        {"sku": "C", "precio": 20.0, "stock": 1},
    ]
    print("ordenados por precio:")
    for p in ranking(productos, "precio"):
        print(f"  {p}")
    # Si descomentas esta línea, mypy te avisa que "color" no es Literal válido:
    # print(ranking(productos, "color"))


# ---------------------------------------------------------------------------
# 4. Protocol: duck typing tipado
# ---------------------------------------------------------------------------

class Imprimible(Protocol):
    def render(self) -> str: ...


@dataclass(frozen=True)
class Producto:
    nombre: str
    precio: float

    def render(self) -> str:
        return f"[Producto] {self.nombre} — ${self.precio:.2f}"


@dataclass(frozen=True)
class Factura:
    numero: int
    total: float

    def render(self) -> str:
        return f"[Factura] #{self.numero} — ${self.total:.2f}"


def imprimir_todo(items: list[Imprimible]) -> None:
    for item in items:
        print(f"  {item.render()}")


def demo_protocol() -> None:
    seccion("4. Protocol: duck typing tipado")
    items: list[Imprimible] = [
        Producto("Auriculares", 89.99),
        Factura(1042, 1234.50),
    ]
    imprimir_todo(items)
    print(
        "  Ni Producto ni Factura heredan de Imprimible — solo cumplen "
        "estructuralmente."
    )


if __name__ == "__main__":
    demo_genericos()
    demo_narrowing()
    demo_typeddict()
    demo_protocol()

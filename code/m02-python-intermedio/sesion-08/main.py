"""Demo de S08 — OOP, dataclasses y diseño con criterio.

Ejecuta con:
    uv run python main.py

Las cinco demos exhiben:
1. Clase mínima a mano (con __init__, métodos, __repr__).
2. La misma clase con @dataclass — menos código, mismo comportamiento.
3. Atributos de clase vs instancia, y la trampa del default mutable.
4. frozen=True y comparación estructural automática.
5. Composición vs herencia para modelar variantes del dominio.
"""

from dataclasses import dataclass, field


def seccion(titulo: str) -> None:
    print()
    print("=" * 60)
    print(titulo)
    print("=" * 60)


# ---------------------------------------------------------------------------
# 1. Clase mínima a mano
# ---------------------------------------------------------------------------

class ProductoManual:
    def __init__(self, nombre: str, precio: float, stock: int) -> None:
        self.nombre = nombre
        self.precio = precio
        self.stock = stock

    def valor_total(self) -> float:
        return self.precio * self.stock

    def disponible(self) -> bool:
        return self.stock > 0

    def __repr__(self) -> str:
        return (
            f"ProductoManual(nombre={self.nombre!r}, "
            f"precio={self.precio}, stock={self.stock})"
        )


def demo_manual() -> None:
    seccion("1. Clase mínima a mano")
    p = ProductoManual("Auriculares", 89.99, 5)
    print(p)
    print(f"valor_total: {p.valor_total()}")
    print(f"disponible: {p.disponible()}")


# ---------------------------------------------------------------------------
# 2. La misma clase con @dataclass
# ---------------------------------------------------------------------------

@dataclass
class Producto:
    nombre: str
    precio: float
    stock: int

    def valor_total(self) -> float:
        return self.precio * self.stock

    def disponible(self) -> bool:
        return self.stock > 0


def demo_dataclass() -> None:
    seccion("2. La misma clase con @dataclass")
    p = Producto("Auriculares", 89.99, 5)
    print(p)                                 # __repr__ generado
    print(f"valor_total: {p.valor_total()}")
    print(f"disponible: {p.disponible()}")
    print(f"comparación: {p == Producto('Auriculares', 89.99, 5)}")  # __eq__ generado


# ---------------------------------------------------------------------------
# 3. Atributos de clase vs instancia: la trampa del default mutable
# ---------------------------------------------------------------------------

@dataclass
class CarritoSeguro:
    items: list[str] = field(default_factory=list)


def demo_atributos() -> None:
    seccion("3. Atributos: cómo evitar la trampa del default mutable")
    a = CarritoSeguro()
    b = CarritoSeguro()
    a.items.append("manzana")
    print(f"a.items = {a.items}")
    print(f"b.items = {b.items}    # ← cada carrito tiene SU propia lista")


# ---------------------------------------------------------------------------
# 4. frozen=True: tipo de valor inmutable, hasheable, comparable
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Punto:
    x: float
    y: float


def demo_frozen() -> None:
    seccion("4. frozen=True: tipo de valor")
    p1 = Punto(1.0, 2.0)
    p2 = Punto(1.0, 2.0)
    print(f"p1 == p2? {p1 == p2}    # comparación estructural")
    print(f"p1 is p2? {p1 is p2}    # objetos distintos en memoria")
    print(f"hash(p1) = {hash(p1)}   # hasheable porque es frozen")
    try:
        p1.x = 99.0  # type: ignore[misc]
    except Exception as e:
        print(f"intentar mutar lanza: {type(e).__name__}: {e}")


# ---------------------------------------------------------------------------
# 5. Composición vs herencia
# ---------------------------------------------------------------------------

@dataclass
class ProductoConModificadores:
    """Composición: una sola clase con campos opcionales para modificadores."""

    nombre: str
    precio: float
    impuesto_pct: float = 0.0
    descuento_pct: float = 0.0

    def precio_final(self) -> float:
        con_impuesto = self.precio * (1 + self.impuesto_pct / 100)
        con_descuento = con_impuesto * (1 - self.descuento_pct / 100)
        return con_descuento


def demo_composicion() -> None:
    seccion("5. Composición vs herencia")
    base = ProductoConModificadores("Cámara", 300.0)
    con_iva = ProductoConModificadores("Cámara", 300.0, impuesto_pct=21.0)
    en_oferta = ProductoConModificadores("Cámara", 300.0, descuento_pct=15.0)
    combo = ProductoConModificadores(
        "Cámara", 300.0, impuesto_pct=21.0, descuento_pct=15.0
    )
    for p in (base, con_iva, en_oferta, combo):
        print(
            f"{p.nombre:<8} imp={p.impuesto_pct:>5.1f}% "
            f"desc={p.descuento_pct:>5.1f}% → ${p.precio_final():.2f}"
        )
    print(
        "\nEl mismo dominio con herencia (Producto, ProductoConIva, "
        "ProductoEnOferta, ProductoConIvaYOferta...) explota en clases "
        "combinatorias. La composición lo resuelve con una sola clase."
    )


if __name__ == "__main__":
    demo_manual()
    demo_dataclass()
    demo_atributos()
    demo_frozen()
    demo_composicion()

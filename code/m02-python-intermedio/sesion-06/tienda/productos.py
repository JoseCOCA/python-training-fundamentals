"""Módulo `tienda.productos` — gestión mínima de productos.

Demuestra cómo un módulo dentro de un paquete expone funciones puras
que otros módulos importan.
"""

_PRODUCTOS: list[dict] = [
    {"nombre": "Auriculares Bluetooth", "precio": 89.99, "disponible": True},
    {"nombre": "Cable USB-C", "precio": 12.50, "disponible": True},
    {"nombre": "Cargador 20W", "precio": 24.00, "disponible": False},
]


def listar() -> list[dict]:
    """Devuelve los productos disponibles ordenados por precio."""
    disponibles = [p for p in _PRODUCTOS if p["disponible"]]
    return sorted(disponibles, key=lambda p: p["precio"])


def imprimir_tabla(productos: list[dict]) -> None:
    """Imprime una tabla simple. Demuestra una función con efecto secundario."""
    print(f"{'Producto':<25} {'Precio':>10}")
    print("-" * 36)
    for p in productos:
        print(f"{p['nombre']:<25} ${p['precio']:>9.2f}")

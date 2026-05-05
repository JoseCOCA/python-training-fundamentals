"""Capa de presentación: convierte modelos en texto para el usuario."""

from collections.abc import Iterable

from tiendapro.modelos import Producto


def imprimir_tabla(productos: Iterable[Producto]) -> None:
    """Imprime una tabla con los productos."""
    print(f"{'Nombre':<28} {'Categoría':<14} {'Precio':>10} {'Stock':>8}")
    print("-" * 62)
    for p in productos:
        print(
            f"{p.nombre:<28} {p.categoria:<14} "
            f"${p.precio:>9.2f} {p.stock:>8}"
        )


def imprimir_resumen(productos: list[Producto]) -> None:
    """Imprime el resumen del catálogo (total, más barato, más caro, valor)."""
    print("\nResumen")
    print("-" * 62)
    print(f"Productos disponibles:    {len(productos)}")

    if productos:
        mas_barato = min(productos, key=lambda p: p.precio)
        mas_caro = max(productos, key=lambda p: p.precio)
        valor = sum(p.valor_inventario() for p in productos)
        print(f"Más barato:               {mas_barato.nombre} (${mas_barato.precio:.2f})")
        print(f"Más caro:                 {mas_caro.nombre} (${mas_caro.precio:.2f})")
        print(f"Valor total inventario:   ${valor:,.2f}")

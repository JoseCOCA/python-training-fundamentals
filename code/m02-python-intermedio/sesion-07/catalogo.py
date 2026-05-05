"""Lógica del catálogo, con manejo de errores explícito."""

from errores import ProductoIncompleto, ProductoNoEncontrado


def obtener_precio(catalogo: dict, sku: str) -> float:
    """Devuelve el precio de un producto.

    Lanza:
        ProductoNoEncontrado: si el SKU no existe.
        ProductoIncompleto: si el producto existe pero el precio falta o no es numérico.
    """
    try:
        producto = catalogo[sku]
    except KeyError as e:
        raise ProductoNoEncontrado(f"SKU {sku!r} no existe en el catálogo") from e

    try:
        return float(producto["precio"])
    except KeyError as e:
        raise ProductoIncompleto(
            f"El producto {sku!r} no tiene precio definido"
        ) from e
    except (TypeError, ValueError) as e:
        raise ProductoIncompleto(
            f"El precio del producto {sku!r} no es un número: "
            f"{producto.get('precio')!r}"
        ) from e

"""TiendaPro Lite — Hito M2.

Punto de entrada de la aplicación. Orquesta la carga del catálogo, el
filtrado, ordenamiento e impresión, y maneja los errores de dominio
de forma legible para el usuario.

Cambios respecto al hito M1:
- El código vive en un paquete real (`src/tiendapro/`).
- Modelos como `@dataclass(frozen=True)` (S08).
- Excepciones de dominio (S07).
- Carga del JSON con `with` (S09) y `disponibles` como generador (S09).

Ejecuta con:

    uv run python main.py
"""

import sys
from pathlib import Path

from tiendapro import TiendaProError
from tiendapro.catalogo import cargar, disponibles, ordenar_por_precio
from tiendapro.presentacion import imprimir_resumen, imprimir_tabla

RUTA_CATALOGO = Path(__file__).parent / "data" / "catalogo.json"


def main() -> int:
    try:
        productos = cargar(RUTA_CATALOGO)
        ordenado = ordenar_por_precio(disponibles(productos))
        imprimir_tabla(ordenado)
        imprimir_resumen(ordenado)
    except TiendaProError as e:
        print(f"Error en TiendaPro: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

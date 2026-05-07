"""TiendaPro Lite — Hito M4.

Punto de entrada. La primera ejecución bootstrappea la base de datos
con el seed JSON; las siguientes leen directamente de la DB. Después de
imprimir la tabla y el resumen, llama a la "API externa" (mockeada con
`httpx.MockTransport`) para enriquecer los productos que conoce.

Stack del hito M4:
- pydantic en bordes, SQLAlchemy v2 en persistencia (S15).
- httpx.AsyncClient + MockTransport para enriquecimiento (S13).
- asyncio para paralelizar las llamadas de enriquecimiento (S12).
- mypy estricto + ruff pasan limpio (M3, mantenido).

Ejecuta con:

    uv run python main.py

Para resetear la DB:

    rm tiendapro.db
"""

import asyncio
import sys
from pathlib import Path

from tiendapro import IntegracionError, TiendaProError
from tiendapro.catalogo import disponibles, inicializar, ordenar_por_precio
from tiendapro.integraciones import enriquecer
from tiendapro.presentacion import imprimir_resumen, imprimir_tabla

RUTA_SEED = Path(__file__).parent / "data" / "catalogo.json"


async def _ejecutar() -> int:
    try:
        cantidad = inicializar(RUTA_SEED)
        print(f"Productos en DB: {cantidad}\n")

        productos = ordenar_por_precio(disponibles())
        imprimir_tabla(productos)
        imprimir_resumen(productos)

        nombres = [p.nombre for p in productos]
        try:
            enriquecimientos = await enriquecer(nombres)
        except IntegracionError as e:
            # El enriquecimiento es opcional: no abortamos por su culpa.
            print(f"\n(aviso) enriquecimiento desactivado: {e}", file=sys.stderr)
            enriquecimientos = {}

        if enriquecimientos:
            print("\nEnriquecimiento (API externa):")
            for nombre, enr in enriquecimientos.items():
                print(f"  {nombre:<28} ★{enr.rating}  {enr.descripcion}")
    except TiendaProError as e:
        print(f"Error en TiendaPro: {e}", file=sys.stderr)
        return 1
    return 0


def main() -> int:
    return asyncio.run(_ejecutar())


if __name__ == "__main__":
    sys.exit(main())

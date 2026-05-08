"""Fixtures compartidas para toda la suite del integrador.

- `client` — TestClient con la app real, DB SQLite efímera por test.
- `producto_base` — Producto de dominio para tests unit.

Notas sobre aislamiento:
- El engine de SQLAlchemy vive como `_engine` global en `tiendapro.db`.
- Settings está cacheado con `lru_cache` (decisión de S18: una sola instancia
  por proceso).
- Para aislar tests: seteamos env vars con `monkeypatch.setenv`, limpiamos el
  cache de `get_settings`, y reconstruimos `_engine` antes de cada TestClient.
"""

from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from tiendapro.modelos import Producto


@pytest.fixture
def client(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> Iterator[TestClient]:
    db_file = tmp_path / "test.db"
    monkeypatch.setenv("TIENDAPRO_DATABASE_URL", f"sqlite:///{db_file}")
    monkeypatch.setenv("TIENDAPRO_LOG_LEVEL", "WARNING")
    monkeypatch.setenv("TIENDAPRO_ENABLE_ENRICHMENT", "false")
    monkeypatch.setenv("TIENDAPRO_DEBUG", "true")

    # Limpiamos el cache de get_settings para que la próxima llamada
    # re-instancie Settings leyendo las env vars que acabamos de setear.
    from tiendapro.config import get_settings

    get_settings.cache_clear()

    # Reconstruimos el engine global con la URL nueva ANTES de levantar
    # la app — el lifespan hace `inicializar()` y necesita el engine listo.
    import tiendapro.db as db_mod

    db_mod._engine = db_mod._build_engine()  # type: ignore[attr-defined]

    from tiendapro.api.app import app

    with TestClient(app) as c:
        yield c

    # Cleanup explícito: dejamos el cache limpio para el siguiente test.
    get_settings.cache_clear()


@pytest.fixture
def producto_base() -> Producto:
    return Producto(
        nombre="Cable USB-C",
        categoria="cables",
        precio=15.0,
        stock=10,
    )

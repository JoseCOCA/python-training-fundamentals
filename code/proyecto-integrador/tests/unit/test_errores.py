"""Tests unit de la jerarquía de excepciones de dominio."""

import pytest

from tiendapro.errores import (
    CatalogoInvalido,
    IntegracionError,
    ProductoNoEncontrado,
    TiendaProError,
)


def test_jerarquia_completa_es_subclase_de_tiendapro_error() -> None:
    assert issubclass(CatalogoInvalido, TiendaProError)
    assert issubclass(ProductoNoEncontrado, TiendaProError)
    assert issubclass(IntegracionError, TiendaProError)


def test_tiendapro_error_es_subclase_de_exception() -> None:
    assert issubclass(TiendaProError, Exception)


def test_se_pueden_levantar_y_capturar_via_base() -> None:
    with pytest.raises(TiendaProError, match="seed roto"):
        raise CatalogoInvalido("seed roto")

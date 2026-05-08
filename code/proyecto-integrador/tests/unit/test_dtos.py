"""Tests unit de los DTOs de la API."""

import pytest
from pydantic import ValidationError

from tiendapro.api.dtos import HealthOut, ProductoCrear, ProductoOut


class TestProductoCrear:
    def test_acepta_input_minimo_valido(self) -> None:
        dto = ProductoCrear(nombre="Cable", categoria="cables", precio=10.0)
        assert dto.stock == 0  # default

    def test_normaliza_espacios_en_nombre(self) -> None:
        dto = ProductoCrear(nombre="  Cable  ", categoria="cables", precio=10.0)
        assert dto.nombre == "Cable"

    def test_rechaza_precio_cero(self) -> None:
        with pytest.raises(ValidationError):
            ProductoCrear(nombre="X", categoria="c", precio=0.0)

    def test_rechaza_precio_negativo(self) -> None:
        with pytest.raises(ValidationError):
            ProductoCrear(nombre="X", categoria="c", precio=-1.0)

    def test_rechaza_precio_excesivo(self) -> None:
        with pytest.raises(ValidationError):
            ProductoCrear(nombre="X", categoria="c", precio=10_000_000.0)

    def test_rechaza_stock_negativo(self) -> None:
        with pytest.raises(ValidationError):
            ProductoCrear(nombre="X", categoria="c", precio=1.0, stock=-1)

    def test_rechaza_campo_extra(self) -> None:
        with pytest.raises(ValidationError):
            ProductoCrear(  # type: ignore[call-arg]
                nombre="X", categoria="c", precio=1.0, color="rojo"
            )


def test_producto_out_serializa_los_campos_publicos() -> None:
    dto = ProductoOut(nombre="Cable", categoria="cables", precio=10.0, stock=5)
    assert dto.model_dump() == {
        "nombre": "Cable",
        "categoria": "cables",
        "precio": 10.0,
        "stock": 5,
    }


def test_health_out_acepta_campos_basicos() -> None:
    h = HealthOut(servicio="tiendapro", estado="ok", productos_en_db=42)
    assert h.estado == "ok"
    assert h.productos_en_db == 42

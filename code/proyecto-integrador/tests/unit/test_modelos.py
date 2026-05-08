"""Tests unit del modelo de dominio Producto."""

import pytest
from pydantic import ValidationError

from tiendapro.modelos import Producto


class TestProductoValidaciones:
    def test_se_construye_con_datos_validos(self) -> None:
        p = Producto(nombre="Cable", categoria="cables", precio=10.0, stock=1)
        assert p.nombre == "Cable"
        assert p.precio == 10.0
        assert p.stock == 1

    def test_es_inmutable(self) -> None:
        p = Producto(nombre="Cable", categoria="cables", precio=10.0, stock=1)
        with pytest.raises(ValidationError):
            p.precio = 99.0  # type: ignore[misc]

    def test_rechaza_precio_negativo(self) -> None:
        with pytest.raises(ValidationError, match="precio"):
            Producto(nombre="X", categoria="c", precio=-1.0, stock=1)

    def test_rechaza_precio_cero(self) -> None:
        with pytest.raises(ValidationError, match="precio"):
            Producto(nombre="X", categoria="c", precio=0.0, stock=1)

    def test_rechaza_stock_negativo(self) -> None:
        with pytest.raises(ValidationError, match="stock"):
            Producto(nombre="X", categoria="c", precio=10.0, stock=-1)

    def test_rechaza_nombre_vacio_o_solo_espacios(self) -> None:
        with pytest.raises(ValidationError):
            Producto(nombre="   ", categoria="c", precio=10.0, stock=1)

    def test_rechaza_categoria_vacia(self) -> None:
        with pytest.raises(ValidationError):
            Producto(nombre="X", categoria="", precio=10.0, stock=1)

    def test_rechaza_campos_extra(self) -> None:
        with pytest.raises(ValidationError):
            Producto(  # type: ignore[call-arg]
                nombre="X",
                categoria="c",
                precio=10.0,
                stock=1,
                color="rojo",
            )


class TestProductoComportamiento:
    @pytest.mark.parametrize("stock,esperado", [(5, True), (1, True), (0, False)])
    def test_disponible(self, stock: int, esperado: bool) -> None:
        p = Producto(nombre="X", categoria="c", precio=10.0, stock=stock)
        assert p.disponible() is esperado

    def test_valor_inventario_es_precio_por_stock(self) -> None:
        p = Producto(nombre="X", categoria="c", precio=12.5, stock=4)
        assert p.valor_inventario() == 50.0

    def test_default_moneda_es_usd(self) -> None:
        p = Producto(nombre="X", categoria="c", precio=1.0, stock=1)
        assert p.moneda == "USD"

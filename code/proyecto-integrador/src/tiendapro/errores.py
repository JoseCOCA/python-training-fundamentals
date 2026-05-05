"""Excepciones de dominio de TiendaPro."""


class TiendaProError(Exception):
    """Base de todas las excepciones del dominio TiendaPro."""


class CatalogoInvalido(TiendaProError):
    """El archivo de catálogo no se puede leer o parsear."""


class ProductoNoEncontrado(TiendaProError):
    """No existe un producto con el identificador buscado."""

"""Excepciones de dominio para la demo del catálogo."""


class CatalogoError(Exception):
    """Base de los errores del catálogo de la demo."""


class ProductoNoEncontrado(CatalogoError):
    """El SKU buscado no existe en el catálogo."""


class ProductoIncompleto(CatalogoError):
    """El producto existe pero le falta o tiene mal un campo requerido."""

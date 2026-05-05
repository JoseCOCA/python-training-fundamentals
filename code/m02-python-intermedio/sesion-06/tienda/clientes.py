"""Módulo `tienda.clientes` — gestión mínima de clientes.

Mantiene un registro en memoria. En M4 esto pasará a una base de datos.
"""

_REGISTRO: list[dict] = []


def crear(nombre: str, email: str) -> dict:
    """Crea un cliente nuevo y lo agrega al registro."""
    cliente = {
        "id": len(_REGISTRO) + 1,
        "nombre": nombre,
        "email": email,
    }
    _REGISTRO.append(cliente)
    return cliente


def listar() -> list[dict]:
    """Devuelve una copia del registro para que nadie lo mute por accidente."""
    return list(_REGISTRO)

"""Demo de S09 — Decoradores, generadores y context managers.

Ejecuta con:
    uv run python main.py

Cuatro demos:
1. Decorador @cronometro con functools.wraps.
2. Generadores: lazy iteration y pipeline composable.
3. Context manager con clase (__enter__ / __exit__).
4. Context manager con @contextlib.contextmanager (más simple).
"""

import functools
import time
from contextlib import contextmanager


def seccion(titulo: str) -> None:
    print()
    print("=" * 60)
    print(titulo)
    print("=" * 60)


# ---------------------------------------------------------------------------
# 1. Decorador @cronometro
# ---------------------------------------------------------------------------

def cronometro(funcion):
    """Mide el tiempo de ejecución de la función decorada."""

    @functools.wraps(funcion)
    def envoltorio(*args, **kwargs):
        inicio = time.perf_counter()
        try:
            return funcion(*args, **kwargs)
        finally:
            duracion = time.perf_counter() - inicio
            print(f"  [{funcion.__name__}] tardó {duracion:.4f}s")

    return envoltorio


@cronometro
def trabajo_lento(n: int) -> int:
    """Simula un cálculo costoso."""
    total = 0
    for i in range(n):
        total += i
    return total


def demo_decorador() -> None:
    seccion("1. Decorador @cronometro")
    resultado = trabajo_lento(1_000_000)
    print(f"  resultado: {resultado}")
    print(f"  trabajo_lento.__name__ = {trabajo_lento.__name__!r}  "
          f"(preservado por functools.wraps)")
    print(f"  trabajo_lento.__doc__   = {trabajo_lento.__doc__!r}")


# ---------------------------------------------------------------------------
# 2. Generadores y pipeline
# ---------------------------------------------------------------------------

def naturales():
    """Genera 1, 2, 3, ... infinitamente. Lazy."""
    n = 1
    while True:
        yield n
        n += 1


def cuadrado(numeros):
    """Eleva al cuadrado los números que le llegan."""
    for n in numeros:
        yield n * n


def pares(numeros):
    """Filtra pares."""
    for n in numeros:
        if n % 2 == 0:
            yield n


def primeros(iterable, k: int):
    """Toma los primeros k valores de un iterable."""
    contador = 0
    for x in iterable:
        if contador >= k:
            return
        yield x
        contador += 1


def demo_generadores() -> None:
    seccion("2. Generadores: pipeline lazy")
    pipeline = primeros(pares(cuadrado(naturales())), 5)
    print("  primeros 5 cuadrados pares de los naturales:")
    for valor in pipeline:
        print(f"    → {valor}")
    print("  (memoria constante; la fuente es infinita)")


# ---------------------------------------------------------------------------
# 3. Context manager con clase
# ---------------------------------------------------------------------------

class CronometroBloque:
    """Mide el tiempo de un bloque dentro de `with`."""

    def __init__(self, nombre: str) -> None:
        self.nombre = nombre

    def __enter__(self):
        self.inicio = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        duracion = time.perf_counter() - self.inicio
        print(f"  [{self.nombre}] {duracion:.4f}s")
        # devuelve None (= no suprimir excepción si la hay)


def demo_cm_clase() -> None:
    seccion("3. Context manager con clase (__enter__/__exit__)")
    with CronometroBloque("suma de 1 a 1_000_000"):
        total = sum(range(1_000_001))
    print(f"  total: {total}")


# ---------------------------------------------------------------------------
# 4. Context manager con @contextmanager (más simple)
# ---------------------------------------------------------------------------

@contextmanager
def cronometro_simple(nombre: str):
    """Versión generador del cronómetro de bloque."""
    inicio = time.perf_counter()
    try:
        yield                           # aquí corre el cuerpo del with
    finally:
        print(f"  [{nombre}] {time.perf_counter() - inicio:.4f}s")


def demo_cm_decorador() -> None:
    seccion("4. Context manager con @contextmanager")
    with cronometro_simple("cuadrado de 0..1_000_000"):
        cuadrados = [n * n for n in range(1_000_001)]
    print(f"  primeros tres cuadrados: {cuadrados[:3]}")


if __name__ == "__main__":
    demo_decorador()
    demo_generadores()
    demo_cm_clase()
    demo_cm_decorador()

"""Demo de S12 — asyncio: qué bloquea, cuándo usar async, runtime model.

Ejecuta el programa con:
    uv run python main.py

Verifica los tipos con:
    uv run mypy .

Verifica el estilo con:
    uv run ruff check .
    uv run ruff format --check .

Cuatro demos:
1. Sync vs async secuencial vs async concurrente — cronometrados.
2. TaskGroup (3.11+) con varias corutinas independientes.
3. Bloquear el loop con código sync vs to_thread.
4. Cancelación y captura de ExceptionGroup con except*.
"""

import asyncio
import time


def seccion(titulo: str) -> None:
    print()
    print("=" * 60)
    print(titulo)
    print("=" * 60)


# ---------------------------------------------------------------------------
# 1. Sync vs async secuencial vs async concurrente
# ---------------------------------------------------------------------------


def llamada_sync(nombre: str) -> str:
    """Versión síncrona — usa time.sleep para simular I/O."""
    time.sleep(0.3)
    return f"resp-{nombre}"


async def llamada_async(nombre: str) -> str:
    """Versión async — usa asyncio.sleep, cede el control en el await."""
    await asyncio.sleep(0.3)
    return f"resp-{nombre}"


async def secuencial(nombres: list[str]) -> list[str]:
    """Async, pero await uno por uno: NO concurrente, mismo tiempo que sync."""
    out: list[str] = []
    for n in nombres:
        out.append(await llamada_async(n))
    return out


async def concurrente(nombres: list[str]) -> list[str]:
    """Concurrencia real — todas las corutinas esperan en paralelo."""
    return await asyncio.gather(*[llamada_async(n) for n in nombres])


def demo_cronometros() -> None:
    seccion("1. Sync vs async secuencial vs async concurrente")
    nombres = [f"s{i}" for i in range(5)]

    inicio = time.perf_counter()
    sync_res = [llamada_sync(n) for n in nombres]
    print(f"  sync           : {len(sync_res)} en {time.perf_counter() - inicio:.2f}s")

    inicio = time.perf_counter()
    sec_res = asyncio.run(secuencial(nombres))
    print(f"  async secuencial: {len(sec_res)} en {time.perf_counter() - inicio:.2f}s")

    inicio = time.perf_counter()
    con_res = asyncio.run(concurrente(nombres))
    print(f"  async paralelo : {len(con_res)} en {time.perf_counter() - inicio:.2f}s")
    print("  → la concurrencia paga solo cuando hay ESPERA externa")


# ---------------------------------------------------------------------------
# 2. TaskGroup
# ---------------------------------------------------------------------------


async def trabajador(i: int) -> int:
    await asyncio.sleep(0.1 * i)
    return i * i


async def demo_taskgroup() -> None:
    seccion("2. TaskGroup — concurrencia estructurada (3.11+)")
    async with asyncio.TaskGroup() as tg:
        tareas = [tg.create_task(trabajador(i)) for i in range(1, 5)]
    resultados = [t.result() for t in tareas]
    print(f"  resultados: {resultados}")
    print("  TaskGroup espera a TODAS antes de salir del 'async with'")


# ---------------------------------------------------------------------------
# 3. Bloquear el loop vs to_thread
# ---------------------------------------------------------------------------


def trabajo_bloqueante(i: int) -> int:
    """Función SÍNCRONA pesada — no puede hacerse async fácilmente."""
    time.sleep(0.2)
    return i * 10


async def via_to_thread(valores: list[int]) -> list[int]:
    """Despacha la función sync al thread pool — no bloquea el event loop."""
    return await asyncio.gather(*[asyncio.to_thread(trabajo_bloqueante, v) for v in valores])


async def demo_to_thread() -> None:
    seccion("3. asyncio.to_thread — integrar código sync sin bloquear el loop")
    valores = list(range(5))

    inicio = time.perf_counter()
    res = await via_to_thread(valores)
    print(f"  con to_thread: {res} en {time.perf_counter() - inicio:.2f}s")
    print("  (sin to_thread, llamarlas directo serializaría todo y tardaría ~1s)")


# ---------------------------------------------------------------------------
# 4. Cancelación y ExceptionGroup
# ---------------------------------------------------------------------------


async def riesgosa(i: int) -> int:
    if i == 3:
        raise ValueError(f"explotó la {i}")
    if i == 4:
        raise RuntimeError(f"otra falla en {i}")
    await asyncio.sleep(0.2)
    return i


async def demo_excepciones() -> None:
    seccion("4. Cancelación y ExceptionGroup")
    try:
        async with asyncio.TaskGroup() as tg:
            for i in range(5):
                tg.create_task(riesgosa(i))
    except* (ValueError, RuntimeError) as eg:
        # except* SIEMPRE entrega un grupo, aunque solo haya fallado una task.
        for exc in eg.exceptions:
            tipo = type(exc).__name__
            print(f"  capturada {tipo}: {exc}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


async def main() -> None:
    await demo_taskgroup()
    await demo_to_thread()
    await demo_excepciones()


if __name__ == "__main__":
    demo_cronometros()
    asyncio.run(main())

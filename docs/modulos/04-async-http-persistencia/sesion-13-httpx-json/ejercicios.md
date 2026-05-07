# S13 — Ejercicios

> **Tiempo estimado:** ~75 min. Tres bloques: ejercicio guiado con un mock-server local (sin internet), libres para entrenar headers / errores / POST, reto con un agregador concurrente. **Aporte parcial al integrador**: agregamos `tiendapro/integraciones.py` con un cliente HTTP de enriquecimiento. **No cerramos M4 todavía** — el cierre con tag `proyecto-m4` viene en S15.

---

## 0. Antes de empezar

Tu sandbox vive en `code/m04-async-http-persistencia/sesion-13/`. Si todavía no lo corriste:

```bash
cd code/m04-async-http-persistencia/sesion-13
uv sync
uv run python main.py
uv run mypy .
uv run ruff check .
```

Confirma que las cuatro demos imprimen, mypy pasa limpio, ruff no reporta nada. Después regresa a este documento.

> **No necesitás internet.** Todas las demos usan `httpx.MockTransport`, una pieza de httpx que te deja interceptar las requests sin tocar la red. Eso permite que los ejercicios sean reproducibles, rápidos y testables.

## 1. Ejercicio guiado — De sync a async, contra un mock local

### Paso 1.1 — Mock con `MockTransport`

Crea `mock_api.py`:

```python
import httpx


CATALOGO = {
    "ABC": {"sku": "ABC", "nombre": "Cable USB", "precio": 12.5, "stock": 30},
    "XYZ": {"sku": "XYZ", "nombre": "Auriculares", "precio": 89.99, "stock": 5},
    "ZZZ": {"sku": "ZZZ", "nombre": "Tablet", "precio": 450.0, "stock": 0},
}


def handler(request: httpx.Request) -> httpx.Response:
    sku = request.url.path.rsplit("/", 1)[-1]
    if sku in CATALOGO:
        return httpx.Response(200, json=CATALOGO[sku])
    return httpx.Response(404, json={"error": "not found", "sku": sku})


def transport() -> httpx.MockTransport:
    return httpx.MockTransport(handler)
```

`MockTransport` te deja construir un Client/AsyncClient que **no toca la red** — cada request se enruta a `handler`. Es la herramienta que vas a usar para tests reales en M6.

### Paso 1.2 — Cliente sync que parsea a pydantic

Crea `cliente_sync.py`:

```python
import httpx
from pydantic import BaseModel, ValidationError

from mock_api import transport


class Producto(BaseModel):
    sku: str
    nombre: str
    precio: float
    stock: int


class IntegracionError(Exception):
    pass


def obtener(sku: str) -> Producto:
    with httpx.Client(transport=transport(), base_url="http://api.local") as client:
        try:
            r = client.get(f"/productos/{sku}", timeout=5.0)
            r.raise_for_status()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise IntegracionError(f"sku no existe: {sku}") from e
            raise IntegracionError(f"HTTP {e.response.status_code}") from e
        except httpx.RequestError as e:
            raise IntegracionError(f"red: {e}") from e

        try:
            return Producto.model_validate(r.json())
        except ValidationError as e:
            raise IntegracionError(f"respuesta inválida: {e}") from e


if __name__ == "__main__":
    print(obtener("ABC"))
    print(obtener("XYZ"))
    try:
        obtener("NOPE")
    except IntegracionError as e:
        print(f"esperado: {e}")
```

Corré: `uv run python cliente_sync.py`. Esperado: dos productos válidos y un `IntegracionError` por el SKU inexistente.

### Paso 1.3 — Migrar a async + concurrencia

Crea `cliente_async.py`:

```python
import asyncio

import httpx
from pydantic import BaseModel, ValidationError

from mock_api import transport


class Producto(BaseModel):
    sku: str
    nombre: str
    precio: float
    stock: int


class IntegracionError(Exception):
    pass


async def obtener(client: httpx.AsyncClient, sku: str) -> Producto:
    try:
        r = await client.get(f"/productos/{sku}")
        r.raise_for_status()
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise IntegracionError(f"sku no existe: {sku}") from e
        raise IntegracionError(f"HTTP {e.response.status_code}") from e
    except httpx.RequestError as e:
        raise IntegracionError(f"red: {e}") from e

    try:
        return Producto.model_validate(r.json())
    except ValidationError as e:
        raise IntegracionError(f"respuesta inválida: {e}") from e


async def obtener_varios(skus: list[str]) -> list[Producto]:
    async with httpx.AsyncClient(
        transport=transport(),
        base_url="http://api.local",
        timeout=5.0,
    ) as client:
        return await asyncio.gather(*[obtener(client, sku) for sku in skus])


if __name__ == "__main__":
    productos = asyncio.run(obtener_varios(["ABC", "XYZ"]))
    for p in productos:
        print(p)
```

Corré: `uv run python cliente_async.py`. Vas a ver dos productos.

### Paso 1.4 — Reflexionar

| Forma | Cuándo elegirla |
|---|---|
| `httpx.get(...)` (función directa) | Una request única en un script chico |
| `with httpx.Client():` | Varias requests sync al mismo host |
| `async with httpx.AsyncClient():` + `gather` | Varias requests independientes — paga cuando son ≥3 |

**Lección:** la diferencia entre estos tres ejemplos no es la sintaxis — es la cantidad y la dependencia de las llamadas. Elegí la más simple que resuelva tu problema.

## 2. Ejercicios libres

### 2.1. Headers compartidos y autenticación

Modificá `cliente_sync.py` para que mande estos headers en cada request:

```
Authorization: Bearer secreto-de-prueba
User-Agent: tiendapro-cli/1.0
Accept: application/json
```

Configurá el `httpx.Client` con `headers=...` en el constructor — **no** en cada `client.get(...)`. Confirmá que el `MockTransport` los recibe imprimiendo `request.headers` en el `handler`.

### 2.2. POST con `json=`

En `mock_api.py`, agregá un branch al handler:

```python
if request.method == "POST" and request.url.path == "/productos":
    payload = json.loads(request.content)
    payload["sku"] = "GEN-" + payload["nombre"][:3].upper()
    return httpx.Response(201, json=payload)
```

Después escribí una corutina `crear(client, nombre, precio, stock) -> Producto` que mande POST a `/productos` con `json={"nombre":..., "precio":..., "stock":...}` y devuelva el `Producto` validado de la respuesta. Maneja también el caso de body inválido (la API devolvería 422 — agregá ese caso al handler).

### 2.3. Timeout que falla a propósito

Modificá el handler para que cuando `request.url.path == "/lento"` haga `time.sleep(2.0)` (con `import time`).

Llamalo desde un cliente con `timeout=0.5`. ¿Qué excepción recibís? ¿De qué subclase de `httpx.RequestError` es? Atrapala y trasladá a un `IntegracionError("timeout pidiendo /lento")`.

### 2.4. Diferenciar 404 de 500

Tu handler devuelve `404` para SKUs inexistentes y, supongamos, `500` cuando hay un bug interno. Mostrá una versión del cliente que **traduce** cada caso a una excepción distinta:

- `ProductoNoEncontrado` (subclass de `IntegracionError`) para 404.
- `ServicioCaido` (subclass de `IntegracionError`) para 5xx.
- `IntegracionError` genérico para otros 4xx.

El caller debería poder hacer:

```python
try:
    obtener("X")
except ProductoNoEncontrado:
    print("no existe")
except ServicioCaido:
    print("avisar oncall")
except IntegracionError as e:
    print(f"otra cosa: {e}")
```

### 2.5. Reintentos a mano para 5xx

Escribí una función `retry_async(corutina, intentos=3, base=0.5)` que:

1. Llame a `corutina()` (sin args — se hace closure).
2. Si tira `ServicioCaido` o `httpx.RequestError`, espere `base * 2 ** n` segundos y reintente.
3. Si sigue fallando después de `intentos` veces, propague la excepción.
4. Si tira otra cosa (404, ValidationError), propague de inmediato sin reintentar.

Probala con un handler que devuelve `500` las primeras dos veces y `200` la tercera. Esperado: la tercera llamada vuelve OK.

## 3. Reto — Agregador concurrente con semáforo

Tenés una lista de 30 SKUs y querés enriquecer todos contra la API. Reglas:

1. Máximo **5 requests en vuelo a la vez** (`asyncio.Semaphore`).
2. Cualquier `IntegracionError` individual NO aborta el lote: se acumula en una lista de errores.
3. Devolvés `(productos: list[Producto], errores: list[tuple[str, str]])` — la primera con los OK, la segunda con `(sku, mensaje)`.
4. Cronométralo. Comparalo con paralelismo 1, 5 y 30. Mirá las curvas.

Pista para que `gather` no aborte por una excepción: `gather(..., return_exceptions=True)` te devuelve la excepción dentro de la lista en lugar de levantarla. Después iterás y separás OK / errores.

**Por qué este patrón importa:** en producción, las APIs se caen parcialmente. Un job que enriquece 10000 productos no puede morir porque uno falló. Esta forma — limitar paralelismo + tolerar fallos individuales — es la base de cualquier batch real.

## 4. Aporte parcial al integrador — `tiendapro/integraciones.py`

> **Esto NO cierra el hito M4.** Solo agregamos la capa de integración HTTP. El cierre completo (con persistencia y tag `proyecto-m4`) viene en S15.

### 4.1. Configurar dependencias

En `code/proyecto-integrador/pyproject.toml`, agregar `httpx`:

```toml
dependencies = [
    "pydantic>=2.6",
    "httpx>=0.27",
]
```

```bash
cd /home/jose/Proyectos/python-training-fundamentals
uv sync --all-groups
```

### 4.2. Excepción de dominio nueva

En `src/tiendapro/errores.py`, agregar:

```python
class IntegracionError(TiendaProError):
    """Falla al hablar con un servicio externo (HTTP, red, formato)."""
```

Re-exportala desde `src/tiendapro/__init__.py`.

### 4.3. Modelo de respuesta enriquecida

En `src/tiendapro/modelos.py` (al final), agregar:

```python
class EnriquecimientoExterno(BaseModel):
    """Datos extra que viene de la 'API de catálogo enriquecido'."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    sku: str
    descripcion: str
    rating: float

    @field_validator("rating")
    @classmethod
    def rating_en_rango(cls, v: float) -> float:
        if not 0.0 <= v <= 5.0:
            raise ValueError("rating debe estar entre 0 y 5")
        return v
```

### 4.4. Cliente de integración

Crea `src/tiendapro/integraciones.py`:

```python
"""Cliente HTTP para enriquecer el catálogo desde una 'API externa'.

En esta etapa la API es simulada con `httpx.MockTransport` — no hay servidor
real. Cuando el ecosistema lo demande (M5, M6) se reemplaza por la URL real
sin cambiar el código de los consumidores.
"""

import asyncio
from collections.abc import Iterable

import httpx
from pydantic import ValidationError

from tiendapro.errores import IntegracionError
from tiendapro.modelos import EnriquecimientoExterno

DATOS_FALSOS: dict[str, dict[str, object]] = {
    "Auriculares Bluetooth": {
        "sku": "AUR-BT",
        "descripcion": "Auriculares con cancelación activa de ruido",
        "rating": 4.4,
    },
    "Teclado Mecánico": {
        "sku": "TEC-MEC",
        "descripcion": "Teclado mecánico con switches azules",
        "rating": 4.7,
    },
    # los demás productos no tienen entrada — la API devuelve 404
}


def _handler(request: httpx.Request) -> httpx.Response:
    nombre = request.url.params.get("nombre", "")
    if nombre in DATOS_FALSOS:
        return httpx.Response(200, json=DATOS_FALSOS[nombre])
    return httpx.Response(404, json={"error": "no enrichment", "nombre": nombre})


def _transporte() -> httpx.MockTransport:
    return httpx.MockTransport(_handler)


async def _enriquecer_uno(
    client: httpx.AsyncClient, nombre: str
) -> EnriquecimientoExterno | None:
    try:
        r = await client.get("/enriquecer", params={"nombre": nombre})
        if r.status_code == 404:
            return None
        r.raise_for_status()
    except httpx.HTTPStatusError as e:
        raise IntegracionError(
            f"HTTP {e.response.status_code} pidiendo enriquecimiento de {nombre!r}"
        ) from e
    except httpx.RequestError as e:
        raise IntegracionError(f"red al enriquecer {nombre!r}: {e}") from e

    try:
        return EnriquecimientoExterno.model_validate(r.json())
    except ValidationError as e:
        raise IntegracionError(f"respuesta inválida para {nombre!r}: {e}") from e


async def enriquecer(
    nombres: Iterable[str], paralelismo: int = 5
) -> dict[str, EnriquecimientoExterno]:
    """Devuelve un dict {nombre → EnriquecimientoExterno} para los nombres encontrados.

    Los productos sin entrada en la API no aparecen en el dict (se silencian
    los 404 individuales, igual que harías al integrar un servicio opcional).
    """
    semaforo = asyncio.Semaphore(paralelismo)

    async def _run(client: httpx.AsyncClient, nombre: str) -> tuple[str, EnriquecimientoExterno | None]:
        async with semaforo:
            return nombre, await _enriquecer_uno(client, nombre)

    async with httpx.AsyncClient(
        transport=_transporte(), base_url="http://api.local", timeout=5.0
    ) as client:
        resultados = await asyncio.gather(
            *[_run(client, n) for n in nombres], return_exceptions=False
        )

    return {nombre: enr for nombre, enr in resultados if enr is not None}
```

### 4.5. Verificar que todo sigue limpio

Desde la raíz del repo:

```bash
uv sync --all-groups
uv run mypy code/proyecto-integrador/src code/proyecto-integrador/main.py
uv run ruff check code/proyecto-integrador
uv run ruff format --check code/proyecto-integrador
cd code/proyecto-integrador && uv run python main.py
```

El `main.py` no cambia — la integración existe pero todavía no la usamos en el flujo principal. Eso queda para S15 cuando ya tengamos persistencia y podamos cachear los resultados.

### 4.6. Commit (NO el del hito)

```bash
git add code/proyecto-integrador
git commit -m "feat(proyecto-integrador): agrega cliente httpx para enriquecimiento (S13)"
```

**No taggeás `proyecto-m4` todavía.** Eso ocurre al final de S15.

---

Cuando termines, vuelve al README y responde las preguntas de auto-evaluación. Si todas se contestan sin dudar, S13 está consolidada y puedes pasar a [S14 — SQL fundamentals](../sesion-14-sql-fundamentos/README.md).

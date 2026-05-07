# S13 — HTTP cliente con httpx + parseo de JSON

> **Sesión 2h.** ~45 min lectura + ~75 min ejercicios. En S12 te dimos el modelo runtime de async; aquí lo usás contra **el primer caso real** donde paga: pedir respuestas a servicios externos por HTTP. Vas a entender HTTP de verdad (no la versión "le pego un GET y veo qué pasa"), conocer `httpx` —el cliente moderno del ecosistema— y conectar la respuesta con tus modelos `pydantic`. Esa cadena `httpx → JSON → BaseModel` es **la frontera** de cualquier aplicación que habla con el mundo exterior.

---

## 1. Objetivos de aprendizaje

Al terminar esta sesión vas a poder:

- Explicar qué es una request HTTP y qué partes la componen (método, URL, headers, body, status, response body).
- Hacer requests sincrónicas con `httpx.Client` y entender por qué el `with` no es opcional.
- Hacer requests concurrentes con `httpx.AsyncClient` + `asyncio.gather` / `TaskGroup`.
- Manejar `response.status_code`, `response.json()`, `response.raise_for_status()`.
- Validar la respuesta JSON con `Modelo.model_validate(response.json())` y traducir `ValidationError` a un error de dominio.
- Configurar timeouts, headers comunes y reintentos básicos.
- Distinguir cuándo un endpoint justifica async (varias llamadas independientes) y cuándo no (una sola llamada en un script).

## 2. Prerequisitos

- [S12 — asyncio](../sesion-12-asyncio/README.md). El `await` y `gather` ya tienen que ser intuitivos.
- [S07 — Errores](../../02-python-intermedio/sesion-07-errores/README.md). Vamos a definir excepciones de dominio para errores HTTP.
- [S11 — pydantic](../../03-tipado-calidad/sesion-11-pydantic-ruff/README.md). Vamos a parsear las respuestas a `BaseModel`.

## 3. Conceptos clave

1. **HTTP request/response.** El cliente envía un método (`GET`, `POST`, ...), una URL, headers y un body opcional. El servidor responde con un status code (`200`, `404`, `500`, ...), headers y un body opcional. Sin entender esto, todo lo demás es magia.
2. **Status codes.** `2xx` éxito, `3xx` redirección, `4xx` error del cliente, `5xx` error del servidor. Cada categoría se maneja distinto.
3. **`httpx.Client` y `httpx.AsyncClient`.** Dos clases gemelas. Misma API. Una bloquea, la otra no. Se usan con `with` / `async with` para que liberen el pool de conexiones.
4. **`response.json()`.** Atajo que llama `json.loads(response.content)`. Devuelve un dict/list crudo — todavía no validaste nada. Aquí entra pydantic.
5. **Timeout.** Tiempo máximo que esperás antes de cancelar. Si no lo configurás, el default de httpx (5 s) te puede pegar; explicítalo siempre.
6. **Pool de conexiones.** El cliente reutiliza conexiones TCP entre requests al mismo host. Por eso se crea **uno** y se reutiliza, no uno por request.

## 4. Teoría

### 4.1. HTTP en cinco minutos

Toda interacción HTTP es esto:

```
─── Request ────────────────────────────────────────
GET /productos/42 HTTP/1.1
Host: api.tiendapro.local
Accept: application/json
Authorization: Bearer abc123
─────────────────────────────────────────────────────

─── Response ────────────────────────────────────────
HTTP/1.1 200 OK
Content-Type: application/json
Content-Length: 84

{"id": 42, "nombre": "Cable USB", "precio": 12.5, "stock": 3}
─────────────────────────────────────────────────────
```

Cinco piezas a recordar:

| Pieza | Quién | Para qué |
|---|---|---|
| **Método** | cliente | Qué quiere hacer: leer (`GET`), crear (`POST`), reemplazar (`PUT`), modificar (`PATCH`), borrar (`DELETE`) |
| **URL + query string** | cliente | A qué recurso |
| **Headers** | ambos | Metadata: tipo de contenido, autenticación, idioma, etc. |
| **Body** | en `POST/PUT/PATCH` y respuestas | El payload — típicamente JSON |
| **Status code** | servidor | El veredicto |

Status codes que vas a ver más:

- **200 OK**: todo bien.
- **201 Created**: tu `POST` creó el recurso.
- **204 No Content**: tu `DELETE` salió pero no hay body.
- **400 Bad Request**: tu request está mal formada.
- **401 Unauthorized**: te falta o está mal el token.
- **403 Forbidden**: estás autenticado pero no tenés permiso.
- **404 Not Found**: el recurso no existe.
- **409 Conflict**: el recurso ya existe o está en un estado incompatible.
- **422 Unprocessable Entity**: el JSON parsea pero las reglas de negocio del servidor lo rechazan (FastAPI lo usa para errores de pydantic).
- **429 Too Many Requests**: rate limit. Te toca esperar.
- **500 Internal Server Error**: el servidor explotó.
- **503 Service Unavailable**: el servidor está caído o sobrecargado.

**No te bases en strings de mensajes de error.** Confía en el status code. Lo otro cambia entre versiones; el código no.

### 4.2. ¿Por qué httpx y no requests?

`requests` fue el cliente de Python por más de una década. Sigue funcionando perfecto para scripts. **Pero**:

- No tiene cliente async. Punto. Si vas a usar asyncio, tenés que cambiar de librería.
- Su API se mantuvo en su versión 1.x para preservar compatibilidad — la última gran ola de mejoras pasó sin tocarlo.
- `httpx` (de Encode, los mismos del framework Starlette/FastAPI) tiene **la misma API que requests** para sync, **+ versión async idéntica**, soporte HTTP/2, mejor manejo de timeouts y tipado.

En el ecosistema FastAPI/SQLAlchemy/asyncio (el de M5/M6), `httpx` es el cliente esperado. Cambialo ahora y deja de pensar en requests.

### 4.3. Cliente sincrónico

```python
import httpx

with httpx.Client(timeout=5.0) as client:
    r = client.get("https://httpbin.org/get")
    r.raise_for_status()                  # tira HTTPStatusError si no es 2xx
    print(r.status_code)                  # 200
    print(r.json())                        # dict
```

Tres cosas a notar:

1. **`with`**. Mismo patrón que en S09: el `with` libera el pool de conexiones cuando salís. Sin `with`, fugás recursos.
2. **`timeout`**. Siempre explicitalo. El default es razonable pero no siempre vas a querer 5 s.
3. **`raise_for_status`**. Si no lo llamás, **2xx y 4xx te llegan igual** y el bug aparece tres pasos después cuando intentás `.json()` sobre un `404`.

Hacer una sola request:

```python
# Para una llamada puntual sin reutilización, el shortcut también existe:
r = httpx.get("https://httpbin.org/get", timeout=5.0)
```

Pero si vas a hacer varias contra el mismo host, **siempre** usá `with httpx.Client()`. Reutiliza la conexión TCP y vuela.

### 4.4. Cliente asíncrono

```python
import asyncio
import httpx


async def precio(client: httpx.AsyncClient, sku: str) -> float:
    r = await client.get(f"https://api.tiendapro.local/precio/{sku}")
    r.raise_for_status()
    return float(r.json()["precio"])


async def precios(skus: list[str]) -> list[float]:
    async with httpx.AsyncClient(timeout=5.0) as client:
        return await asyncio.gather(*[precio(client, sku) for sku in skus])


asyncio.run(precios(["A", "B", "C", "D", "E"]))
```

**El cliente se crea UNA vez** y se le pasa a todas las corutinas. Cada `await client.get(...)` reutiliza el pool. Si crearas un `AsyncClient` por request, perderías la principal ventaja: pool de conexiones.

### 4.5. JSON crudo no es un dominio: parsealo a pydantic

Cuando hacés `response.json()` te llega un `dict`/`list` sin garantías. Eso es **`Any` con cara de objeto bonito**. Lo que tu código quiere es un objeto tipado:

```python
from pydantic import BaseModel, ValidationError


class ProductoExterno(BaseModel):
    sku: str
    nombre: str
    precio: float


async def obtener_producto(client: httpx.AsyncClient, sku: str) -> ProductoExterno:
    r = await client.get(f"/productos/{sku}")
    r.raise_for_status()
    try:
        return ProductoExterno.model_validate(r.json())
    except ValidationError as e:
        raise IntegracionError(f"respuesta malformada para {sku}: {e}") from e
```

Tres beneficios:

- mypy/IDE conocen los campos.
- `precio` está garantizado como `float` —no como `str` que parecía float.
- Si la API cambia y agrega/quita un campo, el `ValidationError` lo detecta **al pegar**, no tres horas después en otro módulo.

### 4.6. Errores: la jerarquía de httpx

```
httpx.HTTPError
├── httpx.RequestError                   ← problemas conectando
│   ├── httpx.ConnectError
│   ├── httpx.ReadTimeout
│   ├── httpx.WriteError
│   └── ...
└── httpx.HTTPStatusError                 ← status 4xx/5xx (lo lanza raise_for_status)
```

Patrón típico para una integración:

```python
class IntegracionError(Exception):
    """Algo salió mal hablando con un servicio externo."""


async def obtener_seguro(client, sku):
    try:
        r = await client.get(f"/productos/{sku}")
        r.raise_for_status()
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise IntegracionError(f"sku no existe: {sku}") from e
        raise IntegracionError(f"error HTTP {e.response.status_code}") from e
    except httpx.RequestError as e:
        raise IntegracionError(f"red caída: {e}") from e
    return r.json()
```

Traducís errores HTTP a errores de **tu** dominio (`IntegracionError`). El resto del código no tiene por qué saber que httpx existe.

### 4.7. Timeouts: la cosa que más bugs evita

```python
httpx.Client(timeout=5.0)                 # 5 s para TODO
httpx.Client(timeout=httpx.Timeout(connect=2.0, read=10.0))   # más fino
```

`httpx.Timeout` te deja dividir:
- **connect**: cuánto esperás establecer la conexión TCP.
- **read**: cuánto esperás recibir cada chunk de la respuesta.
- **write**: cuánto esperás mandar el body.
- **pool**: cuánto esperás obtener una conexión libre del pool.

**Sin timeout** un servidor caído puede colgar tu corutina indefinidamente. Es una de las primeras causas de "mi sistema dejó de responder y nadie sabe por qué".

### 4.8. Headers comunes

```python
headers = {
    "User-Agent": "tiendapro-cli/1.0",
    "Authorization": "Bearer abc123",
    "Accept": "application/json",
    "Content-Type": "application/json",       # solo cuando mandás body
}
async with httpx.AsyncClient(headers=headers, timeout=5.0) as client:
    ...
```

Los headers que pasás al `Client` se aplican a **todas** las requests. Los que pasás al `client.get(...)` se mergean encima.

### 4.9. POST con body JSON

```python
r = await client.post(
    "/productos",
    json={"sku": "ABC", "nombre": "Cable", "precio": 12.5},
)
r.raise_for_status()
```

Pasale `json=...` y httpx serializa + setea `Content-Type: application/json` solo. Si tenés un `BaseModel`, dumpealo:

```python
producto = Producto(sku="ABC", nombre="Cable", precio=12.5)
await client.post("/productos", json=producto.model_dump())
```

`model_dump()` devuelve un dict, que httpx serializa. Cierre del círculo: pydantic adentro, JSON afuera, sin que escribas la conversión a mano.

### 4.10. Reintentos: un poco de pragmatismo

Cuando integrás con APIs reales, a veces fallan transitoriamente (un 502 por un deploy, un 429 por rate limit). Conviene reintentar — pero con límite y con backoff.

`httpx` no tiene reintentos integrados. Hay dos caminos:

- **Pequeño y a mano**: bucle con `try/except` y `await asyncio.sleep(2 ** intento)`.
- **Librería**: `tenacity` (la más usada) te decora una corutina con la política completa.

```python
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, max=10),
    retry=retry_if_exception_type(httpx.RequestError),
)
async def precio_con_retry(client: httpx.AsyncClient, sku: str) -> float:
    r = await client.get(f"/precio/{sku}")
    r.raise_for_status()
    return float(r.json()["precio"])
```

**Cuidado:** no reintentar 4xx. Es problema de tu request, no del servidor. Reintentar `429` solo si el servidor te indica `Retry-After`. Reintentar `5xx` y errores de red, sí.

En este curso usamos el camino pequeño y a mano para entender el patrón; `tenacity` es opcional.

### 4.11. Cuándo async vale en HTTP y cuándo no

✅ Vale:
- Hacés varias requests independientes (catálogo de productos pidiendo detalles a un servicio externo, agregador de noticias, scrapping cuidadoso).
- Tu programa es un servidor (FastAPI) que atiende varias requests a la vez.

❌ No vale:
- Tu CLI hace una sola request al arrancar. La concurrencia no aporta y el código sync es más simple.
- Estás haciendo requests **dependientes**: la URL #2 sale del response de la URL #1. No hay paralelismo posible — usá sync.

Cuando dudes, escribí la versión sync primero. Si profileando ves que las llamadas HTTP son el cuello de botella **y** son independientes, migrá a `AsyncClient`.

## 5. Patrones y antipatrones

| ✅ Patrón | ❌ Antipatrón |
|---|---|
| `with httpx.Client(timeout=...) as client` | `httpx.get(...)` repetidas para el mismo host (tira la conexión cada vez) |
| Crear el `AsyncClient` UNA vez y compartirlo | Un `AsyncClient` por corutina (no aprovecha el pool) |
| `r.raise_for_status()` siempre | Asumir que `r.json()` te va a dar un dict aunque el status sea 500 |
| `Modelo.model_validate(r.json())` | Acceder `r.json()["foo"]` directo y propagar `KeyError` por todo el código |
| Traducir `httpx.*` a una excepción de tu dominio | Dejar que el caller capture `httpx.HTTPStatusError` directo |
| Timeout explícito siempre | Confiar en el default y debuggear cuelgues fantasmas |
| `client.post(url, json=modelo.model_dump())` | Serializar a mano con `json.dumps` y setear el `Content-Type` |
| Reintentos solo en 5xx y errores de red | Reintentar 401/403/404 (es problema tuyo, no del servidor) |
| Headers compartidos en el constructor del Client | Repetir `Authorization` en cada llamada |

## 6. Conexión con el proyecto integrador

**Hoy todavía no cerramos el módulo,** pero el integrador empieza a hablar con el mundo:

1. Vamos a definir un módulo `tiendapro/integraciones.py` con un cliente que pide enriquecimiento (descripción larga, rating) a una "API externa" simulada con `httpx.MockTransport` (no necesitás un servidor real).
2. La respuesta cruda se valida con un `BaseModel` `EnriquecimientoExterno`.
3. Los errores de red/HTTP se traducen a una nueva excepción de dominio `IntegracionError`.
4. **No persistimos nada todavía.** Eso entra en S15.

El cierre M4 con tag `proyecto-m4` ocurre al final de S15 una vez que tengamos persistencia + integración HTTP + asyncio donde aporte.

## 7. Resumen

1. **HTTP es: método + URL + headers + body → status + headers + body.** Memorizalo.
2. **Status codes en categorías: 2xx ok, 3xx redirige, 4xx vos, 5xx el servidor.**
3. **`httpx.Client` para sync, `httpx.AsyncClient` para async, misma API.** Siempre con `with`/`async with` y siempre con timeout.
4. **`raise_for_status()` no es opcional.** Sin él, los errores aparecen tres llamadas después.
5. **`response.json()` es `Any`. Pasalo por `BaseModel.model_validate`.** Esa es la frontera.
6. **Traducí `httpx.HTTPError` a una excepción de TU dominio.** El resto del código no debería saber que httpx existe.
7. **Pool de conexiones: un cliente, muchas requests.** No crees uno nuevo por llamada.
8. **Reintentos solo cuando tienen sentido (5xx, red).** Con backoff exponencial. Bucle a mano o `tenacity`.
9. **Async aporta cuando hay varias llamadas independientes o cuando sos un servidor.** Para un script con una request, sync alcanza.

## 8. Preguntas de auto-evaluación

1. Listá las cinco partes de una request HTTP. ¿Cuáles ve el cliente, cuáles el servidor?
2. ¿Qué diferencia hay entre `r.text`, `r.content` y `r.json()`?
3. ¿Por qué `with httpx.Client()` y no `client = httpx.Client()`?
4. Tenés que hacer 50 GETs al mismo host. ¿Cuántos `httpx.AsyncClient` creás? ¿Por qué?
5. ¿Qué hace `response.raise_for_status()` y por qué no podés saltarlo?
6. ¿Cómo traducirías un `404` a una excepción de tu dominio `ProductoNoEncontrado`?
7. ¿Cuándo reintentar y cuándo no? Da un ejemplo de cada caso.
8. Diferencia entre `timeout=5.0` y `timeout=httpx.Timeout(connect=2, read=10)`.
9. ¿Cómo conectás `response.json()` con un `BaseModel`? Escribí dos líneas.
10. ¿Cuándo migrarías un cliente sync a async? ¿Cuándo NO lo harías a pesar de que "podrías"?

Cuando puedas responder todas, pasa a [`ejercicios.md`](ejercicios.md).

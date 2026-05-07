# S13 — Recursos

## Documentación oficial

- **httpx documentation** ([www.python-httpx.org](https://www.python-httpx.org/)). La doc es excelente. Empezá por "Quickstart" y después "Async Support".
- **httpx — Async support** ([www.python-httpx.org/async/](https://www.python-httpx.org/async/)). El cliente async de httpx con todos sus matices.
- **httpx — MockTransport** ([www.python-httpx.org/advanced/transports/#mock-transport](https://www.python-httpx.org/advanced/transports/#mock-transport)). El transport que usamos para los ejercicios. Es la base de cualquier test que toque HTTP.
- **httpx — Exceptions** ([www.python-httpx.org/exceptions/](https://www.python-httpx.org/exceptions/)). Jerarquía completa de excepciones de httpx.
- **MDN — HTTP overview** ([developer.mozilla.org/en-US/docs/Web/HTTP/Overview](https://developer.mozilla.org/en-US/docs/Web/HTTP/Overview)). Si HTTP todavía es niebla, este es el lugar. La referencia HTTP de la industria.
- **MDN — HTTP response status codes** ([developer.mozilla.org/en-US/docs/Web/HTTP/Status](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status)). Catálogo completo. Volvés cuando necesitás un código que no usás todos los días.

## Lecturas guiadas

- **Real Python — Python's `httpx` Library** ([realpython.com/python-httpx/](https://realpython.com/python-httpx/)). Tutorial práctico con ejemplos de sync, async y mocks.
- **Tom Christie — "httpx and the future of HTTP for Python"** (búsquedas en YouTube). Tom es el autor de httpx y de Starlette. Sus charlas explican el porqué de las decisiones de diseño.
- **Sebastián Ramírez — Casos de uso de httpx con FastAPI**. Sebastián documenta casos de uso reales de cliente y servidor en su blog y tutoriales.

## Para profundizar

- **HTTP/2 explained** ([http2-explained.haxx.se](https://http2-explained.haxx.se/)). Daniel Stenberg (autor de curl) explica HTTP/2 desde cero. Lectura larga pero la mejor que vas a encontrar.
- **High Performance Browser Networking** (Ilya Grigorik) ([hpbn.co](https://hpbn.co/)). Libro libre online. Capítulos 9 y 10 cubren HTTP/1.1, HTTP/2 y persistencia de conexiones — el porqué del pool del cliente.
- **REST APIs** ([restfulapi.net](https://restfulapi.net/)). Resumen pragmático de los principios REST. No "REST teórico" — REST como se usa en la industria.

## Referencias para resolver dudas puntuales

- **"Mi `client.get(url)` cuelga eternamente"** — falta `timeout=`. El default de httpx es razonable pero un servidor caído puede dejarte 5 s con cara de "no pasa nada". Explicítalo.
- **"`r.json()` me tira `JSONDecodeError`"** — el response no es JSON. Imprimí `r.text` y `r.headers["content-type"]` para entender qué te mandaron.
- **"Reusar el `AsyncClient` entre corutinas"** — sí, es lo correcto. Crealo una vez (por ejemplo en el constructor de tu clase) y compartilo.
- **"`MockTransport` no me captura las llamadas reales"** — claro, ese es el punto: solo captura las del Client donde lo configurás. Si tu código crea otro `httpx.AsyncClient()` sin transport, va por la red.
- **"Los headers que paso al `Client` no llegan"** — chequeá que el código no esté pasando `headers={...}` en el `client.get(...)` que machaca los del constructor.

## Errores comunes

- **`requests`-isms en httpx** — la mayoría de la API es idéntica, pero `httpx` exige `data=`, `json=`, `params=` con keyword. Si un snippet de Stack Overflow te falla, suele ser por eso.
- **Olvidar `await`** — `client.get(...)` en `AsyncClient` devuelve una corutina, no el response. Sin `await`, recibís un objeto raro.
- **Compartir `AsyncClient` entre event loops distintos** — un `AsyncClient` está atado al loop donde se creó. Si hacés `asyncio.run` dos veces y pasás el mismo client, vas a ver errores difíciles.
- **Enviar un dataclass o BaseModel en `json=`** — httpx no sabe serializarlo. Pasá `model.model_dump()` o `dataclasses.asdict(model)`.
- **Reintentar 4xx** — un 400/401/404 no se arregla reintentando. Solo 5xx y errores de red merecen retry.

## Si vas hacia el curso 2

En AI Engineering, el patrón de S13 se repite todo el tiempo:

- Llamar a la API de un LLM = `httpx.AsyncClient` + `model.model_dump_json()` en el body.
- Embeddings batch = enviar 100 textos al endpoint y esperar todos en paralelo (`gather` con semaphore).
- Tools de un agente = el agente decide llamar a tu API; tu API a su vez puede llamar a otra API. Cadenas de `AsyncClient`.
- Health checks de servicios externos = ping concurrente con timeout corto.

La **disciplina** que practicás acá — timeout siempre, raise_for_status siempre, traducir excepciones a tu dominio, validar con pydantic — es exactamente la que necesita una integración con LLM, vector store o Slack.

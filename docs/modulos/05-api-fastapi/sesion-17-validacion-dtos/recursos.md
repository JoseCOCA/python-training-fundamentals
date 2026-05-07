# S17 — Recursos

## Documentación oficial

- **FastAPI — Body** ([fastapi.tiangolo.com/tutorial/body/](https://fastapi.tiangolo.com/tutorial/body/)). Cómo declarás bodies con BaseModel.
- **FastAPI — Response Model** ([fastapi.tiangolo.com/tutorial/response-model/](https://fastapi.tiangolo.com/tutorial/response-model/)). `response_model`, `response_model_exclude_unset`, etc.
- **FastAPI — Handling Errors** ([fastapi.tiangolo.com/tutorial/handling-errors/](https://fastapi.tiangolo.com/tutorial/handling-errors/)). `HTTPException`, exception handlers, custom 422.
- **pydantic — Field** ([docs.pydantic.dev/latest/concepts/fields/](https://docs.pydantic.dev/latest/concepts/fields/)). Catálogo completo de constraints (`min_length`, `gt`, `pattern`, `examples`, etc.).
- **pydantic — Validators** ([docs.pydantic.dev/latest/concepts/validators/](https://docs.pydantic.dev/latest/concepts/validators/)). `field_validator`, `model_validator`, modos.
- **pydantic — `from_attributes`** ([docs.pydantic.dev/latest/api/config/#pydantic.config.ConfigDict.from_attributes](https://docs.pydantic.dev/latest/api/config/#pydantic.config.ConfigDict.from_attributes)). El reemplazo del viejo `orm_mode`.
- **HTTP Status Codes — IETF / MDN** ([developer.mozilla.org/en-US/docs/Web/HTTP/Status](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status)). Catálogo. Volvés cuando dudás qué código usar.

## Lecturas guiadas

- **REST API Design Best Practices** — múltiples autores (busca "REST best practices versioning errors"). Los temas universales: versionado, paginación, cómo modelar errores, idempotencia.
- **JSON:API spec** ([jsonapi.org](https://jsonapi.org/)). Una convención exhaustiva sobre cómo modelar respuestas REST. No tenés que seguirla, pero leerla te enseña qué decisiones tomó tu API por omisión.
- **API Design Patterns** (JJ Geewax, Manning). Libro denso pero muy bueno sobre cómo modelar APIs serias (pagination, soft delete, large payloads, cancellation).
- **Real Python — FastAPI: Data Validation with Pydantic** ([realpython.com](https://realpython.com/)). Recorrido práctico de los patrones de hoy.

## Para profundizar

- **Idempotency-Key Header** ([datatracker.ietf.org/doc/draft-ietf-httpapi-idempotency-key-header/](https://datatracker.ietf.org/doc/draft-ietf-httpapi-idempotency-key-header/)). El draft IETF para el header `Idempotency-Key`. Cuando tu API mueve dinero, esto deja de ser opcional.
- **Stripe API Reference** ([stripe.com/docs/api](https://stripe.com/docs/api)). Es probablemente la mejor referencia de "cómo modelar una API REST seria" en producción. Versionado por header, idempotency-keys, paginación cursor-based, errores estructurados.
- **GitHub REST API** ([docs.github.com/en/rest](https://docs.github.com/en/rest)). Otro buen ejemplo. Especialmente fijate en cómo modelan rate limiting y errores de validación.
- **The Vary Header / Content negotiation**. Si vas a servir JSON y XML, o devolver respuestas distintas para distintos clientes, este es el mecanismo HTTP estándar.

## Referencias para resolver dudas puntuales

- **"Mi POST devuelve 200 en vez de 201"** — agregale `status_code=status.HTTP_201_CREATED` al decorador.
- **"FastAPI me devuelve un 422 horrible"** — sí, es feo pero correcto. Si querés tu propio formato, override `RequestValidationError` con un exception handler custom.
- **"`from_attributes=True` no parece hacer nada"** — chequeá que lo pongas en `ConfigDict` del **modelo de salida** (el `ProductoOut`), no del de entrada. Y que estés haciendo `model_validate(orm)`, no `model_validate(orm.__dict__)`.
- **"Tengo un campo opcional que se serializa como `null`"** — si querés que se omita cuando es `None`, usá `response_model_exclude_none=True` en el decorador, o `model_config = ConfigDict(serialize_by_alias=True, ...)`.
- **"Mi exception handler no se dispara"** — chequeá que la excepción que lanzás SEA o herede de la clase que registraste. Y que el handler esté declarado con `async def` (FastAPI lo exige).
- **"`raise HTTPException` vs `raise MiError`"** — en handlers, preferí lanzar tu excepción de dominio. El exception handler lo convierte. Solo usás `HTTPException` directo cuando es un error específico de la API (validación de query no expresable en pydantic, p.ej.).

## Errores comunes

- **Filtrar campos sensibles porque "no los devolvemos"** — sin `response_model`, FastAPI serializa el objeto completo. Si tu objeto interno tiene `password_hash`, `token`, `creado_por`, va al wire. Siempre `response_model`.
- **Mismo modelo para entrada y salida** — funciona en demos, falla en producción. El cliente termina mandando `id` que ignorás silenciosamente o filtrando campos internos.
- **Validación duplicada** — si pydantic ya valida `precio > 0`, no vuelvas a chequearlo en el repositorio. Confiá en la validación de entrada.
- **`HTTPException(status=200)` para "todo bien"** — esto NO existe. 2xx es respuesta normal, no se "raisea".
- **`async def` con `try/except HTTPException`** — `HTTPException` no debería atraparse en handlers. Es una señal — la atrapa FastAPI.
- **Devolver el ORM directamente sin `response_model`** — en mejor caso filtrás cosas; en peor caso, intentás serializar relaciones lazy y disparás N+1 al wire. Mapealo a un DTO.

## Si vas hacia el curso 2

En AI Engineering vas a tener:

- **Modelos pydantic para mensajes a LLMs**: `class Message(BaseModel): role: Literal["user","assistant"]; content: str`. Validación gratis.
- **Tools de un agente** declaradas como `BaseModel`. El LLM "ve" el JSON Schema generado por FastAPI/pydantic.
- **Respuestas estructuradas** del LLM se piden con `response_format=MiModelo` y se validan con pydantic — exactamente el patrón "validación en la frontera" que ves hoy.
- **Errores HTTP idiomáticos** se vuelven crítica cuando tu API la consume otra app que reintenta automáticamente. Un 503 con `Retry-After` es la diferencia entre que reintenten o se rindan.

La disciplina es la misma: **validación en la frontera, exception handler global, status codes correctos**. Lo que cambia es qué hay adentro del handler — un repositorio, un LLM, un agente con multi-step. La forma del contrato la elegís acá.

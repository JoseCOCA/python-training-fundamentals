# S15 — Recursos

## Documentación oficial

- **SQLAlchemy 2.0 Tutorial** ([docs.sqlalchemy.org/en/20/tutorial/](https://docs.sqlalchemy.org/en/20/tutorial/)). El tutorial **oficial** y **moderno**. Lectura obligatoria. Si solo leés una cosa de SQLAlchemy en tu vida, que sea esto.
- **What's New in SQLAlchemy 2.0** ([docs.sqlalchemy.org/en/20/changelog/whatsnew_20.html](https://docs.sqlalchemy.org/en/20/changelog/whatsnew_20.html)). Resumen de los cambios entre v1 y v2. Útil cuando te cruzás con tutoriales viejos.
- **ORM Querying Guide** ([docs.sqlalchemy.org/en/20/orm/queryguide/](https://docs.sqlalchemy.org/en/20/orm/queryguide/)). La doc completa de `select`, `update`, `delete` con el ORM. Sección "Loading Relationships" (`selectinload`/`joinedload`) es la clave para evitar N+1.
- **Asyncio support** ([docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)). Cuando estés listo para `AsyncSession`.
- **Alembic** ([alembic.sqlalchemy.org](https://alembic.sqlalchemy.org/)). El sistema de migraciones de SQLAlchemy. Es lo que vas a usar **en lugar de** `Base.metadata.create_all` en producción.

## Lecturas guiadas

- **Mike Bayer — SQLAlchemy 2.0 talks** (varias en YouTube). Mike es el autor de SQLAlchemy. Sus charlas en PyCon 2022 y 2023 explican por qué se rediseñó la API.
- **Real Python — SQLAlchemy 2.0 / FastAPI articles** ([realpython.com](https://realpython.com/)). Múltiples artículos prácticos, cuidado con que algunos pre-2.0 todavía aparecen en Google.
- **Testdriven.io — Async SQLAlchemy with FastAPI** ([testdriven.io](https://testdriven.io/)). Bueno para ver el patrón real "async stack completo".
- **The SQLAlchemy ORM** (Iván Cordoba) — varios screencasts en YouTube en español. Útil si preferís el formato hablado.

## Para profundizar

- **Database Internals** (Alex Petrov, O'Reilly). Cómo funcionan los engines de DB por dentro. No es SQLAlchemy específico — es entender QUÉ está abstrayendo el ORM.
- **Designing Data-Intensive Applications** (Martin Kleppmann). Otra vez aparece. Capítulos sobre transacciones y consistencia te dan el contexto que un ORM no te da.
- **High Performance Python** (Micha Gorelick & Ian Ozsvald). Cuando necesites bajar el rendimiento del ORM, esta referencia te ayuda con el thinking.
- **SQLModel** ([sqlmodel.tiangolo.com](https://sqlmodel.tiangolo.com/)). De Sebastián Ramírez. Combina pydantic + SQLAlchemy en una sola clase. Para proyectos chicos puede ser conveniente; para entender los conceptos, el approach separado del curso es mejor.

## Herramientas que vale la pena conocer

- **Alembic** — migraciones para SQLAlchemy. Cuando llegues a M5/M6 vas a quererlo en lugar de `create_all`.
- **`sqltap`** — profiler de SQLAlchemy. Te muestra qué queries se ejecutan, cuánto tardan, y dónde están las N+1.
- **`pgcli` / `litecli`** — REPLs interactivos para Postgres y SQLite.
- **DBeaver** / **DataGrip** — clientes gráficos para explorar la base.

## Referencias para resolver dudas puntuales

- **"`session.query` no funciona / da deprecation"** — usás v2 con sintaxis v1. Reemplazá por `session.scalar(select(Modelo).where(...))`.
- **"Mi UPDATE no se aplica"** — falta `session.commit()`, o el objeto está detached (lo cargaste en una sesión que ya cerraste).
- **"`Mapped[int]` no se reconoce"** — heredaste de `Base` que NO es `DeclarativeBase`. La v2 requiere `class Base(DeclarativeBase): pass`.
- **"Mil queries en mi endpoint"** — tenés N+1. Prefijá la relación con `selectinload(Modelo.relacion)`.
- **"`relationship` me devuelve `None`"** — chequeá el `back_populates`. Si solo está en un lado, la sincronía se rompe. Y mirá si la sesión sigue abierta: una relación lazy en una sesión cerrada explota.
- **"`echo=True` me llena la consola"** — desactívalo cuando confirmes lo que necesitabas. En producción siempre `echo=False`.

## Errores comunes

- **Confundir `Engine` y `Session`** — el engine es global; la sesión es por unidad de trabajo. Crearlos al revés explota.
- **Compartir sesiones entre threads** — la `Session` no es thread-safe. Usá `scoped_session` o (mejor) una sesión por request en frameworks como FastAPI.
- **Olvidarse del `commit`** — los cambios se pierden al cerrar la sesión.
- **Usar `Base.metadata.create_all` en producción** — borra y recrea sin avisar; perdés datos. **Migraciones con Alembic** es la respuesta.
- **No diferenciar DTO de modelo ORM** — terminás con un solo modelo que es un poco mutable, un poco frozen, un poco entrada de API, un poco fila de DB. Confuso y propenso a bugs.
- **Tipos pydantic v1 mezclados** — si tu pyproject tiene pydantic v2 pero alguien dejó `class Config: orm_mode = True`, eso es v1. En v2 es `model_config = ConfigDict(from_attributes=True)`.
- **Precargar TODO con `joinedload`** — un join sobre 1-N infla las filas exponencialmente. `selectinload` casi siempre es mejor para 1-N.

## Si vas hacia el curso 2

En AI Engineering vas a usar SQLAlchemy en al menos cuatro contextos:

- **Logs y auditoría de llamadas a LLMs** — cada request, cada respuesta, cada token, persistido para debugging y métricas.
- **Memoria conversacional** — historial de chats, asociado a usuarios. Una tabla `mensaje` con foreign key a `conversacion` y a `usuario`.
- **Metadata de embeddings** — el embedding vive en pgvector, pero el "qué documento es", "qué versión", "quién lo subió" vive en SQLAlchemy.
- **Estados de agentes** — cuando un agente persiste su estado entre turnos (cosa común en LangGraph), SQLAlchemy es lo que lo guarda.

La disciplina del curso 1 — pydantic en bordes, ORM en el centro, repositorios como cremallera — es **exactamente** la que te va a dejar dormir tranquilo en el curso 2 cuando los flujos sean async-everything con cinco servicios externos en juego.

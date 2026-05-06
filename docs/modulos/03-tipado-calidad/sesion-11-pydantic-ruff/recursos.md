# S11 — Recursos

## Documentación oficial — pydantic

- **pydantic v2 documentation** ([docs.pydantic.dev/latest/](https://docs.pydantic.dev/latest/)). La doc completa. Empieza por "Concepts → Models" y "Concepts → Validators".
- **Migration guide v1 → v2** ([docs.pydantic.dev/latest/migration/](https://docs.pydantic.dev/latest/migration/)). Si te cruzas con código pydantic v1 en otros proyectos, esta guía te muestra el mapeo de APIs.
- **Validators** ([docs.pydantic.dev/latest/concepts/validators/](https://docs.pydantic.dev/latest/concepts/validators/)). `@field_validator`, `@model_validator`, modos (`before`, `after`, `wrap`). Léelo cuando necesites validación que cruza campos.
- **Serialization** ([docs.pydantic.dev/latest/concepts/serialization/](https://docs.pydantic.dev/latest/concepts/serialization/)). `model_dump`, `model_dump_json`, `@field_serializer`, `@model_serializer`. Cuando devuelves modelos por una API, esta página es tu compañera.
- **JSON Schema** ([docs.pydantic.dev/latest/concepts/json_schema/](https://docs.pydantic.dev/latest/concepts/json_schema/)). pydantic genera JSON Schema gratis a partir de un `BaseModel`. Útil para documentar APIs en M5.
- **Performance** ([docs.pydantic.dev/latest/concepts/performance/](https://docs.pydantic.dev/latest/concepts/performance/)). Una vez que entiendas el modelo de validación, esta página explica cuándo pagas el costo y cuándo no.

## Documentación oficial — ruff

- **Ruff documentation** ([docs.astral.sh/ruff/](https://docs.astral.sh/ruff/)). La doc completa. Empieza por "Tutorial".
- **Rules** ([docs.astral.sh/ruff/rules/](https://docs.astral.sh/ruff/rules/)). Catálogo completo de reglas. Cada regla con descripción y ejemplos.
- **Configuration** ([docs.astral.sh/ruff/configuration/](https://docs.astral.sh/ruff/configuration/)). Cómo se configura ruff en `pyproject.toml`.
- **Formatter** ([docs.astral.sh/ruff/formatter/](https://docs.astral.sh/ruff/formatter/)). El formatter de ruff es un reemplazo drop-in de black. Esta página explica las pequeñas diferencias.

## Documentación oficial — pre-commit

- **pre-commit documentation** ([pre-commit.com](https://pre-commit.com/)). Setup, formato del config, hooks disponibles.
- **Hooks supported by ruff** ([github.com/astral-sh/ruff-pre-commit](https://github.com/astral-sh/ruff-pre-commit)). Repo oficial con la versión más reciente del hook.

## Lecturas opcionales

- **Real Python — Pydantic: Simplifying Data Validation in Python** ([realpython.com/python-pydantic/](https://realpython.com/python-pydantic/)). Recorrido completo con ejemplos prácticos.
- **Sebastián Ramírez (creador de FastAPI) sobre pydantic** — varios videos en YouTube. Buenas explicaciones de por qué pydantic se diseñó así. [github.com/tiangolo](https://github.com/tiangolo).
- **Astral Blog — "Ruff Becomes the Python Formatter"** ([astral.sh/blog/the-ruff-formatter](https://astral.sh/blog/the-ruff-formatter)). El anuncio del formatter. Útil para entender la motivación.
- **Anthony Sottile — pre-commit videos** ([youtube.com/@anthonywritescode](https://www.youtube.com/@anthonywritescode)). Anthony es el creador de pre-commit. Sus videos son técnicos y van al grano.

## Para profundizar

- **PEP 557 — Data Classes** y **pydantic models**. Comparar las dos páginas oficiales lado a lado es un ejercicio que acelera el entendimiento de cuándo usar cada uno.
- **Hynek Schlawack — "Subclassing in Python Redux"** ([hynek.me/articles/python-subclassing-redux/](https://hynek.me/articles/python-subclassing-redux/)). Discusión sobre cuándo usar herencia, `BaseModel`, `attrs`, etc.

## Referencias para resolver dudas puntuales

- **`@dataclass` vs `BaseModel`**: el resumen del README es: **bordes → BaseModel, internos → dataclass**. Si dudas, la pregunta clave es: ¿estos datos vienen de afuera de mi código?
- **`strict=True` rompe mi conversión** — sí, ese es el punto. Si los datos vienen como string, `Field(coerce_numbers_to_str=False)` no aplica aquí. Considera si el origen debería estar enviando ya el tipo correcto.
- **mypy + pydantic plugin** — `plugins = ["pydantic.mypy"]` en `[tool.mypy]` activa un plugin que mejora la inferencia de tipos sobre BaseModel. Recomendado siempre.
- **Por qué pre-commit no formatea cuando rechaza** — el hook arregla, deja los archivos modificados pero rechaza el commit para que verifiques los cambios y los re-stagees. Es un patrón de "approve once, commit again".

## Errores comunes

- **`ValidationError` no se imprime "bonito"** — usa `e.errors()` para obtener la lista estructurada. Es lo que tu UI consume.
- **`model_validate` recibe lo que parece un dict pero falla** — chequea que sea un dict puro, no una `dict_keys()` ni un objeto que se "parece". `model_validate` no convierte arbitrariamente.
- **Pre-commit "no se ejecuta"** — chequea que ejecutaste `pre-commit install` después de clonar. El comando agrega el hook a `.git/hooks/pre-commit` pero ese directorio NO está versionado.
- **Ruff y mypy reportan cosas distintas** — ruff es estilo + bugs sintácticos; mypy es tipos. Son complementarios. No te quedes con uno solo.

## Si vas hacia el curso 2

En AI Engineering, pydantic es **omnipresente**:

- **Tools de un agente** se definen como `BaseModel`. El LLM "ve" el JSON Schema generado por pydantic.
- **Respuestas estructuradas** se piden con `response_format = MiModelo` en lugar de parsear JSON manualmente.
- **Configuración** del agente con `pydantic-settings` (variables de entorno tipadas).

mypy + ruff son la línea de base de cualquier proyecto serio. Asegúrate de tener fluidez con ambos antes de avanzar — los próximos módulos asumen que el `pyproject.toml` con esta config es **lo normal**, no la excepción.

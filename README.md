# Curso de Fundamentos de Python

Curso de fundamentos de programación en Python, pensado para personas que **apenas están aprendiendo a programar** y quieren llegar a poder construir software real — APIs, bases de datos, contenedores, tests.

Es el **primer curso** de una ruta de dos. Al terminar este vas a estar listo para arrancar [`python-ai-engineer-training`](https://github.com/JoseCOCA/python-ai-engineer-training) (segundo curso, AI Engineering en Python), o cualquier rol de backend junior.

> **Filosofía:** conceptos antes que código. Cimientos sólidos antes que frameworks. Si no entiendes lo que estás escribiendo, no lo estás aprendiendo — lo estás copiando.

---

## ¿A quién está dirigido?

- Personas que **apenas empiezan a programar** o que han visto algo suelto pero no sienten que dominen nada.
- Personas que quieren entrar a la industria del software o, eventualmente, a AI Engineering, **sin saltarse fundamentos**.
- No se asume conocimiento previo de programación, ni de Python, ni de terminal, ni de Git.

**Lo único que se asume:**
- Una computadora con Linux, macOS o Windows.
- Disposición para invertir tiempo. Esto **no** es un curso de "aprende a programar en 30 días".
- Comodidad mínima leyendo inglés (mucha documentación técnica está solo en inglés). Si no la tienes, te la vas a ir construyendo durante el curso.

**Lo que este curso NO es:**
- No es un curso de "scripts de Python" ni de automatización casera.
- No es un curso de Data Science ni de Machine Learning.
- No es un curso para "ya saber Python en una semana". Programar bien lleva tiempo y este curso lo respeta.

## Stack

| Capa | Herramienta |
|------|-------------|
| Lenguaje | **Python 3.12+** |
| Package manager y entornos | **uv** (Astral) — el equivalente moderno de `pip` + `venv`, mucho más rápido y simple |
| Linting y formateo | **ruff** |
| Type checking | **mypy** |
| Tests | **pytest** |
| API framework | **FastAPI** (Módulo 5) |
| Validación de datos | **pydantic** (Módulos 3 y 5) |
| Base de datos | **PostgreSQL** + **SQLAlchemy** (Módulo 4) |
| Contenedores | **Docker** + **docker-compose** (Módulo 6) |
| Versionado | **Git** + GitHub (transversal, profundización en Módulo 6) |

Todo lo necesario corre **localmente**. Costo del curso: **USD 0**.

## Cómo usar este repo

1. Empieza por [`docs/00-curriculum.md`](docs/00-curriculum.md) — el diseño curricular maestro. **Léelo antes de tocar código.**
2. Sigue con [`docs/01-setup.md`](docs/01-setup.md) (cuando esté publicado) — instalación de Python, uv, editor y terminal.
3. Recorre los módulos en orden. Cada sesión vive en `docs/modulos/MM-modulo/sesion-NN-tema/` y tiene:
   - `README.md` — teoría
   - `ejercicios.md` — práctica guiada
   - `recursos.md` — lecturas y referencias
4. El código de cada sesión vive en `code/mMM-modulo/sesion-NN/`.
5. El proyecto integrador (**TiendaPro Lite**, una API REST de e-commerce) vive en `code/proyecto-integrador/` y se construye módulo a módulo.

## Estructura del repo

```
.
├── docs/
│   ├── 00-curriculum.md             ← diseño curricular maestro
│   ├── 01-setup.md
│   └── modulos/
│       ├── 00-setup-mentalidad/
│       ├── 01-python-fundamentos/
│       ├── 02-python-intermedio/
│       ├── 03-tipado-calidad/
│       ├── 04-async-http-persistencia/
│       ├── 05-api-fastapi/
│       └── 06-herramientas-ingeniero/
├── code/                            ← sandboxes de cada sesión + proyecto integrador
│   ├── m00-setup-mentalidad/
│   ├── m01-python-fundamentos/
│   ├── ...
│   └── proyecto-integrador/         ← TiendaPro Lite (API REST que crece sesión a sesión)
├── pyproject.toml                   ← deps de tooling del curso (ruff, mypy, pytest)
├── .python-version                  ← Python 3.12
└── env.example                      ← copiar a .env (variables de entorno)
```

## Mapa de los 7 módulos

0. **Setup y mentalidad del programador** — terminal, Python, uv, editor, cómo aprender a programar sin frustrarse.
1. **Python fundamentos** — variables, control de flujo, estructuras de datos, funciones, strings.
2. **Python intermedio + organización** — módulos, errores, OOP, decoradores y generadores (lo justo).
3. **Tipado y calidad de código** — type hints, mypy, ruff, pre-commit.
4. **Async, HTTP y persistencia** — `asyncio`, `httpx`, SQL básico, SQLAlchemy.
5. **Construir una API real** — FastAPI, pydantic, configuración, logging.
6. **Herramientas del ingeniero** — Git profundizado, Docker, pytest.

Detalle completo en [`docs/00-curriculum.md`](docs/00-curriculum.md).

## Proyecto integrador: TiendaPro Lite

A lo largo del curso vas a construir **TiendaPro Lite**, una API REST de e-commerce con catálogo, clientes y pedidos, persistida en PostgreSQL, validada con pydantic, testeada con pytest y empaquetada en Docker.

Es el **mismo producto** sobre el que arranca el segundo curso ([python-ai-engineer-training](https://github.com/JoseCOCA/python-ai-engineer-training)) — al terminar este curso, tu TiendaPro Lite es exactamente el punto de partida del próximo.

| Hito | Capacidades agregadas |
|------|----------------------|
| `proyecto-m1` | Primer script de Python que valida datos del catálogo desde un JSON |
| `proyecto-m2` | Catálogo modelado con clases, errores manejados, organizado en paquete |
| `proyecto-m3` | Catálogo tipado con pydantic, lint y type-check pasando |
| `proyecto-m4` | Catálogo persistido en PostgreSQL con SQLAlchemy + cliente HTTP que consume APIs externas |
| `proyecto-m5` | API REST funcional con FastAPI: CRUD de productos, clientes y pedidos |
| `proyecto-m6` | API testeada (pytest), versionada (Git), empaquetada (Docker) |

## Setup rápido (referencia — el detalle está en M0)

```bash
# 1. Instala uv (si no lo tienes ya)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Instala Python 3.12 vía uv
uv python install 3.12

# 3. Sincroniza dependencias del curso
uv sync

# 4. Verifica que todo funciona
uv run python --version    # → Python 3.12.x
uv run ruff --version
uv run mypy --version
uv run pytest --version
```

## Licencia

Este repositorio usa **licenciamiento dual** para distinguir entre código y contenido pedagógico:

- **Código** — todo lo que vive en `code/`, los bloques de código dentro de la documentación, y los archivos de configuración (`pyproject.toml`, `docker-compose.yml`, `env.example`, etc.) está licenciado bajo [**MIT**](LICENSE). Libre uso comercial y privado con atribución.
- **Contenido pedagógico** — `README.md`, todo lo que vive en `docs/` y el material escrito de las sesiones está licenciado bajo [**Creative Commons Attribution 4.0 International (CC BY 4.0)**](LICENSE-CONTENT). Libre uso comercial y derivados con atribución obligatoria al autor.

**Atribución sugerida si reutilizas el material:**

> "Curso de Fundamentos de Python (python-training-fundamentals)" por José Coca, licenciado bajo CC BY 4.0.
> Fuente: https://github.com/JoseCOCA/python-training-fundamentals

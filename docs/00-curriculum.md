# 00 — Diseño curricular maestro

> **Léeme primero.** Este documento define el curso entero: a quién va dirigido, qué vas a aprender, en qué orden, con qué stack y cómo se evalúa. Sin esto leído, los módulos individuales pierden contexto.

---

## 1. Filosofía del curso

El curso se construye sobre tres principios:

1. **Conceptos antes que código.** La sintaxis de Python la encuentras en cualquier doc en cinco minutos. Lo que separa a un buen programador de uno mediocre es entender QUÉ está haciendo el código y POR QUÉ. Por cada hora que vas a escribir Python, vas a invertir otra hora entendiendo por qué se escribe así.
2. **Cimientos sólidos antes que frameworks.** Vamos a entender qué es una función ANTES de usar decoradores. Vamos a entender qué es HTTP ANTES de usar FastAPI. Si el framework cambia mañana — y va a cambiar — lo que aprendiste sigue valiendo.
3. **Programar es comunicar.** Tu código lo van a leer otras personas (incluido tu yo de dentro de seis meses). Escribir código que se entiende es tan importante como escribir código que funciona.

**Lo que este curso NO es:**
- No es un tour por la sintaxis de Python — la sintaxis es lo más fácil del oficio, y lo menos importante.
- No es un curso de Data Science, Machine Learning ni AI. Eso viene en el [curso siguiente](https://github.com/JoseCOCA/python-ai-engineer-training).
- No es un "Python en 30 días". Programar bien lleva años. Este curso te da los primeros 3-4 meses sólidos.

## 2. Audiencia

**Para quién:**
- Personas que **apenas empiezan a programar** o que han visto cosas sueltas (un tutorial por aquí, un libro por allá) sin sentir que dominan nada.
- Personas que quieren llegar a roles de software (backend junior, eventualmente AI Engineer) sin saltarse fundamentos.
- Personas con **paciencia** — este curso premia el tiempo invertido, no la velocidad.

**Lo único que se asume:**
- Computadora con Linux, macOS o Windows (con WSL, idealmente).
- Comodidad mínima leyendo inglés. La doc oficial de Python, FastAPI, SQLAlchemy y la mayoría de librerías está en inglés. Es OK si te cuesta — la lectura técnica se entrena leyéndola.

**Lo que este curso NO asume:**
- Programación previa.
- Conocimiento de terminal o Git.
- Conocimiento de inglés más allá de "puedo descifrar el sentido general de un párrafo".
- Matemáticas más allá del nivel de bachillerato.

## 3. Estrategia de lenguaje: Python puro, sin distracciones

A diferencia del curso de AI Engineering que es TypeScript-first, este curso es **100% Python**. La razón es pedagógica: cuando estás aprendiendo a programar, cambiar de lenguaje cada dos por tres es un anti-patrón. Vas a meter las manos profundo en un solo lenguaje hasta entenderlo de verdad.

Python fue elegido porque:
- Sintaxis legible — el "código pseudo-código" más cercano que existe.
- Es **el lenguaje** del ecosistema de IA. Lo que aprendas aquí te sirve directamente para el curso 2.
- Tiene tooling moderno excelente (uv, ruff, mypy, pydantic, FastAPI) que te enseña buenas prácticas desde el primer día.

## 4. Stack tecnológico completo

| Categoría | Tecnología | Cuándo entra |
|-----------|-----------|--------------|
| Lenguaje | Python 3.12+ | Módulo 0 |
| Package manager y venvs | **uv** (Astral) | Módulo 0 |
| Linting y formato | **ruff** | Módulo 3 |
| Type checking | **mypy** | Módulo 3 |
| Tests | **pytest** | Módulo 6 (mención antes) |
| Validación de datos | **pydantic** v2 | Módulos 3 y 5 |
| Cliente HTTP | **httpx** | Módulo 4 |
| Base de datos | **PostgreSQL** | Módulo 4 |
| ORM | **SQLAlchemy** v2 | Módulo 4 |
| API framework | **FastAPI** | Módulo 5 |
| Configuración | **pydantic-settings** | Módulo 5 |
| Contenedores | **Docker** + **docker-compose** | Módulo 6 |
| Versionado | **Git** + GitHub | transversal, profundización en M6 |

**Costo del curso:** USD 0. Todo corre localmente.

**Por qué uv y no pip+venv+requirements.txt:** porque a un alumno que está empezando NO se le puede pedir que pelee con cinco herramientas distintas a la vez. uv unifica package management, virtualenvs, gestión de versiones de Python y lockfiles en una sola herramienta. Es lo más cercano a "no pienses en el tooling, piensa en el código".

## 5. Mapa de aprendizaje y dependencias entre módulos

```
┌─────────────────────────────────────────────────────────────────┐
│ Módulo 0: Setup y mentalidad del programador                    │
│  Terminal, Python, uv, editor, cómo aprender a programar        │
└─────────────────────────────────────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ Módulo 1: Python fundamentos                                    │
│  Variables, control de flujo, estructuras de datos, funciones   │
│  → Primer script Python del proyecto integrador                 │
└─────────────────────────────────────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ Módulo 2: Python intermedio + organización                      │
│  Módulos, errores, OOP, decoradores y generadores básicos       │
│  → El proyecto integrador se vuelve un paquete real             │
└─────────────────────────────────────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ Módulo 3: Tipado y calidad de código                            │
│  Type hints, mypy, pydantic, ruff                               │
│  → El catálogo del integrador queda tipado y validado           │
└─────────────────────────────────────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ Módulo 4: Async, HTTP y persistencia                            │
│  asyncio, httpx, SQL, SQLAlchemy                                │
│  → El integrador persiste en PostgreSQL y consume APIs          │
└─────────────────────────────────────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ Módulo 5: Construir una API real con FastAPI                    │
│  Rutas, validación, configuración, logging                      │
│  → El integrador es ahora una API REST funcional                │
└─────────────────────────────────────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ Módulo 6: Herramientas del ingeniero                            │
│  Git en serio, Docker, pytest                                   │
│  → El integrador queda testeado, versionado y empaquetado       │
└─────────────────────────────────────────────────────────────────┘
                              ▼
                ┌──────────────────────────────────┐
                │  Listo para python-ai-engineer-  │
                │  training (curso 2)              │
                └──────────────────────────────────┘
```

**Cada módulo agrega una capa real al proyecto integrador.** No hay ejercicios desconectados — todo construye el mismo producto.

## 6. Proyecto integrador: TiendaPro Lite

**El producto:** una API REST de e-commerce que un negocio ficticio (**TiendaPro**) puede usar como backend de su sitio web. Expone:

- Catálogo de productos (CRUD).
- Clientes (CRUD).
- Pedidos (crear, listar, consultar estado).

**Por qué este caso:** combina las cuatro cosas que un backend junior tiene que saber hacer — modelar datos, persistirlos en una BD, exponerlos por HTTP y testearlos.

**Por qué TiendaPro y no otra cosa:** es el **mismo producto** que se usa en el curso 2 (`python-ai-engineer-training`). Cuando termines este curso y arranques el siguiente, vas a tomar el código de TiendaPro Lite tal como está y empezar a sumarle capacidades de IA encima. Continuidad pedagógica real, no ejercicios sueltos.

**Cómo crece a lo largo del curso:**

| Módulo | Hito del proyecto | Qué se agrega |
|--------|-------------------|---------------|
| M1 | Primer script | Lee un JSON con productos y los imprime ordenados por precio |
| M2 | Paquete organizado | Catálogo modelado con clases, errores manejados, código en módulos |
| M3 | Tipado y validado | pydantic para los DTOs del catálogo, mypy y ruff pasan limpio |
| M4 | Persistido | PostgreSQL + SQLAlchemy, modelos `Product`/`Customer`/`Order`, cliente `httpx` |
| M5 | API REST | FastAPI con endpoints CRUD, validación pydantic, configuración con pydantic-settings |
| M6 | Production-ready | Tests con pytest (>80% coverage), Dockerfile + docker-compose, README final |

**El código del proyecto vive en `code/proyecto-integrador/`** y cada hito de módulo es un commit etiquetado con tag `proyecto-m{N}`.

## 7. Estructura de los módulos y sesiones

| Módulo | Tema | Sesiones | Duración total estim. |
|--------|------|----------|----------------------|
| M0 | Setup y mentalidad del programador | 2 | ~3h |
| M1 | Python fundamentos | 5 | ~10h |
| M2 | Python intermedio + organización | 4 | ~8h |
| M3 | Tipado y calidad de código | 2 | ~4h |
| M4 | Async, HTTP y persistencia | 4 | ~8h |
| M5 | Construir una API real con FastAPI | 3 | ~6h |
| M6 | Herramientas del ingeniero | 3 | ~6h |
| **Total** | | **23** | **~45h** de contenido + ~30-50h de práctica del integrador |

### Módulo 0 — Setup y mentalidad del programador
| Sesión | Tema | Duración |
|--------|------|----------|
| S00.1 | Cómo aprender a programar (mindset, frustración, debugging mental, leer docs) | 1h |
| S00.2 | Setup del entorno: terminal, Python via uv, editor, primer "hola mundo" ejecutable | 2h |

### Módulo 1 — Python fundamentos
| Sesión | Tema | Duración |
|--------|------|----------|
| S01 | Variables, tipos primitivos y expresiones | 2h |
| S02 | Control de flujo: if/else, while, for, comprensiones de lista | 2h |
| S03 | Estructuras de datos: list, tuple, dict, set | 2h |
| S04 | Funciones, scope, argumentos, valores de retorno | 2h |
| S05 | Strings y manipulación de texto (clave para todo lo que viene) | 2h |

### Módulo 2 — Python intermedio + organización
| Sesión | Tema | Duración |
|--------|------|----------|
| S06 | Módulos, paquetes, imports, virtualenvs con uv | 2h |
| S07 | Manejo de errores: try/except, raise, jerarquía de excepciones | 2h |
| S08 | Programación orientada a objetos: clases, dataclasses, métodos | 2h |
| S09 | Decoradores, generadores y context managers (lo justo y necesario) | 2h |

### Módulo 3 — Tipado y calidad de código
| Sesión | Tema | Duración |
|--------|------|----------|
| S10 | Type hints, mypy y refactoring guiado por tipos | 2h |
| S11 | pydantic v2 + ruff + pre-commit hooks | 2h |

### Módulo 4 — Async, HTTP y persistencia
| Sesión | Tema | Duración |
|--------|------|----------|
| S12 | asyncio: qué bloquea, cuándo usar async, runtime model | 2h |
| S13 | HTTP cliente con httpx + parseo de JSON | 2h |
| S14 | SQL fundamentals: queries, joins, normalización | 2h |
| S15 | SQLAlchemy v2: Core + ORM, sessions, modelos relacionales | 2h |

### Módulo 5 — Construir una API real con FastAPI
| Sesión | Tema | Duración |
|--------|------|----------|
| S16 | FastAPI fundamentos: rutas, request/response, async handlers | 2h |
| S17 | Validación con pydantic, DTOs, manejo de errores HTTP | 2h |
| S18 | Configuración con pydantic-settings, secretos, logging estructurado | 2h |

### Módulo 6 — Herramientas del ingeniero
| Sesión | Tema | Duración |
|--------|------|----------|
| S19 | Git en serio: branches, rebase, conflictos, conventional commits | 2h |
| S20 | Docker y docker-compose: qué resuelven, cómo se construye una imagen | 2h |
| S21 | Testing con pytest: unit, integration, fixtures, mocks, coverage | 2h |

## 8. Estructura de cada sesión

Cada sesión sigue el mismo formato — **predecible y consumible en 1-2h**:

```
docs/modulos/MM-modulo/sesion-NN-tema/
├── README.md       ← Teoría + diagramas (lectura ~30-45 min)
├── ejercicios.md   ← Práctica guiada paso a paso (~30-60 min)
└── recursos.md     ← Enlaces, papers, lecturas opcionales

code/mMM-modulo/sesion-NN/
└── ...             ← Código de los ejercicios y demos
```

**Cada README de sesión tiene esta plantilla:**

1. **Objetivos de aprendizaje** — al terminar esto vas a poder X, Y, Z.
2. **Prerequisitos** — qué sesiones previas tienes que haber completado.
3. **Conceptos clave** — los 3-5 conceptos centrales con definiciones.
4. **Teoría** — desarrollo del tema con diagramas y ejemplos.
5. **Patrones y antipatrones** — qué hacer y qué evitar.
6. **Conexión con el proyecto integrador** — qué de lo que aprendiste vas a aplicar al producto.
7. **Resumen** — los 3 puntos que te tienes que llevar.
8. **Preguntas de auto-evaluación** — si no puedes responderlas, relee.

**Cada `ejercicios.md` tiene:**

1. **Ejercicio guiado** — paso a paso con código.
2. **Ejercicios libres** — variantes y experimentos.
3. **Reto** — algo más difícil para consolidar.
4. **Aporte al proyecto integrador** — el commit del módulo.

## 9. Sistema de evaluación

El curso es **autodidacta** pero está diseñado para evaluarte de forma honesta:

1. **Preguntas de auto-evaluación** al final de cada README. Si no puedes responderlas sin volver a leer, no aprendiste el concepto.
2. **Ejercicios prácticos** — código que tiene que correr y producir el output esperado.
3. **Hito del proyecto integrador** al final de cada módulo. Es el indicador más fuerte de progreso real.
4. **Retos opcionales** para empujarte más allá.

**No hay exámenes.** TiendaPro Lite funcionando, testeada y empaquetada al final del curso es el examen.

## 10. Convenciones del repo

### Convención de commits
**Conventional Commits** sin atribución de IA.

| Tipo | Cuándo se usa |
|------|---------------|
| `feat` | Nueva sesión, nuevo ejercicio, nueva funcionalidad del proyecto |
| `docs` | Cambios solo en documentación |
| `chore` | Setup, configuración, tooling |
| `fix` | Corrección de errores en docs o código |
| `refactor` | Reestructuración sin cambio de funcionalidad |
| `test` | Cambios solo en tests |

**Formato:**
```
<tipo>(<alcance>): <descripción corta>

[cuerpo opcional explicando el porqué]
```

**Ejemplos:**
```
feat(m00-s00.1): agrega sesión de mindset y cómo aprender a programar
docs(curriculum): clarifica esquema del proyecto integrador
chore(repo): añade pyproject.toml con uv + ruff + mypy + pytest
```

### Tags de hitos del proyecto integrador
Al cerrar cada módulo, se etiqueta el commit con:
```
proyecto-m1, proyecto-m2, ..., proyecto-m6
```

(Módulo 0 no tiene hito porque es solo setup.)

### Estructura de directorios de código
```
code/
├── m00-setup-mentalidad/
├── m01-python-fundamentos/
│   ├── sesion-01/
│   ├── sesion-02/
│   └── ...
├── m02-python-intermedio/
├── m03-tipado-calidad/
├── m04-async-http-persistencia/
├── m05-api-fastapi/
├── m06-herramientas-ingeniero/
└── proyecto-integrador/
    ├── README.md
    ├── pyproject.toml
    ├── src/
    └── tests/
```

## 11. Cómo seguir el curso

1. **No saltes módulos.** Cada uno depende del anterior.
2. **Haz los ejercicios.** Leer no es aprender — hacer es aprender.
3. **Construye el proyecto integrador en paralelo.** No lo dejes para el final.
4. **Si una sesión te lleva más del doble del tiempo estimado**, no te preocupes — ajusta el ritmo. Pero si te lleva menos de la mitad, probablemente la estás leyendo en piloto automático.
5. **Si no puedes explicarle el concepto a otra persona, no lo entendiste.** Prueba explicárselo a un compañero, a un patito de goma o a una IA.
6. **Equivocarse es parte del proceso.** Si no rompes nada, no estás aprendiendo. Si todo funciona a la primera, probablemente estás copiando.

## 12. Roadmap del repo

- [x] Estructura base + README + curriculum maestro
- [x] `01-setup.md` — instalación del entorno (Python via uv, editor, terminal)
- [x] Módulo 0 — Setup y mentalidad del programador (2 sesiones)
- [x] Módulo 1 — Python fundamentos (5 sesiones) — tag `proyecto-m1`
- [x] Módulo 2 — Python intermedio + organización (4 sesiones) — tag `proyecto-m2`
- [x] Módulo 3 — Tipado y calidad de código (2 sesiones) — tag `proyecto-m3`
- [x] Módulo 4 — Async, HTTP y persistencia (4 sesiones) — tag `proyecto-m4`
- [ ] Módulo 5 — Construir una API real con FastAPI (3 sesiones) — tag `proyecto-m5`
- [ ] Módulo 6 — Herramientas del ingeniero (3 sesiones) — tag `proyecto-m6`

## 13. Qué viene después

Al terminar este curso, vas a tener:

- Python sólido (de variables hasta async).
- Una API REST funcional, tipada, validada, persistida en PostgreSQL, testeada y dockerizada.
- Git, terminal, Docker, pytest en tu cinturón de herramientas.
- Capacidad de leer documentación técnica en inglés sin parálisis.

Con ese paquete, estás listo para:

- **Roles backend junior en Python** — la mayoría de empresas no te van a pedir más que esto para una posición junior.
- **El curso siguiente:** [`python-ai-engineer-training`](https://github.com/JoseCOCA/python-ai-engineer-training) — AI Engineering en Python, mismo nivel de exigencia que el curso original (`ai-engineer-training`) pero adaptado a Python. Vas a tomar TiendaPro Lite y agregarle capacidades de IA: LLMs, RAG, agentes, observabilidad, despliegue.

## 14. Referencias de recursos públicos

Si quieres contrastar el alcance del curso con otros materiales, o profundizar en un tema concreto:

- **Python Documentation** — [docs.python.org/3/](https://docs.python.org/3/). Referencia canónica del lenguaje. Aprende a leerla.
- **Real Python** — [realpython.com](https://realpython.com/). Tutoriales prácticos de calidad sobre Python intermedio y avanzado.
- **Fluent Python** (Luciano Ramalho, O'Reilly) — referencia para Python idiomático cuando ya tengas los fundamentos.
- **Python Cookbook** (David Beazley & Brian K. Jones) — recetas prácticas de problemas reales.
- **uv documentation** — [docs.astral.sh/uv](https://docs.astral.sh/uv/). Referencia del package manager del curso.
- **FastAPI documentation** — [fastapi.tiangolo.com](https://fastapi.tiangolo.com/). Una de las mejores docs de un framework de Python; vale la pena leerla entera.
- **SQLAlchemy 2.0 Tutorial** — [docs.sqlalchemy.org](https://docs.sqlalchemy.org/en/20/tutorial/). El tutorial oficial es completo y bien escrito.
- **Pro Git** (Scott Chacon) — [git-scm.com/book](https://git-scm.com/book/). Libro libre, referencia canónica de Git.
- **The Rust Book / Python Tutor** — Python Tutor ([pythontutor.com](https://pythontutor.com/)) sirve para visualizar paso a paso cómo se ejecuta tu código.
- **MDN Web Docs — HTTP** — [developer.mozilla.org/docs/Web/HTTP](https://developer.mozilla.org/docs/Web/HTTP). Referencia de HTTP usada por toda la industria.

---

**Próximo paso:** [`01-setup.md`](01-setup.md) → instalación del entorno (cuando esté publicado, primer trabajo del Módulo 0).

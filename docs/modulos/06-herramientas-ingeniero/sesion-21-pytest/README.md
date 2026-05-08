# S21 — Testing con pytest: unit, integration, fixtures, mocks, coverage

> **Sesión 2h.** ~50 min lectura + ~70 min ejercicios. **Cierra el Módulo 6 y el curso completo.** Hasta acá tu app fue creciendo y cada vez te animabas más a refactorearla — pero "no romper nada" se basaba en correr `main.py` y mirar la salida. Eso no escala. Hoy entra el último pilar: **tests automatizados con pytest**. Vas a aprender a escribir tests que sirven como especificación ejecutable, a separar unit de integration, a usar fixtures para evitar boilerplate, a mockear lo que no querés tocar (HTTP real, DB real), a medir cobertura, y a conectarlo todo en TiendaPro Lite. Cuando termines, tenés el integrador listo con tag `proyecto-m6`.

---

## 1. Objetivos de aprendizaje

Al terminar esta sesión vas a poder:

- Explicar **por qué testear**: especificación ejecutable, regression net, doc viva. Distinguir lo que un test prueba de lo que NO prueba.
- Diferenciar **unit, integration y e2e** según qué se aísla y qué se ejercita.
- Estructurar un proyecto con `tests/` y entender el descubrimiento automático de pytest.
- Escribir tests con `assert` plano (sin frameworks XUnit), siguiendo **Arrange-Act-Assert**.
- Usar **fixtures** (`@pytest.fixture`) para preparar contexto reutilizable, con **scopes** (`function`, `module`, `session`).
- Parametrizar tests con `@pytest.mark.parametrize` (un test, N entradas).
- Diferenciar **mock**, **fake**, **stub** y **spy**, y decidir cuál corresponde.
- Mockear con `unittest.mock` (`Mock`, `patch`, `monkeypatch`) **solo cuando hace falta**.
- Testear endpoints de FastAPI con `TestClient` sin levantar un servidor real.
- Inyectar configuración de test (DB en memoria, mocks de HTTP) usando `dependency_overrides`.
- Medir cobertura con `coverage.py` / `pytest-cov` y entender qué te dice (y qué no).
- Cerrar el integrador con la suite de tests, Dockerfile que corre tests en CI, y README final del curso.

## 2. Prerequisitos

- [S19 — Git](../sesion-19-git/README.md) y [S20 — Docker](../sesion-20-docker/README.md). Ya tenés branches de feature, Dockerfile y compose.
- [S15 — SQLAlchemy v2](../../04-async-http-persistencia/sesion-15-sqlalchemy/README.md) y [S17 — Validación + DTOs](../../05-api-fastapi/sesion-17-validacion-dtos/README.md). Vas a testear capas: dominio, repositorio, API.
- [S18 — pydantic-settings + logging](../../05-api-fastapi/sesion-18-config-logging/README.md). Vas a usar `dependency_overrides` para inyectar settings de test.

## 3. Conceptos clave

1. **Test = especificación ejecutable.** Un test bien escrito describe **el contrato** que el código debe cumplir. La doc miente; los tests no.
2. **Pirámide de tests.** Muchos unit (rápidos, aislados), algunos integration (más lentos, prueban combinaciones), pocos e2e (lentos, frágiles, prueban el sistema entero).
3. **AAA — Arrange / Act / Assert.** Estructura mental: preparás contexto, ejecutás la acción, verificás el resultado. Un test no debería entrelazarlas.
4. **Fixture.** Una pieza de "contexto" preparada por una función decorada con `@pytest.fixture`. pytest la inyecta en los tests que la piden por nombre de parámetro.
5. **Scope.** Cuánto tiempo vive una fixture: `function` (default — una por test), `module`, `class`, `session`. Más amplio = más rápido pero menos aislado.
6. **Parametrize.** Misma lógica de test, distintas entradas/expectativas. `@pytest.mark.parametrize` evita duplicación y reporta cada caso por separado.
7. **Mock vs fake vs stub vs spy.** Doubles distintos: el mock verifica interacciones, el fake es una implementación liviana real, el stub devuelve respuestas preparadas, el spy registra llamadas.
8. **Coverage.** % de líneas / branches que tus tests ejecutan. Útil como **señal**, no como meta. 100% de coverage no garantiza calidad — testear mal cubre todo y prueba nada.
9. **`TestClient` de FastAPI.** Cliente HTTP en proceso (no levanta servidor) que ejercita la app real, ideal para integration tests de la API.
10. **`dependency_overrides`.** Mecanismo de FastAPI para reemplazar dependencias en tests: settings con valores fake, repositorio en memoria, etc. Sin tocar el código de producción.

## 4. Teoría

### 4.1. ¿Por qué testear?

Tres razones, en orden de importancia:

1. **Diseño.** Un código fácil de testear es un código bien diseñado. Si para testear `crear_pedido()` necesitás levantar un Postgres, mockear tres APIs externas y un cron job, tu función está acoplada a todo. Los tests **te empujan** hacia funciones puras, dependencias inyectadas, capas separadas.
2. **Regression net.** Cambiás algo y querés saber **inmediatamente** si rompiste otra cosa. Sin tests: probás "a ojo" lo que recordás, y el bug aparece en producción.
3. **Documentación viva.** La doc de un parámetro caduca apenas alguien lo edita sin actualizar. Los tests, si pasan, **prueban** que la función hace lo que dice.

Lo que tests NO te dan:

- Funcionalidad correcta — solo verifican lo que vos imaginaste verificar. Si nunca te imaginaste un input vacío, no hay test que te avise.
- Performance — para eso hay benchmarks, no asserts.
- Compatibilidad de despliegue — eso es CI + integration tests con la stack real.
- Cumplimiento de seguridad — eso requiere otras herramientas (linters de seguridad, SAST, fuzzing).

**Regla**: los tests son **una** capa de defensa, no la única.

### 4.2. La pirámide de tests

```
            ╱╲
           ╱e2╲           ← muy pocos: lentos, frágiles, costosos
          ╱────╲
         ╱      ╲
        ╱  int   ╲        ← algunos: prueban combinaciones (DB real, HTTP real)
       ╱──────────╲
      ╱            ╲
     ╱     unit     ╲     ← muchos: rápidos (ms), aislados, casi puros
    ╱────────────────╲
```

- **Unit**: prueba **una unidad** (función, clase) sin tocar IO. Microsegundos por test. Los corrés cada vez que guardás un archivo.
- **Integration**: prueba **una combinación** de unidades, típicamente con IO real (DB, archivo, HTTP). Décimas de segundo por test. Los corrés antes de pushear.
- **End-to-end (e2e)**: prueba el sistema entero, simulando un cliente real (curl, navegador). Segundos a minutos. Los corrés antes de release.

**Anti-pirámide** (mal): muchos e2e, pocos unit. Suite lenta, frágil (un timeout cualquiera te tira el build entero), debug difícil. Síntoma de que el código es testeable solo "de afuera".

### 4.3. pytest: lo que necesitás saber para arrancar

#### Estructura

```
proyecto/
├── src/
│   └── tiendapro/
│       └── ...
├── tests/
│   ├── conftest.py          ← fixtures compartidas
│   ├── unit/
│   │   └── test_modelos.py
│   └── integration/
│       └── test_api.py
└── pyproject.toml
```

pytest **descubre tests automáticamente**:

- Archivos: `test_*.py` o `*_test.py`.
- Clases: `Test*` (sin `__init__`).
- Funciones: `test_*`.

#### El test más simple

```python
# tests/unit/test_modelos.py
from tiendapro.modelos import Producto


def test_producto_disponible_si_stock_positivo() -> None:
    producto = Producto(nombre="Cable USB-C", categoria="cables", precio=10.0, stock=5)
    assert producto.disponible() is True


def test_producto_no_disponible_si_stock_cero() -> None:
    producto = Producto(nombre="Cable USB-C", categoria="cables", precio=10.0, stock=0)
    assert producto.disponible() is False
```

Correr:

```bash
uv run pytest                           # corre toda la suite
uv run pytest tests/unit                # solo unit
uv run pytest -k disponible             # solo tests que matcheen "disponible"
uv run pytest -v                        # verbose: muestra cada test
uv run pytest -x                        # parar al primer fallo
uv run pytest --lf                      # solo los que fallaron la última vez
uv run pytest --pdb                     # entrá al debugger en el primer fallo
```

#### `assert` plano

A diferencia de unittest (`self.assertEqual(a, b)`), pytest reescribe los `assert` a la hora de fallar y te da output útil:

```
>       assert producto.disponible is False
E       assert True is False
E         where True = Producto(id=1, nombre='X', stock=5).disponible
```

No necesitás `assertEqual`, `assertTrue`, etc. `assert <cualquier cosa>` con el mensaje opcional `assert <cond>, "mensaje"`.

#### `pytest.raises` para excepciones

```python
import pytest
from pydantic import ValidationError


def test_producto_rechaza_precio_negativo() -> None:
    with pytest.raises(ValidationError, match="precio"):
        Producto(nombre="X", categoria="c", precio=-1.0, stock=0)
```

`match` es un regex sobre el mensaje. Útil para verificar que la excepción es la **correcta**, no cualquiera.

### 4.4. Arrange-Act-Assert: la estructura mental

```python
def test_aplicar_descuento_reduce_precio() -> None:
    # Arrange — preparar contexto
    producto = Producto(nombre="Cable", categoria="cables", precio=100.0, stock=1)

    # Act — ejecutar la acción bajo test
    final = aplicar_descuento(producto, porcentaje=20)

    # Assert — verificar resultado
    assert final.precio == 80.0
    assert final.nombre == producto.nombre
    assert producto.precio == 100.0  # el original no se mutó (frozen=True)
```

No hace falta poner los comentarios; el patrón es **mental**. Pero si el test crece más allá de 5-7 líneas, suele ser señal de que la unidad bajo test hace demasiado.

**Regla informal**: un test prueba **una cosa**. Si necesitás varias `assert`, está bien — siempre que sean facetas del mismo resultado. Si verificás dos comportamientos no relacionados, partilo en dos tests.

### 4.5. Fixtures: contexto reutilizable

```python
import pytest
from tiendapro.modelos import Producto


@pytest.fixture
def producto_base() -> Producto:
    return Producto(nombre="Cable", categoria="cables", precio=10.0, stock=5)


def test_disponible(producto_base: Producto) -> None:
    assert producto_base.disponible() is True


def test_aplicar_descuento(producto_base: Producto) -> None:
    final = aplicar_descuento(producto_base, 20)
    assert final.precio == 8.0
```

pytest detecta el parámetro `producto_base`, busca una fixture con ese nombre, la ejecuta y le pasa el resultado al test. Cero magia más allá del nombre.

#### Scopes

```python
@pytest.fixture(scope="session")    # una sola vez por toda la corrida
def engine() -> Engine:
    e = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(e)
    return e


@pytest.fixture(scope="function")   # default: una vez por test
def session(engine: Engine) -> Iterator[Session]:
    s = Session(engine)
    try:
        yield s
    finally:
        s.rollback()                # rollback al final = aislamiento entre tests
        s.close()
```

**Regla**: empezá con `scope="function"` (lo más aislado). Si la fixture es cara (crear engine, levantar contenedor) y los tests no la modifican, subí el scope.

#### `yield` para teardown

Una fixture con `yield` corre lo de antes (setup), entrega el valor, y al terminar el test corre lo de después (teardown):

```python
@pytest.fixture
def archivo_temporal(tmp_path) -> Iterator[Path]:
    path = tmp_path / "datos.json"
    path.write_text('{"x": 1}')
    yield path
    # teardown automático: pytest borra tmp_path al final
```

`tmp_path` es una fixture **builtin** de pytest — te da un directorio temporal único por test que se limpia solo.

#### `conftest.py`

Las fixtures que valen para varios módulos van a `tests/conftest.py`. pytest las descubre automáticamente — no hay que importarlas.

### 4.6. Parametrizar: un test, N entradas

```python
import pytest


@pytest.mark.parametrize("stock,esperado", [
    (5, True),
    (1, True),
    (0, False),
])
def test_producto_disponible_segun_stock(stock: int, esperado: bool) -> None:
    p = Producto(nombre="Cable", categoria="cables", precio=1.0, stock=stock)
    assert p.disponible() is esperado
```

pytest genera 4 tests separados (uno por tupla). Si uno falla, ves cuál y por qué — sin que un fallo enmascare a los otros. `pytest.param(..., id=...)` te deja darle un nombre legible al caso.

**Cuándo parametrizar**: cuando el cuerpo del test sería el mismo para varios inputs y el test es chico. Si cada caso requiere setup distinto, no parametrices — separalos.

### 4.7. Mock, fake, stub, spy: el zoo de los doubles

Todos son "objetos de mentira" que reemplazan dependencias reales. Tienen propósitos distintos:

| Tipo | Qué hace | Ejemplo típico |
|---|---|---|
| **Mock** | Cualquier llamada queda registrada; podés verificarla después | "verificá que `enviar_email` se llamó una vez con `to=...`" |
| **Stub** | Devuelve respuestas predefinidas, no le importa cómo lo llamés | "cuando llamen a `obtener_precio()`, devolvé `99.0`" |
| **Fake** | Implementación real pero liviana, intercambiable por la real | DB en memoria que se comporta como Postgres |
| **Spy** | Wrapper que llama al real Y registra las llamadas | "que la función real corra, pero contá cuántas veces" |

En Python, `unittest.mock.Mock` cubre los tres primeros casos. Los nombres se confunden todo el tiempo — lo importante es la **intención**.

#### `unittest.mock`

```python
from unittest.mock import Mock, patch
import httpx


def test_obtener_clima_con_mock() -> None:
    cliente_mock = Mock(spec=httpx.Client)
    cliente_mock.get.return_value.json.return_value = {"temp": 22}

    resultado = obtener_clima(cliente_mock, "Buenos Aires")

    assert resultado == 22
    cliente_mock.get.assert_called_once_with("/clima?ciudad=Buenos%20Aires")
```

`spec=httpx.Client` hace que el Mock acepte solo atributos que existen en `httpx.Client` real — te avisa si te equivocaste de nombre.

`patch` reemplaza un nombre **donde se usa**, durante el test:

```python
from unittest.mock import patch


def test_envia_alerta_si_falla() -> None:
    with patch("tiendapro.alertas.enviar_email") as enviar_mock:
        ejecutar_job_que_alerta_si_falla(simulado_falla=True)
        enviar_mock.assert_called_once()
```

#### `monkeypatch` — la fixture nativa de pytest

`monkeypatch` es una fixture builtin que permite parchar atributos, env vars y `sys.path`, **con teardown automático** al final del test:

```python
def test_lee_env_var(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TIENDAPRO_DEBUG", "true")
    assert leer_debug() is True
```

Preferida sobre `os.environ[...] = ...` porque revierte automáticamente.

#### Cuándo NO mockear

- **Funciones puras del dominio**: testealas directo, sin mocks. Si `aplicar_descuento(producto, 20)` es pura, no hay nada que mockear.
- **Librerías estándar y bien testeadas**: no mockés `datetime.now()` con un mock complejo si una fixture con un valor fijo alcanza.
- **Tu propio código que ya tiene tests**: si el repositorio ya está testeado, en los tests del servicio que lo usa preferí un fake (repositorio en memoria) antes que un mock. Es más realista.

**Regla**: cada mock es **deuda**. Cuando refactorices y la firma cambie, el mock no se entera y te miente. Mockeá fronteras (HTTP externo, DB cuando sea muy costosa) — no internals tuyos.

### 4.8. Testear FastAPI con `TestClient`

```python
from fastapi.testclient import TestClient
from tiendapro.api import app


def test_health_devuelve_200() -> None:
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["estado"] == "ok"
```

`TestClient` corre la app **en proceso** — no levanta uvicorn. Es **rápido** (cientos de tests por segundo) y permite afirmar sobre status, headers, body. Es lo que vas a usar para integration tests de la API.

#### Configurar fixtures con `dependency_overrides`

```python
import pytest
from fastapi.testclient import TestClient
from tiendapro.api import app
from tiendapro.config import Settings, get_settings


@pytest.fixture
def settings_test() -> Settings:
    return Settings(
        database_url="sqlite:///:memory:",
        log_level="WARNING",
        enable_enrichment=False,        # no llama a la API externa en tests
    )


@pytest.fixture
def client(settings_test: Settings) -> Iterator[TestClient]:
    app.dependency_overrides[get_settings] = lambda: settings_test
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
```

Lo bueno: la app real corre, pero con config controlada. No necesitás un `.env` de test; no necesitás levantar Postgres real.

### 4.9. Coverage: la métrica que mide pero no califica

```bash
uv add --dev pytest-cov
uv run pytest --cov=src/tiendapro --cov-report=term-missing
```

Salida típica:

```
Name                              Stmts   Miss  Cover   Missing
---------------------------------------------------------------
src/tiendapro/modelos.py             18      0   100%
src/tiendapro/repositorio.py         42      6    86%   45-50
src/tiendapro/api/app.py             68     12    82%   23-25, 89-99
---------------------------------------------------------------
TOTAL                               128     18    86%
```

`Missing` te dice qué líneas **no** ejecutó ningún test. Útil para encontrar caminos olvidados (un `except` que nadie ejercita, una rama del `if` que nunca se prueba).

**Lo que coverage NO te dice**:

- Si los tests son buenos. Un test sin `assert` tiene cobertura 100% y prueba 0%.
- Si los caminos son correctos. Cubrís 100% pero todos los `assert` están mal.
- Si te falta un caso de borde. Coverage mide líneas, no equivalencias.

**Regla**: 80-90% es razonable y útil. 100% suele indicar que estás peleando con el porcentaje, no con la calidad. Lo importante es **dónde** están los huecos, no el número final.

### 4.10. Tests del integrador: estructura

Para TiendaPro Lite, una organización razonable:

```
tests/
├── conftest.py                      ← fixtures compartidas (settings, client, engine)
├── unit/
│   ├── test_modelos.py              ← Producto, validaciones
│   ├── test_dtos.py                 ← ProductoCrear, ProductoOut
│   └── test_errores.py              ← jerarquía de excepciones
└── integration/
    ├── test_repositorio.py          ← repositorio contra SQLite en memoria
    ├── test_api_productos.py        ← TestClient: GET, POST, filtros
    └── test_api_errores.py          ← TestClient: 404, 422, formato de error
```

Unit: rápidos, sin DB, sin red.
Integration: con DB en memoria, con la app real vía TestClient.

No hace falta e2e en este curso — la pirámide de TiendaPro Lite con unit + integration cubre los casos importantes.

### 4.11. TDD (test-driven development): mención

TDD = escribir el test **antes** del código. El ciclo es **red → green → refactor**:

1. **Red**: escribís un test que falla (porque el código no existe).
2. **Green**: escribís lo mínimo para que pase.
3. **Refactor**: limpiás el código sin cambiar el comportamiento.

No vamos a hacer TDD estricto en esta sesión, pero internalizá el ciclo: cuando agarrés un nuevo feature, **pensá primero qué tests escribirías**. Te obliga a definir la API antes de implementar, lo cual mejora el diseño.

Para este curso: **escribí los tests al menos junto al código, no después**. Si los dejás "para más tarde" raramente vuelven.

### 4.12. Cómo cierra el curso

Cuando ejecutes la suite final del integrador y todo pase verde, vas a tener:

- Una **API REST** funcional.
- **Configurable por entorno** sin tocar código.
- Con **logging estructurado** y `request_id`.
- **Dockerizada** y orquestable con `docker compose up`.
- **Cubierta por tests automatizados** (>80% coverage).
- Con **historia de git limpia** y **Conventional Commits**.

Ese paquete es **lo que un equipo serio considera "código de producción"**. No es un experimento; es un servicio.

Y desde ahí arranca el curso 2: en `python-ai-engineer-training` vas a tomar **este mismo proyecto** y le vas a sumar capacidades de IA. Cada nueva pieza (LLM client, embeddings, RAG, agentes) va a tener su test, su Dockerfile, su config, su `request_id`. La disciplina no cambia — se agrega vocabulario nuevo encima.

## 5. Patrones y antipatrones

| ✅ Patrón | ❌ Antipatrón |
|---|---|
| Tests rápidos en `tests/unit/`, lentos en `tests/integration/` | Todo en `tests/` mezclado, suite que tarda 4 minutos |
| Un test = un comportamiento (con varias `assert` si son del mismo resultado) | Un test que prueba 5 cosas — si falla, no sabés cuál |
| `assert` plano + mensaje opcional | `self.assertEqual(...)` (estilo unittest) |
| Fixtures en `conftest.py` para reutilizar | Setup repetido manualmente en cada test |
| `@pytest.mark.parametrize` para variantes | Copy-paste del mismo test con valores cambiados |
| Mockear **fronteras** (HTTP externo, DB cuando es lenta) | Mockear cada función interna ("test that calls test that calls test") |
| `dependency_overrides` para inyectar config de test | Variables de entorno del shell de tu máquina filtrándose en los tests |
| Nombre descriptivo: `test_producto_no_disponible_si_stock_cero` | Nombres genéricos: `test_1`, `test_producto`, `test_disponible_2` |
| Tests deterministas (sin `time.sleep`, sin random sin seed) | Tests que pasan a veces ("flaky") |
| `pytest -x` durante desarrollo (parar al primer fallo) | Esperar 8 minutos para ver 12 fallos del mismo problema |
| Coverage como **señal** de huecos | Coverage como **meta** ("hay que llegar al 100%") |
| Tests que sobreviven a refactors (testean comportamiento, no implementación) | Tests acoplados a internals (cualquier rename los rompe) |
| Aislar tests entre sí (rollback de DB, fixtures con teardown) | Test A deja DB sucia y test B falla por eso |

## 6. Conexión con el proyecto integrador — Cierre del hito M6 y del curso

**Hoy cerrás todo.** Después de esta sesión, TiendaPro Lite es un proyecto **completo**.

1. **`tests/`** con suite unit + integration sobre el integrador.
2. **`pyproject.toml`** del integrador con `pytest`, `pytest-cov`, `httpx` (para `TestClient`) en `[dependency-groups].dev`.
3. **`pytest.ini` o sección `[tool.pytest.ini_options]`** con `testpaths`, `addopts`, etc.
4. **`README.md` final del integrador** con el resumen del curso completo (M1-M6) y cómo seguir.
5. **`docs/00-curriculum.md`** marcado con `[x] Módulo 6 — Herramientas del ingeniero ... — tag proyecto-m6`.
6. **Commits + tag**:
   ```bash
   git add code/proyecto-integrador
   git commit -m "feat(proyecto-integrador): cierra M6 con tests pytest (proyecto-m6)"
   git tag proyecto-m6
   ```

Detalles paso a paso en `ejercicios.md`.

## 7. Resumen

1. **Tests son especificación ejecutable** y red de seguridad. No reemplazan diseño, performance ni seguridad.
2. **Pirámide**: muchos unit, algunos integration, pocos e2e. Mantené esa proporción.
3. **AAA**: arrange-act-assert. Si tu test no entra en ese molde, la unidad bajo test hace demasiado.
4. **Fixtures** reutilizan setup; los **scopes** balancean costo y aislamiento.
5. **Parametrize** evita copy-paste; cada caso aparece como un test independiente.
6. **Mock cuando hay fronteras** (HTTP, DB cara). Para tu propio código, preferí fakes.
7. **`TestClient` de FastAPI** corre la app en proceso — rápido y útil para integration tests de la API.
8. **`dependency_overrides`** te permite reemplazar settings, repositorios y servicios sin tocar el código de producción.
9. **Coverage es una señal**, no una meta. 100% no garantiza calidad; 60% en módulos críticos es alarma.
10. **Suite verde + Dockerfile + git limpio + config por entorno + logs estructurados = código de producción.** Eso es lo que cierra el curso.

## 8. Preguntas de auto-evaluación

1. ¿Cuáles son los tres roles de los tests? Da un ejemplo de cada uno.
2. Diferenciá unit, integration y e2e. ¿Qué proporción debería haber de cada uno?
3. ¿Qué es una fixture y para qué sirven los `scope`s? Da un caso para cada scope (`function`, `module`, `session`).
4. Reescribí mentalmente este test usando `@pytest.mark.parametrize`:
   ```python
   def test_descuento_10(): assert aplicar_descuento(100, 10) == 90
   def test_descuento_25(): assert aplicar_descuento(100, 25) == 75
   def test_descuento_0(): assert aplicar_descuento(100, 0) == 100
   ```
5. ¿Cuál es la diferencia entre un mock y un fake? ¿Cuándo usarías uno vs el otro?
6. ¿Para qué sirve `TestClient` de FastAPI? ¿Qué ventaja tiene sobre levantar uvicorn y hacer `httpx.get(...)`?
7. ¿Qué hace `app.dependency_overrides[get_settings] = ...` y por qué importa para los tests?
8. Tenés 100% coverage pero un bug en producción. ¿Es contradictorio? Justificá.
9. Listá tres síntomas de un test "mal escrito" y por qué cada uno es problema.
10. Sumás un endpoint nuevo a TiendaPro Lite (`POST /productos/{id}/descuento`). Listá: (a) qué tests unit escribirías, (b) qué tests integration, (c) qué fixtures te haría falta.

Cuando puedas responder todas, pasá a [`ejercicios.md`](ejercicios.md) para cerrar el curso.

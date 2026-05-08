# S21 — Recursos

## Documentación oficial

- **pytest documentation** ([docs.pytest.org](https://docs.pytest.org/en/stable/)). La fuente. Bien organizada por temas (fixtures, marks, parametrize, plugins). Si solo vas a leer una doc, esta.
- **pytest fixtures** ([docs.pytest.org/en/stable/explanation/fixtures.html](https://docs.pytest.org/en/stable/explanation/fixtures.html)). Lectura corta y clave. Aclara la mecánica de descubrimiento, scopes y cómo combinar fixtures.
- **FastAPI testing** ([fastapi.tiangolo.com/tutorial/testing/](https://fastapi.tiangolo.com/tutorial/testing/)). Cómo se testea una app FastAPI con TestClient. Cubre dependency overrides.
- **Coverage.py** ([coverage.readthedocs.io](https://coverage.readthedocs.io/en/latest/)). Lo que `pytest-cov` envuelve. Lectura útil para entender qué mide (lines, branches) y qué no.
- **unittest.mock** ([docs.python.org/3/library/unittest.mock.html](https://docs.python.org/3/library/unittest.mock.html)). Doc oficial de la stdlib. `Mock`, `patch`, `MagicMock`, `call`, `assert_called_with`. Densa pero exhaustiva.

## Lecturas guiadas

- **Brian Okken — Python Testing with pytest** (libro). El libro definitivo de pytest. Va de cero a expert. Si te gustaron los tests de hoy, leelo entero.
- **Real Python — Effective Python Testing With pytest** ([realpython.com/pytest-python-testing/](https://realpython.com/pytest-python-testing/)). Recorrido práctico con muchos ejemplos. Buena segunda lectura después de la doc oficial.
- **Test Driven Development with Python (Obey the Testing Goat)** ([obeythetestinggoat.com](https://www.obeythetestinggoat.com/)). Libro gratuito de Harry Percival. Enseña TDD construyendo una app real. Más allá de la sintaxis, la **filosofía** de cómo pensar en tests.
- **The Practical Test Pyramid** (Ham Vocke en [martinfowler.com](https://martinfowler.com/articles/practical-test-pyramid.html)). Cómo balancear unit/integration/e2e en un proyecto real. Lectura corta y opinada.
- **xUnit Test Patterns** (Gerard Meszaros). El catálogo de patrones de testing. Cuando empieces a tener una suite de cientos de tests, este libro te da el vocabulario para hablar de ellos.
- **Mocks Aren't Stubs** (Martin Fowler en [martinfowler.com](https://martinfowler.com/articles/mocksArentStubs.html)). El artículo histórico que distingue mock, stub, fake. Pasaron 18 años y sigue siendo la mejor explicación.

## Para profundizar

- **Working Effectively with Legacy Code** (Michael Feathers). Cómo agregar tests a código que no fue diseñado para ser testeado. Cuando entres a tu primer trabajo y heredes código viejo, este libro te salva.
- **Growing Object-Oriented Software, Guided by Tests** (Steve Freeman, Nat Pryce). El "GOOS book". Cómo el TDD guía el diseño hacia objetos pequeños y composables. Java en el código, ideas universales.
- **Property-based testing** con [Hypothesis](https://hypothesis.readthedocs.io/). En lugar de escribir casos a mano, vos describís propiedades (ej: `aplicar_descuento` siempre devuelve un valor `<= precio_original`) y la herramienta genera entradas que las violen. Otra capa de defensa.
- **Mutation testing** con [`mutmut`](https://mutmut.readthedocs.io/) o [`cosmic-ray`](https://cosmic-ray.readthedocs.io/). La herramienta cambia tu código (muta un `>` por `<`, cambia `True` por `False`) y verifica que los tests fallen. Si tus tests no fallan ante cambios de comportamiento, son malos tests.
- **CI con GitHub Actions** ([docs.github.com/en/actions](https://docs.github.com/en/actions)). Correr la suite en cada push. Una vez que tenés tests, el siguiente paso natural es automatizarlos en CI.

## Herramientas que vale la pena conocer

- **`pytest-cov`** — coverage integrado en pytest. `pytest --cov=src --cov-report=html` te genera un reporte navegable.
- **`pytest-xdist`** — paraleliza la suite. `pytest -n auto` corre los tests en N procesos. En suites grandes, baja el tiempo a la mitad.
- **`pytest-asyncio`** — para testear funciones `async`. `@pytest.mark.asyncio` y listo.
- **`pytest-mock`** — wrapper de `unittest.mock` con la API de fixture. `mocker.patch(...)` es como `monkeypatch.setattr` pero para mocks.
- **`pytest-randomly`** — corre tests en orden aleatorio. Si tu suite depende del orden, este plugin te lo expone — y eso es señal de tests con estado compartido (mal).
- **`pytest-watch` / `pytest-watcher`** — corre la suite cuando cambian archivos. TDD-friendly.
- **`hypothesis`** ([hypothesis.readthedocs.io](https://hypothesis.readthedocs.io/)). Property-based testing. Generación automática de inputs.
- **`tox`** — corre la suite en múltiples versiones de Python / configuraciones. Útil para librerías que soportan varias versiones.
- **`pytest-benchmark`** — micro-benchmarks dentro de tu suite. Tests de performance que también detectan regresiones.
- **`responses`** o **`pytest-httpx`** — mockear requests de `requests` o `httpx` sin tocar el código. Útil para testear integraciones HTTP sin red.

## Referencias para resolver dudas puntuales

- **"`ImportError` al correr pytest"** — generalmente porque `src/` no está en el path. Solución: `pythonpath = ["src"]` en `[tool.pytest.ini_options]`, o instalar tu paquete con `uv sync` (que ya lo hace).
- **"Mis fixtures no se descubren"** — están en un archivo distinto a `conftest.py`. Movelas a `tests/conftest.py` (descubre automático) o importalas explícitamente.
- **"Un test pasa solo y falla en suite"** — estado compartido. Algún test está dejando algo (env var, archivo, registro en DB) que afecta a otro. `pytest-randomly` te ayuda a reproducirlo.
- **"`@pytest.fixture(scope='session')` se reinicializa"** — probablemente otra fixture `function`-scoped la depende y la fuerza a reinicializarse. Mismo scope o más amplio en cadena de dependencias.
- **"`monkeypatch.setattr` no parchea"** — chequeá **dónde** se usa el atributo. `monkeypatch.setattr("módulo_donde_se_usa.funcion", ...)`, no donde está definido. Confunde al principio.
- **"Mi mock no falla cuando lo llamo mal"** — `Mock()` acepta cualquier llamada. Usá `Mock(spec=ClaseReal)` o `MagicMock(spec=...)` para que respete la firma de la clase real.
- **"Tests de FastAPI tardan demasiado"** — probablemente cada test reinicia la DB. Compartila a nivel session con scope adecuado, o usá una fixture que rolleback en lugar de drop+create.
- **"`assert response.json() == {...}` falla por orden de keys"** — los dicts en Python son insertion-ordered y la comparación `==` ignora orden. Si falla, las keys o values son distintos, no el orden. Si comparás listas y querés ignorar orden: `set(...)` o `sorted(...)`.
- **"Coverage da 100% pero hay un bug"** — coverage mide ejecución, no correctness. 100% solo dice "ningún assert se ejercita", no "todos los caminos están bien testeados". Combiná con property-based testing y mutation testing.
- **"`pytest --cov` no encuentra mi código"** — `--cov=tiendapro` busca el paquete instalado, no `src/tiendapro/`. Probá con la ruta: `--cov=src/tiendapro`.

## Errores comunes

- **Tests que dependen de orden** — un test deja DB sucia, otro asume DB limpia. Rollback en fixture o usá `tmp_path` / DBs aisladas.
- **Mockear lo propio** — mockear módulos tuyos te acopla los tests a la implementación. Si mañana renombrás una función, los tests siguen verdes pero ya no prueban nada. Mockeá fronteras.
- **Tests sin `assert`** — pasan, cubren coverage, pero no afirman nada. Síntoma: coverage 100%, bugs en producción.
- **Naming malo** — `test_1`, `test_producto`, `test_funciona`. El nombre es la **especificación** del test. Hacelo descriptivo: `test_producto_no_disponible_si_stock_cero`.
- **Setup gigante** — un test con 30 líneas de setup y 1 de assert. Tu unidad bajo test hace demasiado, o tu test cubre demasiado. Partilo.
- **Timeouts y `sleep`** — tests con `time.sleep(1)` para "esperar que algo termine". Flaky garantizado. Usá fixtures de sincronización o mocks de `datetime.now()`.
- **`assert` con tolerancia mal puesta** — comparar floats con `==`: `assert 0.1 + 0.2 == 0.3` falla. Usá `pytest.approx`: `assert 0.1 + 0.2 == pytest.approx(0.3)`.
- **No correr tests en CI** — la suite que solo corre en tu máquina deja de correr cuando vacacionás. Toda PR debería correr la suite automáticamente. GitHub Actions, GitLab CI, Jenkins — algo tiene que correrlo.
- **100% coverage como meta** — empuja a tests inútiles para tapar agujeros. Mejor: 80-90% honesto, con tests **valiosos** en los caminos críticos.
- **Mock de la implementación interna** — `mock.patch("mi_modulo._funcion_privada")`. Si mañana refactorizás esa función, el test rompe sin razón. Mockeá la interfaz pública (la frontera), no el detalle.

## Si vas hacia el curso 2

En AI Engineering, los tests cambian de carácter pero la disciplina es la misma:

- **LLM calls son la frontera más importante a mockear.** Cada llamada a OpenAI/Anthropic cuesta dinero y tiempo. Tus tests **no** deberían pegarle a la API real.
  ```python
  @pytest.fixture
  def llm_mock(monkeypatch):
      def fake_complete(prompt: str) -> str:
          return "respuesta predecible"
      monkeypatch.setattr("mi_paquete.llm.complete", fake_complete)
  ```
- **Embeddings y vector search**: testealos con un fake de la DB vectorial (en memoria) que devuelva resultados controlados.
- **Eval suites**: lo que en software clásico es "pasa o no pasa", en LLMs se vuelve "qué tan bien performa". Vas a escribir suites de evaluación con métricas (precision, recall, similarity scores) — relacionadas pero distintas a las tests.
- **Snapshot tests** se vuelven útiles: capturás la salida del agente para un input dado, y los siguientes runs comparan contra esa snapshot. Detectás regresiones de comportamiento que un assert tradicional no detecta.
- **Property-based testing** se vuelve poderoso: "para cualquier input X, el agente nunca debería revelar credenciales". Hypothesis genera ejemplos adversariales.

La pirámide cambia de forma — en AI hay más "evals" (un nivel intermedio) y los e2e son más caros. Pero los unit tests sobre el código no-LLM (parsing, validación, retries, cache) siguen siendo igual de importantes que en software tradicional.

Lo que aprendiste hoy — fixtures, parametrize, mocks selectivos, coverage como señal — se transfiere al 100%.

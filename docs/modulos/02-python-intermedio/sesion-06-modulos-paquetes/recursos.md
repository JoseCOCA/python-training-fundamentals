# S06 — Recursos

## Documentación oficial — Python

- **The Python Tutorial — Modules** ([docs.python.org/3/tutorial/modules.html](https://docs.python.org/3/tutorial/modules.html)). Capítulo 6 del tutorial oficial. Cubre módulos, paquetes, `__init__.py`, imports relativos y `sys.path`. Lectura obligatoria — es el material canónico.
- **The import system** ([docs.python.org/3/reference/import.html](https://docs.python.org/3/reference/import.html)). Referencia completa. Léela cuando un import te confunda y necesites entender el modelo profundo. No es para una primera lectura.
- **`__main__` — Top-level code environment** ([docs.python.org/3/library/__main__.html](https://docs.python.org/3/library/__main__.html)). Documenta el guard `if __name__ == "__main__"` y el archivo `__main__.py` para hacer paquetes ejecutables con `python -m`.
- **Packaging User Guide — Python Packaging** ([packaging.python.org](https://packaging.python.org/en/latest/)). Referencia oficial de packaging moderno. La sección "Tutorials → Packaging Python Projects" es buena pero usa `pip` y `build`; para nuestro curso reemplaza esos pasos por uv.

## Documentación oficial — uv

- **uv documentation** ([docs.astral.sh/uv](https://docs.astral.sh/uv/)). Guía completa de la herramienta. Lectura recomendada hoy: las secciones "Getting started", "Concepts → Projects" y "Concepts → Dependencies".
- **uv — Project structure** ([docs.astral.sh/uv/concepts/projects/layout/](https://docs.astral.sh/uv/concepts/projects/layout/)). Cómo se organiza un proyecto uv: `pyproject.toml`, `uv.lock`, `.venv`, `src/`.
- **PEP 621 — Storing project metadata in pyproject.toml** ([peps.python.org/pep-0621/](https://peps.python.org/pep-0621/)). El estándar que define la sección `[project]` que estás leyendo y editando. Si te interesa entender de dónde sale, vale la pena.

## Lecturas opcionales

- **Real Python — Python Modules and Packages: An Introduction** ([realpython.com/python-modules-packages/](https://realpython.com/python-modules-packages/)). Recorre los mismos conceptos con más ejemplos visuales. Útil si la doc oficial te resulta seca.
- **Real Python — Absolute vs Relative Imports in Python** ([realpython.com/absolute-vs-relative-python-imports/](https://realpython.com/absolute-vs-relative-python-imports/)). Profundiza en el contraste entre los dos estilos de import.
- **Brett Cannon — How to use Python's import system** ([snarky.ca/](https://snarky.ca/)). Brett es uno de los core developers de Python y mantiene el sistema de imports. Su blog tiene varios posts sobre el tema; busca "import" en el archivo.
- **PEP 8 — Style Guide for Python Code, sección Imports** ([peps.python.org/pep-0008/#imports](https://peps.python.org/pep-0008/#imports)). Cómo organizar los imports en la cabecera de un archivo. Convención respetada en todo el ecosistema.

## Referencias para resolver dudas puntuales

- **`__init__.py` o no?** — [packaging.python.org — Native namespace packages](https://packaging.python.org/en/latest/guides/packaging-namespace-packages/). Resumen rápido: para empezar, **siempre** pon un `__init__.py` aunque esté vacío. Los namespace packages tienen casos de uso reales pero rara vez son los que necesitas.
- **Imports circulares** — [stackoverflow.com/q/744373](https://stackoverflow.com/questions/744373/what-happens-when-using-mutual-or-circular-cyclic-imports-in-python). El hilo clásico que explica qué pasa cuando dos módulos se importan entre sí y cómo evitarlo.
- **`pip` vs `uv`** — [docs.astral.sh/uv/pip/](https://docs.astral.sh/uv/pip/). uv tiene un modo `uv pip` para reemplazar a pip de forma drop-in cuando heredas un proyecto viejo que no usa el flujo moderno.

## Visualización

- **Python Tutor** ([pythontutor.com](https://pythontutor.com/)). No es ideal para imports entre archivos (asume un solo archivo) pero sigue siendo la mejor herramienta para visualizar paso a paso qué hace una porción de código que no entiendes.

## Si estás siguiendo el curso 2 al mismo tiempo

El curso siguiente (`python-ai-engineer-training`) asume que tienes esta sesión absolutamente sólida. Si dudas de algo después de los ejercicios, **vuelve al README y léelo otra vez**. No avances con la duda — los conceptos de M2 se acumulan rápido.

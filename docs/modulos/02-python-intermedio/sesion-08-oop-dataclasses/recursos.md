# S08 — Recursos

## Documentación oficial — Python

- **Classes — The Python Tutorial** ([docs.python.org/3/tutorial/classes.html](https://docs.python.org/3/tutorial/classes.html)). Capítulo 9 del tutorial. Cubre clases, instancias, métodos, herencia y `super()`. Lectura obligatoria.
- **`dataclasses` module** ([docs.python.org/3/library/dataclasses.html](https://docs.python.org/3/library/dataclasses.html)). Referencia del módulo. La sección de `field()` y la nota sobre defaults mutables se vuelven importantes pronto.
- **Data model** ([docs.python.org/3/reference/datamodel.html](https://docs.python.org/3/reference/datamodel.html)). La referencia formal de cómo Python expone su comportamiento mediante dunder methods. Larga, densa, vale para consultar cuando dudes qué hace `__repr__`, `__hash__`, `__eq__`, etc.
- **PEP 557 — Data Classes** ([peps.python.org/pep-0557/](https://peps.python.org/pep-0557/)). Si te interesa la motivación detrás de `@dataclass` (qué problemas resolvía, por qué se diseñó así), este es el documento.

## Lecturas opcionales

- **Real Python — Object-Oriented Programming (OOP) in Python 3** ([realpython.com/python3-object-oriented-programming/](https://realpython.com/python3-object-oriented-programming/)). Recorrido completo con ejemplos.
- **Real Python — Data Classes** ([realpython.com/python-data-classes/](https://realpython.com/python-data-classes/)). Más ejemplos del decorador, incluyendo `field()`, `__post_init__`, herencia entre dataclasses.
- **Raymond Hettinger — "Beyond PEP 8: Best practices for beautiful intelligible code"** ([youtube.com/watch?v=wf-BqAjZb8M](https://www.youtube.com/watch?v=wf-BqAjZb8M)). Charla clásica. La sección sobre cuándo NO usar OOP justifica buena parte de esta sesión.
- **"Stop Writing Classes" — Jack Diederich, PyCon 2012** ([youtube.com/watch?v=o9pEzgHorH0](https://www.youtube.com/watch?v=o9pEzgHorH0)). Charla complementaria al título de la sesión 4.9 del README. Si nunca la viste, vale 30 minutos de tu tiempo.

## Para profundizar

- **Fluent Python (Luciano Ramalho), parte II — "Functions as objects" y parte III — "Object-oriented idioms"**. Cuando ya tengas los fundamentos, estos capítulos son la referencia más profunda en español/inglés sobre OOP idiomática en Python moderno.
- **Hynek Schlawack — "The One Python Library Everyone Needs"** ([youtube.com/watch?v=1S1TgRGpAtw](https://www.youtube.com/watch?v=1S1TgRGpAtw)). Charla sobre `attrs`, predecesor de `@dataclass`. Útil para entender por qué dataclasses se ven así.

## Diseño y filosofía

- **"Composition over inheritance"** — el principio detrás del antipatrón #3 del README. [en.wikipedia.org/wiki/Composition_over_inheritance](https://en.wikipedia.org/wiki/Composition_over_inheritance) — el artículo es corto y va al grano.
- **Joel Spolsky — "Five Worlds"** ([joelonsoftware.com/2002/05/06/five-worlds/](https://www.joelonsoftware.com/2002/05/06/five-worlds/)). No es sobre OOP directamente, pero el principio de "no over-engineerees para casos que no tienes" se aplica a las jerarquías de clase.

## Referencias para resolver dudas puntuales

- **¿Cuándo usar `__repr__` vs `__str__`?** — [stackoverflow.com/q/1436703](https://stackoverflow.com/questions/1436703/what-is-the-difference-between-str-and-repr). La respuesta canónica.
- **`@property` y descriptors** — los vas a ver mencionados; no son temario de S08, pero si te cruzas con código que los usa: [docs.python.org/3/library/functions.html#property](https://docs.python.org/3/library/functions.html#property).
- **`__slots__`** — optimización para clases con muchas instancias. Lo vas a ver eventualmente; para esta sesión basta saber que existe.

## Si vas hacia el curso 2

En AI Engineering los modelos de dominio se hacen con **pydantic**, que aparece en M3. Pydantic es como `@dataclass` pero con validación de runtime. La filosofía es la misma — datos tipados, inmutables cuando se puede, métodos pequeños — pero con la garantía de que los datos efectivamente cumplen los tipos declarados.

Si esta sesión te queda débil, pydantic se vuelve mágico (y mágico = no entiendes qué está pasando). **Asegúrate** de estar cómodo con `@dataclass` antes de avanzar.

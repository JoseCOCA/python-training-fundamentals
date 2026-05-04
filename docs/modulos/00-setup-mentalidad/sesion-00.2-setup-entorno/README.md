# S00.2 — Setup del entorno

> **Sesión 2h.** ~45 min de lectura + ~75 min de práctica guiada en `ejercicios.md`. Al terminar, tu computadora va a tener todo lo necesario para programar en Python moderno y vas a haber ejecutado tu primer script.

---

## 1. Objetivos de aprendizaje

Al terminar esta sesión vas a:

- Entender qué es una **terminal**, qué es un **shell**, y por qué van a ser tu herramienta principal.
- Conocer los comandos básicos para moverte por el sistema de archivos desde la terminal.
- Tener instalado **uv** (package manager) y **Python 3.12** en tu computadora.
- Tener **VS Code** configurado con las extensiones esenciales para Python.
- Haber ejecutado tu primer script Python desde la terminal y entender qué hizo cada herramienta involucrada.

## 2. Prerequisitos

- Haber leído y reflexionado sobre [S00.1 — Cómo aprender a programar](../sesion-00.1-como-aprender-a-programar/README.md). En particular, la parte sobre frustración productiva — porque setup es el momento donde más cosas pueden salir mal por razones aleatorias.
- Una computadora con Linux, macOS, o Windows con WSL2 (en la sección 4.1 explico por qué WSL2 y no Windows nativo).
- Permisos de administrador en tu máquina (para instalar herramientas).

## 3. Conceptos clave

1. **Terminal vs shell vs prompt.** No son lo mismo. La terminal es la ventana, el shell es el programa que interpreta tus comandos, el prompt es el símbolo donde escribes.
2. **Package manager.** Programa que se encarga de instalar, actualizar y desinstalar otros programas (en este caso, librerías de Python). Para nosotros: `uv`.
3. **Virtual environment (venv).** Una "carpeta aislada" donde instalas las dependencias de un proyecto sin contaminar el resto del sistema. Cada proyecto tiene la suya.
4. **Editor vs IDE.** Editor = solo escribir código (VS Code). IDE = editor + herramientas de debugging, refactoring, etc., todo integrado (PyCharm). Para este curso: VS Code, que con extensiones se acerca mucho a un IDE.
5. **Runtime.** El programa que ejecuta tu código. Cuando escribes `python main.py`, el "runtime" de Python lee tu archivo, lo interpreta y lo ejecuta.

## 4. Teoría

### 4.1. Qué es la terminal y por qué es importante

La **terminal** es una ventana donde le hablas a tu computadora escribiendo comandos en lugar de hacer clic en botones. Suena anticuado — y lo es, en el sentido de que es de los años 70 — pero hay una razón por la que sigue siendo el medio principal de los programadores: **es enormemente más eficiente y preciso que la GUI** para tareas técnicas. Mover 1.000 archivos con un solo comando es algo que ningún explorador gráfico te deja hacer.

Tres palabras que la gente confunde:

- **Terminal:** la ventana en sí. Solo dibuja texto.
- **Shell:** el programa que corre dentro de la terminal e interpreta lo que escribes. Los más comunes: `bash` (default en muchos Linux), `zsh` (default en macOS desde 2019), `fish` (alternativo). En este curso vamos a usar bash o zsh — son intercambiables para lo que necesitamos.
- **Prompt:** el símbolo donde aparece el cursor. Suele verse como `$ ` o `usuario@computadora:~$`. Es solo una indicación visual de "escribe aquí".

**Por qué Windows + WSL en lugar de Windows nativo:** la inmensa mayoría de las herramientas de programación moderna (Python, Docker, librerías de linux, scripts de deploy) están pensadas para sistemas tipo Unix (Linux y macOS son Unix-like). Windows nativo tiene su propia terminal (PowerShell, cmd) pero los comandos son distintos, las rutas de archivos usan `\` en lugar de `/`, y hay incompatibilidades sutiles que te van a hacer perder tiempo. **WSL2 (Windows Subsystem for Linux 2)** te da un Linux real corriendo dentro de Windows. La curva de aprendizaje es 30 minutos y te ahorra meses de fricción. Si usas Windows, instala WSL2 antes de seguir.

### 4.2. Comandos básicos de la terminal

Estos son los seis comandos que vas a usar el 90% del tiempo. Los explico una vez aquí; en `ejercicios.md` los practicas.

| Comando | Qué hace | Ejemplo |
|---|---|---|
| `pwd` | Muestra el directorio actual (*print working directory*) | `pwd` → `/home/jose/proyectos` |
| `ls` | Lista archivos y carpetas | `ls` o `ls -la` (incluye ocultos y detalles) |
| `cd` | Cambia de directorio (*change directory*) | `cd proyectos` o `cd ..` (subir uno) |
| `mkdir` | Crea un directorio (*make directory*) | `mkdir mi-proyecto` |
| `cp` | Copia archivos | `cp origen.txt destino.txt` |
| `mv` | Mueve o renombra archivos | `mv viejo.txt nuevo.txt` |
| `rm` | Borra archivos. **Cuidado: NO va a la papelera.** | `rm archivo.txt` |

**Atajos críticos:**

- `Ctrl+C`: cancela el comando que está corriendo.
- `Ctrl+L` o `clear`: limpia la pantalla.
- Flecha arriba/abajo: navega por el historial de comandos.
- `Tab`: autocompleta nombres de archivos y comandos.
- `exit`: cierra la terminal.

**Una regla de oro:** `rm` borra DEFINITIVAMENTE. No hay papelera, no hay confirmación, no hay vuelta atrás. Antes de ejecutar `rm`, lee dos veces qué estás borrando.

### 4.3. El editor de código

Vas a escribir código en un editor, no en un procesador de texto. La diferencia: un editor entiende qué es código (resaltado de sintaxis, autocompletado, detección de errores), un procesador de texto no.

**Recomendación: Visual Studio Code (VS Code).**

- Gratis, mantenido por Microsoft, multiplataforma.
- La mejor extensión de Python del mercado.
- Configuración simple para principiantes, pero escala a proyectos profesionales.

**Alternativas y por qué no las recomiendo para este curso:**

| Editor | Veredicto |
|---|---|
| **PyCharm Community** | Excelente IDE pero pesado y con curva de aprendizaje propia. Útil después de M3-M4. |
| **Cursor** | Es VS Code con IA integrada. Si lo usas, está bien — pero sé estricto contigo: no dejes que la IA escriba código por ti (revisar §4.7 de S00.1). |
| **Sublime Text** | Rápido pero su ecosistema Python es inferior al de VS Code. |
| **Neovim / Emacs** | Para programadores avanzados que quieren control total. **No** para principiantes — la curva de aprendizaje compite con la del propio Python. |
| **Bloc de notas / TextEdit** | No. No es un editor de código. |

**Extensiones esenciales de VS Code para este curso:**

- **Python** (Microsoft) — la oficial. Te da resaltado, autocompletado, navegación.
- **Pylance** (Microsoft) — type checking en tiempo real, basado en Pyright. Crítica para el módulo de tipado.
- **Ruff** (Astral) — el linter del curso, integrado al editor.

Esas tres son obligatorias. Cualquier otra cosa (themes, iconos, etc.) es decoración personal.

### 4.4. Python, runtimes, y package managers

**Python** es un lenguaje de programación. Pero cuando dices "tengo Python 3.12 instalado", lo que tienes instalado es un **runtime de Python**: un programa llamado `python` (o `python3`) que sabe leer archivos `.py` y ejecutarlos.

Históricamente, instalar Python en una computadora era un dolor:

1. Tu sistema operativo trae una versión vieja "del sistema" (a veces Python 2, que no se debe tocar).
2. Tienes que instalar la versión que quieres en paralelo (Python 3.12 en este caso).
3. Necesitas un programa para gestionar versiones (`pyenv`).
4. Necesitas un programa para crear "virtual environments" donde aislar las dependencias de cada proyecto (`venv`).
5. Necesitas un programa para instalar paquetes (`pip`).
6. Necesitas un archivo (`requirements.txt`) para listar tus dependencias.
7. Necesitas otro programa para que tu archivo de dependencias sea reproducible (`pip-tools` o `poetry`).

Eso son **siete cosas** distintas. Para alguien que está aprendiendo, es disuasorio.

### 4.5. Por qué uv (y no las siete herramientas separadas)

**uv** es un package manager y gestor de entornos para Python publicado por Astral en 2024. Reemplaza, en un solo binario:

- `pyenv` (gestionar versiones de Python).
- `venv` (crear virtual environments).
- `pip` (instalar paquetes).
- `pip-tools` / `poetry` (lockfiles deterministas).

Comparativa práctica:

| Tarea | Forma vieja | Con uv |
|---|---|---|
| Instalar Python 3.12 | `pyenv install 3.12.0` | `uv python install 3.12` |
| Crear un proyecto nuevo | `mkdir proyecto && cd proyecto && python -m venv .venv && source .venv/bin/activate && pip install ...` | `uv init proyecto && cd proyecto && uv add ...` |
| Instalar las dependencias del proyecto | `pip install -r requirements.txt` | `uv sync` |
| Correr un script | `source .venv/bin/activate && python main.py` | `uv run python main.py` |
| Velocidad de instalación | Minutos en proyectos grandes | Segundos (uv es escrito en Rust) |

Para alguien que está aprendiendo, la diferencia no es solo de velocidad — es de **carga cognitiva**. Con la forma vieja, tienes que recordar siete herramientas y cuándo usar cada una. Con uv, tienes uno y te concentras en aprender Python.

### 4.6. Cómo se ejecuta Python

Hay tres formas de ejecutar código Python; vas a usar las tres a lo largo del curso.

**1. REPL (Read-Eval-Print Loop) — modo interactivo**

```bash
$ uv run python
Python 3.12.7
>>> 2 + 2
4
>>> print("hola")
hola
>>> exit()
```

Sirve para experimentar rápidamente con expresiones, probar una función, recordar sintaxis. **No** sirve para escribir programas serios — todo lo que escribes se pierde al cerrarlo.

**2. Ejecutar un archivo `.py`**

```bash
$ uv run python main.py
Hola desde python-training-fundamentals!
```

La forma estándar. El runtime lee el archivo, lo interpreta de arriba abajo y se cierra cuando termina.

**3. Ejecutar un módulo o paquete**

```bash
$ uv run python -m mi_paquete
```

Sirve cuando tu código está organizado como un paquete (M2). Por ahora ignóralo.

## 5. Patrones y antipatrones

| ✅ Patrón | ❌ Antipatrón |
|---|---|
| Usar la terminal todos los días, incluso para tareas chicas | Esquivar la terminal y depender de la GUI |
| Tener UN editor configurado bien (VS Code + 3 extensiones) | Saltar entre 5 editores buscando "el mejor" |
| Usar uv para todo (instalar Python, deps, correr scripts) | Mezclar `pip install` global con uv en distintos proyectos |
| Crear un directorio nuevo y `uv init` para cada proyecto | Trabajar todo dentro de la carpeta home sin estructura |
| Leer dos veces antes de ejecutar `rm` | Borrar a ciegas confiando en la "papelera" (no existe) |
| Instalar Python con `uv python install`, no con el instalador del sistema | Instalar Python desde python.org y pelearse con `pyenv` después |

## 6. Conexión con el proyecto integrador

Todo lo que vas a hacer en TiendaPro Lite empieza con `uv run` algo. La sesión de hoy te entrega las llaves del taller: terminal, editor, Python y uv. A partir del Módulo 1 vas a usar estas cuatro cosas todos los días sin pensarlo, igual que un carpintero usa martillo, sierra y metro sin pensarlo.

## 7. Resumen

Los tres puntos que te tienes que llevar:

1. **Terminal + shell + comandos básicos** son tu interfaz principal con la computadora a partir de ahora. Si te resultan incómodos, es solo porque son nuevos — en una semana son automáticos.
2. **uv unifica siete herramientas en una.** Toda la complejidad del ecosistema Python tradicional (pyenv, venv, pip, requirements, lockfiles) la encapsula uv. Aprende UN comando bien antes de aprender los siete por separado.
3. **VS Code + Python + Pylance + Ruff** es la configuración estándar del curso. No la cambies hasta que tengas razones técnicas concretas — y si las tienes, ya no eres principiante.

## 8. Preguntas de auto-evaluación

Si no puedes responderlas sin volver a leer, vuelve a leer.

1. ¿Cuál es la diferencia entre terminal, shell y prompt? Da un ejemplo de cada uno.
2. Tienes un archivo `notas.txt` en el directorio actual. ¿Qué comando usas para renombrarlo a `apuntes.txt`? ¿Y para borrarlo?
3. ¿Qué hace `uv python install 3.12`? ¿Por qué no instalamos Python desde python.org?
4. Tres formas de ejecutar código Python. ¿Cuándo usar cada una?
5. ¿Por qué WSL2 en Windows en lugar de PowerShell nativo?
6. Listas las tres extensiones obligatorias de VS Code para este curso y di brevemente qué hace cada una.

Cuando puedas responder todas, sigue con [`ejercicios.md`](ejercicios.md) — la parte hands-on de la sesión.

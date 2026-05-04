# S00.2 — Ejercicios

Práctica guiada paso a paso. **Hazla en tu computadora, no la leas y sigas.** Si saltas un paso porque "ya sabes lo que hace", te vas a perder lo importante.

> **Si usas Windows:** todo lo que sigue asume que ya tienes WSL2 instalado y abierto. Si todavía no lo tienes, ve a `recursos.md` § "WSL2 setup" antes de seguir.

---

## Ejercicio 1 — Familiarízate con la terminal (10 min)

### 1.1. Abrir la terminal

- **Linux:** busca "Terminal" en el menú de aplicaciones.
- **macOS:** ⌘+espacio, escribe "Terminal", enter.
- **Windows (con WSL2):** busca "Ubuntu" o tu distro de WSL en el menú inicio.

Deberías ver un prompt similar a:

```
usuario@computadora:~$
```

El símbolo `$` es donde escribes. El `~` significa "mi directorio home" (tu carpeta personal).

### 1.2. Comandos básicos

Ejecuta los siguientes comandos uno por uno. Lee la salida después de cada uno; no los pegues todos seguidos.

```bash
pwd                     # ¿Dónde estoy?
ls                      # ¿Qué hay en mi directorio actual?
ls -la                  # ¿Qué hay, incluyendo archivos ocultos y detalles?
cd Documents            # Entra a Documents (puede llamarse "Documentos" en español)
pwd                     # ¿Dónde estoy ahora?
cd ..                   # Vuelve al directorio anterior
cd ~                    # Salta al home directamente
clear                   # Limpia la pantalla
```

**Pregunta para ti mismo:** ¿qué hizo `cd ..`? ¿Por qué `cd ~` salta al home aunque no estés cerca?

### 1.3. Crear, mover y borrar

```bash
mkdir mi-primer-test    # Crea una carpeta
cd mi-primer-test
echo "hola" > nota.txt  # Crea un archivo con la palabra "hola" dentro
ls
cat nota.txt            # Imprime el contenido del archivo
mv nota.txt apunte.txt  # Renombra el archivo
ls
cd ..
rm -r mi-primer-test    # Borra la carpeta y todo su contenido (recursivo)
ls
```

**Atención:** `rm -r` borra carpetas con todo dentro. **No hay papelera.** Léelo dos veces antes de ejecutarlo en otros lados.

---

## Ejercicio 2 — Instalar uv (5 min)

uv es el package manager que vamos a usar para instalar Python y manejar todos los proyectos del curso.

### 2.1. Instalación

En la terminal:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Esto descarga e instala uv. Cuando termine, **cierra la terminal y abrela de nuevo** (para que el sistema reconozca el comando).

### 2.2. Verificación

```bash
uv --version
```

Salida esperada (versión puede variar):

```
uv 0.5.x
```

Si ves `command not found: uv`, abre una nueva terminal o reinicia. Si persiste, revisa `recursos.md` § "Troubleshooting uv".

---

## Ejercicio 3 — Instalar Python 3.12 vía uv (3 min)

```bash
uv python install 3.12
```

uv descarga Python 3.12 (no toca el Python "del sistema"). Verificación:

```bash
uv python list
```

Deberías ver una entrada que indique Python 3.12 instalado y disponible.

---

## Ejercicio 4 — Instalar VS Code y extensiones (10 min)

### 4.1. Descargar VS Code

Ve a https://code.visualstudio.com/ y descarga el instalador para tu sistema operativo. Instala con las opciones por defecto.

> **Para usuarios de WSL2:** instala VS Code en Windows (no dentro de WSL). VS Code detecta WSL automáticamente y te pone una opción "Open Folder in WSL".

### 4.2. Abrir VS Code desde la terminal

Después de instalar, en una terminal nueva, escribe:

```bash
code .
```

Esto abre VS Code en el directorio actual. Si dice `command not found`, sigue las instrucciones en `recursos.md` § "VS Code: comando `code` desde terminal".

### 4.3. Instalar extensiones esenciales

Dentro de VS Code:

1. Click en el ícono de extensiones (cuadrados a la izquierda) o `Ctrl+Shift+X`.
2. Busca e instala:
   - **Python** (Microsoft).
   - **Pylance** (Microsoft) — debería instalarse automáticamente con la anterior.
   - **Ruff** (Astral).

**Verificación:** después de instalar, vuelve a "Extensions" y comprueba que aparecen en la sección "Installed".

---

## Ejercicio 5 — Tu primer proyecto Python (15 min)

Vamos a crear el primer proyecto desde cero. Sigue paso a paso, sin saltar.

### 5.1. Crear el directorio del proyecto

```bash
cd ~                          # Asegúrate de estar en tu home
mkdir mi-hola-mundo
cd mi-hola-mundo
pwd                           # Confirma que estás dentro
```

### 5.2. Inicializar con uv

```bash
uv init --no-readme --bare
```

Esto crea un archivo `pyproject.toml` mínimo. Verifica:

```bash
ls
cat pyproject.toml
```

Deberías ver algo como:

```toml
[project]
name = "mi-hola-mundo"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = []
```

### 5.3. Crear el script

Abre el directorio en VS Code:

```bash
code .
```

Dentro de VS Code, crea un archivo nuevo llamado `main.py` y escribe (no copies — escribe):

```python
import sys

print("Hola desde python-training-fundamentals!")
print(f"Python {sys.version.split()[0]}")
print("Si ves estas tres líneas sin errores, tu entorno está listo.")
```

Guarda el archivo (`Ctrl+S`).

> **No te preocupes si no entiendes cada línea todavía.** `import`, `f-strings` y `split()` los cubrimos en M1. Por ahora basta con que el código se ejecute.

### 5.4. Ejecutarlo

Vuelve a la terminal (puedes usar la integrada de VS Code: `Ctrl+ñ` o View → Terminal). Asegúrate de estar en el directorio del proyecto:

```bash
pwd                           # debería terminar en /mi-hola-mundo
uv run python main.py
```

**Salida esperada:**

```
Hola desde python-training-fundamentals!
Python 3.12.x
Si ves estas tres líneas sin errores, tu entorno está listo.
```

🎉 Ese es tu primer programa Python ejecutado. Tómate un minuto para apreciarlo — es el primero de muchos.

---

## Ejercicio 6 — Romperlo intencionalmente (10 min)

Aprender a programar incluye aprender a leer errores. Vamos a romper el script de tres formas distintas para ver qué dice Python en cada caso.

### 6.1. Error de sintaxis

Edita `main.py` y borra el paréntesis de cierre de la primera línea:

```python
print("Hola desde python-training-fundamentals!"
```

Guarda y ejecuta:

```bash
uv run python main.py
```

**Lee el mensaje de error completo.** Identifica:
- Línea donde Python detectó el error.
- Tipo de error (`SyntaxError`).
- La descripción humana del error.

Vuelve a poner el paréntesis. Comprueba que funciona de nuevo.

### 6.2. Error de nombre

Cambia `print` por `imprime`:

```python
imprime("Hola desde python-training-fundamentals!")
```

Guarda y ejecuta. **¿Qué tipo de error es?** ¿En qué línea? ¿Qué te dice exactamente?

Vuelve a poner `print`.

### 6.3. Error de import

Borra la línea `import sys`:

```python
# import sys                # ← borrada o comentada

print("Hola desde python-training-fundamentals!")
print(f"Python {sys.version.split()[0]}")
```

Guarda y ejecuta. **¿Qué tipo de error es ahora?** ¿En qué línea?

Vuelve a poner `import sys`.

**Para qué sirve este ejercicio:** los buenos programadores no son los que no cometen errores. Son los que **leen los mensajes de error** y los entienden. Esos tres tipos de error (`SyntaxError`, `NameError`, faltante de import) son los que más vas a ver durante M1.

---

## Ejercicio 7 — Un script con interacción (10 min)

Crea un archivo nuevo `saludo.py` en el mismo directorio:

```python
nombre = input("¿Cómo te llamas? ")
print(f"Hola, {nombre}! Bienvenido al curso.")
```

Ejecuta:

```bash
uv run python saludo.py
```

El programa va a pausar y esperar a que escribas tu nombre. Escríbelo, presiona Enter, observa la salida.

---

## Reto opcional — Mostrar info del sistema (15 min)

Crea un script `info.py` que imprima:
- Tu nombre (que el usuario lo escriba con `input()`).
- La versión de Python (usando `sys.version`).
- El sistema operativo (usando `import platform; platform.system()`).
- La hora actual (usando `from datetime import datetime; datetime.now()`).

**Restricción:** intenta resolverlo TÚ primero. Si te trabás más de 20 minutos, pídele a una IA que te explique cómo pensar el problema (NO la solución), o consulta `recursos.md`.

---

## Aporte al proyecto integrador

Esta sesión todavía no aporta código a TiendaPro Lite (eso empieza en M1). Pero deja tu computadora lista para los próximos 6 meses. Concretamente:

- Terminal y comandos básicos: ✅
- uv instalado: ✅
- Python 3.12 disponible: ✅
- VS Code + 3 extensiones: ✅
- Primer script ejecutado y entendido: ✅

---

## Antes de cerrar el Módulo 0

Verifica los cuatro comandos siguientes en tu terminal. Cada uno debería responder sin error:

```bash
uv --version
uv python list           # debería listar Python 3.12
code --version           # versión de VS Code
which python             # debería apuntar a algo de uv (o sin Python global, error — está OK)
```

Si los cuatro funcionan, **terminaste el Módulo 0**. Sigue con [Módulo 1 — Python fundamentos](../../01-python-fundamentos/) (próximamente).

# S00.2 — Recursos

Material complementario y guías de troubleshooting para los problemas más comunes durante el setup. **Nada de esto es obligatorio**, pero si algo del setup no te funciona, busca primero aquí.

---

## Documentación oficial

- **uv** — https://docs.astral.sh/uv/
  La doc oficial es excelente y corta. Léela entera al menos una vez en algún momento durante M0-M1.

- **Visual Studio Code — Python tutorial** — https://code.visualstudio.com/docs/python/python-tutorial
  El tutorial oficial de Python en VS Code. Cubre instalación, configuración del intérprete, debugging.

- **Python tutorial oficial — sección 2 (using the interpreter)** — https://docs.python.org/3/tutorial/interpreter.html
  Profundización sobre las distintas formas de ejecutar Python.

---

## Guías de instalación específicas

### WSL2 setup (Windows)

- **Microsoft — Install WSL** — https://learn.microsoft.com/windows/wsl/install
  Guía oficial. Resumen: abre PowerShell como administrador, ejecuta `wsl --install`, reinicia, configura usuario y contraseña en Ubuntu. Listo.

- **Microsoft — VS Code with WSL** — https://learn.microsoft.com/windows/wsl/tutorials/wsl-vscode
  Cómo VS Code se conecta a WSL. La extensión "Remote - WSL" es la clave (se instala sola la primera vez que abres una carpeta WSL desde VS Code).

### macOS

- En macOS reciente, la terminal trae `zsh` por defecto y todo el flujo del curso funciona sin ajustes.
- Si ves un mensaje sobre "command line developer tools" cuando ejecutas `git` o algún otro comando por primera vez, acepta la instalación — es un setup automático de Apple necesario para muchas herramientas.

### Linux

- En la mayoría de distros (Ubuntu, Fedora, Arch) el flujo del curso funciona directo. Si tu distro no incluye `curl` o `git`, instálalos con tu package manager (`apt`, `dnf`, `pacman`).

---

## Troubleshooting

### `uv: command not found`

Causa más común: la terminal no recargó el PATH después de instalar.

**Solución:**
1. Cierra todas las terminales y abre una nueva.
2. Si persiste, verifica que el directorio `~/.local/bin` esté en tu PATH:
   ```bash
   echo $PATH | tr ':' '\n' | grep .local
   ```
3. Si no aparece, agrega esta línea al final de `~/.bashrc` (Linux/WSL) o `~/.zshrc` (macOS):
   ```bash
   export PATH="$HOME/.local/bin:$PATH"
   ```
4. Recarga: `source ~/.bashrc` (o `source ~/.zshrc`).

### `python: command not found` después de `uv python install`

uv instala Python pero **no** lo agrega al PATH como `python`. Eso es intencional. La forma correcta de ejecutar Python es:

```bash
uv run python main.py
```

No:

```bash
python main.py        # ← puede no funcionar
```

`uv run` se encarga de seleccionar el Python correcto para tu proyecto.

### VS Code: comando `code` desde terminal

**macOS:**
1. Abre VS Code.
2. `Cmd+Shift+P` → busca "Shell Command: Install 'code' command in PATH".
3. Selecciónalo. Ya puedes usar `code .` desde la terminal.

**Linux/Windows:** suele instalarse automáticamente con el instalador.

### El comando `code .` desde WSL abre VS Code en Windows pero no ve los archivos

Asegúrate de que tienes instalada la extensión "Remote - WSL" en VS Code. La primera vez puede pedirte instalarla automáticamente.

### `uv init` me crea más archivos de los que esperaba

Por defecto, `uv init` crea `pyproject.toml`, `README.md`, `main.py`, `.python-version` y `.gitignore`. Para los ejercicios usamos `--no-readme --bare` para tener solo `pyproject.toml` y trabajar desde cero.

---

## Lecturas opcionales (para profundizar)

- **"The Missing Semester of Your CS Education"** — https://missing.csail.mit.edu/
  Curso del MIT (gratis) sobre las herramientas que todo programador usa todos los días pero nadie enseña: shell, vim, git, debugging, automatización. **Altamente recomendado** después de cerrar M0.

- **"The Linux Command Line"** — William Shotts — https://linuxcommand.org/tlcl.php
  Libro gratuito y completísimo sobre la terminal. No lo leas entero ahora — úsalo como referencia.

- **"How Python Runs Your Code"** — varios artículos en Real Python.
  Útil para entender en profundidad qué pasa cuando ejecutas `python script.py` (M1+).

- **"Modern Python Developer's Toolkit"** — distintos cursos cortos en YouTube sobre uv, ruff y pyright. Búscalos cuando quieras profundizar — no son necesarios todavía.

---

## Atajos de teclado útiles

### Terminal (bash/zsh)

- `Ctrl+C` — cancelar comando actual.
- `Ctrl+D` — cerrar terminal (equivalente a `exit`).
- `Ctrl+L` — limpiar pantalla (equivalente a `clear`).
- `Ctrl+R` — buscar en el historial de comandos.
- `Ctrl+A` / `Ctrl+E` — ir al inicio / final de la línea.
- Flecha arriba / abajo — navegar comandos previos.
- `Tab` — autocompletar.

### VS Code

- `Ctrl+P` — abrir archivo por nombre.
- `Ctrl+Shift+P` — paleta de comandos (todo se hace desde aquí).
- `Ctrl+ñ` (o `` Ctrl+` ``) — abrir / cerrar terminal integrada.
- `Ctrl+S` — guardar.
- `Ctrl+/` — comentar / descomentar línea.
- `Ctrl+D` — seleccionar la siguiente ocurrencia de la palabra.

---

## Una nota sobre temas y configuración

VS Code permite cambiar de tema, fuente, tamaño, atajos. Está bien que personalices, **pero hazlo después de M1**. Antes, dedica esa energía a aprender Python — el rato configurando el editor es rato que no estás programando, y el editor recién empieza a importar de verdad cuando ya escribes mucho código.

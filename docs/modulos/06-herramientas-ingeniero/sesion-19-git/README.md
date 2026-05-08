# S19 — Git en serio: branches, rebase, conflictos, conventional commits

> **Sesión 2h.** ~50 min lectura + ~70 min ejercicios. **Abre el Módulo 6 — Herramientas del ingeniero.** Hasta acá usaste git para guardar tu progreso (`git add`, `git commit`, `git push`). Eso alcanza para trabajar **solo**. Cuando entres a un equipo, git es **el lenguaje de coordinación**: cómo proponés cambios, cómo conviven varias personas en el mismo archivo, cómo se reescribe la historia para que sea legible. Hoy aprendés a usarlo como herramienta de ingeniería, no de backup.

---

## 1. Objetivos de aprendizaje

Al terminar esta sesión vas a poder:

- Explicar el modelo mental de git: working tree → staging area → commit, y por qué `git add` existe (no es trámite, es diseño).
- Visualizar la historia como un **grafo de commits** y entender qué es una branch (un puntero, no una "copia").
- Crear, cambiar y borrar branches (`git switch`, `git branch -d`).
- Diferenciar **merge** y **rebase**, decidir cuál usar según el caso (commits compartidos vs. locales).
- Resolver un **conflicto de merge** sin pánico: leer los marcadores, elegir, marcar resuelto, continuar.
- Hacer **rebase interactivo** para reordenar, fusionar (`squash`), reescribir y borrar commits **antes** de pushear.
- Escribir mensajes de commit siguiendo **Conventional Commits** y entender qué le aportan a las herramientas (changelogs, semver, CI).
- Usar `git stash` para guardar cambios a medio camino y volver a ellos.
- Diferenciar `git reset` (mueve el puntero, reescribe historia) de `git revert` (commit nuevo que deshace).
- Configurar un `.gitignore` correcto y entender qué pasa cuando algo ya fue versionado por accidente.
- Trabajar con remotos: `fetch` vs `pull`, qué hace `push --force-with-lease` y cuándo es legítimo.

## 2. Prerequisitos

- Tenés git instalado y `git config user.name` / `user.email` ya seteados (lo viste en [01-setup.md](../../../01-setup.md)).
- Hiciste commits en este curso. Sabés `git status`, `git add`, `git commit`, `git push`, `git log`.
- Una cuenta de GitHub (no estrictamente necesaria para los ejercicios locales, pero útil para los del final).

## 3. Conceptos clave

1. **Snapshot, no diff.** Cada commit guarda **el estado completo** del proyecto en ese momento (con compresión y deduplicación). Los diffs los **calcula** git al pedirlos. Esto explica por qué ramificar es barato.
2. **Tres estados.** Working tree (lo que ves en disco) → staging area / index (lo que `git add` puso a esperar) → repositorio (lo que `git commit` selló).
3. **Commit = snapshot + padre(s) + autor + mensaje + hash.** Inmutable, identificado por un SHA-1. Reescribir la historia significa **crear commits nuevos** y mover punteros.
4. **Branch = puntero móvil a un commit.** No es una copia del código. `git switch otra` solo mueve `HEAD` y reconstruye el working tree con el snapshot apuntado.
5. **`HEAD`.** Puntero al commit actualmente checked-out. Casi siempre apunta a una branch; si apunta directo a un commit, se llama "detached HEAD".
6. **Merge vs rebase.** Dos formas de "traer cambios de otra branch": merge crea un commit de unión y preserva la historia; rebase reaplica tus commits encima de la otra branch, dejando una línea recta.
7. **Conflicto.** Aparece cuando dos cambios tocan la **misma región** de un archivo y git no puede combinar automáticamente. Lo resolvés vos, le decís a git "ya está", y seguís.
8. **Conventional Commits.** Convención para mensajes (`feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`...) que permite a herramientas generar changelogs y bumps de versión automáticos.
9. **Remoto (`origin`).** Otro repositorio (típicamente en GitHub) con el que sincronizás. `fetch` baja los cambios sin tocar tu working tree; `pull` = `fetch` + `merge` (o `rebase`).
10. **Reescribir historia es seguro localmente, peligroso después de push.** La regla: nunca `--force` sobre commits que otros ya tienen.

## 4. Teoría

### 4.1. El modelo mental: tres áreas

```
+-----------------+       git add       +------------+      git commit      +------------+
|  Working tree   |  -------------->    |   Index    |  ----------------->  |  Repo .git |
|  (archivos en   |                     |  (staging) |                      |  (commits) |
|   disco)        |  <--------------    |            |  <----------------   |            |
+-----------------+    git restore      +------------+   git checkout       +------------+
                       --staged
```

Cuando editás `archivo.py`, el cambio vive en el **working tree**. Hasta que no hagas `git add archivo.py`, git lo ignora a la hora de commitear. El **index** (staging area) es la "lista de cosas que voy a meter en el próximo commit".

¿Por qué dos pasos? Porque te permite **componer un commit** que NO sea un volcado de todo lo que cambió en disco. Editaste cinco archivos pero solo tres pertenecen al mismo cambio lógico → `git add` los tres, `commit`, después `git add` los otros dos, otro `commit`. La historia queda **más fácil de leer y revertir**.

`git status` te muestra los tres estados:

```
On branch main
Changes to be committed:        ← lo que está en el index (staged)
    modified:   src/api/rutas.py

Changes not staged for commit:  ← cambiado en working tree, no staged
    modified:   src/api/dtos.py

Untracked files:                ← ni siquiera lo sigue git
    nuevo.py
```

`git diff` te muestra el diff del **working tree vs index**. `git diff --staged` te muestra el diff del **index vs último commit**. Memorizalo — es la diferencia entre "qué llevo escrito" y "qué se va a commitear".

### 4.2. La historia es un grafo

Un commit es un **nodo**. Su `parent` es el commit anterior. Una branch es un **puntero** al commit más reciente de esa línea. `HEAD` es un puntero a la branch actual.

```
            (main)
              v
A --- B --- C
              ^
            (HEAD)
```

Cuando hacés un commit, el commit nuevo apunta al anterior, y la branch (y `HEAD`) avanzan al nuevo:

```
                  (main)
                    v
A --- B --- C --- D
                    ^
                  (HEAD)
```

Cuando creás una branch, **solo creás un puntero más**:

```bash
git switch -c feature/precio
```

```
                  (main)
                    v
A --- B --- C --- D
                    ^
              (feature/precio, HEAD)
```

Hasta acá ambas branches apuntan al mismo commit. **No se duplicó nada en disco.** Cuando hagas un commit en `feature/precio`, ahora sí divergen:

```
                       (main)
                         v
A --- B --- C --- D
                    \
                     E       (feature/precio, HEAD)
```

Esto explica varias cosas que de afuera son misteriosas:

- Crear branches es **instantáneo** (solo es escribir un archivo de texto con un SHA).
- Borrar una branch no borra los commits — solo borra el puntero. Los commits quedan vivos hasta que nadie los apunta y el garbage collector los limpia (semanas después).
- "Cambiar de branch" no es copiar archivos — es mover `HEAD` y dejar el working tree en el estado del commit destino.

Ver el grafo en la terminal:

```bash
git log --oneline --graph --all --decorate
```

Lo vas a usar mucho. Conviene ponerle un alias:

```bash
git config --global alias.lg "log --oneline --graph --all --decorate"
```

Después: `git lg`.

### 4.3. Branches: la unidad de trabajo

Comandos modernos (a partir de git 2.23):

```bash
git switch main                    # cambia a main
git switch -c feature/cors         # crea feature/cors desde HEAD y se mueve allá
git switch -                       # vuelve a la branch anterior (como `cd -`)
git branch                         # lista branches locales
git branch -d feature/cors         # borra branch (debe estar mergeada)
git branch -D feature/cors         # borra branch SIN chequear merge (peligroso)
```

Comandos clásicos (`checkout`) siguen funcionando, pero `switch` (para branches) y `restore` (para archivos) son **más claros** y menos propensos a confusión. Usá los nuevos.

**Cuándo crear una branch**: cualquier cambio que no sea trivial. Trabajar sobre `main` directo está bien si el repo es solo tuyo; en cuanto entra alguien más, **toda feature, fix o experimento va a su branch**. Eso te da:

- PRs revisables.
- Capacidad de tirar el experimento sin tocar `main`.
- CI que corre sobre la branch antes de mergear.

Naming convention sugerida (no obligatoria): `feature/descripcion-corta`, `fix/numero-issue`, `docs/loquesea`, `chore/loquesea`.

### 4.4. Merge vs rebase

Dos formas de **integrar** los commits de una branch en otra. Hacen cosas diferentes y se confunden seguido.

**Estado inicial:**

```
        E --- F        (feature)
       /
A --- B --- C --- D    (main)
```

**Merge** (`git switch main && git merge feature`):

```
        E --- F
       /       \
A --- B --- C --- D --- M    (main)
```

`M` es un **merge commit** con dos padres (`D` y `F`). La historia preserva la "rama". Los commits originales no se modifican.

**Rebase** (`git switch feature && git rebase main`):

```
                      E' --- F'    (feature)
                     /
A --- B --- C --- D                (main)
```

Tus commits `E` y `F` se "reaplican" sobre `D`, generando `E'` y `F'` (commits **nuevos**, con padre distinto y por ende SHA distinto). La historia queda **lineal**.

Después de rebasear, podés hacer `git switch main && git merge feature` y como `feature` es ahora un descendiente directo de `main`, el merge es **fast-forward** (no crea merge commit).

**¿Cuándo usar cuál?**

| Caso | Recomendación |
|---|---|
| Tu branch local todavía no se pushó / nadie la usa | `rebase` (historia más limpia) |
| Branch compartida con otros (varios pushean) | `merge` (rebase reescribe SHAs y rompe a los demás) |
| `main` después de revisar un PR | `merge` con fast-forward o squash, según política del equipo |
| Traer cambios de `main` a tu feature antes de PR | `rebase` (mantiene tu PR limpio) |

**La regla de oro**: nunca rebases commits que **ya están compartidos**. Si los pushaste y alguien los puede haber bajado, rebasearlos cambia los SHAs y obliga a todos a recoordinar.

### 4.5. Conflictos: el momento de la verdad

Un conflicto aparece cuando vos y otra persona (o vos en otra branch) editaron **la misma región** del mismo archivo. Git intenta combinar automáticamente; cuando no puede, te marca el archivo y para.

```
$ git merge feature/precio
Auto-merging src/tiendapro/modelos.py
CONFLICT (content): Merge conflict in src/tiendapro/modelos.py
Automatic merge failed; fix conflicts and then commit the result.
```

El archivo en disco queda con marcadores:

```python
class Producto(BaseModel):
    nombre: str
<<<<<<< HEAD
    precio: float
=======
    precio: Decimal
>>>>>>> feature/precio
```

- Entre `<<<<<<< HEAD` y `=======` está **tu** versión (la de la branch en la que estás).
- Entre `=======` y `>>>>>>> feature/precio` está la de la otra branch.

Para resolver:

1. Editás el archivo y dejás **lo que querés** (puede ser una de las dos versiones, una mezcla, o algo nuevo). **Borrá los marcadores** `<<<<<<<`, `=======`, `>>>>>>>`.
2. `git add src/tiendapro/modelos.py` — le decís a git "este archivo está resuelto".
3. `git status` para verificar que no queden conflictos.
4. `git merge --continue` (o `git rebase --continue` si estabas en un rebase).

Si te empantanás y querés cancelar:

```bash
git merge --abort       # vuelve al estado anterior al merge
git rebase --abort      # vuelve al estado anterior al rebase
```

**Consejo pragmático**: cuando el conflicto sea grande, abrí el archivo en tu editor y mirá el `git log` de ambos lados (`git log HEAD..feature/precio -- src/tiendapro/modelos.py`) para entender **por qué** cada lado quedó así. No resuelvas a las apuradas — un conflicto mal resuelto introduce bugs sutiles.

### 4.6. Rebase interactivo: reescribir historia local

Esta es la herramienta que separa a alguien que "usa git" de alguien que **piensa en commits**.

Antes de abrir un PR, querés que tu historia sea **legible**. Si hiciste 12 commits del estilo `wip`, `arreglo typo`, `volví a probar`, `ahora sí`, `final final`, eso es ruido para el reviewer.

Rebase interactivo permite, sobre tu propia branch local:

- **Reordenar** commits.
- **Fusionar** (squash) varios en uno.
- **Editar** el mensaje de un commit pasado.
- **Editar** el contenido de un commit pasado.
- **Eliminar** un commit.

```bash
git rebase -i HEAD~5    # interactúa sobre los últimos 5 commits
```

Te abre el editor con algo como:

```
pick a1b2c3d feat: agregar endpoint productos
pick d4e5f6g wip
pick 7h8i9j0 arreglo typo
pick k1l2m3n feat: agregar filtro por categoria
pick n4o5p6q final
```

Cambiás `pick` por:

- `reword` (`r`) — quedate con el commit pero editá el mensaje.
- `squash` (`s`) — fusioná este commit con el anterior, te deja editar el mensaje resultante.
- `fixup` (`f`) — como squash pero descarta el mensaje de este commit.
- `drop` (`d`) — eliminá este commit.
- Las líneas se ejecutan **de arriba abajo**; reordenarlas reordena los commits.

Resultado deseable:

```
pick a1b2c3d feat: agregar endpoint productos
fixup d4e5f6g wip
fixup 7h8i9j0 arreglo typo
fixup n4o5p6q final
pick k1l2m3n feat: agregar filtro por categoria
```

Quedan **dos** commits limpios. Tu historia ahora es contable.

**Otra vez la regla**: rebase interactivo es seguro **antes** de pushear o si tu branch es solo tuya. Después de pushear, considerá que cualquier `force-push` puede romperle el clon a otros — y nunca lo hagas en `main`.

### 4.7. Conventional Commits

Convención para mensajes. Estructura:

```
<type>(<scope>): <descripción corta>

[cuerpo opcional]

[footer opcional]
```

Tipos comunes:

| Tipo | Cuándo |
|---|---|
| `feat` | Nueva funcionalidad para el usuario |
| `fix` | Corrección de bug |
| `docs` | Solo documentación |
| `style` | Formato, espacios, comas — sin cambio funcional |
| `refactor` | Cambio interno, sin nueva feature ni fix |
| `test` | Sumar o corregir tests |
| `chore` | Tareas de mantenimiento (deps, configs) |
| `perf` | Mejora de performance |
| `ci` | Cambios en pipeline / GitHub Actions |
| `build` | Cambios en build, compilación o empaquetado |

Scope (opcional): a qué parte afecta (`feat(api):`, `fix(db):`, `chore(deps):`).

Ejemplos buenos del propio curso:

```
feat(m05-s17): añade sesión validación + DTOs + manejo de errores HTTP
fix(repositorio): evita N+1 al cargar productos por categoría
docs(curriculum): marca M5 como completado en el roadmap
chore(deps): bump fastapi a 0.115
```

¿Por qué importa?

- **Changelogs automáticos**: herramientas como `git-cliff`, `semantic-release` o `release-please` leen estos commits y generan el `CHANGELOG.md` solos.
- **Semver automático**: `feat` → minor bump, `fix` → patch bump, `feat!` o `BREAKING CHANGE:` en footer → major bump.
- **Filtros**: `git log --grep="^fix"` para ver todos los fixes.
- **Comunicación**: el reviewer entiende **antes** de leer el diff.

**Breaking change**:

```
feat(api)!: renombrar /producto a /productos

BREAKING CHANGE: el endpoint /producto desaparece. Los clientes deben usar
/productos. La forma del payload no cambia.
```

El `!` después del scope (o el footer `BREAKING CHANGE:`) marca el cambio incompatible. Es la forma de comunicar "esto rompe a alguien que actualice sin leer".

### 4.8. `.gitignore`: qué NO seguir

Lista de patrones que git ignora. Va en la raíz del repo (también pueden haber `.gitignore` por subdirectorio).

Ejemplo típico de un proyecto Python:

```gitignore
# Bytecode
__pycache__/
*.pyc

# Virtualenvs y caches
.venv/
.mypy_cache/
.ruff_cache/
.pytest_cache/

# Build artifacts
build/
dist/
*.egg-info/

# Datos locales
*.db
*.sqlite
*.log

# Configs locales (NUNCA versionar secretos)
.env
.env.local

# Editor
.vscode/
.idea/
```

**Importante**: `.gitignore` solo afecta a archivos **untracked**. Si un archivo ya fue committeado por error y después lo agregás al `.gitignore`, sigue tracked.

Para sacarlo del tracking sin borrarlo del disco:

```bash
git rm --cached .env
git commit -m "chore: deja de trackear .env"
```

Y si era un secreto: **rotalo**. Asumí que se filtró. La historia sigue conservando el archivo aunque lo saques (hay que reescribirla con `git filter-repo` para borrarlo de verdad — y eso es invasivo).

### 4.9. `git stash`: pausar para hacer otra cosa

Estás a medio implementar algo y aparece un bug urgente. No querés commitear basura, pero tampoco perder tus cambios. `stash` es la guardería temporal:

```bash
git stash push -m "wip: refactor de productos"
# ahora tu working tree está limpio
git switch hotfix/algo-urgente
# ... hacés el fix, commit, vuelves ...
git switch feature/refactor
git stash pop          # recupera y borra del stash
```

Útil. Pero abusarlo es signo de que necesitás commits más chicos. Un `git stash list` con 12 entradas viejas es deuda.

### 4.10. `reset` vs `revert`

Dos formas de "deshacer" — hacen cosas diferentes.

**`git revert <sha>`**: crea un **commit nuevo** que invierte los cambios del commit indicado. La historia anterior **no se modifica**. Es la forma segura de deshacer algo en una branch compartida.

```bash
git revert a1b2c3d
# crea un commit "Revert ..." encima de HEAD
```

**`git reset <sha>`**: mueve el puntero de la branch a otro commit, **reescribiendo** la historia.

Tres modos:

```bash
git reset --soft HEAD~1     # mueve la branch, deja el index y working tree intactos
git reset --mixed HEAD~1    # default: mueve la branch e índice; working tree intacto
git reset --hard HEAD~1     # mueve TODO. Cambios sin commitear se PIERDEN.
```

`reset --hard` es **destructivo**: borra cambios sin commitear. Si te equivocás, el `git reflog` puede salvarte (registra dónde estuvo `HEAD` últimamente, así que podés volver a ese punto), pero no tientes a la suerte.

**Regla**: `reset` para historia local; `revert` para historia compartida.

### 4.11. Remotos: `fetch`, `pull`, `push`

```bash
git remote -v                      # lista los remotos
git remote add origin <url>        # agrega un remoto
git fetch origin                   # baja commits y refs sin tocar tu working tree
git pull origin main               # = fetch + merge (o rebase, si lo configurás)
git push origin main               # sube tus commits a la branch remota
git push -u origin feature/algo    # primer push de una branch nueva: linkea local↔remoto
```

**`fetch` vs `pull`**:

- `fetch` baja los datos del remoto y actualiza `origin/main`, **sin** modificar tu branch local. Para inspeccionar antes de integrar.
- `pull` es `fetch` + integración automática. Cómodo, pero a veces sorprende (mete merge commits "de relleno"). Si querés rebase en vez de merge:

  ```bash
  git config --global pull.rebase true
  ```

  Recomendado para uso solo / equipos que prefieren historia lineal.

**`push --force-with-lease`**: si rebaseaste tu branch local y necesitás pushear (la branch remota tiene los SHAs viejos), **NO uses `--force` a secas**. Usá `--force-with-lease`:

```bash
git push --force-with-lease origin feature/refactor
```

Eso falla si alguien empujó algo nuevo desde tu último fetch — o sea, te protege de pisar trabajo de otros sin querer. `--force` puro pisa y no pregunta.

**Regla**: nunca `--force` (de ningún tipo) sobre `main`. Sobre tu propia feature branch, `--force-with-lease` es aceptable.

### 4.12. Workflow típico de feature branch

Resumen del ciclo para un cambio en un equipo:

```bash
# 1. Empezar desde main actualizado
git switch main
git pull

# 2. Crear branch de feature
git switch -c feature/agregar-busqueda

# 3. Trabajar, ir commiteando seguido (commits chicos)
# ... edits ...
git add src/api/rutas.py
git commit -m "feat(api): agregar endpoint /productos/buscar"

# 4. Antes de abrir el PR, traer cambios recientes de main
git fetch origin
git rebase origin/main          # tu branch queda encima de lo último

# 5. Si la historia tiene "wip"s o ruido, limpiarla
git rebase -i origin/main

# 6. Pushear
git push -u origin feature/agregar-busqueda
# o, si ya pushaste y rebaseaste:
git push --force-with-lease

# 7. Abrir PR, esperar review, mergear (típicamente con squash)

# 8. Limpiar
git switch main
git pull
git branch -d feature/agregar-busqueda
```

Lo vas a hacer cientos de veces. Memorizá la secuencia, no los comandos sueltos.

## 5. Patrones y antipatrones

| ✅ Patrón | ❌ Antipatrón |
|---|---|
| Commits chicos y atómicos (un cambio lógico = un commit) | Commits gigantes "guardo todo lo que hice hoy" |
| Mensajes con Conventional Commits (`feat:`, `fix:`, etc.) | Mensajes tipo `wip`, `cambios`, `.`, `lo de antes` |
| Rebase interactivo antes del PR para limpiar la historia | Pushear 15 commits `wip` y dejar que el reviewer adivine |
| `git switch` y `git restore` (post 2.23) | `git checkout` para todo (sigue funcionando, pero es ambiguo) |
| `--force-with-lease` sobre branches propias | `--force` sin pensar |
| `.gitignore` versionado, secretos NUNCA committeados | `.env` con keys reales en la historia |
| `git revert` para deshacer en branches compartidas | `git reset --hard` sobre algo ya pushado |
| Branch por feature/fix | Trabajar todo en `main` y "ya lo arreglo después" |
| `git pull --rebase` (o `pull.rebase=true`) | Pull con merge crea ruido en historia chica |
| Resolver conflictos con calma, leyendo ambos lados | "Acepto el mío", commit, cruzar dedos |
| Commit firmado y con autor real (`user.email` correcto) | Commits con `unknown` porque no configuraste |
| `git stash` puntual para emergencias | 14 stashes acumulados sin nombre |
| Mergear con `--no-ff` o squash según política del equipo | Mergear sin enterarte de qué política tiene el equipo |

## 6. Conexión con el proyecto integrador

En esta sesión **no agregás código** al integrador — agregás **disciplina**. Pero el módulo se cierra después de S20 y S21, y para cuando llegues al hito M6 vas a haber:

- Practicado branches de feature en un sandbox.
- Resuelto al menos un conflicto de merge a mano.
- Hecho un rebase interactivo para limpiar tu historia.
- Configurado tu workflow de commits en el repo del curso (Conventional Commits ya lo venimos usando — fijate en `git log --oneline | head -20` de este mismo repo).

**Mini-aporte hoy**: revisá tu propio historial del curso. ¿Hay commits que romperían los tres tipos de "antipatrón"? ¿Mensajes vagos? ¿Cambios no relacionados pegados? No vamos a reescribir la historia del curso (ya está pushada y no vale la pena), pero **tomá nota** de qué harías distinto.

Detalles paso a paso en `ejercicios.md`.

## 7. Resumen

1. **Git modela la historia como un grafo de snapshots**, no de diffs. Branches son punteros, no copias.
2. **Tres áreas**: working tree → index → repo. `add` mueve a index; `commit` sella en repo.
3. **`switch` y `restore`** son los comandos modernos, claros y específicos. Usalos.
4. **Merge preserva, rebase reescribe.** Rebase para historia local; merge para integración compartida.
5. **Conflictos** se resuelven editando el archivo, `add`, `--continue`. No hay magia.
6. **Rebase interactivo** es la herramienta para hacer historia legible **antes** del PR.
7. **Conventional Commits** convierte mensajes en metadata accionable (changelogs, semver).
8. **`.gitignore`** desde el día 1; secretos nunca al repo. Si se filtró, rotalos.
9. **`reset`** reescribe; **`revert`** suma un commit. Reset para local, revert para compartido.
10. **Nunca `--force` sobre branches compartidas o `main`.** `--force-with-lease` es la red de seguridad para tu propia branch.

## 8. Preguntas de auto-evaluación

1. ¿Qué diferencia hay entre el working tree, el index y el repo? ¿Qué comando mueve cosas entre cada par?
2. Una branch nueva, ¿duplica los archivos en disco? Justificá tu respuesta a partir del modelo mental de git.
3. Tenés `feature/cors` divergida de `main`. ¿Cuándo conviene `merge` y cuándo `rebase`? Da un ejemplo de cada caso.
4. Estás en medio de un rebase y aparece un conflicto. ¿Cuál es la secuencia exacta de comandos para resolverlo y continuar? ¿Qué comando usarías para abortar?
5. ¿Qué hace `git rebase -i HEAD~3`? Listá tres operaciones que podés hacer en él.
6. Escribí tres commits según Conventional Commits para: (a) agregar un endpoint nuevo, (b) corregir un bug en validación, (c) actualizar la versión de fastapi.
7. Hiciste `git commit -m "wip"` con un secreto en `.env`. ¿Qué pasos seguís?
8. ¿Cuál es la diferencia entre `git reset --soft`, `--mixed` y `--hard`? ¿Cuál perdería tus cambios sin commitear?
9. Rebaseaste tu branch y querés pushearla. ¿Por qué `--force-with-lease` es preferible a `--force`?
10. Tu compañero pushó cambios a `feature/X` mientras vos trabajabas localmente sobre la misma branch. ¿Qué pasos seguís para integrar lo de él sin perder lo tuyo?

Cuando puedas responder todas, pasá a [`ejercicios.md`](ejercicios.md) para practicar en un sandbox.

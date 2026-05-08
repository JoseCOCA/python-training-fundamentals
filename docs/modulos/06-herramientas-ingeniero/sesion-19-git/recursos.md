# S19 — Recursos

## Documentación oficial

- **Pro Git Book** ([git-scm.com/book](https://git-scm.com/book/en/v2)). El libro de referencia escrito por los mantenedores de git. Gratis, completo, en varios idiomas. Si solo vas a leer un libro de git, este es.
- **Git Reference** ([git-scm.com/docs](https://git-scm.com/docs)). Las man pages oficiales en HTML. `git help <comando>` desde la terminal te lleva al mismo contenido.
- **Conventional Commits 1.0.0** ([conventionalcommits.org](https://www.conventionalcommits.org/en/v1.0.0/)). Spec corto y autoritativo. Léelo entero — son 10 minutos.
- **GitHub Flow** ([docs.github.com/en/get-started/quickstart/github-flow](https://docs.github.com/en/get-started/using-github/github-flow)). El workflow que asume GitHub: branch → commits → PR → review → merge. La mayoría de los equipos arrancan con esto.

## Lecturas guiadas

- **Atlassian Git Tutorials** ([atlassian.com/git/tutorials](https://www.atlassian.com/git/tutorials)). Tutoriales con diagramas. Mejor explicación visual de merge vs rebase que vas a encontrar.
- **Oh Shit, Git!?!** ([ohshitgit.com](https://ohshitgit.com/)). Recetas para "rompí algo, ¿cómo lo arreglo?". Tenelo en favoritos — vas a volver.
- **Git from the inside out** ([maryrosecook.com/blog/post/git-from-the-inside-out](https://maryrosecook.com/blog/post/git-from-the-inside-out)). Cómo funciona git por dentro: blobs, trees, commits, refs. Cuando entiendas esto, todo lo demás es trivial.
- **Trunk-Based Development** ([trunkbaseddevelopment.com](https://trunkbaseddevelopment.com/)). Una alternativa al "GitHub Flow" más simple cuando hay buen CI/CD: branches cortas, integración continua a `main`. Vale la pena conocer las dos filosofías.
- **A Git Story: Not So Final Words** ([github.com/blog/2019-08-19-git-on-the-web](https://github.blog/open-source/git/highlights-from-git-2-23/)). El blog post de GitHub anunciando `git switch` y `git restore` en git 2.23. Útil para entender por qué existen.

## Para profundizar

- **Pro Git, capítulos 7-10** (de [git-scm.com/book](https://git-scm.com/book/en/v2)). "Git Tools", "Customizing Git", "Git and Other Systems", "Git Internals". Después de los primeros 6 capítulos básicos, estos te llevan al nivel power user.
- **Building Git** (James Coglan). Reimplementás un subset de git en Ruby. La mejor forma de entender los internals si te gusta aprender escribiendo el sistema.
- **gitignore.io** ([gitignore.io](https://www.toptal.com/developers/gitignore)). Generador de `.gitignore` por lenguaje/IDE. Útil para arrancar un proyecto rápido.
- **Git Worktrees** ([git-scm.com/docs/git-worktree](https://git-scm.com/docs/git-worktree)). Permite tener varios working trees del mismo repo a la vez (una branch por carpeta). Cuando manejás 5 PRs en paralelo, esto te ahorra cambiar de branch todo el tiempo.

## Herramientas que vale la pena conocer

- **`gh`** — CLI oficial de GitHub. `gh pr create`, `gh pr list`, `gh pr checkout 42`. Te ahorra abrir el browser para tareas comunes.
- **`tig`** — TUI para navegar la historia de git. `tig` (sin args) es el `git log --graph` más bonito que vas a ver.
- **`lazygit`** — TUI más completa, atajos de teclado para todo (commit, stage hunks, rebase interactivo). Si te gustan las TUI, probala.
- **`delta`** — formatter de diffs con sintaxis highlighted, side-by-side, números de línea. Reemplazo del diff default de git. Una vez que lo probás, no volvés.
- **`pre-commit`** — framework de hooks de git pre-commit (lo viste en M3). Garantiza que linters/tests/formatters corren antes de cada commit.
- **`commitizen`** o **`czg`** — wizards interactivos para escribir Conventional Commits. Útiles al principio; después se vuelve manual.
- **`git-cliff`** — generador de changelogs a partir de Conventional Commits. Una sola corrida y tenés `CHANGELOG.md` actualizado.
- **Sourcetree / GitKraken / Fork** — GUIs de git. Útiles para ver el grafo en proyectos grandes; el resto del trabajo es más rápido en terminal.

## Referencias para resolver dudas puntuales

- **"Hice un commit con un mensaje mal escrito"** — `git commit --amend` (si es el último y no lo pushaste) o `git rebase -i HEAD~N` con `reword`.
- **"Quiero deshacer el último commit pero conservar los cambios en disco"** — `git reset --soft HEAD~1` (los cambios quedan staged) o `--mixed` (quedan unstaged).
- **"Pushé un secreto al repo"** — primero **rotalo**. Después, removelo del archivo + `git rm --cached` + commit. Para borrarlo de la historia entera necesitás `git filter-repo` (más invasivo) y avisar a todos los que tienen clones.
- **"`git pull` me crea merge commits feos"** — `git config --global pull.rebase true` o usá `git pull --rebase` cada vez.
- **"Un archivo aparece como modificado pero yo no lo toqué"** — generalmente es por line endings (Windows ↔ Linux). Configurá `git config --global core.autocrlf input` (Linux/Mac) o `true` (Windows).
- **"Quiero ver qué cambió en un commit puntual"** — `git show <sha>`.
- **"Me equivoqué de branch — commiteé en main lo que iba en feature"** — `git switch -c feature/correcto` (te lleva el commit), `git switch main`, `git reset --hard HEAD~1` (saca el commit de main).
- **"`git rebase` me dice 'detached HEAD'"** — estás en un commit que ninguna branch apunta. Si querés conservar lo que hiciste, `git switch -c rama-rescate` antes de moverte.
- **"`git status` muestra archivos en `.gitignore`"** — generalmente porque ya estaban trackeados antes de agregarlos al `.gitignore`. `git rm --cached <archivo>`.
- **"`git log` con muchos archivos pierde el grafo"** — usá `--graph --oneline --all --decorate`. Mejor: ponelo en un alias (`git lg`).

## Errores comunes

- **Commits gigantes** — un commit por "lo que hice esta tarde" hace imposible revertir un cambio puntual. Atómicos: un commit = un cambio lógico.
- **Mensajes vagos** — `wip`, `cambios`, `arreglo`. Tu yo de seis meses no va a entender. Usá Conventional Commits y describí el **por qué** en el cuerpo si hace falta.
- **`git push --force` sobre `main` o branches compartidas** — pisa el trabajo de otros. **Nunca** sobre `main`. Si necesitás force-push en tu propia branch, usá `--force-with-lease`.
- **Mergear sin saber qué política tiene el equipo** — algunos equipos prefieren squash, otros merge commits, otros rebase + fast-forward. Preguntá antes de ensuciar la historia.
- **Trabajar siempre sobre `main`** — funciona solo, deja de funcionar al segundo colaborador. Acostumbrate a feature branches desde el día 1.
- **Commitear `.env`, claves, tokens** — el escenario más común de filtración. Asumí que cualquier cosa que llegue a un repo público (incluso por cinco minutos) está filtrada para siempre. Rotala.
- **Usar `git checkout` para todo** — sigue funcionando pero es ambiguo (cambia branches **y** archivos). `switch` para branches, `restore` para archivos. Más claro al leer scripts.
- **No configurar `user.name` / `user.email`** — tus commits aparecen como `unknown <unknown@unknown>`. Setealo de una.
- **`git pull` con merge** — si trabajás solo o el equipo prefiere historia lineal, `pull.rebase=true` te ahorra ruido.
- **Resolver conflictos sin entender** — borrar marcadores y dejar "lo mío" sin leer es un bug en producción esperando. Tomate los minutos.

## Si vas hacia el curso 2

En AI Engineering vas a manejar muchos experimentos en paralelo (modelos distintos, prompts distintos, configs distintas). Las branches dejan de ser "una feature" y pasan a ser **"un experimento"**.

Buen workflow:

- `feature/exp-prompt-v3-with-cot` — nombre que describe la hipótesis del experimento.
- Commits chicos con resultados (`feat: corre suite eval con temp=0.2 (acc=0.84)`).
- Después del experimento, mergeás (con squash) lo que ganó y dropeás las otras branches.

Y cuando los modelos cambien (`claude-3` → `claude-4` → `claude-4.6`), querés un changelog claro de qué cambió cuándo. Conventional Commits + `git-cliff` te da eso sin esfuerzo.

La disciplina de hoy — branches por unidad de trabajo, mensajes accionables, historia limpia antes del PR — es la misma que te va a salvar cuando tengas 12 prompts en paralelo y un colaborador.

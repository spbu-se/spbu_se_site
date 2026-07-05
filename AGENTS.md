# SE Site

Сайт кафедры системного программирования СПбГУ.
`doc/DEVELOPMENT_PROCESS.md` for full workflow.

## Commands

```bash
uv sync                                       # install dependencies (dev + main)
uv run python src/flask_se.py                 # run dev server (http://127.0.0.1:5000)
uv run python src/flask_se.py init            # initialize database
uv run python src/wsgi.py                     # run via WSGI
uv run pytest                                 # run tests (parallel -n 2)
uv run ruff check src/                        # lint
uv run ruff format src/                       # format
uv export --no-dev --no-hashes > requirements.txt  # update prod requirements (PowerShell: use `[System.IO.File]::WriteAllText("requirements.txt", $(uv export --no-dev --no-hashes), [System.Text.UTF8Encoding]::new($false))` to avoid BOM)
```

```
Run these BEFORE any commit — CI runs them and will fail:
  uv run mdformat .          # all markdown files (CI runs --check on Linux)
  uv run ruff format src/    # Python files
  uv run ruff check src/     # Python lint (pre-commit also runs this)

Then:
  git add && git commit (hooks auto-run) → git push

After staging merge: verify CI is green before further work.
```

## Quirks & Gotchas

- **Python**: 3.9 (production), 3.13 (dev tooling, pinned in `.python-version`)
- **Dependency mgmt**: `uv` for dev, `pip` for prod — see `doc/ARCHITECTURE.md` Design Decisions
- **Main branch**: `current` (not `main`)
- **Database**: SQLite (`se.db`), initialized via `flask_se.py init`
- **Config files**: `flask_se_secret.conf`, `flask_se_mail.conf`, `flask_se_practice_yandex_secret.conf` — never committed
- **Docker**: `docker-compose.yml` for Flask + nginx; `Dockerfile` uses uWSGI
- **Session start**: see `doc/GIT_FLOW.md` §3 — before any work, sync staging, check for orphaned WIP. Quick reference: `git fetch --prune origin → git status → git checkout staging && git pull --ff-only origin staging → git log --oneline origin/staging ^origin/current → git checkout -b <prefix>/<name>`
- **Planning phase first** — no code without prior user discussion and approval
- **Staging is mandatory** — all branches merge to `staging` first, never directly to `main`
- **Plan mode: NO git writes** — in plan mode, only `git log`, `git status`, `git diff`, `git branch` are allowed. No `reset`, `checkout -b`, `add`, `commit`, `merge`, `push`, `tag`.
- **Auto-mode branching**: in unattended/batch mode, branch `staging-auto-<UTC-timestamp>` from staging — never commit to staging directly, never merge the branch, retrospective + report commit before handoff. Later squash-merged to staging. Non-auto staging merges require GPG signoff.
- **Tool source of truth**: Python tools via `uv` (pyproject.toml `[dependency-groups]`), non-Python tools via pre-commit repo hooks — see `doc/DEVELOPMENT_PROCESS.md` §0.7

See `doc/GIT_FLOW.md` section 3 for the session start ritual.

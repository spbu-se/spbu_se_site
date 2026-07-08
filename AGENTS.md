# SE Site

<!-- encoding: utf-8 -->

Сайт кафедры системного программирования СПбГУ.
`docs/DEVELOPMENT_PROCESS.md` for full workflow. `docs/GIT_FLOW.md` for branching.
`docs/TESTING.md` for testing strategy.

Available skills: `docs/OPENSE_CONFIG.md` §3 lists all `.skills/<name>/` workflows.
Load the matching skill before starting a task (`skill` tool).

Every line must answer: "Would an agent likely miss this without help?" If not, cut it.
CLAUDE.md defers to this file. This file defers to `docs/`.

## Pre-flight checklist (auto/batch mode)

- `git fetch --prune origin`
- Check `origin/staging` CI — if red, stop and fix first
- Branch: `git checkout -b staging-auto-<UTC-ts> origin/staging`
- Never commit to `staging`
- If `git config commit.gpgsign` is true, use `--no-gpg-sign` on every commit
- Before writing piped/chained commands, read `.tooling.md` §PowerShell 5.1

## Before committing

```powershell
uv run mdformat docs/ AGENTS.md CLAUDE.md README.md TODO.md .skills/ .opencode/commands/ .claude/ .agents/
uv run ruff format src/
uv run ruff check src/
uv run pytest -n 2
```

Also verify `requirements.txt` is fresh (CI uses pip, not uv):

See `.tooling.md` §"UTF-8 BOM in requirements.txt" for the correct PowerShell command — the `$(...)` subexpression flattens multi-line output to a single line.

## Testing quirks

- **Whoosh not thread-safe** — pytest-xdist limited to `-n 2`, each worker needs its own index dir
- **No Flask factory** — `app` is a module-level global. Patch configs BEFORE `from flask_se import app`
- **scrypt unsupported on Python 3.13** — conftest.py mocks `check_password_hash` at module level
- **APScheduler fires in tests** — `scheduler.shutdown(wait=False)` called at conftest module level
- **Session-scoped DB template** — `_seeded_db_path` fixture creates + seeds once; per-test fixtures copy it (~ms)
- **Login bypass fixture** — `logged_client` injects `session["_user_id"]` instead of POST login (avoids scrypt)

## Environment quirks

- **Python**: 3.13 dev (`.python-version`), 3.9 prod (Dockerfile)
- **Dep management**: `uv` for dev, `pip install -r requirements.txt` for prod/CI
- **Main branch**: `current` (not `main`)
- **Database**: SQLite (`se.db`), init via `uv run python src/flask_se.py init`
- **Config files** (never committed): `flask_se_secret.conf`, `flask_se_mail.conf`, `flask_se_practice_yandex_secret.conf`
- **Docker**: uWSGI-based Flask container + nginx (docker-compose.yml)
- **requirements.txt staleness** — CI runs `pip install -r` on every push. Must match `uv.lock`. Always regenerate before pushing
- **mdformat CI vs local** — CI uses Linux (LF). Always run `uv run mdformat ...` (not `--check`) before committing on Windows
- **PowerShell encoding** — `Set-Content` defaults to Windows-1252. Use `[System.IO.File]::WriteAllText` for UTF-8
- **Encoding declarations**: every `.py` needs `# -*- coding: utf-8 -*-` on line 1, every `.md` needs `<!-- encoding: utf-8 -->` on line 2
- **GPG keylocker** — if signingkey is set, `git commit` hangs waiting for unlock. Always use `--no-gpg-sign` on feature/auto branches
- **`git config commit.gpgsign`** — check this first; if true, never commit without `--no-gpg-sign`

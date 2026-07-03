# SE Site

Сайт кафедры системного программирования СПбГУ.
`doc/DEVELOPMENT_PROCESS.md` for full workflow.

## Commands

```bash
pip install -r requirements.txt              # install dependencies
python src/flask_se.py                       # run dev server (http://127.0.0.1:5000)
python src/flask_se.py init                  # initialize database
python src/wsgi.py                           # run via WSGI
pytest                                       # run tests
ruff check src/                              # lint
ruff format src/                             # format
```

Commit sequence: `format → git add && git commit (hooks auto-run) → test`.

## Quirks & Gotchas

- **Python**: 3.9 (production), 3.13 (dev tooling)
- **Main branch**: `current` (not `main`)
- **Database**: SQLite (`se.db`), initialized via `flask_se.py init`
- **Config files**: `flask_se_secret.conf`, `flask_se_mail.conf`, `flask_se_practice_yandex_secret.conf` — never committed
- **Docker**: `docker-compose.yml` for Flask + nginx; `Dockerfile` uses uWSGI
- **Session start**: see `doc/GIT_FLOW.md` §3 — before any work, sync main, check for orphaned WIP
- **Planning phase first** — no code without prior user discussion and approval
- **Staging is mandatory** — all branches merge to `staging` first, never directly to `main`
- **Plan mode: NO git writes** — in plan mode, only `git log`, `git status`, `git diff`, `git branch` are allowed. No `reset`, `checkout -b`, `add`, `commit`, `merge`, `push`, `tag`.

See `doc/GIT_FLOW.md` section 3 for the session start ritual.

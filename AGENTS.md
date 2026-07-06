# SE Site

<!-- encoding: utf-8 -->

РЎР°Р№С‚ РєР°С„РµРґСЂС‹ СЃРёСЃС‚РµРјРЅРѕРіРѕ РїСЂРѕРіСЂР°РјРјРёСЂРѕРІР°РЅРёСЏ РЎРџР±Р“РЈ.
`doc/DEVELOPMENT_PROCESS.md` for full workflow.

## Pre-flight checklist (auto/batch mode)

Before writing ANY code in auto/batch mode:

- [ ] `git fetch --prune origin` — sync remote
- [ ] Check `origin/staging` CI status — if red, stop and fix first
- [ ] Record start UTC timestamp
- [ ] Create branch: `git checkout -b staging-auto-<UTC-ts> origin/staging`
- [ ] Load relevant skills: `uv run pre-commit run --all-files` to verify hooks work, then load `.skills/<name>/` for the task
- [ ] Never commit to `staging` — all work goes to the auto-branch
- [ ] Never trust memory — encode every finding in docs

Before committing:

- [ ] Run `uv run pytest -n 2` — full suite must pass
- [ ] Run `uv run ruff check src/ && uv run ruff format --check src/`
- [ ] Run `uv run mdformat --check docs/ AGENTS.md CLAUDE.md README.md TODO.md .opencode/commands/`
- [ ] Run `uv run pre-commit run --all-files` — parity with CI
- [ ] Check for secrets in staged files — if any real secret found, DO NOT PUSH
- [ ] Verify `requirements.txt` is fresh

After push to auto-branch:

- [ ] Wait for CI (staging) to complete
- [ ] If CI red → fix before any further work
- [ ] Compile retrospective report (start time, branch, outcomes, bugs found)

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
Run these BEFORE any commit вЂ” CI runs them and will fail:
  uv run mdformat .          # all markdown files (CI runs --check on Linux)
  uv run ruff format src/    # Python files
  uv run ruff check src/     # Python lint (pre-commit also runs this)

Before pushing to remote, simulate CI locally:
  uv run mdformat --check . && uv run ruff format --check src/ && uv run ruff check src/

Also verify requirements.txt is fresh (serviceability.yml uses pip, not uv):
  uv run python -c "import subprocess; r=subprocess.run(['uv','export','--no-dev','--no-hashes'],capture_output=True,text=True); r.check_returncode(); open('requirements.txt','w',encoding='utf-8',newline='\n').write(r.stdout)"
  (PowerShell: use the above — `uv export > file` and `[IO.File]::WriteAllText` both corrupt output with stderr or flatten newlines)

Then:
  git add && git commit (hooks auto-run) в†’ git push

After staging merge: verify CI is green before further work.
```

## Quirks & Gotchas

- **Python**: 3.9 (production), 3.13 (dev tooling, pinned in `.python-version`)
- **Dependency mgmt**: `uv` for dev, `pip` for prod вЂ” see `doc/ARCHITECTURE.md` Design Decisions
- **Main branch**: `current` (not `main`)
- **Database**: SQLite (`se.db`), initialized via `flask_se.py init`
- **Config files**: `flask_se_secret.conf`, `flask_se_mail.conf`, `flask_se_practice_yandex_secret.conf` вЂ” never committed
- **Docker**: `docker-compose.yml` for Flask + nginx; `Dockerfile` uses uWSGI
- **Session start**: see `doc/GIT_FLOW.md` В§3 вЂ” before any work, sync staging, check for orphaned WIP. Quick reference: `git fetch --prune origin в†’ git status в†’ git checkout staging && git pull --ff-only origin staging в†’ git log --oneline origin/staging ^origin/current в†’ git checkout -b <prefix>/<name>`
- **Planning phase first** вЂ” no code without prior user discussion and approval
- **Staging is mandatory** вЂ” all branches merge to `staging` first, never directly to `main`
- **Plan mode: NO git writes** вЂ” in plan mode, only `git log`, `git status`, `git diff`, `git branch` are allowed. No `reset`, `checkout -b`, `add`, `commit`, `merge`, `push`, `tag`.
- **Auto-mode branching**: in unattended/batch mode, branch `staging-auto-<UTC-timestamp>` from staging вЂ” never commit to staging directly, never merge the branch, retrospective + report commit before handoff. Later squash-merged to staging. Non-auto staging merges require GPG signoff.
- **Tool source of truth**: Python tools via `uv` (pyproject.toml `[dependency-groups]`), non-Python tools via pre-commit repo hooks вЂ” see `doc/DEVELOPMENT_PROCESS.md` В§0.7
- **CI pitfall вЂ” requirements.txt staleness**: `serviceability.yml` runs `pip install -r requirements.txt` on EVERY push to ANY branch. If `requirements.txt` doesn't match current `uv.lock`, it fails. Always run `uv export --no-dev --no-hashes > requirements.txt` before pushing.
- **mdformat CI vs local**: CI uses Linux which formats markdown differently (LF vs CRLF). Always run `uv run mdformat .` (not just `--check`) before committing to ensure files are in CI-compatible format.
- **Encoding audit**: See `.skills/encoding-audit/README.md` — detect and fix non-UTF-8 encoding on Windows.
- **Flask test patterns**: See `.skills/flask-test-patterns/README.md` — reusable fixtures for Flask + SQLAlchemy + xdist tests.

See `doc/GIT_FLOW.md` section 3 for the session start ritual.

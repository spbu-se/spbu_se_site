# TOOLING

Portable tooling knowledge reusable across projects.
Not local host quirks (see `.tooling.md`) and not project-specific errors (see `doc/TROUBLESHOOTING.md`).

## uv

### Universal lockfile resolution
`uv lock` resolves for ALL platforms by default. If a dependency is source-only and can't build on one platform, `uv lock` fails even with platform markers. **Remove such deps from pyproject.toml entirely** and install separately (e.g., in Dockerfile).

### Cross-platform export differences
`uv export` output differs between platforms — wheel comment hashes for platform-specific packages (e.g., `msgpack`, `cachecontrol`) vary. CI checks that `diff` the exported output against a committed file are inherently fragile.

### Build artifacts
If `[build-system]` is present, `uv sync` builds the project and creates `*.egg-info/` directories. Add to `.gitignore`.

### First pre-commit run
`uv run pre-commit run --all-files` downloads environments on first run (2-3 min). Pre-warm with:
```bash
uv run pre-commit install --install-hooks
```

## pytest + SQLAlchemy

### Flask app test setup (no factory pattern)
When the app uses module-level globals (no `create_app()` factory), monkeypatch configs BEFORE importing the app:

```python
import flask_se_config
flask_se_config.SQLITE_DATABASE_NAME = "test.db"
from flask_se import app, db
```

This works because `flask_se` reads the config values at import time. Any imports triggered by `flask_se` (auth libs, scheduler) also see the patched values.

### Per-test temp directories
Each test fixture that needs a database must create its own `tempfile.mkdtemp()`. Shared global paths cause cross-test pollution — one test's teardown breaks the next test's setup.

### NamedTemporaryFile on Linux
`tempfile.NamedTemporaryFile` on Linux keeps the file descriptor open. SQLAlchemy gets "attempt to write a readonly database" on CREATE TABLE. Always use `tempfile.mkdtemp()` and let SQLAlchemy create the `.db` file.

### Engine caching
Changing `app.config["SQLALCHEMY_DATABASE_URI"]` after the app is initialized requires `db.engine.dispose()` before `db.create_all()`. Without it, the old engine is reused.

## pre-commit

### Hook ordering
Run formatters before linters. `ruff-format` before `ruff check --fix` avoids formatting-then-linting false positives.

### System hooks
`language: system` hooks run whatever is on PATH. Use `uv run <tool>` as the entry point to ensure the project's venv version is used.

### First run performance
First invocation downloads and caches hook environments. Install hooks early to make repeated runs fast.

## GitHub CLI

```bash
# Quick CI status on a branch
gh run list --branch staging --json status,conclusion,databaseId

# Only failed steps
gh run view <run-id> --log-failed

# Block until complete
gh run watch <run-id>

# Get latest run ID as a variable
gh run list --branch staging --limit 1 --json databaseId --jq ".[0].databaseId"
```

## Ruff

### Unsafe fixes
`--unsafe-fixes` enables rules that safe mode skips:
- E722 — bare `except`
- E711 — `!= None` comparison  
- F841 — unused variable assignment

Run: `ruff check --fix --unsafe-fixes`

### Target version
Set `target-version` in `[tool.ruff]` to match minimum supported Python. Affects which syntax is flagged as invalid.

## General

### Never use pip._vendor
Importing from `pip._vendor` is fragile — it depends on pip being installed and its internal structure being stable. Always install vendored packages as explicit dependencies.

### Generated artifact diff fragility
`diff` on generated files (requirements.txt, lockfiles) across platforms is unreliable. Comments and platform-specific hashes differ. Prefer CI checks that tolerate minor variations, or run the generation step in CI to verify consistency.

### Coverage exclusions
Exclude scripts that run once (importers, migrations) from coverage for realistic metrics:
```toml
[tool.coverage.run]
omit = ["src/thesesImport.py", "src/migrations/*"]
```

## Commits & GPG

### Signoff policy pattern
Regular commits to staging/feature branches don't need signoff — only merge commits to production. This avoids GPG agent timeouts when password storage is locked.

### Never touch global git config
Global git options (`git config --global`) are user-specific and should never be modified by automation without explicit user approval.

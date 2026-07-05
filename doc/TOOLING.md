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

### Windows SQLite URI path format

On Windows, SQLite URIs with forward slashes (`sqlite:///C:/Users/.../test.db`) silently fail — `db.create_all()` does NOT create the file and raises no error. Use backslash paths from `str(Path() / ...)` instead:

```python
# Works on all platforms:
_p = str(Path(_dir) / "test.db")
uri = f"sqlite:///{_p}"

# Does NOT work on Windows (silent failure):
_p = Path(_dir).as_posix() + "/test.db"
uri = f"sqlite:///{_p}"
```

### Engine caching

Changing `app.config["SQLALCHEMY_DATABASE_URI"]` after the app is initialized requires replacing the cached engine directly. `db.engine.dispose()` alone does NOT reset the cached engine — it only disposes the connection pool.

**Correct pattern:**

```python
from sqlalchemy import create_engine

app.config["SQLALCHEMY_DATABASE_URI"] = new_uri
db.engines[None] = create_engine(new_uri)
```

This replaces the engine in Flask-SQLAlchemy's internal engine cache, so subsequent calls to `db.engine`, `db.create_all()`, etc. use the new URI.

### Test data seeding is slow

Seeded DB tests (`init_db()`) take 10-15s each due to seed data insertion. Mitigate by creating a session-scoped template and copying it per test:

```python
@pytest.fixture(scope="session")
def _seeded_db_path():
    ...  # create + seed once
    yield _p

@pytest.fixture
def seeded_client(_seeded_db_path):
    _p = str(Path(_dir) / _db_name)
    shutil.copy2(_seeded_db_path, _p)
    uri = "sqlite:///" + _p
    app.config["SQLALCHEMY_DATABASE_URI"] = uri
    db.engines[None] = create_engine(uri)
    ...
```

### Login-required test fixture (session injection)

When testing `@login_required` routes and the password hash is unavailable (e.g., scrypt unsupported on Python 3.13), inject the user ID directly into the Flask session instead of going through the login POST:

```python
@pytest.fixture
def logged_client(seeded_client):
    from se_models import Users
    u = Users.query.first()
    with seeded_client.session_transaction() as sess:
        sess["_user_id"] = str(u.id)
    return seeded_client
```

This works because Flask-Login reads `session["_user_id"]` on every request to load the current user via `user_loader`.

## pytest config

`pytest` reads `[tool.pytest.ini_options]` from `pyproject.toml` directly — no separate `pytest.ini` or `setup.cfg` needed.

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

### Never use pip.\_vendor

Importing from `pip._vendor` is fragile — it depends on pip being installed and its internal structure being stable. Always install vendored packages as explicit dependencies.

### Generated artifact diff fragility

`diff` on generated files (requirements.txt, lockfiles) across platforms is unreliable. Comments and platform-specific hashes differ. Prefer CI checks that tolerate minor variations, or run the generation step in CI to verify consistency.

### Coverage exclusions

Exclude scripts that run once (importers, migrations) from coverage for realistic metrics:

```toml
[tool.coverage.run]
omit = ["src/thesesImport.py", "src/migrations/*"]
```

## Commit signing

Signoff policy is defined in `doc/GIT_FLOW.md §4`. This doc only adds cross-cutting notes.

### Never touch global git config

Global git options (`git config --global`) are user-specific and should never be modified by automation without explicit user approval.

## pytest-xdist + Whoosh

Whoosh indexes are not thread-safe. Using `pytest-xdist -n auto` causes sporadic `LockError` or `EmptyIndexError` because multiple workers share the same index directory. Fix: use `-n 2` (proven stable) and set a per-worker temp dir in conftest.py:

```python
_whoosh_dir = tempfile.mkdtemp()
app.config["WHOOSHEE_DIR"] = _whoosh_dir
```

This ensures each worker process gets its own Whoosh index. Still insufficient for tests that create new DB state and then trigger Whoosh queries — the index must be rebuilt via `whooshee.reindex()` after each DB change.

## Scrypt mock for tests on Python 3.13+

Python 3.13 OpenSSL builds may lack scrypt support, causing `check_password_hash` to raise `ValueError: unsupported hash type scrypt`. Mock at conftest module level before any auth module is imported:

```python
import werkzeug.security as _ws
_ws.check_password_hash = lambda pwhash, password: True
_ws.generate_password_hash = lambda password, method="pbkdf2:sha256": f"mock:{password}"
```

This is safe for testing view logic and route behavior, but means password security logic is never exercised in tests.

## APScheduler shutdown in tests

`Flask-APScheduler` starts background jobs at import time (every 10 seconds for `SendMailNotification`). During tests, these jobs fire against the test DB which may not have the `notification` table, causing `sqlite3.OperationalError: no such table: notification`. Shut down at conftest module level:

```python
import flask_se as _fs
_fs.scheduler.shutdown(wait=False)
```

## pytest config in pyproject.toml

`pytest` reads `[tool.pytest.ini_options]` from `pyproject.toml` directly — no separate `pytest.ini` or `setup.cfg` needed.

## pre-commit

### Hook ordering

Run formatters before linters. `ruff-format` before `ruff check --fix` avoids formatting-then-linting false positives.

### System hooks

`language: system` hooks run whatever is on PATH. Use `uv run <tool>` as the entry point to ensure the project's venv version is used.

### First run performance

First invocation downloads and caches hook environments. Install hooks early to make repeated runs fast.

## GitHub CLI

### Retrospective — Windows SQLite URI path format undocumented

After introducing a session-scoped seeded DB template, the `Path.as_posix()` URI format silently failed on Windows — `db.create_all()` raised no error but didn't create the file. The fix (`str(Path() / ...)`) was applied directly to `conftest.py` but never extracted as a documented quirk. A later retro session identified the gap and added the note above.

**What went wrong**: The fix was code-only — no doc entry was created even though the issue (Windows path format) is a portable tooling knowledge item that affects all Windows developers.

**Root cause**: Missing convention — agent applied a fix but didn't create the corresponding doc note because the retrospective hadn't been run yet. The retro skill didn't require retro entries for every gap found.

**Fix**: Added the Windows SQLite URI path format section above. Updated the retrospective-analysis skill §7 to require that every classified gap gets a retrospective entry, even if the fix was applied directly.

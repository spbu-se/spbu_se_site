# TOOLING

<!-- encoding: utf-8 -->

Portable tooling knowledge reusable across projects.
Not local host quirks (see `.tooling.md`) and not project-specific errors (see `docs/TROUBLESHOOTING.md`).

## uv

### Universal lockfile resolution

`uv lock` resolves for ALL platforms by default. If a dependency is source-only and can't build on one platform, `uv lock` fails even with platform markers. **Remove such deps from pyproject.toml entirely** and install separately (e.g., in Dockerfile).

### Cross-platform export differences

`uv export` output differs between platforms вЂ” wheel comment hashes for platform-specific packages (e.g., `msgpack`, `cachecontrol`) vary. CI checks that `diff` the exported output against a committed file are inherently fragile.

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

Each test fixture that needs a database must create its own `tempfile.mkdtemp()`. Shared global paths cause cross-test pollution вЂ” one test's teardown breaks the next test's setup.

### NamedTemporaryFile on Linux

`tempfile.NamedTemporaryFile` on Linux keeps the file descriptor open. SQLAlchemy gets "attempt to write a readonly database" on CREATE TABLE. Always use `tempfile.mkdtemp()` and let SQLAlchemy create the `.db` file.

### Windows SQLite URI path format

On Windows, SQLite URIs with forward slashes (`sqlite:///C:/Users/.../test.db`) silently fail вЂ” `db.create_all()` does NOT create the file and raises no error. Use backslash paths from `str(Path() / ...)` instead:

```python
# Works on all platforms:
_p = str(Path(_dir) / "test.db")
uri = f"sqlite:///{_p}"

# Does NOT work on Windows (silent failure):
_p = Path(_dir).as_posix() + "/test.db"
uri = f"sqlite:///{_p}"
```

### Engine caching

Changing `app.config["SQLALCHEMY_DATABASE_URI"]` after the app is initialized requires replacing the cached engine directly. `db.engine.dispose()` alone does NOT reset the cached engine вЂ” it only disposes the connection pool.

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

### Hook listing

The following hooks block obvious garbage (defined in `.pre-commit-config.yaml`):

| Hook | Blocks |
|---|---|
| `check-added-large-files` | Files > 500 KB |
| `check-case-conflict` | Case conflicts on case-insensitive FS |
| `check-json` / `check-yaml` | Invalid syntax in structured files |
| `commitlint` | Non-conventional commit messages |

### Hook ordering

Run formatters before linters. `ruff-format` before `ruff check --fix` avoids formatting-then-linting false positives.

### System hooks

`language: system` hooks run whatever is on PATH. Use `uv run <tool>` as the entry point to ensure the project's venv version is used.

### First run performance

First invocation downloads and caches hook environments. Install hooks early to make repeated runs fast.

### CLI conciseness

When a CLI option or path is implied by another option or glob, omit the redundant part. A directory path covers all files within it; listing a child file explicitly is noise. Keep commands short and clear — every redundant token distracts from the real structure.

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

### Diagnosis: mdformat failure with truncated path

When CI mdformat fails and the filename is truncated in logs, use:

```powershell
gh run view <run-id> --log | Select-String -Pattern "not formatted" -Context 0,1
```

## Ruff

### N801 (class name convention) suppressed for tests

`pyproject.toml` has `"tests/*.py" = ["N801"]` — test class names don't need to follow PascalCase conventions (e.g., `test_basic_auth` as a class is acceptable). This is intentional: test classes often describe scenarios rather than being named after the class under test.

### Unsafe fixes

`--unsafe-fixes` enables rules that safe mode skips:

- E722 — bare `except`
- E711 — `!= None` comparison
- F841 — unused variable assignment

Run: `ruff check --fix --unsafe-fixes`

### Target version

Set `target-version` in `[tool.ruff]` to match minimum supported Python. Affects which syntax is flagged as invalid.

## lxml dependency for BeautifulSoup HTML parsing

`lxml>=6.1.1` is a dev dependency in `pyproject.toml` (`[dependency-groups] dev`). It's required for BeautifulSoup HTML parser tests (`features="lxml"`) in scrape tests under `test_theses_import.py`. The built-in `html.parser` is too lenient — it doesn't raise on malformed HTML that triggers different code paths.

## General

### Never use pip.\_vendor

Importing from `pip._vendor` is fragile вЂ” it depends on pip being installed and its internal structure being stable. Always install vendored packages as explicit dependencies.

### Generated artifact diff fragility

`diff` on generated files (requirements.txt, lockfiles) across platforms is unreliable. Comments and platform-specific hashes differ. Prefer CI checks that tolerate minor variations, or run the generation step in CI to verify consistency.

### Coverage exclusions

Exclude scripts that run once (importers, migrations) from coverage for realistic metrics:

```toml
[tool.coverage.run]
omit = ["src/thesesImport.py", "src/migrations/*"]
```

## Commit signing

Signoff policy is defined in `docs/GIT_FLOW.md §4`. This doc only adds cross-cutting notes.

### Never touch global git config

Global git options (`git config --global`) are user-specific and should never be modified by automation without explicit user approval.

### Auto-branch commits: disable GPG signoff

Auto/batch mode branches (`staging-auto-*`) must use `--no-gpg-sign` — they are throwaway branches that are squash-merged and never appear as individual commits in permanent history.

```bash
git commit --no-gpg-sign -m "..."
```

## pytest-xdist + Whoosh

Whoosh indexes are not thread-safe. Using `pytest-xdist -n auto` causes sporadic `LockError` or `EmptyIndexError` because multiple workers share the same index directory. Fix: use `-n 2` (proven stable) and set a per-worker temp dir in conftest.py:

```python
_whoosh_dir = tempfile.mkdtemp()
app.config["WHOOSHEE_DIR"] = _whoosh_dir
```

This ensures each worker process gets its own Whoosh index. Still insufficient for tests that create new DB state and then trigger Whoosh queries вЂ” the index must be rebuilt via `whooshee.reindex()` after each DB change.

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

## PowerShell encoding

See `.skills/encoding-audit/README.md` for detection scripts, git recovery workflow, fix patterns, and encoding declaration templates.

### `Set-Content` / `Out-File` default to Windows-1252 on en-US systems

PowerShell's `Set-Content` and `Out-File` cmdlets default to the system's active ANSI code page (Windows-1252 on en-US Windows), NOT UTF-8. This corrupts any file containing non-ASCII characters when the file is expected to be UTF-8.

```powershell
# WRONG — writes Windows-1252
Set-Content -Path file.md -Value $content

# WRONG — also Windows-1252
$content > file.md

# WRONG — also Windows-1252
Out-File -FilePath file.md -InputObject $content

# CORRECT — writes UTF-8 without BOM
[System.IO.File]::WriteAllText($path, $content, [System.Text.UTF8Encoding]::new($false))

# CORRECT — reads UTF-8
[System.IO.File]::ReadAllText($path, [System.Text.Encoding]::UTF8)

# CORRECT — writes bytes as UTF-8
[System.IO.File]::WriteAllBytes($path, [System.Text.Encoding]::UTF8.GetBytes($content))
```

**Applies to**: Any `.py`, `.md`, `.yaml`, `.json`, `.toml`, `.cfg` file — anything that should be UTF-8.

### `Get-Content` with `-Raw` still defaults to Windows-1252

Even `Get-Content -Path file.md -Raw` uses Windows-1252. Always use the .NET overload.

### `$(...)` subexpression flattens multi-line output to space-joined string

`$(command)` in PowerShell captures stdout as an **array of strings** (one per line). When passed to a function expecting a `string` (like `WriteAllText`), PowerShell joins the array with **spaces** — collapsing all lines into one.

This corrupts files like `requirements.txt` that must retain line breaks:

```powershell
# WRONG — collapses to single line
[System.IO.File]::WriteAllText("requirements.txt", $(uv export --no-dev --no-hashes), [System.Text.UTF8Encoding]::new($false))

# CORRECT — capture as array, join explicitly
$lines = uv export --no-dev --no-hashes 2>($null)
[System.IO.File]::WriteAllText("requirements.txt", ($lines -join "`r`n"), [System.Text.UTF8Encoding]::new($false))
```

This quirk does NOT apply when the output is a single line (no `\n` in the captured text). Always verify multi-line output with `($content).GetType()` before passing to a string parameter.

**See also**: `.tooling.md` §UTF-8 BOM in requirements.txt for the complete pattern.

### mdformat doesn't show file path on UnicodeDecodeError

When `uv run mdformat .` encounters a non-UTF-8 file, the error message omits the file path. To find the offending file:

```powershell
Get-ChildItem -Recurse -Include "*.md" | ForEach-Object {
    try { $null = [System.Text.UTF8Encoding]::UTF8.GetString([System.IO.File]::ReadAllBytes($_.FullName)) }
    catch { Write-Host $_.FullName }
}
```

### Encoding declaration policy

See `docs/DOCS.md §6` for the project's encoding declaration policy.

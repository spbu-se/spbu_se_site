# Troubleshooting

<!-- encoding: utf-8 -->

Common errors, root causes, and fixes encountered during development.

## APScheduler: background jobs fire during tests

**When:** Running pytest вЂ” `SendMailNotification` fires every 10s against the test DB.
**Cause:** `Flask-APScheduler` auto-starts at import time. Background jobs see the test DB with no tables.
**Fix:** Set `app.config["TESTING"] = True` before yielding the test client, or disable the scheduler in test fixtures.

## init_db: crashes on second call

**When:** Calling `init_db()` twice in the same test.
**Cause:** `init_db()` runs `db.session.commit()` before `db.drop_all()`. If the session has expired objects from the first call, the flush crashes.
**Fix:** Call `db.session.remove()` before the second `init_db()` call.

## Whooshee: creates index directory in CWD

**When:** Running any Whooshee-enabled query (thesis search).
**Cause:** Whooshee creates its index at the configured path relative to CWD at query time.
**Effect:** `whooshee/` directory appears at project root. Already in `.gitignore`.

## VK/Google OAuth: import crashes with missing deps

**When:** Importing `flask_se_auth` without all OAuth dependencies installed.
**Cause:** OAuth libraries are imported at module level. `vk_api` or `google_auth_oauthlib` failures propagate up.
**Fix:** Ensure all OAuth deps are in `pyproject.toml`. During testing, the monkeypatch in `conftest.py` must happen before any `from flask_se import` line.

## SQLite: "attempt to write a readonly database"

**When:** CI (Linux) test fixtures try to `CREATE TABLE`.
**Cause:** `tempfile.NamedTemporaryFile` keeps the fd open вЂ” SQLAlchemy engine can't write.
**Fix:** Use `tempfile.mkdtemp()` instead; let SQLAlchemy create the `.db` file.

## SQLite: "no such table: notification"

**When:** APScheduler fires `SendMailNotification` during tests.
**Cause:** Scheduler started during app init; runs on the test's temp DB which has no tables yet.
**Fix:** Ensure scheduler is stopped in test teardown or use `TESTING` config.

## Password hashing: "unsupported hash type scrypt"

**When:** `check_password_hash` on Python 3.13.
**Cause:** OpenSSL build of Python 3.13 doesn't include scrypt support.
**Fix:** Skip password-verification tests, or use a different hash algorithm in dev config.

## pip install: "UnicodeDecodeError: 'utf-16-le'"

**When:** `pip install -r requirements.txt` on Linux CI.
**Cause:** `requirements.txt` written with UTF-8 BOM on Windows.
**Fix:** Use `[System.IO.File]::WriteAllText()` with `UTF8Encoding($false)` to omit BOM.

## Flask: SECRET_KEY is a file path string

**When:** `flask_se_secret.conf` doesn't exist.
**Cause:** `SECRET_KEY` is set to the config file path, not its contents.
**Effect:** App still works (any string works as a key). Not a bug.

## Coverage metrics accumulate across runs

**When:** Running `pytest --cov` multiple times.
**Cause:** `.coverage` file appends data, not replaces. Subsequent runs include old data.
**Fix:** Delete `.coverage` before each session, or use `coverage erase`.

## Restoring vendor files bypassing hooks

**When:** Formatters (trailing-whitespace, dprint) modify vendor/static files.
**Fix:** `git checkout HEAD -- path/to/dir` restores files and bypasses pre-commit hooks entirely вЂ” no need to disable hooks.

## uv lock fails with "No solution found"

**When:** Adding a new dependency with `requires-python` constraints.
**Cause:** `pyproject.toml` `requires-python` includes versions the dep doesn't support.
**Fix:** Run `uv lock --python <version>` or narrow `requires-python`.

## uv sync: "Failed to build uwsgi"

**When:** `uwsgi` is in `pyproject.toml` dependencies on Windows.
**Cause:** uWSGI is source-only, uses Unix-only `os.uname()`.
**Fix:** Remove from pyproject; install via `RUN pip install uwsgi` in Dockerfile only.

## None.strip() AttributeError on missing form fields

**When:** POST request to a form handler without all expected fields.
**Cause:** `request.form.get("field_name")` returns `None` when the field is absent from the form data. Calling `.strip()` on `None` raises `AttributeError`.
**Fix:** Replace `.get("field_name").strip()` with `.get("field_name", "").strip()`.
**Known occurrences:** `flask_se_auth.py:197` (register_basic), `flask_se_auth.py:239-242` (user_profile), `flask_se_review.py` (submit_thesis_on_review).

## Whoosh EmptyIndexError in parallel test workers

**When:** Running `pytest -n auto` or `pytest -n N` with `N > 2`.
**Error:** `whoosh.index.EmptyIndexError: Index 'MAIN' does not exist in FileStorage('whooshee\thesis')`.
**Cause:** Whoosh index is created in a shared temp directory. Multiple xdist workers try to access the same index simultaneously. The index may not exist yet when a worker queries it.
**Fix:** Use `-n 2` (stable), ensure `whooshee.reindex()` is called during DB seeding. See `doc/TOOLING.md В§ pytest-xdist + Whoosh`.

## datetime.timezone.UTC vs datetime.timezone.utc

**When:** Using `datetime.timezone.UTC` on Python 3.13.
**Cause:** Python 3.13 removed the deprecated `timezone.UTC` alias. Only `timezone.utc` (lowercase) is available.
**Fix:** Replace `timezone.UTC` with `timezone.utc`.

## Mypy skips analyzing src/ when tests/ is configured

**When:** `pyproject.toml [tool.mypy] files = ["tests/"]` вЂ” mypy only checks listed files. Source files are not checked even if they're imported by tests.
**Cause:** Mypy's `files` option is a whitelist, not a "check these additionally" list.
**Fix:** To check both src and tests, list both: `files = ["src/", "tests/"]`. Use `[[tool.mypy.overrides]] module = "tests.*"` to apply relaxed rules for tests.

## CI mdformat failure: truncated filename in logs

**When:** CI (staging) fails on `mdformat --check` but the log output only shows `Error: File ... is not formatted` — the filename is truncated.

**Cause:** GitHub Actions log lines are wrapped at ~80 characters. The filename is on a separate line from "Error:" and both get captured separately.

**Fix:** Use `Select-String -Context` to see the full path:

```powershell
gh run view <run-id> --log | Select-String -Pattern "not formatted" -Context 0,1
```

Or get the run ID dynamically:

```powershell
$id = gh run list --branch staging --limit 1 --json databaseId --jq ".[0].databaseId"
gh run view $id --log | Select-String -Pattern "not formatted" -Context 0,1
```

**Prevention:** Run `uv run mdformat --check docs/ AGENTS.md CLAUDE.md README.md TODO.md .skills/ .opencode/commands/ .claude/ .agents/` locally before pushing. This uses the same paths as CI.

## linecache returns stale content after file edits

**When:** Using `linecache.getlines()` or `linecache.getline()` to read a Python file that was modified during the same test run.
**Cause:** `linecache` caches file contents on first read and never invalidates the cache unless explicitly told to. File modifications (adding/removing lines) shift line numbers, but `linecache` still returns the pre-modification content.
**Fix:** Use `open().readlines()` directly, or call `linecache.clearcache()` before each read that follows a file modification.

## db.init_app: "already registered" on module-level import

**When:** Importing a module that calls `db.init_app(app)` at module level when `conftest.py`
has already registered the same `db` on the same `app`.

**Error:** `RuntimeError: A 'SQLAlchemy' instance has already been registered on this Flask app.`

**Occurs in:** `thesesImport.py:20` — `from flask_se import app; db.init_app(app)` runs at import time.

**Root cause:** Flask-SQLAlchemy v3 raises when `init_app` is called twice on the same app.
`conftest.py` calls it first via `from flask_se import app, db`. Any later import of `thesesImport`
calls it again.

**Fix for tests:** Patch `init_app` before importing the module:

```python
import flask_sqlalchemy
import contextlib

_orig_init_app = flask_sqlalchemy.SQLAlchemy.init_app

def _patched_init_app(self, app):
    with contextlib.suppress(RuntimeError):
        _orig_init_app(self, app)

with patch.object(flask_sqlalchemy.SQLAlchemy, "init_app", _patched_init_app):
    import thesesImport  # now safe to import
```

## thesesImport: module-level state breaks test isolation

**When:** Writing tests for functions in `thesesImport.py` that share module-level state.

**Symptoms:**

- Tests pass when run individually but fail when run as part of the full suite.
- `TypeError: can only concatenate str (not "NoneType") to str` — caused by `thesesImport.download`
  flag being accidentally left `True` by a previous test.
- `sys.exit` is called by the function under test, terminating the test process.

**Root cause:** `thesesImport.py` has two mutable module-level variables:

1. `download = False` — controls whether `download_file()` actually writes files.
   If a test sets `download = True` and doesn't restore it, subsequent tests that call
   scraper functions will try to write files to disk.
1. Direct calls to `sys.exit()` on error conditions — when mocked with `patch.object(sys, "exit")`,
   the mock prevents process exit but the function continues executing, potentially corrupting
   state for the next test.

**Fix for tests:**

- Always restore `thesesImport.download` after any test that modifies it (use `try/finally`).
- Mock `Users.query`, `Staff.query`, and `db.session` in every test that calls a scraper function.
- Use `app.app_context()` when patching `thesesImport.Users.query` — the model descriptor
  requires an active app context.

**Long-term fix:** Refactor `thesesImport.py` to remove module-level side effects:

- Move `db.app = app; db.init_app(app)` into a function called on demand
- Remove the `download` flag in favor of config injection
- Replace `sys.exit()` with raising a custom exception

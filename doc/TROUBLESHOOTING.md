# Troubleshooting

Common errors, root causes, and fixes encountered during development.

## SQLite: "attempt to write a readonly database"

**When:** CI (Linux) test fixtures try to `CREATE TABLE`.
**Cause:** `tempfile.NamedTemporaryFile` keeps the fd open — SQLAlchemy engine can't write.
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

## uv lock fails with "No solution found"

**When:** Adding a new dependency with `requires-python` constraints.
**Cause:** `pyproject.toml` `requires-python` includes versions the dep doesn't support.
**Fix:** Run `uv lock --python <version>` or narrow `requires-python`.

## uv sync: "Failed to build uwsgi"

**When:** `uwsgi` is in `pyproject.toml` dependencies on Windows.
**Cause:** uWSGI is source-only, uses Unix-only `os.uname()`.
**Fix:** Remove from pyproject; install via `RUN pip install uwsgi` in Dockerfile only.

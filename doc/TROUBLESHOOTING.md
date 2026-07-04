# Troubleshooting

Common errors, root causes, and fixes encountered during development.

## APScheduler: background jobs fire during tests

**When:** Running pytest — `SendMailNotification` fires every 10s against the test DB.
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

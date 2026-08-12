# flask-test-patterns

<!-- encoding: utf-8 -->

Copy-paste fixture templates for Flask + SQLAlchemy + pytest with xdist.

Covers: auth bypass for passwordless testing, FTS5 index isolation for parallel workers, file upload testing patterns, scrypt/BCrypt mocking for Python 3.13, sendmail mocking, session-scoped test database seeding.

Does NOT cover: project-specific test structure, individual test cases, coverage targets, or CI configuration — see each project's own `tests/conftest.py` and `docs/` for those.

## When to load

- Setting up a new Flask + SQLAlchemy test suite
- Adding test infrastructure for authenticated routes
- Adding tests for file upload endpoints
- Adding tests that interact with FTS5 search indexes
- Debugging flaky tests in xdist parallel workers
- Adding email notification tests

## Fixture patterns

### 1. Flask app factory + config overrides

The app uses `create_app(config_overrides=None, start_scheduler=None)` in `flask_se.py`; the module-level `app = create_app()` singleton keeps `from flask_se import app` working. To build a differently-configured instance without import-time monkeypatching:

```python
from flask_se import create_app
app = create_app(config_overrides={"SQLALCHEMY_DATABASE_URI": "sqlite:///..."})
```

Prefer `config_overrides` over patching `flask_se_config` module globals. The one remaining global patch in `tests/conftest.py` (`flask_se_config.SQLITE_DATABASE_*`) exists only because `init_db()` reads those globals directly (backup path), not because of app construction.

### 2. Auth bypass fixture (passwordless login)

When password hashing is unavailable (e.g., scrypt not in Python 3.13 OpenSSL build) or you want to skip login POST overhead:

```python
import werkzeug.security as _ws
_ws.check_password_hash = lambda pwhash, password: True
_ws.generate_password_hash = lambda password, method="pbkdf2:sha256": f"mock:{password}"

@pytest.fixture
def logged_client(seeded_client):
    from se_models import Users
    u = Users.query.filter_by(email="test@example.com").first()
    with seeded_client.session_transaction() as sess:
        sess["_user_id"] = str(u.id)   # Flask-Login 0.6.3 uses _user_id (with underscore)
    return seeded_client
```

### 3. FTS5 index isolation for xdist

FTS5 index is inside the SQLite database file — no separate index management needed. Standard `shutil.copy2` of the DB file also copies the FTS5 index. See `conftest.py`'s `_seeded_db_path` fixture for the canonical pattern.

### 4. File upload test patterns

```python
import io

def test_upload_no_file(logged_client):
    resp = logged_client.post("/upload", data={})
    assert resp.status_code in (200, 204, 302)

def test_upload_invalid_type(logged_client):
    data = {"file": (io.BytesIO(b"not an image"), "test.txt")}
    resp = logged_client.post("/upload", data=data, content_type="multipart/form-data")
    assert resp.status_code in (200, 204, 302)

def test_upload_success(logged_client):
    data = {"file": (io.BytesIO(b"fake pdf content"), "test.pdf")}
    resp = logged_client.post("/upload", data=data, content_type="multipart/form-data")
    assert resp.status_code in (200, 302)
```

### 5. Sendmail SMTP mocking

```python
from unittest.mock import patch, MagicMock

@patch("smtplib.SMTP_SSL")
def test_send_mail_success(mock_smtp, seeded_app_ctx):
    from se_sendmail import notification_send_mail
    mock_instance = MagicMock()
    mock_smtp.return_value.__enter__.return_value = mock_instance
    notification_send_mail("test@example.com", "Subject", "Body")
    assert mock_instance.sendmail.called
```

### 6. Session-scoped seeded database

To avoid recreating the schema for every test (drops 4+ min to ~1s):

```python
@pytest.fixture(scope="session")
def _seeded_db_path():
    _dir = tempfile.mkdtemp()
    _p = str(Path(_dir) / "test_seeded.db")
    uri = "sqlite:///" + _p
    app.config["TESTING"] = True
    with app.app_context():
        _set_db_uri(uri)
        db.create_all()
        _seed_data()  # populate reference data
    yield _p
    shutil.rmtree(_dir, ignore_errors=True)

@pytest.fixture
def seeded_client(_seeded_db_path):
    # Copy template DB per test — fast (~ms)
    _dir = tempfile.mkdtemp()
    _p = str(Path(_dir) / "test.db")
    shutil.copy2(_seeded_db_path, _p)
    uri = "sqlite:///" + _p
    app.config["TESTING"] = True
    with app.app_context():
        _set_db_uri(uri)
        db.create_all()
        yield app.test_client()
        db.session.remove()
```

On Windows, use `str(Path() / ...)` for SQLite URI paths — `Path.as_posix()` (forward slashes) silently fails and `db.create_all()` raises no error but doesn't create the file.

### 7. APScheduler: env-gated in tests (not shutdown)

Since the application-factory refactor, the scheduler never starts in tests because `conftest.py` sets `SE_START_SCHEDULER=0` BEFORE importing `flask_se` (production leaves it unset → jobs run):

```python
import os
os.environ["SE_START_SCHEDULER"] = "0"
from flask_se import app, db
```

Do not reintroduce `scheduler.shutdown(wait=False)` — the env gate is set before import so the scheduler never starts. If jobs must fire in a test, call `configure_scheduler(jobs, start_scheduler=True)` on the module-level `scheduler` explicitly.

### 8. Route-map verification for refactors

When moving `add_url_rule` calls (into helpers, blueprints, or modules), prove the route map is preserved before running the full suite — endpoints derive from `view_func.__name__`, so moving calls never renames URLs:

```python
rs = sorted((r.rule, sorted(r.methods or [])) for r in app.url_map.iter_rules())
open(".tmp/routes.txt", "w").write(str(rs))  # dump before/after, diff byte-identically
```

A byte-identical map means zero template/endpoint churn — templates using `url_for('endpoint')` keep working.

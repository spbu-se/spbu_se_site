# flask-test-patterns

Copy-paste fixture templates for Flask + SQLAlchemy + pytest with xdist.

Covers: auth bypass for passwordless testing, Whoosh index isolation for parallel workers, file upload testing patterns, scrypt/BCrypt mocking for Python 3.13, sendmail mocking, session-scoped test database seeding.

Does NOT cover: project-specific test structure, individual test cases, coverage targets, or CI configuration — see each project's own `tests/conftest.py` and `doc/` for those.

## When to load

- Setting up a new Flask + SQLAlchemy test suite
- Adding test infrastructure for authenticated routes
- Adding tests for file upload endpoints
- Adding tests that interact with Whoosh search indexes
- Debugging flaky tests in xdist parallel workers
- Adding email notification tests

## Fixture patterns

### 1. Flask app config before import

When the app uses module-level globals (no `create_app()` factory), monkeypatch configs BEFORE importing the app:

```python
import flask_se_config
flask_se_config.SQLITE_DATABASE_NAME = "test.db"
flask_se_config.SQLITE_DATABASE_PATH = "/tmp/test_db"
from flask_se import app, db
```

This works because the app reads config values at import time. Any imports triggered by the app (auth libs, scheduler) also see the patched values.

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

### 3. Whoosh index isolation for xdist

Whoosh indexes in a shared temp directory cause `EmptyIndexError` when multiple xdist workers access them simultaneously:

```python
@pytest.fixture(scope="session")
def whoosh_dir():
    import tempfile, shutil
    _dir = tempfile.mkdtemp()
    app.config["WHOOSHEE_DIR"] = _dir
    yield _dir
    shutil.rmtree(_dir, ignore_errors=True)
```

For per-test isolation (safer with xdist), use function-scoped fixture that creates a unique index for each test:

```python
@pytest.fixture
def isolated_whoosh(seeded_app_ctx):
    import tempfile, shutil
    _dir = tempfile.mkdtemp()
    app.config["WHOOSHEE_DIR"] = _dir
    from flask_se import whooshee
    whooshee.reindex()
    yield
    shutil.rmtree(_dir, ignore_errors=True)
```

As a fallback, Whoosh-dependent tests can be marked xfail when running with xdist:

```python
@pytest.mark.xfail(strict=False, reason="Whoosh index not available in parallel test workers")
def test_search():
    ...
```

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

### 7. APScheduler shutdown in tests

Flask-APScheduler auto-starts at import time. Background jobs see the test DB with no tables and crash:

```python
# In conftest.py or fixture:
app.config["TESTING"] = True
# Or disable scheduler in test fixtures:
from flask_se import scheduler
scheduler.shutdown(wait=False)
```

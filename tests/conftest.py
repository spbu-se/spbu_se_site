import shutil
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

_db_dir = None
_db_name = "test.db"
_db_path = None


def _init_db_path():
    global _db_dir, _db_path
    _db_dir = tempfile.mkdtemp()
    _db_path = str(Path(_db_dir) / _db_name)
    import flask_se_config

    flask_se_config.SQLITE_DATABASE_NAME = _db_name
    flask_se_config.SQLITE_DATABASE_PATH = _db_dir


_init_db_path()

import pytest
from sqlalchemy import create_engine

from flask_se import app, db
from se_models import init_db


def _set_db_uri(uri):
    """Set SQLAlchemy URI and reset engine cache."""
    app.config["SQLALCHEMY_DATABASE_URI"] = uri
    db.engines[None] = create_engine(uri)


# Create a single seeded database template once per session
@pytest.fixture(scope="session")
def _seeded_db_path():
    _dir = tempfile.mkdtemp()
    _p = str(Path(_dir) / _db_name)
    uri = "sqlite:///" + _p
    with app.app_context():
        _set_db_uri(uri)
        db.create_all()
        init_db()
        db.session.remove()
    yield _p
    shutil.rmtree(_dir, ignore_errors=True)


@pytest.fixture
def app_ctx():
    _dir = tempfile.mkdtemp()
    _p = str(Path(_dir) / _db_name)
    uri = "sqlite:///" + _p
    with app.app_context():
        _set_db_uri(uri)
        db.create_all()
        yield
        db.session.remove()
        db.drop_all()
    shutil.rmtree(_dir, ignore_errors=True)


@pytest.fixture
def client():
    _dir = tempfile.mkdtemp()
    _p = str(Path(_dir) / _db_name)
    uri = "sqlite:///" + _p
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    with app.app_context():
        _set_db_uri(uri)
        db.create_all()
        yield app.test_client()
        db.session.remove()
        db.drop_all()
    shutil.rmtree(_dir, ignore_errors=True)


@pytest.fixture
def seeded_client(_seeded_db_path):
    """Copy the pre-seeded template DB once per test — fast (~ms)."""
    _dir = tempfile.mkdtemp()
    _p = str(Path(_dir) / _db_name)
    shutil.copy2(str(_seeded_db_path), _p)
    uri = "sqlite:///" + _p
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    with app.app_context():
        _set_db_uri(uri)
        db.create_all()
        yield app.test_client()
        db.session.remove()
        db.drop_all()
    shutil.rmtree(_dir, ignore_errors=True)


@pytest.fixture
def logged_client(seeded_client):
    """Seeded client with logged-in test user. Bypasses login to avoid scrypt hash issues on 3.13."""
    from se_models import Users
    u = Users.query.filter_by(email="a.terekhov@spbu.ru").first()
    with seeded_client.session_transaction() as sess:
        sess["_user_id"] = str(u.id)
    return seeded_client


def assert_ok(client, path, methods=None, data=None, code=None):
    """Helper: GET (or POST) a path, assert status matches."""
    if methods is None:
        methods = {"GET"}
    if code is None:
        code = {200}
    if isinstance(code, int):
        code = {code}
    for method in methods:
        if method == "GET":
            resp = client.get(path)
        elif method == "POST":
            resp = client.post(path, data=data or {})
        assert resp.status_code in code, f"{method} {path}: expected {code}, got {resp.status_code}"


def assert_ok_or_redirect(client, path):
    """GET a path, assert 200 or 302."""
    assert_ok(client, path, code={200, 302})

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

from flask_se import app, db
from se_models import init_db


@pytest.fixture
def app_ctx():
    _dir = tempfile.mkdtemp()
    _p = str(Path(_dir) / _db_name)
    sqlalchemy_uri = f"sqlite:///{_p}"
    with app.app_context():
        app.config["SQLALCHEMY_DATABASE_URI"] = sqlalchemy_uri
        db.engine.dispose()
        db.create_all()
        yield
        db.session.remove()
        db.drop_all()
    shutil.rmtree(_dir, ignore_errors=True)


@pytest.fixture
def client():
    _dir = tempfile.mkdtemp()
    _p = str(Path(_dir) / _db_name)
    sqlalchemy_uri = f"sqlite:///{_p}"
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = sqlalchemy_uri
    app.config["WTF_CSRF_ENABLED"] = False
    with app.app_context():
        db.engine.dispose()
        db.create_all()
        yield app.test_client()
        db.session.remove()
        db.drop_all()
    shutil.rmtree(_dir, ignore_errors=True)


@pytest.fixture
def seeded_client():
    _dir = tempfile.mkdtemp()
    _p = str(Path(_dir) / _db_name)
    sqlalchemy_uri = f"sqlite:///{_p}"
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = sqlalchemy_uri
    app.config["WTF_CSRF_ENABLED"] = False
    with app.app_context():
        db.engine.dispose()
        db.create_all()
        init_db()
        yield app.test_client()
        db.session.remove()
        db.drop_all()
    shutil.rmtree(_dir, ignore_errors=True)

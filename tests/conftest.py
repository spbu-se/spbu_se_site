import sys
import os
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

_fd, _db_path = tempfile.mkstemp(suffix=".db")
os.close(_fd)

import flask_se_config
flask_se_config.SQLITE_DATABASE_NAME = _db_path
flask_se_config.SQLITE_DATABASE_PATH = str(Path(_db_path).parent)

from flask_se import app, db
from se_models import init_db

import pytest


def _setup_db():
    with app.app_context():
        db.create_all()


def _teardown_db():
    try:
        with app.app_context():
            db.session.remove()
            db.drop_all()
    finally:
        try:
            Path(_db_path).unlink(missing_ok=True)
        except PermissionError:
            pass


@pytest.fixture
def app_ctx():
    _setup_db()
    with app.app_context():
        yield
    _teardown_db()


@pytest.fixture
def client():
    _setup_db()
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{_db_path}"
    app.config["WTF_CSRF_ENABLED"] = False
    with app.app_context():
        yield app.test_client()
    _teardown_db()


@pytest.fixture
def seeded_client():
    _setup_db()
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{_db_path}"
    app.config["WTF_CSRF_ENABLED"] = False
    with app.app_context():
        init_db()
        yield app.test_client()
    _teardown_db()

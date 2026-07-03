import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import flask_se_config

flask_se_config.SQLITE_DATABASE_NAME = ":memory:"

import pytest

from flask_se import app, db
from se_models import init_db


@pytest.fixture
def app_ctx():
    with app.app_context():
        yield


@pytest.fixture
def client(app_ctx):
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["WTF_CSRF_ENABLED"] = False
    db.create_all()
    yield app.test_client()
    db.drop_all()


@pytest.fixture
def seeded_client(app_ctx):
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["WTF_CSRF_ENABLED"] = False
    db.create_all()
    init_db()
    yield app.test_client()
    db.drop_all()

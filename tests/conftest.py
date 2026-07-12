# -*- coding: utf-8 -*-
import os
import shutil
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

# Mock scrypt hash before any auth import (Python 3.13 lacks scrypt)
import werkzeug.security as _ws

_ws.check_password_hash = lambda pwhash, password: True
_ws.generate_password_hash = lambda password, method="pbkdf2:sha256": f"mock:{password}"

_db_dir = None
_db_name = "test.db"
_db_path = None


def _init_db_path():
    _db_dir = tempfile.mkdtemp()
    _db_path = str(Path(_db_dir) / _db_name)
    import flask_se_config

    flask_se_config.SQLITE_DATABASE_NAME = _db_name
    flask_se_config.SQLITE_DATABASE_PATH = _db_dir
    flask_se_config.WHOOSHEE_DIR = tempfile.mkdtemp()
    return _db_dir, _db_path


_db_dir, _db_path = _init_db_path()

import pytest
from sqlalchemy import create_engine

import flask_se as _fs
from flask_se import app, db

_fs.scheduler.shutdown(wait=False)

from se_models import init_db

UPLOAD_DIRS = [
    "static/practice/texts/",
    "static/practice/reviews/",
    "static/practice/slides/",
    "static/tmp/texts/",
    "static/tmp/slides/",
    "static/tmp/reviews/",
]


@pytest.fixture(autouse=True)
def _ensure_upload_dirs():
    for d in UPLOAD_DIRS:
        os.makedirs(d, exist_ok=True)
    yield


@pytest.fixture
def staff_client(logged_client):
    from se_models import Staff, db

    if not Staff.query.filter_by(user_id=1).first():
        db.session.add(
            Staff(user_id=1, official_email="test@spbu.ru", position="Test", still_working=True)
        )
        db.session.commit()
    return logged_client


LIST_VIEWS = [
    ("admin_index", "/admin/"),
    ("users", "/admin/users/"),
    ("staff", "/admin/staff/"),
    ("thesis", "/admin/thesis/"),
    ("summerschool", "/admin/summerschool/"),
    ("news", "/admin/posts/"),
    ("diplomathemes", "/admin/diplomathemes/"),
    ("reviewdiplomathemes", "/admin/reviewdiplomathemes/"),
    ("currentthesis", "/admin/currentthesis/"),
]


def _set_db_uri(uri):
    """Set SQLAlchemy URI and reset engine cache."""
    app.config["SQLALCHEMY_DATABASE_URI"] = uri
    old = db.engines.get(None)
    if old is not None:
        old.dispose()
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
    _whoosh_dir = tempfile.mkdtemp()
    uri = "sqlite:///" + _p
    with app.app_context():
        _set_db_uri(uri)
        app.config["WHOOSHEE_DIR"] = _whoosh_dir
        app.extensions['whooshee']['index_path_root'] = _whoosh_dir
        app.extensions['whooshee']['whoosheers_indexes'] = {}
        db.create_all()
        _fs.whooshee.reindex()
        yield
        db.session.remove()
        db.drop_all()
    shutil.rmtree(_dir, ignore_errors=True)
    shutil.rmtree(_whoosh_dir, ignore_errors=True)


@pytest.fixture
def client():
    _dir = tempfile.mkdtemp()
    _p = str(Path(_dir) / _db_name)
    _whoosh_dir = tempfile.mkdtemp()
    uri = "sqlite:///" + _p
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    with app.app_context():
        _set_db_uri(uri)
        app.config["WHOOSHEE_DIR"] = _whoosh_dir
        app.extensions['whooshee']['index_path_root'] = _whoosh_dir
        app.extensions['whooshee']['whoosheers_indexes'] = {}
        db.create_all()
        _fs.whooshee.reindex()
        yield app.test_client()
        db.session.remove()
        db.drop_all()
    shutil.rmtree(_dir, ignore_errors=True)
    shutil.rmtree(_whoosh_dir, ignore_errors=True)


@pytest.fixture
def seeded_client(_seeded_db_path):
    """Copy the pre-seeded template DB once per test — fast (~ms)."""
    _dir = tempfile.mkdtemp()
    _p = str(Path(_dir) / _db_name)
    _whoosh_dir = tempfile.mkdtemp()
    shutil.copy2(str(_seeded_db_path), _p)
    uri = "sqlite:///" + _p
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    with app.app_context():
        _set_db_uri(uri)
        app.config["WHOOSHEE_DIR"] = _whoosh_dir
        app.extensions['whooshee']['index_path_root'] = _whoosh_dir
        app.extensions['whooshee']['whoosheers_indexes'] = {}
        db.create_all()
        _fs.whooshee.reindex()
        yield app.test_client()
        db.session.remove()
        db.drop_all()
    shutil.rmtree(_dir, ignore_errors=True)
    shutil.rmtree(_whoosh_dir, ignore_errors=True)


@pytest.fixture
def logged_client(seeded_client):
    """Seeded client with logged-in test user. Bypasses login to avoid scrypt hash issues on 3.13."""
    from se_models import Users

    u = Users.query.filter_by(email="a.terekhov@spbu.ru").first()
    with seeded_client.session_transaction() as sess:
        sess["_user_id"] = str(u.id)
    return seeded_client


@pytest.fixture
def practice_thesis(logged_client):
    """Seeded client + a CurrentThesis belonging to the logged-in user."""
    from se_models import CurrentThesis, ThesisReport, ThesisTask, db

    ct = CurrentThesis(author_id=1, worktype_id=1, area_id=1)
    ct.title = "Test Practice Thesis"
    ct.supervisor_id = 1
    db.session.add(ct)
    db.session.flush()

    task = ThesisTask(task_text="Test task", current_thesis_id=ct.id)
    db.session.add(task)

    report = ThesisReport(
        was_done="Completed task 1", planned_to_do="Task 2", current_thesis_id=ct.id, author_id=1
    )
    db.session.add(report)
    db.session.commit()
    return logged_client


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


def _min_pdf(text="dummy"):
    """Return a minimal valid PDF as bytes. Self-contained, no external deps."""
    import zlib
    contents = b"BT /F1 12 Tf 100 700 Td (" + text.encode() + b") Tj ET"
    compressed = zlib.compress(contents)
    objs = [
        b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj",
        b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj",
        b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> >> >> >>\nendobj",
        b"4 0 obj\n<< /Length " + str(len(compressed)).encode() + b" /Filter /FlateDecode >>\nstream\n" + compressed + b"\nendstream\nendobj",
    ]
    body = b"\n".join(objs)
    return b"%PDF-1.4\n" + body + b"\ntrailer\n<< /Size 5 /Root 1 0 R >>\nstartxref\n9\n%%EOF"


@pytest.fixture
def seeded_app_ctx(app_ctx):
    from se_models import Users, db

    u = Users(email="test@spbu.ru", first_name="Test", last_name="User")
    db.session.add(u)
    db.session.commit()
    return app_ctx

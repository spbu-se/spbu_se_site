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

# Do not start the APScheduler: the module-level app is created on import via
# create_app(), and conftest must not fire background jobs during the suite.
os.environ["SE_START_SCHEDULER"] = "0"
# Do not run boot-time ensure_schema() against the module-level app: the suite
# builds its own seeded DB templates per fixture.
os.environ["SE_AUTO_MIGRATE"] = "0"

_db_dir = None
_db_name = "test.db"
_db_path = None


def _init_db_path():
    _db_dir = tempfile.mkdtemp()
    _db_path = str(Path(_db_dir) / _db_name)
    import flask_se_config as _fsc

    _fsc.SQLITE_DATABASE_NAME = _db_name
    _fsc.SQLITE_DATABASE_PATH = _db_dir
    return _db_dir, _db_path


_db_dir, _db_path = _init_db_path()

import pytest
from sqlalchemy import create_engine

# Isolate the theses upload scratch dir per process (xdist worker) so parallel
# tests never write the same file in the shared static/tmp tree.
_upload_root = Path(tempfile.mkdtemp(prefix="se_uploads_"))
for _sub in ("texts", "slides", "reviews"):
    (_upload_root / _sub).mkdir(parents=True, exist_ok=True)
os.environ["SE_THESIS_UPLOAD_ROOT"] = str(_upload_root)

# Deterministic thesis-secret per process: the config file is absent on CI, so
# the random fallback differed between two flask_se_config module instances
# under xdist ("Invalid secret key" flakiness). Env is process-global so every
# import instance reads the same value.
os.environ["SE_THESIS_SECRET"] = "test-thesis-secret"

from flask_se import app, db
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


# Build a seeded DB template once per session (FTS5 index is inside the DB)
@pytest.fixture(scope="session")
def _seeded_db_path():
    _dir = tempfile.mkdtemp()
    _db_p = str(Path(_dir) / _db_name)
    uri = "sqlite:///" + _db_p
    with app.app_context():
        _set_db_uri(uri)
        db.create_all()
        init_db()
        db.session.remove()
    yield _db_p
    shutil.rmtree(_dir, ignore_errors=True)


@pytest.fixture
def app_ctx():
    _dir = tempfile.mkdtemp()
    _p = str(Path(_dir) / _db_name)
    uri = "sqlite:///" + _p
    with app.app_context():
        _set_db_uri(uri)
        db.create_all()
        yield app.test_client()
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
    """Copy the pre-seeded DB template once per test — fast (~ms). FTS5 index is inside the DB."""
    _dir = tempfile.mkdtemp()
    _p = str(Path(_dir) / _db_name)
    shutil.copy2(_seeded_db_path, _p)
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


@pytest.fixture
def admin_client(seeded_client):
    """Seeded client logged in as the admin user (role >= 5)."""
    from se_models import Users, db

    u = Users.query.filter_by(email="a.terekhov@spbu.ru").first()
    u.role = 5
    db.session.commit()
    with seeded_client.session_transaction() as sess:
        sess["_user_id"] = str(u.id)
    return seeded_client


@pytest.fixture
def practice_thesis(logged_client):
    """Seeded client + a CurrentThesis belonging to the logged-in user."""
    _setup_current_thesis_with_report()
    return logged_client


def _setup_current_thesis_with_report():
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
    return ct.id, report.id


def _seed_internship(
    client,
    *,
    company="Existing Co",
    vacancy="Existing Vacancy",
    description="Desc",
    requirements="Req",
) -> int:
    """Shared internship seeding helper (was duplicated in test_og_cards + test_internships_deep)."""
    from se_models import InternshipCompany, InternshipFormat, Internships, InternshipTag, db

    company_obj = InternshipCompany(name=company)
    db.session.add(company_obj)
    db.session.flush()

    fmt = db.session.get(InternshipFormat, 1)
    tag = db.session.get(InternshipTag, 1)

    internship = Internships(
        name_vacancy=vacancy,
        salary="50000",
        description=description,
        location="SPb",
        company_id=company_obj.id,
        requirements=requirements,
        more_inf="https://example.com",
        author_id=1,
    )
    internship.format = [fmt]
    internship.tag = [tag]
    db.session.add(internship)
    db.session.commit()
    return internship.id


def _make_published_thesis(name="Thesis", author="Author"):
    """Shared published-thesis seeding helper (was duplicated in test_og_cards + test_ssr_lists)."""
    from se_models import Thesis, db

    thesis = Thesis(
        name_ru=name,
        author=author,
        type_id=2,
        course_id=1,
        publish_year=2024,
        temporary=False,
    )
    db.session.add(thesis)
    db.session.commit()
    return thesis


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
        b"4 0 obj\n<< /Length "
        + str(len(compressed)).encode()
        + b" /Filter /FlateDecode >>\nstream\n"
        + compressed
        + b"\nendstream\nendobj",
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


@pytest.fixture
def notification_in_db(seeded_app_ctx):
    from se_models import Notification, db

    n = Notification(recipient=1, title="Test", content="Test content", type=0)
    db.session.add(n)
    db.session.commit()
    return n


def _assert_seeded_tables():
    from se_models import (
        AreasOfStudy,
        Courses,
        Curriculum,
        DiplomaThemes,
        InternshipFormat,
        InternshipTag,
        Posts,
        Staff,
        ThemesLevel,
        Users,
        Worktype,
    )

    assert AreasOfStudy.query.count() > 0
    assert Users.query.count() > 0
    assert Staff.query.count() > 0
    assert Worktype.query.count() > 0
    assert Courses.query.count() > 0
    assert Posts.query.count() > 0
    assert ThemesLevel.query.count() > 0
    assert DiplomaThemes.query.count() > 0
    assert InternshipFormat.query.count() > 0
    assert InternshipTag.query.count() > 0
    return Curriculum


def _approve_temp_thesis(client, thesis_id):
    return client.post("/theses_add_tmp", data={"thesis_id": thesis_id})


def _make_temp_thesis(author: str = "T", text_uri: str | None = None, name_ru: str | None = None):
    from se_models import Thesis, db

    t = Thesis(
        name_ru=name_ru or ("ApproveMe" if author == "T" else "Temp Thesis"),
        author=author,
        type_id=2,
        course_id=1,
        publish_year=2024,
        temporary=True,
    )
    if text_uri:
        t.text_uri = text_uri
    db.session.add(t)
    db.session.commit()
    return t

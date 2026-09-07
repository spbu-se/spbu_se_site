# -*- coding: utf-8 -*-
"""Live-browser fixtures: real Flask server, real hashing and CSRF.

Runs against the real application (no test mocks): a fresh seeded SQLite DB is
built in ``.tmp`` and served by the module-level ``app`` through werkzeug on an
ephemeral port. The seeded accounts from ``se_seed_data`` (password ``1``) are
what every surface logs in as — see ``docs/ROLE_FEATURE_MATRIX.md``.

Not part of the default suite: ``pyproject.toml`` restricts ``testpaths`` to
``tests/``, and e2e tests carry the ``e2e`` marker. Run explicitly with::

    uv run pytest e2e -m e2e --no-cov -n 0
"""

import os
import sys
import threading
from pathlib import Path

from playwright.sync_api import sync_playwright

_REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO / "src"))

# Mirror tests/conftest process-level toggles (module-level app is created on
# import); everything else stays real — werkzeug hashing, CSRF, rate limiters.
os.environ["SE_START_SCHEDULER"] = "0"
os.environ["SE_AUTO_MIGRATE"] = "0"

_db_dir = Path(_REPO / ".tmp" / "e2e-db")
_db_dir.mkdir(parents=True, exist_ok=True)
_upload_root = _REPO / ".tmp" / "e2e_uploads"
for _sub in ("texts", "slides", "reviews"):
    (_upload_root / _sub).mkdir(parents=True, exist_ok=True)
os.environ["SE_THESIS_UPLOAD_ROOT"] = str(_upload_root)
os.environ["SE_THESIS_SECRET"] = "e2e-thesis-secret"

import flask_se_config as _fsc

_fsc.SQLITE_DATABASE_NAME = "e2e.db"
_fsc.SQLITE_DATABASE_PATH = _db_dir.as_posix()

import pytest
from werkzeug.serving import make_server

from flask_se import app, db
from se_models import init_db


@pytest.fixture(scope="session")
def live_server():
    """Seed a fresh DB and serve the real app on an ephemeral port."""
    db_file = _db_dir / _fsc.SQLITE_DATABASE_NAME
    if db_file.exists():
        db_file.unlink()
    with app.app_context():
        db.create_all()
        init_db()
    server = make_server("127.0.0.1", 0, app, threaded=True)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    host, port = server.server_address[0], server.server_address[1]
    yield f"http://{host}:{port}"
    server.shutdown()
    thread.join(timeout=5)


@pytest.fixture(scope="session")
def browser():
    p = sync_playwright().start()
    browser = p.chromium.launch(headless=True)
    yield browser
    browser.close()
    p.stop()


@pytest.fixture
def page(live_server, browser):
    context = browser.new_context()
    page = context.new_page()
    page.set_default_timeout(15_000)
    yield page
    context.close()

# -*- coding: utf-8 -*-
"""HTTP role journeys over the seeded, deterministic local environment.

These tests drive real forms through the WSGI test client as each seeded
account (see docs/ROLE_FEATURE_MATRIX.md). They complement the module-deep
suites by exercising the cross-cutting auth lifecycle against the actual seed:
real login per account, password recovery end-to-end via the local .eml mail
capture (SE_MAIL_DEV_DIR), and self-registration.

One login per test client: the module-level app singleton cannot reliably
serve two session switches on the same client (recorded in RETROSPECTIVES),
so the account logins are parametrized per client.
"""

import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

import se_seed_data

_ACCOUNT_EMAILS = [a["email"] for a in se_seed_data.ROLE_ACCOUNTS + se_seed_data.STAFF_ACCOUNTS]


def test_seed_passwords_verify_against_real_hash(tmp_path):
    """Seeded password hashes really equal DEV_PASSWORD (no test mocks involved)."""
    src = str(Path(__file__).resolve().parent.parent / "src")
    db_dir = tmp_path / "db"
    script = (
        "import os\n"
        f"import flask_se_config as c\n"
        f"db_dir = {str(db_dir)!r}\n"
        f"os.makedirs(db_dir, exist_ok=True)\n"
        f"c.SQLITE_DATABASE_NAME = 'j.db'\n"
        f"c.SQLITE_DATABASE_PATH = db_dir\n"
        "from flask_se import app, db\n"
        "from se_models import init_db, Users\n"
        "from werkzeug.security import check_password_hash\n"
        "with app.app_context():\n"
        "    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_dir + '/j.db'\n"
        "    db.create_all()\n"
        "    init_db()\n"
        "    for acc in __import__('se_seed_data').ROLE_ACCOUNTS:\n"
        "        u = Users.query.filter_by(email=acc['email']).first()\n"
        "        assert u and check_password_hash(u.password_hash, '1')\n"
        "print('OK')\n"
    )
    result = subprocess.run(  # noqa: S603 — static local script, no untrusted input
        [sys.executable, "-c", script],
        capture_output=True,
        text=True,
        env={**os.environ, "PYTHONPATH": src},
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "OK" in result.stdout


@pytest.mark.parametrize("email", _ACCOUNT_EMAILS)
def test_login_as_each_seed_account(seeded_client, email):
    """Real POST login succeeds for every seeded account with password '1'."""
    resp = seeded_client.post(
        "/login.html",
        data={"email": email, "password": "1"},
        follow_redirects=False,
    )
    assert resp.status_code == 302, f"{email} login failed"
    assert "/profile.html" in resp.headers.get("Location", "")


def test_password_recovery_flow_via_mail_capture(seeded_client, monkeypatch, tmp_path):
    """Recovery e-mail is captured locally and its link completes a reset."""
    monkeypatch.setenv("SE_MAIL_DEV_DIR", str(tmp_path))

    resp = seeded_client.post(
        "/password_recovery.html",
        data={"email": "user@se.dev"},
    )
    assert resp.status_code == 200

    mails = list(tmp_path.glob("*.eml"))
    assert len(mails) == 1
    body = mails[0].read_text(encoding="utf-8")
    match = re.search(r"/password_recovery/([^/\s\"]+)", body)
    assert match is not None
    token = match.group(1)

    reset_page = seeded_client.get(f"/password_recovery/{token}")
    assert reset_page.status_code == 200

    reset = seeded_client.post(
        f"/password_recovery/{token}",
        data={"password": "new-pass-123", "password2": "new-pass-123"},
    )
    assert reset.status_code == 302
    assert "/profile.html" in reset.headers.get("Location", "")


def test_register_then_login(client):
    """Self-registration creates a usable account that logs in afterwards."""
    register = client.post(
        "/register_basic.html",
        data={
            "email": "new@se.dev",
            "password": "register-pass",
            "password2": "register-pass",
            "first_name": "Новый",
            "last_name": "Пользователь",
            "consent": "on",
        },
    )
    assert register.status_code == 302
    assert "/profile.html" in register.headers.get("Location", "")

    logout = client.get("/logout")
    assert logout.status_code == 302

    login = client.post("/login.html", data={"email": "new@se.dev", "password": "register-pass"})
    assert login.status_code == 302
    assert "/profile.html" in login.headers.get("Location", "")

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
from itertools import count
from pathlib import Path

import pytest

import se_seed_data

_ACCOUNT_EMAILS = [a["email"] for a in se_seed_data.ROLE_ACCOUNTS + se_seed_data.STAFF_ACCOUNTS]

# The per-IP login/register/recovery limiters are process-global, and many
# suite tests share the default 127.0.0.1 client address. Each journey request
# uses a unique REMOTE_ADDR so the count stays within window limits regardless
# of xdist worker scheduling.
_client_ip = count(1)


def _req(client, method, path, data=None):
    ip = next(_client_ip)
    return client.open(
        path,
        method=method,
        data=data,
        environ_base={"REMOTE_ADDR": f"10.250.{ip // 250}.{ip % 250 + 1}"},
    )


def test_real_password_hash_roundtrip():
    """Werkzeug (unmocked) can verify a pbkdf2 hash of DEV_PASSWORD.

    Runs in a fresh process: the tests/conftest check_password_hash mock
    accepts everything, so the real implementation is verified here.
    """
    src = str(Path(__file__).resolve().parent.parent / "src")
    script = (
        "from werkzeug.security import check_password_hash, generate_password_hash\n"
        "h = generate_password_hash('1', method='pbkdf2:sha256')\n"
        "assert h != '1'\n"
        "assert check_password_hash(h, '1')\n"
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


def test_seed_accounts_store_dev_password(seeded_client):
    """Seeded accounts carry the DEV_PASSWORD-derived hash.

    In this process hashing is mocked to ``mock:<password>``, which still
    proves the seed passed DEV_PASSWORD to the generator.
    """
    from se_models import Users

    for email in _ACCOUNT_EMAILS:
        user = Users.query.filter_by(email=email).first()
        assert user is not None
        assert user.password_hash == f"mock:{se_seed_data.DEV_PASSWORD}"


@pytest.mark.parametrize("email", _ACCOUNT_EMAILS)
def test_login_as_each_seed_account(seeded_client, email):
    """Real POST login succeeds for every seeded account with password '1'."""
    resp = _req(seeded_client, "POST", "/login.html", {"email": email, "password": "1"})
    assert resp.status_code == 302, f"{email} login failed"
    assert "/profile.html" in resp.headers.get("Location", "")


def test_password_recovery_flow_via_mail_capture(seeded_client, monkeypatch, tmp_path):
    """Recovery e-mail is captured locally and its link completes a reset."""
    monkeypatch.setenv("SE_MAIL_DEV_DIR", str(tmp_path))

    resp = _req(seeded_client, "POST", "/password_recovery.html", {"email": "user@se.dev"})
    assert resp.status_code == 200

    mails = list(tmp_path.glob("*.eml"))
    assert len(mails) == 1
    body = mails[0].read_text(encoding="utf-8")
    match = re.search(r"/password_recovery/([^/\s\"]+)", body)
    assert match is not None
    token = match.group(1)

    reset_page = _req(seeded_client, "GET", f"/password_recovery/{token}")
    assert reset_page.status_code == 200

    reset = _req(
        seeded_client,
        "POST",
        f"/password_recovery/{token}",
        {"password": "new-pass-123", "password2": "new-pass-123"},
    )
    assert reset.status_code == 302
    assert "/profile.html" in reset.headers.get("Location", "")


def test_register_then_login(client):
    """Self-registration creates a usable account that logs in afterwards."""
    register = _req(
        client,
        "POST",
        "/register_basic.html",
        {
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

    logout = _req(client, "GET", "/logout")
    assert logout.status_code == 302

    login = _req(
        client, "POST", "/login.html", {"email": "new@se.dev", "password": "register-pass"}
    )
    assert login.status_code == 302
    assert "/profile.html" in login.headers.get("Location", "")

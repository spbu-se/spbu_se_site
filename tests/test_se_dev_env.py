# -*- coding: utf-8 -*-
import os
import subprocess
import sys
from pathlib import Path

import se_sendmail
from flask_se_config import RateLimiter


def test_dev_mail_capture_writes_eml_and_skips_smtp(monkeypatch, tmp_path):
    monkeypatch.setenv("SE_MAIL_DEV_DIR", str(tmp_path))

    def _fail(*args, **kwargs):
        raise AssertionError

    monkeypatch.setattr(se_sendmail.smtplib, "SMTP", _fail)

    ok = se_sendmail.send_mail("dev@example.org", "Тема", "Текст", "<b>Текст</b>")
    assert ok is True

    files = list(tmp_path.glob("*.eml"))
    assert len(files) == 1
    content = files[0].read_text(encoding="utf-8")
    assert "dev@example.org" in content
    assert "Тема" in content
    assert "<b>Текст</b>" in content


def test_dev_mail_capture_keeps_staging_noop(monkeypatch, tmp_path):
    monkeypatch.setenv("SE_STAGING", "1")
    monkeypatch.setenv("SE_MAIL_DEV_DIR", str(tmp_path))

    ok = se_sendmail.send_mail("dev@example.org", "Тема", "Текст")
    assert ok is False
    assert list(tmp_path.glob("*.eml")) == []


def test_rate_limiter_unlimited_when_disabled():
    limiter = RateLimiter(limit=None, window_seconds=300)
    for _ in range(100):
        assert limiter.allow("k") is True


def test_rate_limiter_still_enforced_with_limit():
    limiter = RateLimiter(limit=2, window_seconds=300)
    assert limiter.allow("k") is True
    assert limiter.allow("k") is True
    assert limiter.allow("k") is False
    assert limiter.allow("other") is True


def test_secret_key_env_override(monkeypatch, tmp_path):
    src = str(Path(__file__).resolve().parent.parent / "src")
    env = dict(os.environ)
    env["SE_SECRET_KEY"] = "deterministic-dev-key"
    env["PYTHONPATH"] = src
    result = subprocess.run(
        [sys.executable, "-c", "import flask_se_config as c; print(c.SECRET_KEY)"],
        capture_output=True,
        text=True,
        env=env,
        check=True,
    )
    assert result.stdout.strip() == "deterministic-dev-key"

# -*- coding: utf-8 -*-
"""Yandex SmartCaptcha: config-gated verification on the registration form.

Disabled (no keys) the site behaves exactly as before; enabled it fails closed
on a missing/invalid token and never raises on a network error.
"""

from unittest.mock import patch

import requests

from flask_se_auth import _check_smartcaptcha
from se_models import Users

REGISTER_URL = "/register_basic.html"

REGISTER_DATA = {
    "email": "captcha.user@spbu.ru",
    "password": "pass1234",
    "password2": "pass1234",
    "first_name": "Иван",
    "last_name": "Иванов",
    "consent": "on",
}


class _FakeResponse:
    def __init__(self, payload):
        self._payload = payload

    def json(self):
        return self._payload


def _clear_keys(monkeypatch):
    monkeypatch.delenv("SE_SMARTCAPTCHA_SITEKEY", raising=False)
    monkeypatch.delenv("SE_SMARTCAPTCHA_SECRET", raising=False)


def _set_keys(monkeypatch):
    monkeypatch.setenv("SE_SMARTCAPTCHA_SITEKEY", "test-sitekey")
    monkeypatch.setenv("SE_SMARTCAPTCHA_SECRET", "test-secret")


class TestCheckSmartcaptcha:
    def test_disabled_without_keys(self, seeded_client, monkeypatch):
        _clear_keys(monkeypatch)
        with seeded_client.application.test_request_context(REGISTER_URL, method="POST"):
            assert _check_smartcaptcha() is None

    def test_missing_token_when_enabled(self, seeded_client, monkeypatch):
        _set_keys(monkeypatch)
        with seeded_client.application.test_request_context(REGISTER_URL, method="POST"):
            assert _check_smartcaptcha() is not None

    def test_valid_token_passes(self, seeded_client, monkeypatch):
        _set_keys(monkeypatch)
        with (
            seeded_client.application.test_request_context(
                REGISTER_URL, method="POST", data={"smart-token": "token"}
            ),
            patch(
                "flask_se_auth.requests.post", return_value=_FakeResponse({"status": "ok"})
            ) as post,
        ):
            assert _check_smartcaptcha() is None
        post.assert_called_once()

    def test_rejected_token_fails(self, seeded_client, monkeypatch):
        _set_keys(monkeypatch)
        with (
            seeded_client.application.test_request_context(
                REGISTER_URL, method="POST", data={"smart-token": "token"}
            ),
            patch("flask_se_auth.requests.post", return_value=_FakeResponse({"status": "failed"})),
        ):
            assert _check_smartcaptcha() is not None

    def test_network_error_fails_closed(self, seeded_client, monkeypatch):
        _set_keys(monkeypatch)
        with (
            seeded_client.application.test_request_context(
                REGISTER_URL, method="POST", data={"smart-token": "token"}
            ),
            patch("flask_se_auth.requests.post", side_effect=requests.RequestException()),
        ):
            assert _check_smartcaptcha() is not None


class TestRegistrationTemplate:
    def test_widget_absent_without_keys(self, seeded_client, monkeypatch):
        _clear_keys(monkeypatch)
        html = seeded_client.get(REGISTER_URL).get_data(as_text=True)
        assert "smart-captcha" not in html
        assert "smartcaptcha.yandexcloud.net" not in html

    def test_widget_present_with_keys(self, seeded_client, monkeypatch):
        _set_keys(monkeypatch)
        html = seeded_client.get(REGISTER_URL).get_data(as_text=True)
        assert "smart-captcha" in html
        assert "test-sitekey" in html


class TestRegisterWithCaptcha:
    def test_blocked_without_token(self, seeded_client, monkeypatch):
        import flask_se_auth

        _set_keys(monkeypatch)
        with patch.object(flask_se_auth.REGISTER_RATE_LIMITER, "allow", return_value=True):
            resp = seeded_client.post(REGISTER_URL, data=dict(REGISTER_DATA))
        assert resp.status_code == 200
        assert "не робот" in resp.data.decode()
        with seeded_client.application.app_context():
            assert Users.query.filter_by(email="captcha.user@spbu.ru").first() is None

    def test_succeeds_with_valid_token(self, seeded_client, monkeypatch):
        import flask_se_auth

        _set_keys(monkeypatch)
        with (
            patch.object(flask_se_auth.REGISTER_RATE_LIMITER, "allow", return_value=True),
            patch("flask_se_auth.requests.post", return_value=_FakeResponse({"status": "ok"})),
        ):
            resp = seeded_client.post(REGISTER_URL, data={**REGISTER_DATA, "smart-token": "token"})
        assert resp.status_code == 302
        with seeded_client.application.app_context():
            assert Users.query.filter_by(email="captcha.user@spbu.ru").first() is not None

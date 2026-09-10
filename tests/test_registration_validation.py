# -*- coding: utf-8 -*-
"""Server-side validation for person names and e-mails (registration + profile).

Reproduces the prod abuse where a scanner stored SSTI/SSRF/XSS probe payloads
as a ``Users`` name; those characters must be rejected before persistence.
"""

from unittest.mock import patch

import pytest

from se_models import Users
from se_validation import (
    MAX_PERSON_NAME_LENGTH,
    clean_person_name,
    validate_email,
    validate_person_name,
)

MALICIOUS_SURNAME = '"\n"+"A".concat(70-3).concat(22*4)+(require"socket")'


class TestValidatePersonName:
    def test_accepts_cyrillic_and_latin(self):
        assert validate_person_name("Терехов") is None
        assert validate_person_name("Smith-Jones") is None
        assert validate_person_name("О'Нил") is None
        assert validate_person_name("Иван Петров") is None

    @pytest.mark.parametrize(
        "bad",
        ["<script>", 'a"b', "a'b;", "a{b}", "$(id)", "x\nINJECT", "Терехов<", "a|b", "a&b"],
    )
    def test_rejects_payload_characters(self, bad):
        assert validate_person_name(bad) is not None

    def test_empty_required_vs_optional(self):
        assert validate_person_name("") is not None
        assert validate_person_name("", required=False) is None

    def test_rejects_over_max_length(self):
        assert validate_person_name("я" * (MAX_PERSON_NAME_LENGTH + 1)) is not None


class TestCleanPersonName:
    def test_strips_disallowed_characters(self):
        cleaned = clean_person_name('Ив<script>ан"')
        assert not (set(cleaned) & set('<>"{}()$|&;'))
        assert cleaned.startswith("Ив") and cleaned.endswith("ан")

    def test_falls_back_when_nothing_safe_remains(self):
        assert clean_person_name("<<>>", fallback="Пользователь") == "Пользователь"


class TestValidateEmail:
    @pytest.mark.parametrize("good", ["a@b.co", "new.user@spbu.ru", "x+y@sub.domain.org"])
    def test_accepts_valid(self, good):
        assert validate_email(good) is None

    @pytest.mark.parametrize("bad", ["short", "no-at.ru", "a@b", "a b@c.ru", "a@b.c d"])
    def test_rejects_invalid(self, bad):
        assert validate_email(bad) is not None


class TestRegisterRejectsMaliciousInput:
    def test_malicious_surname_not_stored(self, seeded_client):
        import flask_se_auth

        with patch.object(flask_se_auth.REGISTER_RATE_LIMITER, "allow", return_value=True):
            resp = seeded_client.post(
                "/register_basic.html",
                data={
                    "email": "scanner@example.com",
                    "password": "pass1234",
                    "password2": "pass1234",
                    "first_name": "A",
                    "last_name": MALICIOUS_SURNAME,
                    "consent": "on",
                },
            )
        assert resp.status_code == 200
        assert "недопустимые символы" in resp.data.decode()
        with seeded_client.application.app_context():
            assert Users.query.filter_by(email="scanner@example.com").first() is None

    def test_invalid_email_rejected(self, seeded_client):
        import flask_se_auth

        with patch.object(flask_se_auth.REGISTER_RATE_LIMITER, "allow", return_value=True):
            resp = seeded_client.post(
                "/register_basic.html",
                data={
                    "email": "not-an-email",
                    "password": "pass1234",
                    "password2": "pass1234",
                    "first_name": "Иван",
                    "last_name": "Иванов",
                    "consent": "on",
                },
            )
        assert resp.status_code == 200
        assert "Некорректный почтовый адрес" in resp.data.decode()
        with seeded_client.application.app_context():
            assert Users.query.filter_by(email="not-an-email").first() is None


class TestProfileRejectsMaliciousName:
    def test_malicious_surname_not_saved(self, logged_client):
        with logged_client.application.app_context():
            before = Users.query.filter_by(email="a.terekhov@spbu.ru").first()
            assert before is not None
            before_last_name = before.last_name

        resp = logged_client.post(
            "/profile.html",
            data={
                "first_name": "Андрей",
                "last_name": MALICIOUS_SURNAME,
                "middle_name": "",
                "how_to_contact": "",
            },
        )
        assert resp.status_code == 200
        assert "недопустимые символы" in resp.data.decode()
        with logged_client.application.app_context():
            after = Users.query.filter_by(email="a.terekhov@spbu.ru").first()
            assert after is not None
            assert after.last_name == before_last_name

# -*- coding: utf-8 -*-
"""Canonical browser journeys over the real, seeded local server.

Run: ``uv run pytest e2e -m e2e --no-cov -n 0``
"""

import time

import pytest

from se_seed_data import ROLE_ACCOUNTS


@pytest.mark.e2e
def test_anonymous_admin_redirects_to_login(page, live_server):
    """The admin gate is real in the browser: unauthenticated → login page."""
    page.goto(f"{live_server}/admin/users/")
    page.wait_for_load_state("networkidle")
    assert "/login.html" in page.url, page.url
    assert page.get_by_role("heading", name="Авторизация").is_visible() or "Войти" in page.content()


@pytest.mark.e2e
def test_admin_login_opens_user_list(page, live_server):
    """Seed admin@se.dev (password 1) reaches the admin user surface."""
    admin = next(a for a in ROLE_ACCOUNTS if a["email"] == "admin@se.dev")
    page.goto(f"{live_server}/login.html")
    page.fill("input[name=email]", admin["email"])
    page.fill("input[name=password]", "1")
    page.click("button[type=submit]")
    page.wait_for_load_state("networkidle")
    assert "/profile.html" in page.url, page.url
    assert "Личный кабинет" in page.content()

    page.goto(f"{live_server}/admin/")
    page.wait_for_load_state("networkidle")
    assert "Автоматизация загрузки ВКР и учебных практик" in page.content()


@pytest.mark.e2e
def test_register_new_user_reaches_profile(page, live_server):
    """A real registration (8-char password) lands on the personal cabinet."""
    email = f"e2e-{int(time.time())}@se.dev"
    page.goto(f"{live_server}/register_basic.html")
    page.fill("input[name=email]", email)
    page.fill("input[name=password]", "e2e-pass-123")
    page.fill("input[name=password2]", "e2e-pass-123")
    page.fill("input[name=first_name]", "Браузер")
    page.fill("input[name=last_name]", "Тест")
    page.click("label[for=consent]")
    page.click("#register-submit")
    page.wait_for_load_state("networkidle")
    assert "/profile.html" in page.url, page.url
    assert "Личный кабинет" in page.content()
    assert email in page.content()

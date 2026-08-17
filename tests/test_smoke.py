# -*- coding: utf-8 -*-
from conftest import assert_ok


def test_app_exists():
    from flask_se import app

    assert app is not None


def test_index_returns_200(client):
    assert_ok(client, "/")


def test_index_html_redirects_to_root(client):
    resp = client.get("/index.html")
    assert resp.status_code == 301
    assert resp.location == "/"


def test_nonexistent_returns_404(client):
    assert_ok(client, "/nonexistent-page", code=404)


def test_login_page_loads(client):
    assert_ok(client, "/login.html")


def test_contacts_page_loads(client):
    assert_ok(client, "/contacts.html")


def test_students_index_loads(client):
    assert_ok(client, "/students/index.html")


def test_sitemap_returns_200(client):
    assert_ok(client, "/sitemap.xml")


def test_research_directions_loads(client):
    assert_ok(client, "/research-directions")

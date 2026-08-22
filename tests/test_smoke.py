# -*- coding: utf-8 -*-
import pytest
from conftest import assert_ok


@pytest.mark.parametrize(
    "path,code",
    [
        ("/", 200),
        ("/nonexistent-page", 404),
        ("/login.html", 200),
        ("/contacts.html", 200),
        ("/students/index.html", 200),
        ("/sitemap.xml", 200),
        ("/research-directions", 200),
    ],
)
def test_pages_return_expected_code(client, path, code):
    assert_ok(client, path, code=code)


def test_index_html_redirects_to_root(client):
    resp = client.get("/index.html")
    assert resp.status_code == 301
    assert resp.location == "/"

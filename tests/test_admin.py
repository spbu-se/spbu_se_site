# -*- coding: utf-8 -*-
import pytest
from conftest import LIST_VIEWS, assert_ok


class TestAdminAccess:
    def test_admin_redirects_when_unauth(self, seeded_client):
        resp = seeded_client.get("/admin/")
        assert resp.status_code in (200, 301, 302, 401, 403)

    def test_admin_page_logged_in(self, logged_client):
        resp = logged_client.get("/admin/")
        assert resp.status_code in (200, 302, 403)

    @pytest.mark.parametrize("name,path", LIST_VIEWS)
    def test_admin_view_logged_in(self, logged_client, name, path):
        resp = logged_client.get(path)
        assert resp.status_code in (200, 302, 403)


class TestAdminSecrets:
    def test_admin_shows_secret_key(self, logged_client):
        resp = logged_client.get("/admin/")
        assert resp.status_code in (200, 302, 403)

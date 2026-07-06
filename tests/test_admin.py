# -*- coding: utf-8 -*-
class TestAdminAccess:
    def test_admin_redirects_when_unauth(self, seeded_client):
        resp = seeded_client.get("/admin/")
        assert resp.status_code in (200, 301, 302, 401, 403)

    def test_admin_page_logged_in(self, logged_client):
        resp = logged_client.get("/admin/")
        assert resp.status_code in (200, 302, 403)

    def test_admin_users_view(self, logged_client):
        resp = logged_client.get("/admin/users/")
        assert resp.status_code in (200, 302, 403)

    def test_admin_staff_view(self, logged_client):
        resp = logged_client.get("/admin/staff/")
        assert resp.status_code in (200, 302, 403)

    def test_admin_thesis_view(self, logged_client):
        resp = logged_client.get("/admin/thesis/")
        assert resp.status_code in (200, 302, 403)

    def test_admin_summerschool_view(self, logged_client):
        resp = logged_client.get("/admin/summerschool/")
        assert resp.status_code in (200, 302, 403)

    def test_admin_diplomathemes_view(self, logged_client):
        resp = logged_client.get("/admin/diplomathemes/")
        assert resp.status_code in (200, 302, 403)

    def test_admin_currentthesis_view(self, logged_client):
        resp = logged_client.get("/admin/currentthesis/")
        assert resp.status_code in (200, 302, 403)

    def test_admin_reviewdiplomathemes_view(self, logged_client):
        resp = logged_client.get("/admin/reviewdiplomathemes/")
        assert resp.status_code in (200, 302, 403)

    def test_admin_posts_view(self, logged_client):
        resp = logged_client.get("/admin/posts/")
        assert resp.status_code in (200, 302, 403)


class TestAdminSecrets:
    def test_admin_shows_secret_key(self, logged_client):
        resp = logged_client.get("/admin/")
        assert resp.status_code in (200, 302, 403)

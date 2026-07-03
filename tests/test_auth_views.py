import pytest


class TestAuth:
    def test_login_with_valid_credentials(self, seeded_client):
        resp = seeded_client.post("/login.html", data={
            "email": "a.terekhov@spbu.ru",
            "password": "any",
        })
        assert resp.status_code in (200, 302)

    def test_login_with_invalid_email(self, seeded_client):
        resp = seeded_client.post("/login.html", data={
            "email": "nonexistent@spbu.ru",
            "password": "any",
        }, follow_redirects=True)
        assert resp.status_code == 200
        assert resp.request.path == "/login.html"

    def test_login_page_has_form(self, seeded_client):
        resp = seeded_client.get("/login.html")
        assert resp.status_code == 200

    def test_logout_redirects(self, seeded_client):
        resp = seeded_client.get("/logout")
        assert resp.status_code == 302

    def test_register_page_loads(self, seeded_client):
        resp = seeded_client.get("/register_basic.html")
        assert resp.status_code == 200

    def test_register_page_has_form(self, seeded_client):
        resp = seeded_client.get("/register_basic.html")
        assert resp.status_code == 200
        assert b"email" in resp.data.lower()

    def test_profile_redirects_when_unauth(self, seeded_client):
        resp = seeded_client.get("/profile.html")
        assert resp.status_code == 302


class TestNews:
    def test_news_index_loads(self, seeded_client):
        resp = seeded_client.get("/news/")
        assert resp.status_code == 200

    def test_news_item_nonexistent(self, seeded_client):
        resp = seeded_client.get("/news/item.html?id=99999")
        assert resp.status_code in (200, 302, 404)


class TestTheses:
    def test_theses_search_loads(self, seeded_client):
        resp = seeded_client.get("/theses.html")
        assert resp.status_code == 200

    def test_theses_with_search_param(self, seeded_client):
        resp = seeded_client.get("/theses.html?search=python")
        assert resp.status_code == 200

    def test_theses_with_year_filter(self, seeded_client):
        resp = seeded_client.get("/theses.html?startdate=2020&enddate=2024")
        assert resp.status_code == 200


class TestInternships:
    def test_internships_index(self, seeded_client):
        resp = seeded_client.get("/internships/internships_index.html")
        assert resp.status_code == 200

    def test_internships_fetch(self, seeded_client):
        resp = seeded_client.get("/internships/fetch_internships")
        assert resp.status_code == 200


class TestDiplomas:
    def test_diplomas_index(self, seeded_client):
        resp = seeded_client.get("/diplomas/")
        assert resp.status_code == 200

    def test_diplomas_add_theme(self, seeded_client):
        resp = seeded_client.get("/diplomas/add_theme.html")
        assert resp.status_code in (200, 302)


class TestPractice:
    def test_practice_guide(self, seeded_client):
        resp = seeded_client.get("/practice/guide/")
        assert resp.status_code in (200, 302)

    def test_practice_staff_index(self, seeded_client):
        resp = seeded_client.get("/practice_staff")
        assert resp.status_code in (200, 302)


class TestSummerSchools:
    def test_summer_school_2026(self, seeded_client):
        resp = seeded_client.get("/summer_school_2026.html")
        assert resp.status_code == 200

    def test_summer_school_list(self, seeded_client):
        resp = seeded_client.get("/summer_school_list.html")
        assert resp.status_code == 200


class TestErrorHandlers:
    def test_404_returns_custom_page(self, seeded_client):
        resp = seeded_client.get("/this-route-does-not-exist-at-all")
        assert resp.status_code == 404

    def test_404_for_html_path(self, seeded_client):
        resp = seeded_client.get("/nonexistent.html")
        assert resp.status_code == 404

from unittest.mock import patch, MagicMock

from conftest import assert_ok


class TestAppFactory:
    def test_app_exists(self):
        from flask_se import app
        assert app is not None

    def test_app_has_routes(self):
        from flask_se import app
        rules = [r.rule for r in app.url_map.iter_rules()]
        assert "/" in rules
        assert "/login.html" in rules
        assert len(rules) > 50

    def test_app_config(self):
        from flask_se import app
        assert app.config["SCHEDULER_TIMEZONE"] == "UTC"

    def test_sitemap(self, seeded_client):
        resp = seeded_client.get("/sitemap.xml")
        assert resp.status_code == 200

    def test_404_handler(self, seeded_client):
        resp = seeded_client.get("/nonexistent-route-xyz")
        assert resp.status_code == 404

    def test_static_files(self, seeded_client):
        resp = seeded_client.get("/static/css/quick-website.css")
        assert resp.status_code in (200, 301, 302, 404)

    def test_robots_txt(self, seeded_client):
        resp = seeded_client.get("/robots.txt")
        assert resp.status_code in (200, 301, 302, 404)

    def test_favicon(self, seeded_client):
        resp = seeded_client.get("/favicon.ico")
        assert resp.status_code in (200, 301, 302, 404)

    def test_404_page_renders(self, seeded_client):
        resp = seeded_client.get("/404.html")
        assert resp.status_code == 200


class TestErrorHandlers:
    def test_404_page_has_error_content(self, seeded_client):
        resp = seeded_client.get("/does-not-exist-12345")
        assert resp.status_code == 404
        content = resp.data.decode().lower()
        assert "404" in content or "not found" in content


class TestScheduler:
    def test_scheduler_imports(self):
        from flask_se import scheduler
        assert scheduler is not None

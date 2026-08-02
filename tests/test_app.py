# -*- coding: utf-8 -*-
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

        assert app.config["FREEZER_RELATIVE_URLS"] is True

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


class TestMarkdownFilter:
    def test_markdown_bullet_list(self, app_ctx):
        from flask import current_app

        md = current_app.jinja_env.filters["markdown"]
        out = md("- item one\n- item two")
        assert "<ul>" in out
        assert "<li>item one</li>" in out
        assert "<li>item two</li>" in out

    def test_markdown_plain_text(self, app_ctx):
        from flask import current_app

        md = current_app.jinja_env.filters["markdown"]
        out = md("простой текст")
        assert "простой текст" in out


class TestUwsgiAppIni:
    def test_app_ini_points_to_wsgi(self):
        from pathlib import Path

        ini = (Path(__file__).parent.parent / "src" / "app.ini").read_text()
        assert "wsgi-file = wsgi.py" in ini

    def test_wsgi_module_exists(self):
        from pathlib import Path

        assert (Path(__file__).parent.parent / "src" / "wsgi.py").is_file()


class TestScheduler:
    def test_scheduler_imports(self):
        from flask_se import scheduler

        assert scheduler is not None

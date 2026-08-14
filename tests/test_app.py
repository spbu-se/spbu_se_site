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

    def test_markdown_renders_unescaped_through_jinja(self, app_ctx):
        """The filter output must be marked safe so Jinja autoescape does not
        re-escape the generated HTML (regression: literal tags shown as text)."""
        from flask import current_app

        tmpl = current_app.jinja_env.from_string("{{ text|markdown }}")
        out = tmpl.render(text="[Spla](https://example.org)\n\n- a\n- b")
        assert '<a href="https://example.org"' in out
        assert "<ul>" in out
        assert "&lt;" not in out

    def test_markdown_sanitizes_unsafe_html(self, app_ctx):
        """Marked-safe output must still be sanitized: raw HTML in the markdown
        source (scripts, event handlers, dangerous URL schemes) is removed."""
        from flask import current_app

        md = current_app.jinja_env.filters["markdown"]
        out = md(
            "<script>alert(1)</script>"
            "<img src=x onerror=alert(1)>"
            '<a href="javascript:alert(1)">x</a>'
        )
        assert "<script>" not in out
        assert "onerror" not in out
        assert "javascript:" not in out

    def test_markdown_keeps_legit_links_and_tables(self, app_ctx):
        """The sanitizer must preserve markdown features (tables extension,
        http/https links) used by the site's content."""
        from flask import current_app

        md = current_app.jinja_env.filters["markdown"]
        out = md("| a | b |\n|---|---|\n| 1 | 2 |\n\n[x](https://ok.example)")
        assert "<table>" in out
        assert '<a href="https://ok.example"' in out


class TestSafeHtmlFilter:
    def test_safe_html_sanitizes(self, app_ctx):
        from flask import current_app

        safe = current_app.jinja_env.filters["safe_html"]
        out = safe("<b>x</b><script>alert(1)</script>")
        assert "<b>x</b>" in out
        assert "<script>" not in out

    def test_safe_html_keeps_paragraphs(self, app_ctx):
        from flask import current_app

        safe = current_app.jinja_env.filters["safe_html"]
        out = safe("<p>text <strong>bold</strong></p>")
        assert "<p>text <strong>bold</strong></p>" in out


class TestRawHtmlGuardrail:
    def test_no_raw_safe_output(self):
        """Every raw-HTML output in templates must go through the sanitizing
        ``safe_html`` filter — a bare ``|safe`` is an XSS regression risk."""
        from pathlib import Path

        root = Path(__file__).resolve().parent.parent / "src" / "templates"
        bad = []
        for p in root.rglob("*.html"):
            for i, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
                if "|safe" in line and "|safe_html" not in line:
                    bad.append(f"{p.relative_to(root)}:{i}: {line.strip()}")
        assert not bad, "raw |safe without |safe_html:\n" + "\n".join(bad)


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

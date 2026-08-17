# -*- coding: utf-8 -*-
"""Long-term cache headers for app-served static assets (perf/fa-subset).

The host nginx is a pure reverse proxy, so the immutable/30-day cache headers
are set by the app for /assets/*. Pages and other static files stay no-cache.
"""

IMMUTABLE = "public, max-age=31536000, immutable"
IMG_CACHE = "public, max-age=2592000"


class TestAssetCacheHeaders:
    def test_css_immutable(self, client):
        resp = client.get("/assets/css/quick-website.css")
        assert resp.status_code == 200
        assert resp.headers["Cache-Control"] == IMMUTABLE

    def test_js_immutable(self, client):
        resp = client.get("/assets/js/se_scripts.js")
        assert resp.status_code == 200
        assert resp.headers["Cache-Control"] == IMMUTABLE

    def test_libs_immutable(self, client):
        resp = client.get("/assets/libs/jquery/dist/jquery.min.js")
        assert resp.status_code == 200
        assert resp.headers["Cache-Control"] == IMMUTABLE

    def test_img_30_day_cap(self, client):
        resp = client.get("/assets/img/mm.jpg")
        assert resp.status_code == 200
        assert resp.headers["Cache-Control"] == IMG_CACHE

    def test_versioned_url_path_unchanged(self, client):
        resp = client.get("/assets/css/quick-website.css?v=2026-08-17")
        assert resp.headers["Cache-Control"] == IMMUTABLE


class TestNonAssetsStayUncached:
    def test_homepage_not_cached(self, client):
        resp = client.get("/")
        cc = resp.headers.get("Cache-Control", "")
        assert "immutable" not in cc
        assert "max-age=2592000" not in cc

    def test_root_static_file_not_cached(self, client):
        resp = client.get("/llms.txt")
        assert resp.status_code == 200
        assert "immutable" not in resp.headers.get("Cache-Control", "")

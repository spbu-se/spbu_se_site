# -*- coding: utf-8 -*-
"""Long-term cache headers for app-served static assets (perf/fa-subset).

The host nginx is a pure reverse proxy, so the immutable/30-day cache headers
are set by the app for /assets/*. Pages and other static files stay no-cache.
"""

import pytest

IMMUTABLE = "public, max-age=31536000, immutable"
IMG_CACHE = "public, max-age=2592000"


class TestAssetCacheHeaders:
    @pytest.mark.parametrize(
        ("path", "expected_cc"),
        [
            ("/assets/css/quick-website.css", IMMUTABLE),
            ("/assets/js/se_scripts.js", IMMUTABLE),
            ("/assets/libs/jquery/dist/jquery.min.js", IMMUTABLE),
            ("/assets/img/mm.jpg", IMG_CACHE),
            ("/assets/css/quick-website.css?v=2026-08-17", IMMUTABLE),
        ],
    )
    def test_asset_cache_header(self, client, path, expected_cc):
        resp = client.get(path)
        assert resp.status_code == 200
        assert resp.headers["Cache-Control"] == expected_cc


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

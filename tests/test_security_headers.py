# SPDX-License-Identifier: Apache-2.0
"""Security-header guardrails (docs/SEO_A11Y_ROADMAP.md §CSP + security headers).

Every response (HTML page, static asset, error page) carries the security
headers set by `flask_se_headers.register_security_headers`. These tests pin
the strict nonce-CSP and the HTTPS-only directives' gate on
`SE_COOKIE_SECURE`, and assert `Cross-Origin-Resource-Policy` stays omitted.
"""

import pytest

import flask_se_headers


class TestHeaderPresence:
    def test_page_sets_security_headers(self, seeded_client):
        resp = seeded_client.get("/")
        assert resp.status_code == 200
        assert resp.headers["X-Content-Type-Options"] == "nosniff"
        assert resp.headers["X-Frame-Options"] == "DENY"
        assert resp.headers["Referrer-Policy"] == "strict-origin-when-cross-origin"
        assert resp.headers["Permissions-Policy"] == flask_se_headers.PERMISSIONS_POLICY
        assert resp.headers["Cross-Origin-Opener-Policy"] == "same-origin"

    def test_static_asset_sets_security_headers(self, seeded_client):
        resp = seeded_client.get("/assets/css/quick-website.min.css")
        assert resp.status_code in (200, 301, 302, 404)
        if resp.status_code == 200:
            assert resp.headers["Content-Security-Policy"]
            assert resp.headers["X-Content-Type-Options"] == "nosniff"

    def test_404_sets_security_headers(self, seeded_client):
        resp = seeded_client.get("/definitely-not-a-page-xyz")
        assert resp.status_code == 404
        assert resp.headers["Content-Security-Policy"]
        assert resp.headers["X-Frame-Options"] == "DENY"

    def test_corp_omitted(self, seeded_client):
        resp = seeded_client.get("/")
        assert "Cross-Origin-Resource-Policy" not in resp.headers


class TestCspAllowlist:
    def test_homepage_csp_is_allowlist(self, seeded_client):
        csp = seeded_client.get("/").headers["Content-Security-Policy"]
        assert "default-src 'self'" in csp
        assert "object-src 'none'" in csp
        assert "base-uri 'self'" in csp
        assert "form-action 'self'" in csp
        assert "frame-ancestors 'self'" in csp
        assert "googletagmanager.com" not in csp
        assert "topbar.spbu.ru" not in csp
        assert "mc.yandex.ru" in csp
        assert "api-maps.yandex.ru" in csp
        assert "maps.googleapis.com" in csp
        assert "report-uri /csp-report" in csp

    def test_no_unsafe_inline_in_script_src(self, seeded_client):
        csp = seeded_client.get("/").headers["Content-Security-Policy"]
        script_src = csp.split("script-src")[1].split(";")[0]
        assert "'unsafe-inline'" not in script_src
        assert "nonce-" in csp

    def test_csp_string_has_https_only_upgrade(self, seeded_client, monkeypatch):
        monkeypatch.setenv("SE_COOKIE_SECURE", "1")
        csp_secure = seeded_client.get("/").headers["Content-Security-Policy"]
        assert "; upgrade-insecure-requests" in csp_secure

        monkeypatch.setenv("SE_COOKIE_SECURE", "0")
        csp_dev = seeded_client.get("/").headers["Content-Security-Policy"]
        assert "; upgrade-insecure-requests" not in csp_dev


class TestHttpsGate:
    @pytest.mark.parametrize(
        ("secure_flag", "expected_hsts"),
        [
            ("1", "max-age=31536000; includeSubDomains"),
            ("0", None),
        ],
    )
    def test_hsts_and_upgrade_gated_on_secure_flag(
        self, seeded_client, monkeypatch, secure_flag, expected_hsts
    ):
        monkeypatch.setenv("SE_COOKIE_SECURE", secure_flag)
        resp = seeded_client.get("/")
        if expected_hsts is None:
            assert "Strict-Transport-Security" not in resp.headers
            assert "upgrade-insecure-requests" not in resp.headers["Content-Security-Policy"]
        else:
            assert resp.headers["Strict-Transport-Security"] == expected_hsts
            assert "upgrade-insecure-requests" in resp.headers["Content-Security-Policy"]

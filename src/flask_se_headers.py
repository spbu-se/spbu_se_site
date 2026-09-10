# SPDX-License-Identifier: Apache-2.0

import os
import secrets

from flask import Flask, g

# Security headers, set on every response via `after_request`. nginx only sets
# `server_tokens off`; content headers come from Flask so there is no
# double-header risk (see `docs/SEO_A11Y_ROADMAP.md` §CSP + security headers).
#
# Strict nonce-CSP (v2026.08.+): every inline <script> carries a per-request
# nonce; `'unsafe-inline'` is absent from script-src. 'unsafe-eval' remains
# (three external services + one bundled lib require eval at runtime:
#  svg-injector.min.js via new Function(); Yandex Metrica; Yandex Maps v3
#  module loader; Google Maps callback system). Google Tag Manager was
#  removed in v2026.08.20, so `googletagmanager.com` is deliberately absent.
# The SPbU topbar was removed in v2026.08.31 — `topbar.spbu.ru/loader.js`
# returns HTTP 410 Gone (SPbU retired the service) — so `topbar.spbu.ru` is
# deliberately absent from script-src and connect-src (see
# docs/SPBU_REGULATIONS.md §3.1.9: only the header link to spbu.ru is
# mandated, and that is satisfied by the navbar SPbU logo link).
# Yandex Metrica (`mc.yandex.ru`) is consent-gated (see
# docs/PRIVACY_COMPLIANCE.md) and only loads on pages where the visitor
# accepted the `statistics` category. Maps hosts cover the Yandex v3 API
# (+ its `*.maps.yandex.net` module/tile loader) and the Google Maps API;
# map tiles themselves are covered by the https-wildcard `img-src`.
#
# CSP violation reports: POST /csp-report (Content-Type: application/csp-report
# or application/json). Logged via app.logger.warning with rate-limiting
# (100 req/min per IP).
_CSP_BASE = (
    "default-src 'self'; "
    "script-src 'self' 'nonce-{nonce}' 'unsafe-eval' "
    "https://mc.yandex.ru "
    "https://api-maps.yandex.ru https://*.maps.yandex.net "
    "https://maps.googleapis.com https://*.googleapis.com "
    "https://smartcaptcha.yandexcloud.net; "
    "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
    "img-src 'self' data: https:; "
    "font-src 'self' data: https://fonts.gstatic.com; "
    "connect-src 'self' "
    "https://mc.yandex.ru "
    "https://api-maps.yandex.ru https://*.maps.yandex.net "
    "https://maps.googleapis.com https://*.googleapis.com "
    "https://smartcaptcha.yandexcloud.net; "
    "frame-src 'self' https://smartcaptcha.yandexcloud.net; "
    "object-src 'none'; "
    "base-uri 'self'; "
    "form-action 'self'; "
    "frame-ancestors 'self'; "
    "upgrade-insecure-requests; "
    "report-uri /csp-report"
)

PERMISSIONS_POLICY = "camera=(), microphone=(), geolocation=(), payment=(), usb=()"


def _secure_enabled() -> bool:
    """HTTPS is on when ``SE_COOKIE_SECURE`` is not explicitly disabled."""
    return os.environ.get("SE_COOKIE_SECURE", "1") == "1"


def _set_csp_nonce() -> None:
    g.csp_nonce = secrets.token_urlsafe(16)


def _build_csp() -> str:
    """CSP with the current request's nonce. Drops `upgrade-insecure-requests`
    when not behind TLS (mirrors the SESSION_COOKIE_SECURE gate)."""
    nonce = getattr(g, "csp_nonce", secrets.token_urlsafe(16))
    csp = _CSP_BASE.format(nonce=nonce)
    if not _secure_enabled():
        csp = csp.replace("; upgrade-insecure-requests", "")
    return csp


def register_security_headers(app: Flask) -> None:
    """Attach security headers and CSP reporting to every response."""

    app.before_request(_set_csp_nonce)

    @app.after_request
    def _set_security_headers(response):  # pyright: ignore[reportUnusedFunction]
        if _secure_enabled():
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = _build_csp()
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = PERMISSIONS_POLICY
        response.headers["Cross-Origin-Opener-Policy"] = "same-origin"
        # Cross-Origin-Resource-Policy is deliberately omitted: blocking it
        # would break cross-site og-image hotlinking.
        return response

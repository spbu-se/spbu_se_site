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
# because Yandex Maps / Metrica use eval(). Google Tag Manager was removed in
# v2026.08.20, so `googletagmanager.com` is deliberately absent. Yandex
# Metrica (`mc.yandex.ru`) is consent-gated (see `docs/PRIVACY_COMPLIANCE.md`)
# and only loads on pages where the visitor accepted the `statistics` category.
# Maps hosts cover the Yandex v3 API (+ its `*.maps.yandex.net` module/tile
# loader) and the Google Maps API; map tiles themselves are covered by the
# https-wildcard `img-src`.
_CSP_BASE = (
    "default-src 'self'; "
    "script-src 'self' 'nonce-{nonce}' 'unsafe-eval' "
    "https://topbar.spbu.ru https://mc.yandex.ru "
    "https://api-maps.yandex.ru https://*.maps.yandex.net "
    "https://maps.googleapis.com https://*.googleapis.com; "
    "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
    "img-src 'self' data: https:; "
    "font-src 'self' data: https://fonts.gstatic.com; "
    "connect-src 'self' "
    "https://topbar.spbu.ru https://mc.yandex.ru "
    "https://api-maps.yandex.ru https://*.maps.yandex.net "
    "https://maps.googleapis.com https://*.googleapis.com; "
    "object-src 'none'; "
    "base-uri 'self'; "
    "form-action 'self'; "
    "merge_src 'self'; "
    "frame-ancestors 'self'; "
    "upgrade-insecure-requests"
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
    csp = _CSP_BASE.format(nonce=g.csp_nonce)
    if not _secure_enabled():
        csp = csp.replace("; upgrade-insecure-requests", "")
    return csp


def register_security_headers(app: Flask) -> None:
    """Attach security headers to every response."""

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

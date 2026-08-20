# SPDX-License-Identifier: Apache-2.0

import os

from flask import Flask

# Security headers, set on every response via `after_request`. nginx only sets
# `server_tokens off`; content headers come from Flask so there is no
# double-header risk (see `docs/SEO_A11Y_ROADMAP.md` §CSP + security headers).
#
# Allowlist CSP (Option B): strict nonce-CSP is deferred — 15 templates carry
# inline scripts and Google Maps (when provisioned) requires 'unsafe-inline'/
# 'unsafe-eval'. Google Tag Manager was removed in v2026.08.20, so
# `googletagmanager.com` is deliberately absent. Yandex Metrica (`mc.yandex.ru`)
# is consent-gated (see `docs/PRIVACY_COMPLIANCE.md`) and only loads on pages
# where the visitor accepted the `statistics` category. Maps hosts cover the
# Yandex v3 API (+ its `*.maps.yandex.net` module/tile loader) and the Google
# Maps API; map tiles themselves are covered by the https-wildcard `img-src`.
CSP = (
    "default-src 'self'; "
    "script-src 'self' 'unsafe-inline' 'unsafe-eval' "
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
    "frame-ancestors 'self'; "
    "upgrade-insecure-requests"
)

# Drop the HTTPS-only directives when not running behind TLS (dev on plain
# HTTP must not upgrade its own subresources or advertise HSTS). Mirrors the
# SESSION_COOKIE_SECURE gate in `flask_se.py`.
_UPGRADE_DIRECTIVE = "; upgrade-insecure-requests"
CSP_DEV = CSP.replace(_UPGRADE_DIRECTIVE, "")

PERMISSIONS_POLICY = "camera=(), microphone=(), geolocation=(), payment=(), usb=()"


def _secure_enabled() -> bool:
    """HTTPS is on when ``SE_COOKIE_SECURE`` is not explicitly disabled."""
    return os.environ.get("SE_COOKIE_SECURE", "1") == "1"


def register_security_headers(app: Flask) -> None:
    """Attach security headers to every response."""

    @app.after_request
    def _set_security_headers(response):  # pyright: ignore[reportUnusedFunction]
        if _secure_enabled():
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
            csp = CSP
        else:
            csp = CSP_DEV
        response.headers["Content-Security-Policy"] = csp
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = PERMISSIONS_POLICY
        response.headers["Cross-Origin-Opener-Policy"] = "same-origin"
        # Cross-Origin-Resource-Policy is deliberately omitted: blocking it
        # would break cross-site og-image hotlinking.
        return response

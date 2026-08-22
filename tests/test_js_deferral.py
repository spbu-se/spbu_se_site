# -*- coding: utf-8 -*-
"""Guardrail for the JS deferral / SE_ON_READY work (perf/js-defer).

Core scripts (jquery, bootstrap, the theme bundle, first-party scripts) are
loaded with `defer` so the parser is not blocked, while document order is
preserved (deferred scripts execute in order, before DOMContentLoaded).

These tests protect the contract:

- jquery/bootstrap/theme/first-party scripts carry `defer` in all 4 bases and
  are ordered (jquery before bootstrap before quick-website before se_scripts);
- every base defines the SE_ON_READY helper (`seReady`) that content-block
  inline scripts use instead of `$(document).ready`, since deferred jquery is
  not available while the inline scripts parse;
- no template still calls `$(document).ready` / `$()` inline at parse time;
- libs loaded in the light bases (bootstrap-notify, flatpickr,
  se_practice_script.js) are also deferred;
- the maps lazy loader (se_maps.js) stays deferred.
"""

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = REPO_ROOT / "src" / "templates"

BASES = [
    "base_dark.html",
    "base_dark_footer_white.html",
    "base_light.html",
    "base_light_footer_white.html",
]

CORE_SCRIPTS = [
    "libs/jquery/dist/jquery.min.js",
    "libs/bootstrap/dist/js/bootstrap.bundle.min.js",
    "js/quick-website.min.js",
    "js/se_scripts.js",
]


def _script_src_attrs(text: str) -> list[tuple[str, str]]:
    """Return (script-src, attributes-block) pairs for `<script src=...>` tags."""
    return [
        (m.group(1), m.group(2))
        for m in re.finditer(r"<script\s+src=\"\{\{ asset\('([^']+)'\) \}\}\"([^>]*)>", text)
    ]


class TestCoreScriptsDeferred:
    def test_all_bases_defer_core_scripts(self):
        for base in BASES:
            text = (TEMPLATES_DIR / base).read_text(encoding="utf-8")
            attrs = dict(_script_src_attrs(text))
            missing = [s for s in CORE_SCRIPTS if s not in attrs]
            assert not missing, f"{base} missing core scripts: {missing}"
            for src, attr in _script_src_attrs(text):
                if src in CORE_SCRIPTS:
                    assert "defer" in attr, f"{base}: {src} is not deferred: '{attr}'"

    def test_core_scripts_preserve_document_order(self):
        for base in BASES:
            text = (TEMPLATES_DIR / base).read_text(encoding="utf-8")
            order = [src for src, _ in _script_src_attrs(text)]
            idx = [order.index(s) for s in CORE_SCRIPTS]
            assert idx == sorted(idx), (
                f"{base}: core scripts out of order: {order}. "
                "defer preserves document order, so jquery must precede "
                "bootstrap, the theme bundle, and se_scripts.js."
            )


class TestLightBaseLibsDeferred:
    @pytest.mark.parametrize(
        ("base", "libs"),
        [
            (
                "base_light.html",
                [
                    "libs/bootstrap-notify/bootstrap-notify.min.js",
                    "libs/flatpickr/dist/flatpickr.min.js",
                    "js/se_practice_script.js",
                ],
            ),
            ("base_light_footer_white.html", ["libs/bootstrap-notify/bootstrap-notify.min.js"]),
        ],
    )
    def test_light_base_deferred_libs(self, base, libs):
        text = (TEMPLATES_DIR / base).read_text(encoding="utf-8")
        attrs = dict(_script_src_attrs(text))
        for src in libs:
            assert src in attrs, f"{base} missing {src}"
            assert "defer" in attrs[src], f"{base}: {src} not deferred: '{attrs[src]}'"


class TestSEOnReadyHelper:
    @pytest.mark.parametrize("base", BASES)
    def test_se_ready_defined_in_head_before_content(self, base):
        text = (TEMPLATES_DIR / base).read_text(encoding="utf-8")
        assert "SE_ON_READY" in text, f"{base} missing SE_ON_READY helper"
        assert re.search(r"function\s+seReady\(", text), f"{base} missing `function seReady(...)`"
        helper_at = text.index("seReady")
        content_at = text.index("block content")
        assert helper_at < content_at, (
            f"{base}: seReady defined after content block; inline scripts "
            "in content would call an undefined seReady"
        )


class TestNoInlineJquery:
    def test_no_template_uses_document_ready(self):
        offenders = [
            f"{p.relative_to(REPO_ROOT)}:{m.start()}"
            for p in TEMPLATES_DIR.rglob("*.html")
            if "curriculum.html" not in p.name
            for m in re.finditer(r"\$\(\s*document\s*\)\s*\.ready", p.read_text(encoding="utf-8"))
        ]
        assert not offenders, (
            f"inline $(document).ready is unsupported now that jquery is deferred: "
            f"{offenders}. Use seReady(...) instead."
        )

    def test_no_inline_jquery_calls_in_templates(self):
        """No template calls `$()`/`$.` at parse time (except Plotly bundles)."""
        offenders = []
        for p in TEMPLATES_DIR.rglob("*.html"):
            if "curriculum.html" in p.name:
                continue
            text = p.read_text(encoding="utf-8")
            offenders.extend(
                f"{p.relative_to(REPO_ROOT)}:{text[: m.start()].count(chr(10)) + 1}"
                for m in re.finditer(r"\$\s*\(|\$\s*\.|jQuery\(", text)
            )
        assert not offenders, (
            f"inline jquery calls found (deferred jquery is not loaded at parse time): {offenders}"
        )


class TestMapsStaysDeferred:
    def test_se_maps_js_deferred_in_base_dark(self):
        text = (TEMPLATES_DIR / "base_dark.html").read_text(encoding="utf-8")
        attrs = dict(_script_src_attrs(text))
        src = "js/se_maps.js"
        assert src in attrs, "base_dark missing se_maps.js"
        assert "defer" in attrs[src], f"base_dark: se_maps.js not deferred: '{attrs[src]}'"

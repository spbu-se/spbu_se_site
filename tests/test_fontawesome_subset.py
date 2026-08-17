# -*- coding: utf-8 -*-
"""Guardrail for the Font Awesome subset (perf/fa-subset).

The subset CSS + woff2 are hand-generated. If a template starts using a new
`fas fa-*` icon, these tests fail and the subset must be regenerated (command
in the fa-subset.css header).
"""

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = REPO_ROOT / "src" / "templates"
SUBSET_CSS = REPO_ROOT / "src" / "static" / "assets" / "css" / "fa-subset.css"
SUBSET_WOFF2 = SUBSET_CSS.parent / "fa-solid-subset.woff2"


def _icons_in_templates():
    icons = set()
    for p in TEMPLATES_DIR.rglob("*.html"):
        text = p.read_text(encoding="utf-8")
        for m in re.finditer(r'\bclass="[^"]*\bfas fa-([a-z0-9-]+)', text):
            icons.add(m.group(1))
    return icons


def _icons_in_css():
    css = SUBSET_CSS.read_text(encoding="utf-8")
    return set(re.findall(r"\.fa-([a-z0-9-]+):before", css))


class TestSubsetCompleteness:
    def test_every_used_icon_is_subsetted(self):
        used = _icons_in_templates()
        assert used, "no fas fa-* icons found in templates (scan broken?)"
        missing = used - _icons_in_css()
        assert not missing, (
            f"icons used in templates but missing from fa-subset.css: {sorted(missing)}. "
            "Regenerate the subset (see fa-subset.css header)."
        )

    def test_subset_has_no_unused_icons(self):
        used = _icons_in_templates()
        extra = _icons_in_css() - used
        assert not extra, f"fa-subset.css defines icons not used by any template: {sorted(extra)}"

    def test_subset_font_file_exists(self):
        assert SUBSET_WOFF2.exists(), "fa-solid-subset.woff2 missing"
        assert SUBSET_WOFF2.stat().st_size > 0

    def test_subset_css_references_font(self):
        assert "fa-solid-subset.woff2" in SUBSET_CSS.read_text(encoding="utf-8")


class TestSubsetInPages:
    def test_homepage_does_not_load_font_awesome(self, seeded_client):
        body = seeded_client.get("/").get_data(as_text=True)
        assert "all.min.css" not in body
        assert "fa-subset.css" not in body

    def test_fa_page_loads_subset(self, seeded_client):
        body = seeded_client.get("/theses.html").get_data(as_text=True)
        assert "fa-subset.css" in body
        assert "all.min.css" not in body

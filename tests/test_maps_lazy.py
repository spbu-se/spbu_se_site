# -*- coding: utf-8 -*-
"""Guardrail for lazy-loaded Google Maps (perf/maps-lazy).

The Maps JS API is no longer loaded synchronously in the bases. quick-website.js
registers its map initializers into `window.__seMaps` instead of touching
`google.maps` at parse time; js/se_maps.js injects the API when a map element
scrolls into view. These tests protect the structural contract:
- no base still carries the synchronous maps `<script>`;
- base_dark wires the key block + the lazy loader;
- the 3 map pages carry the key block;
- the registered initializers exist and no eager `google.maps` trigger remains.
"""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = REPO_ROOT / "src" / "templates"
JS_DIR = REPO_ROOT / "src" / "static" / "assets" / "js"

ALL_BASES = [
    "base_dark.html",
    "base_dark_footer_white.html",
    "base_light.html",
    "base_light_footer_white.html",
]
MAP_PAGES = [
    "index.html",
    "contacts.html",
    "bachelor_admission.html",
]
MAP_IDS = ["map-custom", "map-mm-dormitory", "map-default"]


class TestNoSyncMapsScript:
    def test_no_base_loads_maps_api_synchronously(self):
        for base in ALL_BASES:
            text = (TEMPLATES_DIR / base).read_text(encoding="utf-8")
            assert "maps.googleapis.com" not in text, f"{base} still loads the maps API"

    def test_no_maps_key_leaks_on_non_map_bases(self):
        for base in ALL_BASES:
            text = (TEMPLATES_DIR / base).read_text(encoding="utf-8")
            assert "SE_GMAPS_KEY" not in text, f"{base} sets the maps key globally"


class TestLazyLoaderWiring:
    def test_base_dark_has_key_block_and_loader(self):
        text = (TEMPLATES_DIR / "base_dark.html").read_text(encoding="utf-8")
        assert "{% block se_maps_key %}{% endblock %}" in text
        assert "js/se_maps.js" in text

    def test_map_pages_define_the_key_block(self):
        for page in MAP_PAGES:
            text = (TEMPLATES_DIR / page).read_text(encoding="utf-8")
            assert "{% block se_maps_key %}" in text, f"{page} missing the maps key block"
            assert "se_google_maps_key" in text, f"{page} does not render the configured key"

    def test_se_maps_loader_exists(self):
        loader = JS_DIR / "se_maps.js"
        assert loader.exists()
        text = loader.read_text(encoding="utf-8")
        assert "IntersectionObserver" in text
        assert "__seMaps" in text
        assert "maps.googleapis.com/maps/api/js" in text


class TestInitializersRegistered:
    def test_quick_website_registers_instead_of_eager_init(self):
        text = (JS_DIR / "quick-website.js").read_text(encoding="utf-8")
        assert "addDomListener(window, 'load'" not in text, "an eager google.maps trigger remains"
        for map_id in MAP_IDS:
            assert f"id: '{map_id}'" in text, f"initializer for {map_id} not registered"

    def test_min_js_contains_registration(self):
        text = (JS_DIR / "quick-website.min.js").read_text(encoding="utf-8")
        assert "__seMaps" in text, "min js not rebuilt with the registered initializers"


class TestRenderedPages:
    def test_homepage_renders_lazy_loader_without_sync_api(self, seeded_client):
        body = seeded_client.get("/").get_data(as_text=True)
        assert "js/se_maps.js" in body
        assert "maps.googleapis.com/maps/api/js?key=AIza" not in body
        assert "window.SE_GMAPS_KEY" in body

    def test_news_page_renders_no_maps_loader(self, seeded_client):
        body = seeded_client.get("/news/").get_data(as_text=True)
        assert "se_maps.js" not in body
        assert "maps.googleapis.com" not in body

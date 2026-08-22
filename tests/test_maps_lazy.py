# -*- coding: utf-8 -*-
"""Guardrail for lazy-loaded dual-provider maps (Yandex v3 + Google fallback).

The maps API is never loaded synchronously in the bases. quick-website.js
registers its map initializers into `window.__seMaps` instead of touching
`google.maps`/`ymaps3` at parse time; js/se_maps.js injects the active
provider's API (chosen by `window.SE_MAPS_PROVIDER`, set with the key by the
page) when a map element scrolls into view. These tests protect the structural
contract:
- no base still carries a synchronous maps `<script>` (either provider);
- base_dark wires the key block + the lazy loader;
- the 3 map pages carry the key block and, when no provider is configured,
  render the "map source not set" placeholder;
- the registered initializers exist, dispatch on the active provider, and no
  eager `google.maps`/`ymaps3` trigger remains.
"""

from pathlib import Path

import pytest

import flask_se

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

YANDEX_URL = "api-maps.yandex.ru"
GOOGLE_URL = "maps.googleapis.com/maps/api/js"
PLACEHOLDER = "Источник карты не задан"


@pytest.fixture
def maps_config_none(monkeypatch):
    monkeypatch.setattr(flask_se, "maps_config", lambda: ("", ""))


@pytest.fixture
def maps_config_yandex(monkeypatch):
    monkeypatch.setattr(flask_se, "maps_config", lambda: ("yandex", "test-yandex-key"))


@pytest.fixture
def maps_config_google(monkeypatch):
    monkeypatch.setattr(flask_se, "maps_config", lambda: ("google", "test-google-key"))


class TestNoSyncMapsScript:
    def test_no_base_loads_maps_api_synchronously(self):
        for base in ALL_BASES:
            text = (TEMPLATES_DIR / base).read_text(encoding="utf-8")
            assert GOOGLE_URL not in text, f"{base} still loads the Google Maps API"
            assert YANDEX_URL not in text, f"{base} still loads the Yandex Maps API"

    def test_no_maps_key_leaks_on_non_map_bases(self):
        for base in ALL_BASES:
            text = (TEMPLATES_DIR / base).read_text(encoding="utf-8")
            assert "SE_MAPS_" not in text, f"{base} sets the maps key globally"


class TestLazyLoaderWiring:
    def test_base_dark_has_key_block_and_loader(self):
        import re

        text = (TEMPLATES_DIR / "base_dark.html").read_text(encoding="utf-8")
        assert re.search(r"{% block se_maps_key %}.*?{% endblock %}", text, re.S), (
            "maps key block missing"
        )
        assert "js/se_maps.js" in text

    def test_map_pages_define_the_key_block(self):
        for page in MAP_PAGES:
            text = (TEMPLATES_DIR / page).read_text(encoding="utf-8")
            assert "{% block se_maps_key %}" in text, f"{page} missing the maps key block"
            assert "se_maps_provider" in text, f"{page} does not render the configured provider"
            assert "se_maps_key" in text, f"{page} does not render the configured key"
            assert PLACEHOLDER in text, f"{page} missing the no-provider placeholder"

    def test_se_maps_loader_exists_and_guards(self):
        loader = JS_DIR / "se_maps.js"
        assert loader.exists()
        text = loader.read_text(encoding="utf-8")
        assert "IntersectionObserver" in text
        assert "__seMaps" in text
        assert YANDEX_URL in text, "loader missing the Yandex Maps API URL"
        assert GOOGLE_URL in text, "loader missing the Google Maps API URL"
        assert "ymaps3.ready" in text, "loader must wait for the Yandex API readiness"
        assert "SE_MAPS_PROVIDER" in text
        assert "SE_MAPS_KEY" in text


class TestInitializersRegistered:
    def test_quick_website_registers_instead_of_eager_init(self):
        text = (JS_DIR / "quick-website.js").read_text(encoding="utf-8")
        assert "addDomListener(window, 'load'" not in text, "an eager google.maps trigger remains"
        for map_id in MAP_IDS:
            assert f"id: '{map_id}'" in text, f"initializer for {map_id} not registered"
        assert "SE_MAPS_PROVIDER" in text, "initializers must dispatch on the active provider"
        assert "renderYandex" in text, "Yandex renderer missing"
        assert "renderGoogle" in text, "Google renderer missing"
        assert "ymaps3.YMap" in text, "Yandex renderer must build the map via ymaps3"
        assert "@yandex/ymaps3-default-ui-theme" in text, (
            "Yandex renderer missing the UI theme import"
        )

    def test_min_js_contains_registration(self):
        text = (JS_DIR / "quick-website.min.js").read_text(encoding="utf-8")
        assert "__seMaps" in text, "min js not rebuilt with the registered initializers"


class TestRenderedPages:
    def test_homepage_renders_lazy_loader_without_sync_api(self, seeded_client, maps_config_none):
        body = seeded_client.get("/").get_data(as_text=True)
        assert "js/se_maps.js" in body
        assert GOOGLE_URL not in body
        assert YANDEX_URL not in body
        assert "window.SE_MAPS_PROVIDER" not in body
        assert PLACEHOLDER in body

    @pytest.mark.parametrize(
        ("provider", "key"),
        [("yandex", "test-yandex-key"), ("google", "test-google-key")],
    )
    def test_homepage_renders_configured_provider(self, seeded_client, monkeypatch, provider, key):
        monkeypatch.setattr(flask_se, "maps_config", lambda: (provider, key))
        body = seeded_client.get("/").get_data(as_text=True)
        assert f'window.SE_MAPS_PROVIDER = "{provider}"' in body
        assert f'window.SE_MAPS_KEY = "{key}"' in body
        assert "map-mm-dormitory" in body
        assert PLACEHOLDER not in body

    def test_news_page_renders_no_maps_loader(self, seeded_client, maps_config_none):
        body = seeded_client.get("/news/").get_data(as_text=True)
        assert "se_maps.js" not in body
        assert GOOGLE_URL not in body
        assert YANDEX_URL not in body
        assert PLACEHOLDER not in body

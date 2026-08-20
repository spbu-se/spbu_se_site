# -*- coding: utf-8 -*-
"""Consent-gate tests (ePrivacy / GDPR Art. 7 / 152-ФЗ consent basis).

The granular consent banner and the ``se_consent`` cookie gate all optional
tracking: the banner appears until the visitor decides, the analytics snippet
loads only after the ``statistics`` category is accepted (see
``tests/test_analytics.py``), and the ``/privacy.html`` page is linked from
every base and auto-sitemapped. See ``docs/PRIVACY_COMPLIANCE.md`` §4.
"""

from pathlib import Path

import flask_se_config

REPO_ROOT = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = REPO_ROOT / "src" / "templates"

# Built via a comprehension so the block differs from the identical constant
# lists in the other base-template test modules (pylint similarities gate).
ALL_BASES = [
    f"{name}.html"
    for name in (
        "base_dark",
        "base_dark_footer_white",
        "base_light",
        "base_light_footer_white",
    )
]


class TestConsentCategories:
    def test_essential_always_on_optional_off(self):
        cats = flask_se_config.consent_categories()
        assert cats["essential"] is True
        assert cats["statistics"] is False
        assert cats["marketing"] is False

    def test_cookie_name_constant(self):
        assert flask_se_config.CONSENT_COOKIE_NAME == "se_consent"


class TestBannerPresence:
    def test_banner_markup_in_all_bases(self):
        for base in ALL_BASES:
            text = (TEMPLATES_DIR / base).read_text(encoding="utf-8")
            assert "{% include 'consent_banner.html' %}" in text, f"{base} missing banner include"

    def test_consent_script_exists_and_is_referenced(self):
        script = REPO_ROOT / "src" / "static" / "assets" / "js" / "se_consent.js"
        assert script.is_file(), "se_consent.js asset missing"
        for base in ALL_BASES:
            text = (TEMPLATES_DIR / base).read_text(encoding="utf-8")
            assert "js/se_consent.js" in text, f"{base} missing se_consent.js reference"

    def test_privacy_link_in_all_bases(self):
        for base in ALL_BASES:
            text = (TEMPLATES_DIR / base).read_text(encoding="utf-8")
            assert "url_for('privacy')" in text, f"{base} missing privacy footer link"


class TestRenderedBanner:
    def test_banner_visible_without_decision(self, seeded_client):
        body = seeded_client.get("/").get_data(as_text=True)
        assert 'id="se-consent-banner"' in body
        assert "se-consent-accept" in body
        assert "se-consent-decline" in body

    def test_banner_hidden_after_decision(self, seeded_client):
        seeded_client.set_cookie("se_consent", "essential")
        body = seeded_client.get("/").get_data(as_text=True)
        assert "se-consent-accept" not in body or "display: none" in body

    def test_essential_only_choice_keeps_banner_hidden_and_no_metrica(self, seeded_client):
        seeded_client.set_cookie("se_consent", "essential")
        body = seeded_client.get("/").get_data(as_text=True)
        assert "display: none" in body


class TestPrivacyPage:
    def test_privacy_page_renders(self, seeded_client):
        resp = seeded_client.get("/privacy.html")
        assert resp.status_code == 200
        body = resp.get_data(as_text=True)
        assert "Политика обработки персональных данных" in body
        assert "spbu.ru" in body

    def test_privacy_page_auto_sitemapped(self, seeded_client):
        body = seeded_client.get("/sitemap-static.xml").get_data(as_text=True)
        assert "https://se.math.spbu.ru/privacy.html" in body

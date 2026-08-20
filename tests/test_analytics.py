# -*- coding: utf-8 -*-
"""Guardrail for the GTM removal + config-driven Yandex Metrica wiring.

GTM (`GTM-NGT2J3Z`) was removed from every template as the GDPR/152-ФЗ
mitigation release (see `docs/PRIVACY_COMPLIANCE.md`). Yandex Metrica is the
only analytics provider allowed; its counter id comes from the gitignored
`configs/flask_se_metrica.conf` or the `SE_YANDEX_METRICA_ID` env var and is
rendered only when a digit-only id is configured — an unconfigured site makes
zero analytics requests. These tests protect the structural contract:
- no base (or any HTML template) carries a GTM reference;
- every base gates the Metrica snippet behind `se_metrica_id`;
- `metrica_id()` returns "" for missing/invalid values and digits otherwise;
- a rendered page includes the Metrica snippet only when an id is configured.
"""

from pathlib import Path

import pytest

import flask_se
import flask_se_config

REPO_ROOT = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = REPO_ROOT / "src" / "templates"

ALL_BASES = [
    "base_dark.html",
    "base_dark_footer_white.html",
    "base_light.html",
    "base_light_footer_white.html",
]

GTM_MARKERS = ["googletagmanager", "GTM-", "dataLayer"]
METRICA_URL = "mc.yandex.ru"


class TestGtmRemoved:
    def test_no_base_mentions_gtm(self):
        for base in ALL_BASES:
            text = (TEMPLATES_DIR / base).read_text(encoding="utf-8")
            for marker in GTM_MARKERS:
                assert marker not in text, f"{base} still contains {marker}"

    def test_no_html_template_mentions_gtm(self):
        for html in TEMPLATES_DIR.rglob("*.html"):
            text = html.read_text(encoding="utf-8")
            for marker in GTM_MARKERS:
                assert marker not in text, f"{html} still contains {marker}"


class TestMetricaWiring:
    def test_every_base_gates_metrica_behind_global(self):
        for base in ALL_BASES:
            text = (TEMPLATES_DIR / base).read_text(encoding="utf-8")
            assert "{% if se_metrica_id %}" in text, f"{base} missing the metrica gate"
            assert METRICA_URL in text, f"{base} missing the metrica snippet"
            assert "{{ se_metrica_id }}" in text, f"{base} missing the counter interpolation"


class TestMetricaConfig:
    def test_empty_when_no_file_and_no_env(self, monkeypatch, tmp_path):
        monkeypatch.delenv("SE_YANDEX_METRICA_ID", raising=False)
        monkeypatch.setattr(flask_se_config, "METRICA_ID_FILE", str(tmp_path / "absent.conf"))
        assert flask_se_config.metrica_id() == ""

    def test_reads_digits_from_file(self, monkeypatch, tmp_path):
        conf = tmp_path / "metrica.conf"
        conf.write_text(" 48234321 \n", encoding="utf-8")
        monkeypatch.delenv("SE_YANDEX_METRICA_ID", raising=False)
        monkeypatch.setattr(flask_se_config, "METRICA_ID_FILE", str(conf))
        assert flask_se_config.metrica_id() == "48234321"

    def test_rejects_non_digits(self, monkeypatch, tmp_path):
        conf = tmp_path / "metrica.conf"
        conf.write_text("id=123;alert(1)\n", encoding="utf-8")
        monkeypatch.delenv("SE_YANDEX_METRICA_ID", raising=False)
        monkeypatch.setattr(flask_se_config, "METRICA_ID_FILE", str(conf))
        assert flask_se_config.metrica_id() == ""

    def test_env_overrides_file(self, monkeypatch, tmp_path):
        conf = tmp_path / "metrica.conf"
        conf.write_text("111\n", encoding="utf-8")
        monkeypatch.setenv("SE_YANDEX_METRICA_ID", "222")
        monkeypatch.setattr(flask_se_config, "METRICA_ID_FILE", str(conf))
        assert flask_se_config.metrica_id() == "222"


@pytest.fixture
def metrica_none(monkeypatch):
    monkeypatch.setattr(flask_se, "metrica_id", lambda: "")


@pytest.fixture
def metrica_set(monkeypatch):
    monkeypatch.setattr(flask_se, "metrica_id", lambda: "48234321")


class TestRenderedPages:
    def test_homepage_has_no_analytics_without_id(self, seeded_client, metrica_none):
        body = seeded_client.get("/").get_data(as_text=True)
        assert METRICA_URL not in body
        assert "ym(" not in body

    def test_homepage_renders_metrica_with_id(self, seeded_client, metrica_set):
        body = seeded_client.get("/").get_data(as_text=True)
        assert METRICA_URL in body
        assert 'ym(48234321, "init"' in body
        assert "https://mc.yandex.ru/watch/48234321" in body

    def test_news_page_renders_metrica_with_id(self, seeded_client, metrica_set):
        body = seeded_client.get("/news/").get_data(as_text=True)
        assert METRICA_URL in body
        assert "ym(48234321" in body

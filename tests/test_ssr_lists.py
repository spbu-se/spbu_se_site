# -*- coding: utf-8 -*-
import re

import pytest
from conftest import _make_published_thesis, assert_ok


class TestThesesSsr:
    def test_archive_renders_list_server_side(self, seeded_client):
        _make_published_thesis(name="SSR Thesis", author="SSR Author")
        resp = seeded_client.get("/theses.html")
        html = resp.get_data(as_text=True)
        assert resp.status_code == 200
        assert "SSR Thesis" in html
        assert 'id="ThesisList"' in html

    def test_archive_search_renders_server_side(self, seeded_client):
        _make_published_thesis(name="Android Performance", author="SSR Author")
        resp = seeded_client.get("/theses.html?search=android")
        html = resp.get_data(as_text=True)
        assert resp.status_code == 200
        assert "Android Performance" in html

    def test_archive_pagination_is_crawlable(self, seeded_client):
        for i in range(15):
            _make_published_thesis(name=f"Thesis {i}", author="SSR Author")
        resp = seeded_client.get("/theses.html?page=2")
        html = resp.get_data(as_text=True)
        assert resp.status_code == 200
        assert 'href="/theses.html?page=' in html

    def test_archive_empty_shows_blank(self, seeded_client):
        resp = seeded_client.get("/theses.html?search=zzzzzznomatch")
        html = resp.get_data(as_text=True)
        assert "Работы по выбранным критериям отсутствуют" in html

    def test_fetch_fragment_still_works(self, seeded_client):
        _make_published_thesis(name="SSR Thesis", author="SSR Author")
        assert_ok(seeded_client, "/fetch_theses", code={200})


class TestDiplomasSsr:
    def test_index_renders_themes_server_side(self, seeded_client):
        resp = seeded_client.get("/diplomas/")
        html = resp.get_data(as_text=True)
        assert resp.status_code == 200
        assert 'id="ThemesList"' in html

    def test_fetch_fragment_still_works(self, seeded_client):
        assert_ok(seeded_client, "/diplomas/fetch_themes", code={200})


class TestReviewSsr:
    def test_index_renders_list_server_side(self, seeded_client):
        resp = seeded_client.get("/review/")
        html = resp.get_data(as_text=True)
        assert resp.status_code == 200
        assert 'id="ThesisReviewList"' in html

    def test_fetch_fragment_still_works(self, seeded_client):
        assert_ok(seeded_client, "/review/fetch_thesis_on_review", code={200})


class TestNoContentNoJsFallback:
    @pytest.mark.parametrize(
        ("path", "element_id"),
        [
            ("/theses.html", "ThesisList"),
            ("/diplomas/", "ThemesList"),
            ("/review/", "ThesisReviewList"),
        ],
    )
    def test_list_has_aria_live(self, seeded_client, path, element_id):
        resp = seeded_client.get(path)
        assert f'id="{element_id}" aria-live="polite"' in resp.get_data(as_text=True)


class TestJsGuards:
    def _js(self):
        from pathlib import Path

        return Path("src/static/assets/js/se_scripts.js").read_text(encoding="utf-8")

    @pytest.mark.parametrize(
        ("func_name", "anchor_regex"),
        [
            (
                "theses_load",
                r"let wt_select = document\.getElementById\('worktype'\);",
            ),
            (
                "themes_load",
                r"let themes_level_select = document\.getElementById\('level'\);",
            ),
            ("thesis_on_review_load", r"let thesis_on_review_status_select"),
        ],
    )
    def test_load_skips_rendered_content(self, func_name, anchor_regex):
        js = self._js()
        m = re.search(rf"function {func_name}\(\) \{{(.*?){anchor_regex}", js, re.S)
        assert m is not None
        assert "childElementCount > 0" in m.group(1)

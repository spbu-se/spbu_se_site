# -*- coding: utf-8 -*-
import re

from conftest import assert_ok


def _make_published_thesis(client, name="SSR Thesis"):
    from se_models import Thesis, db

    thesis = Thesis(
        name_ru=name,
        author="SSR Author",
        type_id=2,
        course_id=1,
        publish_year=2024,
        temporary=False,
    )
    db.session.add(thesis)
    db.session.commit()
    return thesis


class TestThesesSsr:
    def test_archive_renders_list_server_side(self, seeded_client):
        _make_published_thesis(seeded_client)
        resp = seeded_client.get("/theses.html")
        html = resp.get_data(as_text=True)
        assert resp.status_code == 200
        assert "SSR Thesis" in html
        assert 'id="ThesisList"' in html

    def test_archive_search_renders_server_side(self, seeded_client):
        _make_published_thesis(seeded_client, name="Android Performance")
        resp = seeded_client.get("/theses.html?search=android")
        html = resp.get_data(as_text=True)
        assert resp.status_code == 200
        assert "Android Performance" in html

    def test_archive_pagination_is_crawlable(self, seeded_client):
        for i in range(15):
            _make_published_thesis(seeded_client, name=f"Thesis {i}")
        resp = seeded_client.get("/theses.html?page=2")
        html = resp.get_data(as_text=True)
        assert resp.status_code == 200
        assert 'href="/theses.html?page=' in html

    def test_archive_empty_shows_blank(self, seeded_client):
        resp = seeded_client.get("/theses.html?search=zzzzzznomatch")
        html = resp.get_data(as_text=True)
        assert "Работы по выбранным критериям отсутствуют" in html

    def test_fetch_fragment_still_works(self, seeded_client):
        _make_published_thesis(seeded_client)
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
    def test_theses_list_has_aria_live(self, seeded_client):
        resp = seeded_client.get("/theses.html")
        assert 'id="ThesisList" aria-live="polite"' in resp.get_data(as_text=True)

    def test_diplomas_list_has_aria_live(self, seeded_client):
        resp = seeded_client.get("/diplomas/")
        assert 'id="ThemesList" aria-live="polite"' in resp.get_data(as_text=True)

    def test_review_list_has_aria_live(self, seeded_client):
        resp = seeded_client.get("/review/")
        assert 'id="ThesisReviewList" aria-live="polite"' in resp.get_data(as_text=True)


class TestJsGuards:
    def _js(self):
        from pathlib import Path

        return Path("src/static/assets/js/se_scripts.js").read_text(encoding="utf-8")

    def test_theses_load_skips_rendered_content(self):
        js = self._js()
        m = re.search(
            r"function theses_load\(\) \{(.*?)let wt_select = document\.getElementById\('worktype'\);",
            js,
            re.S,
        )
        assert m is not None
        assert "childElementCount > 0" in m.group(1)

    def test_themes_load_skips_rendered_content(self):
        js = self._js()
        m = re.search(
            r"function themes_load\(\) \{(.*?)let themes_level_select = document\.getElementById\('level'\);",
            js,
            re.S,
        )
        assert m is not None
        assert "childElementCount > 0" in m.group(1)

    def test_thesis_on_review_load_skips_rendered_content(self):
        js = self._js()
        m = re.search(
            r"function thesis_on_review_load\(\) \{(.*?)let thesis_on_review_status_select",
            js,
            re.S,
        )
        assert m is not None
        assert "childElementCount > 0" in m.group(1)

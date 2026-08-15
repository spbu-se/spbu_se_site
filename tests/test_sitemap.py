# -*- coding: utf-8 -*-
import re

import pytest


def _seed_thesis(client, year, temporary=False):
    from se_models import Thesis, db

    thesis = Thesis(
        name_ru=f"Sitemap thesis {year}",
        author="Sitemap Author",
        type_id=2,
        course_id=1,
        publish_year=year,
        temporary=temporary,
    )
    db.session.add(thesis)
    db.session.commit()
    return thesis.id


class TestSitemapIndex:
    def test_index_uppercase_alias(self, seeded_client):
        resp = seeded_client.get("/Sitemap.xml")
        assert resp.status_code == 200

    def test_index_is_sitemapindex(self, seeded_client):
        resp = seeded_client.get("/sitemap.xml")
        body = resp.get_data(as_text=True)
        assert "<sitemapindex" in body
        assert "sitemap-static.xml" in body

    def test_index_lists_thesis_years(self, seeded_client):
        _seed_thesis(seeded_client, 2023)
        _seed_thesis(seeded_client, 2021)
        body = seeded_client.get("/sitemap.xml").get_data(as_text=True)
        assert "sitemap-theses-2023.xml" in body
        assert "sitemap-theses-2021.xml" in body

    def test_index_excludes_temporary_theses_year(self, seeded_client):
        _seed_thesis(seeded_client, 2024, temporary=True)
        body = seeded_client.get("/sitemap.xml").get_data(as_text=True)
        assert "sitemap-theses-2024.xml" not in body


class TestSitemapStatic:
    def test_static_sitemap_lists_public_pages(self, seeded_client):
        resp = seeded_client.get("/sitemap-static.xml")
        body = resp.get_data(as_text=True)
        assert resp.status_code == 200
        for path in ("/contacts.html", "/theses.html", "/scholarships/1.html"):
            assert path in body

    def test_static_sitemap_excludes_private_pages(self, seeded_client):
        resp = seeded_client.get("/sitemap-static.xml")
        body = resp.get_data(as_text=True)
        for path in (
            "/login.html",
            "/admin/",
            "/fetch_theses",
            "/practice_staff",
            "/google_callback",
        ):
            assert path not in body

    def test_static_lastmod_is_stable(self, seeded_client):
        resp = seeded_client.get("/sitemap-static.xml")
        body = resp.get_data(as_text=True)
        assert re.search(r"<lastmod>(\d{4}-\d{2}-\d{2})</lastmod>", body)


class TestSitemapTheses:
    def test_thesis_sitemap_lists_cards(self, seeded_client):
        thesis_id = _seed_thesis(seeded_client, 2023)
        resp = seeded_client.get("/sitemap-theses-2023.xml")
        body = resp.get_data(as_text=True)
        assert resp.status_code == 200
        assert f"thesis_card?thesis_id={thesis_id}" in body
        assert "<lastmod>2023-12-31</lastmod>" in body

    def test_missing_year_returns_404(self, seeded_client):
        resp = seeded_client.get("/sitemap-theses-1900.xml")
        assert resp.status_code == 404

    @pytest.mark.parametrize("path", ["/sitemap.xml", "/sitemap-static.xml"])
    def test_sitemap_routes_return_xml(self, seeded_client, path):
        resp = seeded_client.get(path)
        assert resp.headers["Content-Type"] == "application/xml"

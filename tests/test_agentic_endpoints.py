# -*- coding: utf-8 -*-
"""Agent-friendly / SEO hygiene endpoints added 2026-08-17."""

import pytest


class TestWellKnown:
    def test_root_llms_served(self, seeded_client):
        resp = seeded_client.get("/llms.txt")
        assert resp.status_code == 200

    def test_security_txt_served(self, seeded_client):
        resp = seeded_client.get("/.well-known/security.txt")
        assert resp.status_code == 200
        assert "mailto:dluciv@spbu.ru" in resp.get_data(as_text=True)


class TestOpenSearch:
    def test_opensearch_description_served(self, seeded_client):
        resp = seeded_client.get("/opensearch.xml")
        assert resp.status_code == 200
        assert "theses.html?search={searchTerms}" in resp.get_data(as_text=True)

    def test_homepage_autodiscovers_search(self, seeded_client):
        body = seeded_client.get("/").get_data(as_text=True)
        assert 'rel="search"' in body
        assert "opensearch.xml" in body


class TestCanonicalRedirects:
    @pytest.mark.parametrize(
        ("path", "target"),
        [
            ("/.well-known/llms.txt", "/llms.txt"),
            ("/security.txt", "/.well-known/security.txt"),
            ("/index.html", "/"),
        ],
    )
    def test_canonical_redirect(self, seeded_client, path, target):
        resp = seeded_client.get(path)
        assert resp.status_code == 301
        assert resp.headers["Location"] == target


class TestSectionIndexes:
    @pytest.mark.parametrize(
        ("path", "target"),
        [
            ("/bachelor/", "/bachelor/software-engineering.html"),
            ("/master/", "/master/software-engineering.html"),
            ("/department/", "/department/staff.html"),
            ("/students/", "/students/index.html"),
        ],
    )
    def test_section_index_redirects(self, seeded_client, path, target):
        resp = seeded_client.get(path)
        assert resp.status_code == 301
        assert resp.headers["Location"] == target


class TestSitemapDedup:
    def test_news_canonical_kept_in_sitemap(self, seeded_client):
        body = seeded_client.get("/sitemap-static.xml").get_data(as_text=True)
        assert "/news/" in body

    def test_news_index_duplicate_removed(self, seeded_client):
        body = seeded_client.get("/sitemap-static.xml").get_data(as_text=True)
        assert "/news/index.html" not in body

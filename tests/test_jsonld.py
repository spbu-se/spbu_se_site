# -*- coding: utf-8 -*-
import json
import re

import pytest


def _jsonld_blocks(resp):
    html = resp.get_data(as_text=True)
    return re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)


def _assert_type(blocks, expected_type):
    for block in blocks:
        data = json.loads(block)
        types = data["@type"] if isinstance(data["@type"], list) else [data["@type"]]
        if expected_type in types:
            return data
    pytest.fail(f"@type {expected_type} not found")


class TestOrganizationJsonLd:
    @pytest.mark.parametrize(
        "path", ["/", "/contacts.html", "/theses.html", "/scholarships/1.html"]
    )
    def test_organization_block_present(self, seeded_client, path):
        blocks = _jsonld_blocks(seeded_client.get(path))
        data = _assert_type(blocks, "EducationalOrganization")
        assert "Кафедра системного программирования" in data["name"]
        assert data["url"] == "https://se.math.spbu.ru/"
        assert data["address"]["addressLocality"] == "Санкт-Петербург"

    def test_blocks_are_valid_json(self, seeded_client):
        for block in _jsonld_blocks(seeded_client.get("/")):
            assert json.loads(block) is not None


class TestWebSiteJsonLd:
    def test_website_search_action(self, seeded_client):
        data = _assert_type(_jsonld_blocks(seeded_client.get("/")), "WebSite")
        assert data["potentialAction"]["@type"] == "SearchAction"
        assert "theses.html?search=" in data["potentialAction"]["target"]


class TestCourseJsonLd:
    @pytest.mark.parametrize(
        "path",
        [
            "/bachelor/software-engineering.html",
            "/bachelor/programming-technology.html",
            "/master/software-engineering.html",
            "/master/information-systems-administration.html",
        ],
    )
    def test_course_block_present(self, seeded_client, path):
        data = _assert_type(_jsonld_blocks(seeded_client.get(path)), "Course")
        assert data["provider"]["@type"] == "EducationalOrganization"


class TestBreadcrumbJsonLd:
    def test_news_post_breadcrumb(self, seeded_client):
        resp = seeded_client.get("/news/item.html?post=1")
        if resp.status_code != 200:
            pytest.skip("news post 1 not seeded")
        data = _assert_type(_jsonld_blocks(resp), "BreadcrumbList")
        assert len(data["itemListElement"]) >= 2
        assert (
            data["itemListElement"][-1]["item"] == "https://se.math.spbu.ru/news/item.html?post=1"
        )

    def test_internship_breadcrumb(self, seeded_client):
        from se_models import Internships

        internship = Internships.query.first()
        if internship is None:
            pytest.skip("no internships seeded")
        resp = seeded_client.get(f"/internships/{internship.id}")
        data = _assert_type(_jsonld_blocks(resp), "BreadcrumbList")
        assert (
            data["itemListElement"][-1]["item"]
            == f"https://se.math.spbu.ru/internships/{internship.id}"
        )

    def test_thesis_card_breadcrumb(self, seeded_client):
        from se_models import Thesis

        thesis = Thesis.query.filter(~Thesis.temporary).first()
        if thesis is None:
            pytest.skip("no published theses seeded")
        resp = seeded_client.get(f"/thesis_card?thesis_id={thesis.id}")
        data = _assert_type(_jsonld_blocks(resp), "BreadcrumbList")
        assert f"thesis_id={thesis.id}" in data["itemListElement"][-1]["item"]


class TestLlmsTxt:
    def test_llms_txt_exists(self, client):
        resp = client.get("/llms.txt")
        assert resp.status_code == 200
        body = resp.get_data(as_text=True)
        assert "Кафедра системного программирования" in body
        assert "https://se.math.spbu.ru/theses.html" in body

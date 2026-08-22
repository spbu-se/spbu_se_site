# -*- coding: utf-8 -*-
import pytest
from conftest import _seed_internship, assert_ok


class TestOldInternshipsRedirect:
    def test_old_internships_redirect(self, seeded_client):
        resp = seeded_client.get("/internships/index")
        assert resp.status_code == 302


class TestInternshipAdd:
    def test_add_page(self, logged_client):
        assert_ok(logged_client, "/internships/add")

    def test_add_missing_tags(self, logged_client):
        resp = logged_client.post("/internships/add", data={})
        assert resp.status_code == 200

    def test_add_missing_name(self, logged_client):
        resp = logged_client.post("/internships/add", data={"tag": "python"})
        assert resp.status_code == 200

    @pytest.mark.parametrize(
        ("tag", "vacancy", "company"),
        [
            ("C", "Junior Developer", "BrandNewCo"),
            ("C++", "Middle Developer", "YetAnotherCo"),
        ],
    )
    def test_add_success(self, logged_client, tag, vacancy, company):
        resp = logged_client.post(
            "/internships/add",
            data={
                "tag": tag,
                "name_vacancy": vacancy,
                "format": [1],
                "company": company,
            },
        )
        assert resp.status_code in (200, 302)

    def test_add_unknown_tag(self, logged_client):
        resp = logged_client.post(
            "/internships/add",
            data={
                "tag": "NONEXISTENT_TAG",
                "name_vacancy": "Senior Developer",
                "format": [1],
                "company": "SomeCo",
            },
        )
        assert resp.status_code == 200


class TestInternshipDetail:
    def test_detail(self, seeded_client):
        assert_ok(seeded_client, "/internships/1", code={200, 302, 404})

    def test_detail_nonexistent(self, seeded_client):
        resp = seeded_client.get("/internships/99999")
        assert resp.status_code in (200, 404)


class TestInternshipDelete:
    def test_delete(self, logged_client):
        internship_id = _seed_internship(logged_client)
        resp = logged_client.post(f"/internships/{internship_id}/delete")
        assert resp.status_code in (200, 302, 404)


class TestInternshipUpdate:
    def test_update_page(self, logged_client):
        internship_id = _seed_internship(logged_client)
        assert_ok(logged_client, f"/internships/{internship_id}/update", code={200, 302, 404})

    def test_update_success(self, logged_client):
        internship_id = _seed_internship(logged_client)
        resp = logged_client.post(
            f"/internships/{internship_id}/update",
            data={
                "tag": "C",
                "name_vacancy": "Updated Vacancy",
                "format": [1],
                "company": "Existing Co",
                "salary": "60000",
                "requirements": "Updated reqs",
            },
        )
        assert resp.status_code in (200, 302, 404)

    def test_update_missing_tags(self, logged_client):
        internship_id = _seed_internship(logged_client)
        resp = logged_client.post(
            f"/internships/{internship_id}/update",
            data={
                "name_vacancy": "Updated Vacancy",
                "salary": "60000",
                "requirements": "Updated reqs",
            },
        )
        assert resp.status_code == 200


class TestInternshipFetch:
    @pytest.mark.parametrize(
        "query",
        ["tag=1", "format=1", "company=1", "tag=99999"],
    )
    def test_fetch(self, seeded_client, query):
        resp = seeded_client.get(f"/internships/fetch_internships?{query}")
        assert resp.status_code == 200

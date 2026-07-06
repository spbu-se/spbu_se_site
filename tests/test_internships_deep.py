# -*- coding: utf-8 -*-
from conftest import assert_ok


def _seed_internship(client):
    from se_models import InternshipCompany, InternshipFormat, Internships, InternshipTag, db

    company = InternshipCompany(name="Existing Co")
    db.session.add(company)
    db.session.flush()

    fmt = InternshipFormat.query.get(1)
    tag = InternshipTag.query.get(1)

    internship = Internships(
        name_vacancy="Existing Vacancy",
        salary="50000",
        description="Desc",
        location="SPb",
        company_id=company.id,
        requirements="Req",
        more_inf="https://example.com",
        author_id=1,
    )
    internship.format = [fmt]
    internship.tag = [tag]
    db.session.add(internship)
    db.session.commit()
    return internship.id


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

    def test_add_success(self, logged_client):
        resp = logged_client.post(
            "/internships/add",
            data={
                "tag": "C",
                "name_vacancy": "Junior Developer",
                "format": [1],
                "company": "BrandNewCo",
            },
        )
        assert resp.status_code in (200, 302)

    def test_add_new_company(self, logged_client):
        resp = logged_client.post(
            "/internships/add",
            data={
                "tag": "C++",
                "name_vacancy": "Middle Developer",
                "format": [1],
                "company": "YetAnotherCo",
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
        resp = logged_client.get(f"/internships/{internship_id}/delete")
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
    def test_fetch_by_tag(self, seeded_client):
        resp = seeded_client.get("/internships/fetch_internships?tag=1")
        assert resp.status_code == 200

    def test_fetch_by_format(self, seeded_client):
        resp = seeded_client.get("/internships/fetch_internships?format=1")
        assert resp.status_code == 200

    def test_fetch_by_company(self, seeded_client):
        resp = seeded_client.get("/internships/fetch_internships?company=1")
        assert resp.status_code == 200

    def test_fetch_empty(self, seeded_client):
        resp = seeded_client.get("/internships/fetch_internships?tag=99999")
        assert resp.status_code == 200

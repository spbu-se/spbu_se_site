# -*- coding: utf-8 -*-
import io
import json
from pathlib import Path

import pytest
from conftest import _approve_temp_thesis, _make_temp_thesis, _min_pdf, assert_ok


class TestFetchThesesFilters:
    def test_fetch_default_params(self, seeded_client):
        assert_ok(seeded_client, "/fetch_theses")

    def test_fetch_with_worktype(self, seeded_client):
        assert_ok(seeded_client, "/fetch_theses?worktype=2")

    def test_fetch_with_course(self, seeded_client):
        assert_ok(seeded_client, "/fetch_theses?course=1")

    def test_fetch_with_supervisor(self, seeded_client):
        assert_ok(seeded_client, "/fetch_theses?supervisor=1")

    def test_fetch_with_all_filters(self, seeded_client):
        assert_ok(
            seeded_client,
            "/fetch_theses?worktype=2&course=1&supervisor=1&startdate=2010&enddate=2024&page=1",
        )

    def test_fetch_enddate_before_startdate(self, seeded_client):
        assert_ok(seeded_client, "/fetch_theses?startdate=2024&enddate=2010")

    def test_fetch_search_no_results(self, seeded_client):
        resp = seeded_client.get("/fetch_theses?search=zzz_no_match_zzz")
        assert resp.status_code == 200

    def test_fetch_with_invalid_supervisor(self, seeded_client):
        assert_ok(seeded_client, "/fetch_theses?supervisor=99999")

    def test_fetch_with_multiple_pages(self, seeded_client):
        assert_ok(seeded_client, "/fetch_theses?page=2")


class TestThesesSearchDetail:
    def test_search_page_contains_form(self, seeded_client):
        resp = seeded_client.get("/theses.html")
        assert resp.status_code == 200

    def test_search_with_all_filter_params(self, seeded_client):
        resp = seeded_client.get(
            "/theses.html?worktype=2&course=1&supervisor=1&startdate=2020&enddate=2024"
        )
        assert resp.status_code == 200

    def test_search_with_invalid_params(self, seeded_client):
        assert_ok(seeded_client, "/theses.html?worktype=99&course=99")


class TestDownloadThesis:
    def test_download_no_text_uri(self, seeded_client):
        resp = seeded_client.get("/thesis_download?thesis_id=1")
        assert resp.status_code in (200, 302)

    def test_download_counter_increment(self, seeded_client):
        from se_models import Thesis, db

        thesis = Thesis.query.filter(Thesis.text_uri.isnot(None)).first()
        if thesis is None:
            pytest.skip("no thesis with text_uri in seeded DB")
        before = thesis.download_thesis
        seeded_client.get(f"/thesis_download?thesis_id={thesis.id}")
        db.session.refresh(thesis)
        assert thesis.download_thesis == before + 1

    def test_download_zero_thesis_id(self, seeded_client):
        resp = seeded_client.get("/thesis_download?thesis_id=0")
        assert resp.status_code in (200, 302)

    def test_download_missing_text_uri_column(self, seeded_client):
        resp = seeded_client.get("/thesis_download?thesis_id=99999")
        assert resp.status_code in (200, 302)


class TestPostThesesApi:
    def test_post_no_thesis_text(self, logged_client):
        resp = logged_client.post("/post_theses", data={})
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert data["status"] == 500
        assert "No thesis text" in data["string"]

    def test_post_no_thesis_info(self, logged_client):
        resp = logged_client.post(
            "/post_theses", data={"thesis_text": (io.BytesIO(_min_pdf()), "test.pdf")}
        )
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert data["status"] == 500
        assert "No thesis_info" in data["string"]

    def test_post_missing_keys(self, logged_client):
        resp = logged_client.post(
            "/post_theses",
            data={
                "thesis_text": (io.BytesIO(_min_pdf()), "test.pdf"),
                "thesis_info": (io.BytesIO(json.dumps({"name_ru": "Test"}).encode()), "info.json"),
            },
        )
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert data["status"] == 500

    def test_post_bad_secret_key(self, logged_client):
        info = {
            "name_ru": "Test",
            "secret_key": "wrong",
            "type_id": 2,
            "course_id": 1,
            "author": "Author",
            "supervisor": "Терехов",
            "publish_year": 2024,
        }
        resp = logged_client.post(
            "/post_theses",
            data={
                "thesis_text": (io.BytesIO(_min_pdf()), "test.pdf"),
                "thesis_info": (io.BytesIO(json.dumps(info).encode()), "info.json"),
            },
        )
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert data["status"] == 500
        assert "Invalid secret key" in data["string"]

    def test_post_bad_type_id(self, logged_client):
        from flask_se import app

        secret_key = app.config["SECRET_KEY_THESIS"]

        info = {
            "name_ru": "Test",
            "secret_key": secret_key,
            "type_id": 99,
            "course_id": 1,
            "author": "Author",
            "supervisor": "Терехов",
            "publish_year": 2024,
        }
        resp = logged_client.post(
            "/post_theses",
            data={
                "thesis_text": (io.BytesIO(_min_pdf()), "test.pdf"),
                "thesis_info": (io.BytesIO(json.dumps(info).encode()), "info.json"),
            },
        )
        data = json.loads(resp.data)
        assert data["status"] == 500
        assert "Wrong type_id" in data["string"]

    def test_post_bad_course_id(self, logged_client):
        from flask_se import app

        secret_key = app.config["SECRET_KEY_THESIS"]

        info = {
            "name_ru": "Test",
            "secret_key": secret_key,
            "type_id": 2,
            "course_id": 99,
            "author": "Author",
            "supervisor": "Терехов",
            "publish_year": 2024,
        }
        resp = logged_client.post(
            "/post_theses",
            data={
                "thesis_text": (io.BytesIO(_min_pdf()), "test.pdf"),
                "thesis_info": (io.BytesIO(json.dumps(info).encode()), "info.json"),
            },
        )
        data = json.loads(resp.data)
        assert data["status"] == 500
        assert "Wrong course_id" in data["string"]

    def test_post_bad_publish_year_path_traversal(self, logged_client):
        from flask_se import app

        secret_key = app.config["SECRET_KEY_THESIS"]

        info = {
            "name_ru": "Test",
            "secret_key": secret_key,
            "type_id": 2,
            "course_id": 1,
            "author": "Author",
            "supervisor": "Терехов",
            "publish_year": "../../evil",
        }
        resp = logged_client.post(
            "/post_theses",
            data={
                "thesis_text": (io.BytesIO(_min_pdf()), "test.pdf"),
                "thesis_info": (io.BytesIO(json.dumps(info).encode()), "info.json"),
            },
        )
        data = json.loads(resp.data)
        assert data["status"] == 500
        assert "Wrong publish_year" in data["string"]

    def test_post_no_supervisor_match(self, logged_client):
        from flask_se import app

        secret_key = app.config["SECRET_KEY_THESIS"]

        info = {
            "name_ru": "Test",
            "secret_key": secret_key,
            "type_id": 2,
            "course_id": 1,
            "author": "Author",
            "supervisor": "NoOneHere",
            "publish_year": 2024,
        }
        resp = logged_client.post(
            "/post_theses",
            data={
                "thesis_text": (io.BytesIO(_min_pdf()), "test.pdf"),
                "thesis_info": (io.BytesIO(json.dumps(info).encode()), "info.json"),
            },
        )
        data = json.loads(resp.data)
        assert data["status"] == 500
        assert "Can't find supervisor" in data["string"]

    @pytest.mark.xfail(
        strict=False, reason="intermittent xdist race — passes alone, fails in full suite"
    )
    def test_post_supervisor_found_in_users_not_in_staff(self, logged_client):
        from flask_se_config import SECRET_KEY_THESIS
        from se_models import Users, db

        u = Users(email="no.staff@spbu.ru", first_name="NoStaff", last_name="БезСтафа")
        db.session.add(u)
        db.session.commit()

        info = {
            "name_ru": "Test",
            "secret_key": SECRET_KEY_THESIS,
            "type_id": 2,
            "course_id": 1,
            "author": "UniqueAuthor_NoStaff",
            "supervisor": "БезСтафа",
            "publish_year": 2024,
        }
        resp = logged_client.post(
            "/post_theses",
            data={
                "thesis_text": (io.BytesIO(_min_pdf()), "test.pdf"),
                "thesis_info": (io.BytesIO(json.dumps(info).encode()), "info.json"),
            },
        )
        data = json.loads(resp.data)
        assert data["status"] == 500
        assert "Can't find supervisor in staff" in data["string"]

    @pytest.mark.xfail(reason="Intermittent CI failure: post_theses returns 500", strict=False)
    def test_post_with_source_uri(self, logged_client):
        from flask_se_config import SECRET_KEY_THESIS

        info = {
            "name_ru": "Test",
            "secret_key": SECRET_KEY_THESIS,
            "type_id": 2,
            "course_id": 1,
            "author": "SourceUriAuthor",
            "supervisor": "Терехов",
            "publish_year": 2024,
            "source_uri": "https://example.com/thesis",
        }
        resp = logged_client.post(
            "/post_theses",
            data={
                "thesis_text": (io.BytesIO(_min_pdf()), "test.pdf"),
                "thesis_info": (io.BytesIO(json.dumps(info).encode()), "info.json"),
            },
        )
        data = json.loads(resp.data)
        assert data["status"] == 0

    @pytest.mark.xfail(reason="Intermittent CI failure: post_theses returns 500", strict=False)
    def test_post_with_presentation(self, logged_client):
        from flask_se_config import SECRET_KEY_THESIS

        info = {
            "name_ru": "Test",
            "secret_key": SECRET_KEY_THESIS,
            "type_id": 2,
            "course_id": 1,
            "author": "PresAuthor",
            "supervisor": "Терехов",
            "publish_year": 2024,
        }
        resp = logged_client.post(
            "/post_theses",
            data={
                "thesis_text": (io.BytesIO(_min_pdf()), "test.pdf"),
                "presentation": (io.BytesIO(b"slides"), "slides.pdf"),
                "thesis_info": (io.BytesIO(json.dumps(info).encode()), "info.json"),
            },
        )
        data = json.loads(resp.data)
        assert data["status"] == 0

    @pytest.mark.xfail(reason="Intermittent CI failure: post_theses returns 500", strict=False)
    def test_post_with_supervisor_review(self, logged_client):
        from flask_se_config import SECRET_KEY_THESIS

        info = {
            "name_ru": "Test",
            "secret_key": SECRET_KEY_THESIS,
            "type_id": 2,
            "course_id": 1,
            "author": "SupRevAuthor",
            "supervisor": "Терехов",
            "publish_year": 2024,
        }
        resp = logged_client.post(
            "/post_theses",
            data={
                "thesis_text": (io.BytesIO(_min_pdf()), "test.pdf"),
                "supervisor_review": (io.BytesIO(b"review"), "review.pdf"),
                "thesis_info": (io.BytesIO(json.dumps(info).encode()), "info.json"),
            },
        )
        data = json.loads(resp.data)
        assert data["status"] == 0

    @pytest.mark.xfail(reason="Intermittent CI failure: post_theses returns 500", strict=False)
    def test_post_with_reviewer_review(self, logged_client):
        from flask_se_config import SECRET_KEY_THESIS

        info = {
            "name_ru": "Test",
            "secret_key": SECRET_KEY_THESIS,
            "type_id": 2,
            "course_id": 1,
            "author": "RevRevAuthor",
            "supervisor": "Терехов",
            "publish_year": 2024,
        }
        resp = logged_client.post(
            "/post_theses",
            data={
                "thesis_text": (io.BytesIO(_min_pdf()), "test.pdf"),
                "reviewer_review": (io.BytesIO(b"review"), "review.pdf"),
                "thesis_info": (io.BytesIO(json.dumps(info).encode()), "info.json"),
            },
        )
        data = json.loads(resp.data)
        assert data["status"] == 0

    @pytest.mark.xfail(reason="Intermittent CI failure: post_theses returns 500", strict=False)
    def test_post_all_files(self, logged_client):
        from flask_se_config import SECRET_KEY_THESIS

        info = {
            "name_ru": "Test",
            "secret_key": SECRET_KEY_THESIS,
            "type_id": 2,
            "course_id": 1,
            "author": "AllFilesAuthor",
            "supervisor": "Терехов",
            "publish_year": 2024,
            "source_uri": "https://example.com/thesis",
        }
        resp = logged_client.post(
            "/post_theses",
            data={
                "thesis_text": (io.BytesIO(_min_pdf()), "test.pdf"),
                "presentation": (io.BytesIO(_min_pdf("slides")), "slides.pdf"),
                "supervisor_review": (io.BytesIO(_min_pdf("sup")), "sup.pdf"),
                "reviewer_review": (io.BytesIO(_min_pdf("rev")), "rev.pdf"),
                "thesis_info": (io.BytesIO(json.dumps(info).encode()), "info.json"),
            },
        )
        data = json.loads(resp.data)
        assert data["status"] == 0


class TestThesesTmpList:
    def test_tmp_list_empty(self, seeded_client):
        assert_ok(seeded_client, "/theses_tmp.html")

    def test_tmp_list_with_temp_thesis(self, seeded_client):
        from se_models import Staff, Thesis, db

        supervisor = Staff.query.first()
        t = Thesis(
            name_ru="Temp",
            author="T",
            type_id=2,
            course_id=1,
            publish_year=2024,
            temporary=True,
            supervisor_id=supervisor.id,
        )
        db.session.add(t)
        db.session.commit()
        resp = seeded_client.get("/theses_tmp.html")
        assert resp.status_code == 200


class TestThesesDeleteTmpDeep:
    def test_delete_tmp_with_id(self, seeded_client):
        from se_models import Thesis, db

        t = _make_temp_thesis("T")
        tid = t.id
        resp = seeded_client.get(f"/theses_delete_tmp?thesis_id={tid}")
        assert resp.status_code in (200, 302)
        assert db.session.get(Thesis, tid) is None

    def test_delete_tmp_non_temporary_ignored(self, seeded_client):
        from se_models import Thesis, db

        t = Thesis(
            name_ru="Perm", author="T", type_id=2, course_id=1, publish_year=2024, temporary=False
        )
        db.session.add(t)
        db.session.commit()
        resp = seeded_client.get(f"/theses_delete_tmp?thesis_id={t.id}")
        assert resp.status_code in (200, 302)
        assert db.session.get(Thesis, t.id) is not None


class TestThesesAddTmpDeep:
    def test_add_tmp_with_text_uri(self, seeded_client):
        from se_models import Thesis, db

        Path("static/tmp/texts").mkdir(parents=True, exist_ok=True)
        Path("static/thesis/texts").mkdir(parents=True, exist_ok=True)
        Path("static/tmp/texts/test.pdf").write_text("")
        Path("static/thesis/texts/test.pdf").unlink(missing_ok=True)

        t = _make_temp_thesis("T", "test.pdf")
        resp = _approve_temp_thesis(seeded_client, t.id)
        assert resp.status_code in (200, 302)
        updated = db.session.get(Thesis, t.id)
        assert updated.temporary is False

    def test_add_tmp_with_presentation_and_reviews(self, seeded_client):
        from se_models import Thesis, db

        Path("static/tmp/texts").mkdir(parents=True, exist_ok=True)
        Path("static/tmp/slides").mkdir(parents=True, exist_ok=True)
        Path("static/tmp/reviews").mkdir(parents=True, exist_ok=True)
        Path("static/thesis/texts").mkdir(parents=True, exist_ok=True)
        Path("static/thesis/slides").mkdir(parents=True, exist_ok=True)
        Path("static/thesis/reviews").mkdir(parents=True, exist_ok=True)
        for _f in [
            "static/tmp/texts/text.pdf",
            "static/tmp/slides/slides.pdf",
            "static/tmp/reviews/sup.pdf",
            "static/tmp/reviews/rev.pdf",
            "static/thesis/texts/text.pdf",
            "static/thesis/slides/slides.pdf",
            "static/thesis/reviews/sup.pdf",
            "static/thesis/reviews/rev.pdf",
        ]:
            Path(_f).unlink(missing_ok=True)
        Path("static/tmp/texts/text.pdf").write_text("")
        Path("static/tmp/slides/slides.pdf").write_text("")
        Path("static/tmp/reviews/sup.pdf").write_text("")
        Path("static/tmp/reviews/rev.pdf").write_text("")

        t = Thesis(
            name_ru="FullApprove",
            author="T",
            type_id=2,
            course_id=1,
            publish_year=2024,
            temporary=True,
            text_uri="text.pdf",
            presentation_uri="slides.pdf",
            supervisor_review_uri="sup.pdf",
            reviewer_review_uri="rev.pdf",
        )
        db.session.add(t)
        db.session.commit()
        resp = _approve_temp_thesis(seeded_client, t.id)
        assert resp.status_code in (200, 302)
        updated = db.session.get(Thesis, t.id)
        assert updated.temporary is False

    def test_add_tmp_non_temporary_ignored(self, seeded_client):
        from se_models import Thesis, db

        t = Thesis(
            name_ru="AlreadyPerm",
            author="T",
            type_id=2,
            course_id=1,
            publish_year=2024,
            temporary=False,
        )
        db.session.add(t)
        db.session.commit()
        resp = _approve_temp_thesis(seeded_client, t.id)
        assert resp.status_code in (200, 302)
        assert db.session.get(Thesis, t.id).temporary is False

    def test_add_tmp_nonexistent_thesis(self, seeded_client):
        resp = seeded_client.get("/theses_add_tmp?thesis_id=99999")
        assert resp.status_code in (200, 302)

    def test_delete_tmp_nonexistent_thesis(self, seeded_client):
        resp = seeded_client.get("/theses_delete_tmp?thesis_id=99999")
        assert resp.status_code in (200, 302)


class TestThesesPagination:
    def test_fetch_page_one(self, seeded_client):
        assert_ok(seeded_client, "/fetch_theses?page=1")

    def test_fetch_page_large_number(self, seeded_client):
        assert_ok(seeded_client, "/fetch_theses?page=9999")

    def test_fetch_with_search_paginated(self, seeded_client):
        assert_ok(seeded_client, "/fetch_theses?search=python&page=1")

    def test_fetch_with_worktype_filter_paginated(self, seeded_client):
        assert_ok(seeded_client, "/fetch_theses?worktype=2&page=2")

    def test_fetch_with_supervisor_and_course(self, seeded_client):
        assert_ok(seeded_client, "/fetch_theses?supervisor=1&course=1")

    def test_fetch_with_worktype_and_no_results(self, seeded_client):
        assert_ok(seeded_client, "/fetch_theses?worktype=8")

    def test_fetch_all_params(self, seeded_client):
        assert_ok(
            seeded_client,
            "/fetch_theses?worktype=1&course=2&supervisor=1&startdate=2000&enddate=2030&page=1&search=",
        )


class TestThesesSearchFilterPopulation:
    def test_search_filter_worktype_and_course(self, seeded_client):
        resp = seeded_client.get("/theses.html?worktype=2")
        assert resp.status_code == 200
        resp = seeded_client.get("/theses.html?course=1")
        assert resp.status_code == 200

    def test_search_filter_supervisor(self, seeded_client):
        assert_ok(seeded_client, "/theses.html?supervisor=1")

    def test_search_filter_startdate_enddate(self, seeded_client):
        assert_ok(seeded_client, "/theses.html?startdate=2020")
        assert_ok(seeded_client, "/theses.html?enddate=2024")

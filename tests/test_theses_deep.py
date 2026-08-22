# -*- coding: utf-8 -*-
import io
import json
from pathlib import Path

import pytest
from conftest import _approve_temp_thesis, _make_temp_thesis, _min_pdf, assert_ok


class TestFetchThesesFilters:
    @pytest.mark.parametrize(
        "path",
        [
            "/fetch_theses",
            "/fetch_theses?worktype=2",
            "/fetch_theses?course=1",
            "/fetch_theses?supervisor=1",
            "/fetch_theses?worktype=2&course=1&supervisor=1&startdate=2010&enddate=2024&page=1",
            "/fetch_theses?startdate=2024&enddate=2010",
            "/fetch_theses?search=zzz_no_match_zzz",
            "/fetch_theses?supervisor=99999",
            "/fetch_theses?page=2",
        ],
    )
    def test_fetch_filters(self, seeded_client, path):
        assert_ok(seeded_client, path)


class TestFetchThesesConsultantFilter:
    def test_fetch_with_consultant_no_match(self, seeded_client):
        resp = seeded_client.get("/fetch_theses?consultant=no_such_consultant_zzz")
        assert resp.status_code == 200
        assert "no_such_consultant_zzz" not in resp.get_data(as_text=True)

    @pytest.mark.parametrize(
        "search_term, expected_title",
        [
            ("Консультантов", "Consultant Match Thesis"),
            ("Консульт", "Partial Consultant Thesis"),
        ],
    )
    def test_fetch_consultant_match(self, app_ctx, search_term, expected_title):
        from se_models import Thesis, db

        t = Thesis(
            name_ru=expected_title,
            author="Author",
            type_id=2,
            course_id=1,
            publish_year=2024,
            consultant="Иван Консультантов",
        )
        db.session.add(t)
        db.session.commit()
        resp = app_ctx.get(f"/fetch_theses?consultant={search_term}")
        assert resp.status_code == 200
        assert expected_title in resp.get_data(as_text=True)

    @pytest.mark.parametrize(
        "path",
        [
            "/fetch_theses?consultant=",
            "/fetch_theses?consultant=test&supervisor=1",
        ],
    )
    def test_fetch_consultant_ok(self, seeded_client, path):
        assert_ok(seeded_client, path)


class TestThesesSearchDetail:
    @pytest.mark.parametrize(
        "path",
        [
            "/theses.html",
            "/theses.html?worktype=2&course=1&supervisor=1&startdate=2020&enddate=2024",
            "/theses.html?worktype=99&course=99",
        ],
    )
    def test_search_page_renders(self, seeded_client, path):
        assert_ok(seeded_client, path)


class TestDownloadThesis:
    @pytest.mark.parametrize(
        "path",
        [
            "/thesis_download?thesis_id=1",
            "/thesis_download?thesis_id=0",
            "/thesis_download?thesis_id=99999",
        ],
    )
    def test_download_status(self, seeded_client, path):
        resp = seeded_client.get(path)
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


class TestPostThesesApi:
    @pytest.mark.parametrize(
        "payload, expected_string",
        [
            ({}, "No thesis text"),
            ({"thesis_text": (io.BytesIO(_min_pdf()), "test.pdf")}, "No thesis_info"),
            (
                {
                    "thesis_text": (io.BytesIO(_min_pdf()), "test.pdf"),
                    "thesis_info": (
                        io.BytesIO(json.dumps({"name_ru": "Test"}).encode()),
                        "info.json",
                    ),
                },
                None,
            ),
        ],
    )
    def test_post_missing_inputs(self, logged_client, payload, expected_string):
        resp = logged_client.post("/post_theses", data=payload)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert body["status"] == 500
        if expected_string:
            assert expected_string in body["string"]

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

    @pytest.mark.parametrize(
        "info_overrides, expected_error",
        [
            ({"type_id": 99}, "Wrong type_id"),
            ({"course_id": 99}, "Wrong course_id"),
            ({"publish_year": "../../evil"}, "Wrong publish_year"),
            ({"supervisor": "NoOneHere"}, "Can't find supervisor"),
        ],
    )
    def test_post_bad_field(self, logged_client, info_overrides, expected_error):
        from flask_se import app

        secret_key = app.config["SECRET_KEY_THESIS"]

        info = {
            "name_ru": "Test",
            "secret_key": secret_key,
            "type_id": 2,
            "course_id": 1,
            "author": "Author",
            "supervisor": "Терехов",
            "publish_year": 2024,
        }
        info.update(info_overrides)
        resp = logged_client.post(
            "/post_theses",
            data={
                "thesis_text": (io.BytesIO(_min_pdf()), "test.pdf"),
                "thesis_info": (io.BytesIO(json.dumps(info).encode()), "info.json"),
            },
        )
        body = json.loads(resp.data)
        assert body["status"] == 500
        assert expected_error in body["string"]

    @pytest.mark.xdist_group("post_theses")
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

    @pytest.mark.xdist_group("post_theses")
    @pytest.mark.parametrize(
        "author, extra_files, source_uri",
        [
            ("SourceUriAuthor", [], "https://example.com/thesis"),
            ("PresAuthor", [("presentation", b"slides", "slides.pdf")], None),
            ("SupRevAuthor", [("supervisor_review", b"review", "review.pdf")], None),
            ("RevRevAuthor", [("reviewer_review", b"review", "review.pdf")], None),
            (
                "AllFilesAuthor",
                [
                    ("presentation", _min_pdf("slides"), "slides.pdf"),
                    ("supervisor_review", _min_pdf("sup"), "sup.pdf"),
                    ("reviewer_review", _min_pdf("rev"), "rev.pdf"),
                ],
                "https://example.com/thesis",
            ),
        ],
    )
    def test_post_with_files(self, logged_client, author, extra_files, source_uri):
        from flask_se_config import SECRET_KEY_THESIS

        info = {
            "name_ru": "Test",
            "secret_key": SECRET_KEY_THESIS,
            "type_id": 2,
            "course_id": 1,
            "author": author,
            "supervisor": "Терехов",
            "publish_year": 2024,
        }
        if source_uri:
            info["source_uri"] = source_uri
        data = {
            "thesis_text": (io.BytesIO(_min_pdf()), "test.pdf"),
            "thesis_info": (io.BytesIO(json.dumps(info).encode()), "info.json"),
        }
        for field, content, filename in extra_files:
            data[field] = (io.BytesIO(content), filename)
        resp = logged_client.post("/post_theses", data=data)
        body = json.loads(resp.data)
        assert body["status"] == 0, body


class TestThesesTmpList:
    def test_tmp_list_empty(self, admin_client):
        assert_ok(admin_client, "/theses_tmp.html")

    def test_tmp_list_with_temp_thesis(self, admin_client):
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
        resp = admin_client.get("/theses_tmp.html")
        assert resp.status_code == 200


class TestThesesDeleteTmpDeep:
    def test_delete_tmp_with_id(self, admin_client):
        from se_models import Thesis, db

        t = _make_temp_thesis("T")
        tid = t.id
        resp = admin_client.post("/theses_delete_tmp", data={"thesis_id": tid})
        assert resp.status_code in (200, 302)
        assert db.session.get(Thesis, tid) is None


class TestThesesAddTmpDeep:
    @staticmethod
    def _upload_root() -> Path:
        from flask_se_theses import THESIS_UPLOAD_ROOT

        return Path(THESIS_UPLOAD_ROOT)

    def test_add_tmp_with_text_uri(self, admin_client):
        from se_models import Thesis, db

        root = self._upload_root()
        (root / "texts").mkdir(parents=True, exist_ok=True)
        Path("static/thesis/texts").mkdir(parents=True, exist_ok=True)
        (root / "texts" / "test.pdf").write_text("")
        Path("static/thesis/texts/test.pdf").unlink(missing_ok=True)

        t = _make_temp_thesis("T", "test.pdf")
        resp = _approve_temp_thesis(admin_client, t.id)
        assert resp.status_code in (200, 302)
        updated = db.session.get(Thesis, t.id)
        assert updated.temporary is False

    def test_add_tmp_with_presentation_and_reviews(self, admin_client):
        from se_models import Thesis, db

        root = self._upload_root()
        for _sub in ("texts", "slides", "reviews"):
            (root / _sub).mkdir(parents=True, exist_ok=True)
            Path(f"static/thesis/{_sub}").mkdir(parents=True, exist_ok=True)
        for _f in [
            root / "texts" / "text.pdf",
            root / "slides" / "slides.pdf",
            root / "reviews" / "sup.pdf",
            root / "reviews" / "rev.pdf",
            Path("static/thesis/texts/text.pdf"),
            Path("static/thesis/slides/slides.pdf"),
            Path("static/thesis/reviews/sup.pdf"),
            Path("static/thesis/reviews/rev.pdf"),
        ]:
            _f.unlink(missing_ok=True)
        for _f in [
            root / "texts" / "text.pdf",
            root / "slides" / "slides.pdf",
            root / "reviews" / "sup.pdf",
            root / "reviews" / "rev.pdf",
        ]:
            _f.write_text("")

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
        resp = _approve_temp_thesis(admin_client, t.id)
        assert resp.status_code in (200, 302)
        updated = db.session.get(Thesis, t.id)
        assert updated.temporary is False

    @pytest.mark.parametrize(
        "endpoint, title",
        [
            ("/theses_add_tmp", "AlreadyPerm"),
            ("/theses_delete_tmp", "Perm"),
        ],
    )
    def test_tmp_non_temporary_ignored(self, admin_client, endpoint, title):
        from se_models import Thesis, db

        t = Thesis(
            name_ru=title, author="T", type_id=2, course_id=1, publish_year=2024, temporary=False
        )
        db.session.add(t)
        db.session.commit()
        resp = admin_client.post(endpoint, data={"thesis_id": t.id})
        assert resp.status_code in (200, 302)
        thesis = db.session.get(Thesis, t.id)
        assert thesis is not None
        assert thesis.temporary is False

    @pytest.mark.parametrize("endpoint", ["/theses_add_tmp", "/theses_delete_tmp"])
    def test_tmp_nonexistent_thesis(self, admin_client, endpoint):
        resp = admin_client.post(endpoint, data={"thesis_id": 99999})
        assert resp.status_code in (200, 302)


class TestThesesPagination:
    @pytest.mark.parametrize(
        "path",
        [
            "/fetch_theses?page=1",
            "/fetch_theses?page=9999",
            "/fetch_theses?search=python&page=1",
            "/fetch_theses?worktype=2&page=2",
            "/fetch_theses?supervisor=1&course=1",
            "/fetch_theses?worktype=8",
            "/fetch_theses?worktype=1&course=2&supervisor=1&startdate=2000&enddate=2030&page=1&search=",
        ],
    )
    def test_fetch_pagination(self, seeded_client, path):
        assert_ok(seeded_client, path)


class TestThesesSearchFilterPopulation:
    @pytest.mark.parametrize(
        "path",
        [
            "/theses.html?worktype=2",
            "/theses.html?course=1",
            "/theses.html?supervisor=1",
            "/theses.html?startdate=2020",
            "/theses.html?enddate=2024",
        ],
    )
    def test_search_filter_population(self, seeded_client, path):
        assert_ok(seeded_client, path)


class TestThesesFtsWildcardSearch:
    @pytest.mark.parametrize(
        "name_ru, author, term",
        [
            ("Компьютерные сети", "Максим Иванов", "сети"),
            ("Компьютерные сети", "Максим Иванов", "макс*"),
            ("Программная инженерия", "Алексей", "*грамм*"),
        ],
    )
    def test_fts_search(self, seeded_client, name_ru, author, term):
        from se_models import Thesis, db, thesis_fts_search

        t = Thesis(
            name_ru=name_ru,
            author=author,
            type_id=2,
            course_id=1,
            publish_year=2024,
        )
        db.session.add(t)
        db.session.commit()
        ids = thesis_fts_search(term)
        assert t.id in ids

    def test_fts_search_no_crash_on_wildcard_route(self, seeded_client):
        assert_ok(seeded_client, "/fetch_theses?search=фаз*")
        assert_ok(seeded_client, "/fetch_theses?search=*акс*")
        assert_ok(seeded_client, "/fetch_theses?search=д?м")

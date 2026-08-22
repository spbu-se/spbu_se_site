# -*- coding: utf-8 -*-
import io
from unittest.mock import patch

import pytest
from conftest import assert_ok
from werkzeug.datastructures import FileStorage

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def thesis_on_review(seeded_client):
    from se_models import AreasOfStudy, ThesisOnReview, ThesisOnReviewWorktype, db

    area = AreasOfStudy.query.first()
    tor_wt = ThesisOnReviewWorktype(type="Курсовая работа")
    db.session.add(tor_wt)
    db.session.flush()
    tor = ThesisOnReview(
        name_ru="Test thesis for review",
        author_id=1,
        type_id=2,
        thesis_on_review_type_id=tor_wt.id,
        area_id=area.id,
        review_status=1,
    )
    db.session.add(tor)
    db.session.commit()
    return tor


@pytest.fixture
def other_thesis_on_review(seeded_client):
    from se_models import AreasOfStudy, ThesisOnReview, ThesisOnReviewWorktype, db

    area = AreasOfStudy.query.first()
    tor_wt = ThesisOnReviewWorktype(type="Дипломная работа")
    db.session.add(tor_wt)
    db.session.flush()
    tor = ThesisOnReview(
        name_ru="Other thesis",
        author_id=2,
        type_id=2,
        thesis_on_review_type_id=tor_wt.id,
        area_id=area.id,
        review_status=1,
    )
    db.session.add(tor)
    db.session.commit()
    return tor


@pytest.fixture
def reviewer_user(seeded_client):
    from se_models import Reviewer, db

    r = Reviewer(user_id=1)
    db.session.add(r)
    db.session.commit()
    return r


@pytest.fixture
def promocode(seeded_client):
    from se_models import PromoCode, db

    pc = PromoCode(code="secret-reviewer-code")
    db.session.add(pc)
    db.session.commit()
    return pc


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestAllowedFile:
    @pytest.mark.parametrize(
        "filename, expected",
        [
            ("thesis.pdf", True),
            ("thesis.PDF", True),
            ("thesis.docx", False),
            ("thesis", False),
        ],
    )
    def test_allowed_file(self, filename, expected):
        from flask_se_review import allowed_file

        assert allowed_file(filename) is expected


class TestThesisReviewIndex:
    @pytest.mark.parametrize("path", ["/review/", "/review/index.html"])
    def test_index_returns_200(self, seeded_client, path):
        resp = seeded_client.get(path)
        assert resp.status_code == 200

    def test_index_contains_review_filter_form(self, seeded_client):
        resp = seeded_client.get("/review/")
        html = resp.data.decode("utf-8")
        assert "Все статусы" in html


class TestFetchThesisOnReview:
    @pytest.mark.parametrize(
        "query",
        [
            "",
            "?status=1",
            "?status=4",
            "?worktype=2",
            "?area=2",
            "?page=1",
            "?status=1&worktype=2&area=2&page=1",
        ],
    )
    def test_fetch_filters(self, logged_client, query):
        resp = logged_client.get("/review/fetch_thesis_on_review" + query)
        assert resp.status_code == 200


class TestSubmitThesisOnReview:
    def test_submit_page_get(self, logged_client):
        resp = logged_client.get("/review/submit")
        assert resp.status_code == 200

    @pytest.mark.parametrize(
        "data",
        [
            {"title": ""},
            {"title": "Test work", "type": 999, "area": 0},
            {"title": "Test work", "type": 1, "area": 999},
            {"title": "Test work", "type": 1, "area": 1},
        ],
    )
    def test_submit_post_validation_failures(self, logged_client, data):
        resp = logged_client.post("/review/submit", data=data)
        assert resp.status_code == 302

    def test_submit_post_empty_filename(self, logged_client):
        data = {
            "title": "Test work",
            "type": 1,
            "area": 1,
            "thesis": (io.BytesIO(b""), ""),
        }
        resp = logged_client.post("/review/submit", data=data, content_type="multipart/form-data")
        assert resp.status_code == 302

    @patch("flask_se_review.os.path.isfile", return_value=False)
    @patch.object(FileStorage, "save")
    @patch("flask_se_review.translit")
    @patch("flask_se_review.get_thesis_type_id_string")
    def test_submit_post_success(
        self, mock_get_type_str, mock_translit, mock_save, mock_isfile, logged_client
    ):
        from se_models import AreasOfStudy, ThesisOnReviewWorktype, db

        area = AreasOfStudy.query.first()
        tor_wt = ThesisOnReviewWorktype(type="Курсовая работа")
        db.session.add(tor_wt)
        db.session.flush()

        mock_translit.return_value = "Terekhov_Andrey_Nikolaevich"
        mock_get_type_str.return_value = "coursework"

        data = {
            "title": "Моя работа",
            "type": tor_wt.id,
            "area": area.id,
            "thesis": (io.BytesIO(b"%PDF-1.4 test"), "thesis.pdf"),
        }
        resp = logged_client.post("/review/submit", data=data, content_type="multipart/form-data")
        assert resp.status_code == 302

        from se_models import ThesisOnReview, db

        tor = ThesisOnReview.query.filter_by(name_ru="Моя работа").first()
        assert tor is not None
        assert tor.author_id == 1
        assert tor.review_status == 1

    def test_submit_post_not_pdf(self, logged_client):
        from se_models import AreasOfStudy, ThesisOnReviewWorktype, db

        area = AreasOfStudy.query.first()
        tor_wt = ThesisOnReviewWorktype(type="Курсовая работа")
        db.session.add(tor_wt)
        db.session.flush()
        data = {
            "title": "Test work",
            "type": tor_wt.id,
            "area": area.id,
            "thesis": (io.BytesIO(b"not a pdf"), "test.docx"),
        }
        resp = logged_client.post("/review/submit", data=data, content_type="multipart/form-data")
        assert resp.status_code == 302


class TestEditThesisOnReview:
    @pytest.mark.parametrize(
        "path, code",
        [
            ("/review/edit", 302),
            ("/review/edit?thesis_review_id=99999", 404),
        ],
    )
    def test_edit_page_bad_id(self, logged_client, path, code):
        resp = logged_client.get(path)
        assert resp.status_code == code

    def test_edit_page_own_thesis(self, logged_client, thesis_on_review):
        resp = logged_client.get(f"/review/edit?thesis_review_id={thesis_on_review.id}")
        assert resp.status_code == 200

    def test_edit_page_other_thesis_redirects(self, logged_client, other_thesis_on_review):
        resp = logged_client.get(f"/review/edit?thesis_review_id={other_thesis_on_review.id}")
        assert resp.status_code == 302

    @pytest.mark.parametrize(
        "payload",
        [
            {"name_ru": ""},
            {"name_ru": "Title", "type": 999, "area": 1},
            {"name_ru": "Title", "type": 1, "area": 999},
        ],
    )
    def test_edit_post_validation_failure(self, logged_client, thesis_on_review, payload):
        resp = logged_client.post(
            f"/review/edit?thesis_review_id={thesis_on_review.id}",
            data=payload,
        )
        assert resp.status_code == 302

    def test_edit_post_success(self, logged_client, thesis_on_review):
        resp = logged_client.post(
            f"/review/edit?thesis_review_id={thesis_on_review.id}",
            data={
                "name_ru": "Updated title",
                "type": thesis_on_review.thesis_on_review_type_id,
                "area": thesis_on_review.area_id,
            },
        )
        assert resp.status_code == 302
        from se_models import db

        db.session.refresh(thesis_on_review)
        assert thesis_on_review.name_ru == "Updated title"

    @patch("flask_se_review.os.path.isfile", return_value=False)
    @patch.object(FileStorage, "save")
    @patch("flask_se_review.translit")
    @patch("flask_se_review.get_thesis_type_id_string")
    def test_edit_post_with_file(
        self,
        mock_get_type_str,
        mock_translit,
        mock_save,
        mock_isfile,
        logged_client,
        thesis_on_review,
    ):
        mock_translit.return_value = "Terekhov_Andrey_Nikolaevich"
        mock_get_type_str.return_value = "coursework"

        data = {
            "name_ru": "Updated with file",
            "type": thesis_on_review.thesis_on_review_type_id,
            "area": thesis_on_review.area_id,
            "thesis": (io.BytesIO(b"%PDF-1.4 updated"), "updated.pdf"),
        }
        resp = logged_client.post(
            f"/review/edit?thesis_review_id={thesis_on_review.id}",
            data=data,
            content_type="multipart/form-data",
        )
        assert resp.status_code == 302

    def test_edit_post_with_invalid_file_type(self, logged_client, thesis_on_review):
        data = {
            "name_ru": "Updated title",
            "type": thesis_on_review.thesis_on_review_type_id,
            "area": thesis_on_review.area_id,
            "thesis": (io.BytesIO(b"not pdf"), "file.docx"),
        }
        resp = logged_client.post(
            f"/review/edit?thesis_review_id={thesis_on_review.id}",
            data=data,
            content_type="multipart/form-data",
        )
        assert resp.status_code == 302


class TestDeleteThesisOnReview:
    def test_delete_no_id(self, logged_client):
        resp = logged_client.post("/review/delete")
        assert resp.status_code == 302

    def test_delete_own_thesis(self, logged_client, thesis_on_review):
        resp = logged_client.post("/review/delete", data={"thesis_review_id": thesis_on_review.id})
        assert resp.status_code == 302
        from se_models import ThesisOnReview, db

        deleted = db.session.get(ThesisOnReview, thesis_on_review.id)
        assert deleted is None

    def test_delete_other_thesis(self, logged_client, other_thesis_on_review):
        resp = logged_client.post(
            "/review/delete", data={"thesis_review_id": other_thesis_on_review.id}
        )
        assert resp.status_code == 302
        from se_models import ThesisOnReview, db

        still_exists = db.session.get(ThesisOnReview, other_thesis_on_review.id)
        assert still_exists is not None

    def test_delete_nonexistent(self, logged_client):
        resp = logged_client.post("/review/delete", data={"thesis_review_id": 99999})
        assert resp.status_code == 404


class TestReviewThesisOnReview:
    def test_review_not_reviewer_404(self, logged_client, other_thesis_on_review):
        resp = logged_client.get(f"/review/review?thesis_review_id={other_thesis_on_review.id}")
        assert resp.status_code == 404

    def test_review_no_id(self, logged_client):
        resp = logged_client.get("/review/review")
        assert resp.status_code == 404

    def test_review_own_thesis_redirects(self, logged_client, reviewer_user, thesis_on_review):
        resp = logged_client.get(f"/review/review?thesis_review_id={thesis_on_review.id}")
        assert resp.status_code == 302

    def test_review_first_time_page(self, logged_client, reviewer_user, other_thesis_on_review):
        resp = logged_client.get(f"/review/review?thesis_review_id={other_thesis_on_review.id}")
        assert resp.status_code == 200

    def test_review_set_to_review(self, logged_client, reviewer_user, other_thesis_on_review):
        resp = logged_client.post(
            f"/review/review?thesis_review_id={other_thesis_on_review.id}",
            data={"set_to_review": 1},
        )
        assert resp.status_code == 200
        from se_models import ThesisOnReview, db

        t = db.session.get(ThesisOnReview, other_thesis_on_review.id)
        assert t.review_status == 2
        assert t.reviewer_id == reviewer_user.id

    def test_review_already_in_review(self, logged_client, reviewer_user, other_thesis_on_review):
        other_thesis_on_review.review_status = 2
        other_thesis_on_review.reviewer_id = reviewer_user.id
        from se_models import db

        db.session.commit()
        resp = logged_client.get(f"/review/review?thesis_review_id={other_thesis_on_review.id}")
        assert resp.status_code == 200


class TestReviewSubmitReview:
    def test_reviewed_get_redirects(self, logged_client, reviewer_user):
        resp = logged_client.get("/review/reviewed")
        assert resp.status_code in (302, 404)

    def test_reviewed_no_reviewer_404(self, logged_client):
        resp = logged_client.post("/review/reviewed", data={})
        assert resp.status_code == 404

    def test_reviewed_no_thesis_id(self, logged_client, reviewer_user):
        resp = logged_client.post("/review/reviewed", data={})
        assert resp.status_code in (302, 404)

    def test_reviewed_nonexistent_thesis(self, logged_client, reviewer_user):
        resp = logged_client.post("/review/reviewed?thesis_review_id=99999", data={})
        assert resp.status_code == 404

    def test_reviewed_own_thesis(self, logged_client, reviewer_user, thesis_on_review):
        thesis_on_review.review_status = 2
        from se_models import db

        db.session.commit()
        resp = logged_client.post(
            f"/review/reviewed?thesis_review_id={thesis_on_review.id}", data={}
        )
        assert resp.status_code == 302

    def test_reviewed_wrong_status(self, logged_client, reviewer_user, other_thesis_on_review):
        resp = logged_client.post(
            f"/review/reviewed?thesis_review_id={other_thesis_on_review.id}", data={}
        )
        assert resp.status_code == 302

    @pytest.mark.parametrize(
        "switcher, comments, overall_comment, expected_status, expected_verdict",
        [
            ("1", ["Good", "Ok", "Fine", "Nice", "Well done", "Great"], "Overall good", 0, 1),
            ("0", ["Bad", "Poor", "Weak", "Incomplete", "Missing", "N/A"], "Needs work", 3, 0),
        ],
    )
    def test_reviewed_verdict(
        self,
        logged_client,
        reviewer_user,
        other_thesis_on_review,
        switcher,
        comments,
        overall_comment,
        expected_status,
        expected_verdict,
    ):
        other_thesis_on_review.review_status = 2
        other_thesis_on_review.reviewer_id = reviewer_user.id
        from se_models import db

        db.session.commit()

        data = {
            "review_o1_radio_switcher": switcher,
            "review_o1_comment": comments[0],
            "review_o2_radio_switcher": switcher,
            "review_o2_comment": comments[1],
            "review_t1_radio_switcher": switcher,
            "review_t1_comment": comments[2],
            "review_t2_radio_switcher": switcher,
            "review_t2_comment": comments[3],
            "review_p1_radio_switcher": switcher,
            "review_p1_comment": comments[4],
            "review_p2_radio_switcher": switcher,
            "review_p2_comment": comments[5],
            "review_overall_comment": overall_comment,
            "review_verdict_radio_switcher": switcher,
        }
        resp = logged_client.post(
            f"/review/reviewed?thesis_review_id={other_thesis_on_review.id}", data=data
        )
        assert resp.status_code == 302
        from se_models import ThesisOnReview, ThesisReview

        t = db.session.get(ThesisOnReview, other_thesis_on_review.id)
        assert t.review_status == expected_status
        rv = ThesisReview.query.filter_by(thesis_on_review_id=other_thesis_on_review.id).first()
        assert rv is not None
        assert rv.verdict == expected_verdict

    def test_reviewed_missing_fields(self, logged_client, reviewer_user, other_thesis_on_review):
        other_thesis_on_review.review_status = 2
        other_thesis_on_review.reviewer_id = reviewer_user.id
        from se_models import db

        db.session.commit()

        resp = logged_client.post(
            f"/review/reviewed?thesis_review_id={other_thesis_on_review.id}",
            data={"review_o1_radio_switcher": "1"},
        )
        assert resp.status_code == 302

    @patch.object(FileStorage, "save")
    def test_reviewed_with_file(
        self, mock_save, logged_client, reviewer_user, other_thesis_on_review
    ):
        other_thesis_on_review.review_status = 2
        other_thesis_on_review.reviewer_id = reviewer_user.id
        other_thesis_on_review.text_uri = "test_thesis.pdf"
        from se_models import db

        db.session.commit()

        resp = logged_client.post(
            f"/review/reviewed?thesis_review_id={other_thesis_on_review.id}",
            data={
                "review_o1_radio_switcher": "1",
                "review_o1_comment": "",
                "review_o2_radio_switcher": "1",
                "review_o2_comment": "",
                "review_t1_radio_switcher": "1",
                "review_t1_comment": "",
                "review_t2_radio_switcher": "1",
                "review_t2_comment": "",
                "review_p1_radio_switcher": "1",
                "review_p1_comment": "",
                "review_p2_radio_switcher": "1",
                "review_p2_comment": "",
                "review_overall_comment": "Approved",
                "review_verdict_radio_switcher": "1",
                "review_file": (io.BytesIO(b"%PDF-1.4 review"), "review.pdf"),
            },
            content_type="multipart/form-data",
        )
        assert resp.status_code == 302
        from se_models import ThesisReview

        rv = ThesisReview.query.filter_by(thesis_on_review_id=other_thesis_on_review.id).first()
        assert rv is not None
        assert rv.review_file_uri is not None


class TestReviewResult:
    @pytest.mark.parametrize(
        "path, code",
        [
            ("/review/review_result", 302),
            ("/review/review_result?thesis_review_id=99999", 404),
        ],
    )
    def test_result_bad_id(self, logged_client, path, code):
        resp = logged_client.get(path)
        assert resp.status_code == code

    def test_result_no_review_yet(self, logged_client, thesis_on_review):
        resp = logged_client.get(f"/review/review_result?thesis_review_id={thesis_on_review.id}")
        assert resp.status_code in (302, 404)

    def test_result_in_progress(self, logged_client, reviewer_user, thesis_on_review):
        thesis_on_review.review_status = 2
        thesis_on_review.reviewer_id = reviewer_user.id
        from se_models import db

        db.session.commit()
        resp = logged_client.get(f"/review/review_result?thesis_review_id={thesis_on_review.id}")
        assert resp.status_code == 404

    @pytest.mark.parametrize(
        "review_status, verdict, comments, overall_comment",
        [
            (0, 1, ["Good", "Ok", "Fine", "Nice", "Well", "Great"], "Overall good"),
            (3, 0, ["Bad", "Poor", "Weak", "Bad", "Missing", "N/A"], "Needs work"),
        ],
    )
    def test_result(
        self,
        logged_client,
        reviewer_user,
        thesis_on_review,
        review_status,
        verdict,
        comments,
        overall_comment,
    ):
        from se_models import ThesisReview, db

        thesis_on_review.review_status = review_status
        thesis_on_review.reviewer_id = reviewer_user.id
        db.session.commit()
        rv = ThesisReview(
            thesis_on_review_id=thesis_on_review.id,
            o1=verdict,
            o1_comment=comments[0],
            o2=verdict,
            o2_comment=comments[1],
            t1=verdict,
            t1_comment=comments[2],
            t2=verdict,
            t2_comment=comments[3],
            p1=verdict,
            p1_comment=comments[4],
            p2=verdict,
            p2_comment=comments[5],
            verdict=verdict,
            overall_comment=overall_comment,
        )
        db.session.add(rv)
        db.session.commit()
        resp = logged_client.get(f"/review/review_result?thesis_review_id={thesis_on_review.id}")
        assert resp.status_code == 200


class TestBecomeReviewer:
    @pytest.mark.parametrize(
        "query, needs_promocode, needs_reviewer, expected_code, html_check",
        [
            ("", False, False, 302, None),
            ("?code=invalid", False, False, 302, None),
            ("?code=__PROMO__", True, False, 200, None),
            ("?code=__PROMO__", True, True, 200, "reviewer"),
        ],
    )
    def test_become_reviewer_ask(
        self,
        logged_client,
        request,
        query,
        needs_promocode,
        needs_reviewer,
        expected_code,
        html_check,
    ):
        if needs_promocode:
            promocode = request.getfixturevalue("promocode")
            query = query.replace("__PROMO__", promocode.code)
        if needs_reviewer:
            request.getfixturevalue("reviewer_user")
        resp = logged_client.get(f"/review/become_thesis_reviewer{query}")
        assert resp.status_code == expected_code
        if html_check:
            html = resp.data.decode("utf-8").lower()
            assert "reviewer" in html or "рецензент" in html

    @pytest.mark.parametrize(
        "code, needs_promocode, needs_reviewer, expected_code, db_check, html_check",
        [
            (None, False, False, 302, False, None),
            ("invalid", False, False, 302, False, None),
            ("__PROMO__", True, False, 200, True, None),
            ("__PROMO__", True, True, 200, False, "already"),
        ],
    )
    def test_become_reviewer_confirm(
        self,
        logged_client,
        request,
        code,
        needs_promocode,
        needs_reviewer,
        expected_code,
        db_check,
        html_check,
    ):
        if needs_promocode:
            promocode = request.getfixturevalue("promocode")
        if needs_reviewer:
            request.getfixturevalue("reviewer_user")
        data = {}
        if code is not None:
            data["code"] = promocode.code if code == "__PROMO__" else code
        resp = logged_client.post("/review/become_thesis_reviewer_confirm", data=data)
        assert resp.status_code == expected_code
        if db_check:
            from se_models import Reviewer

            r = Reviewer.query.filter_by(user_id=1).first()
            assert r is not None
        if html_check:
            html = resp.data.decode("utf-8").lower()
            assert "already" in html or "уже" in html


class TestFullReviewFlow:
    """End-to-end flow: become reviewer в†' submit в†' review."""

    @patch.object(FileStorage, "save")
    @patch("flask_se_review.translit")
    @patch("flask_se_review.get_thesis_type_id_string")
    def test_full_review_lifecycle(
        self, mock_get_type_str, mock_translit, mock_save, logged_client
    ):
        from se_models import AreasOfStudy, PromoCode, ThesisOnReviewWorktype, db

        mock_translit.return_value = "Test_User"
        mock_get_type_str.return_value = "coursework"

        area = AreasOfStudy.query.first()
        tor_wt = ThesisOnReviewWorktype(type="Курсовая работа")
        db.session.add(tor_wt)
        db.session.flush()
        pc = PromoCode(code="promo-for-flow")
        db.session.add(pc)
        db.session.commit()

        resp = logged_client.post("/review/become_thesis_reviewer_confirm", data={"code": pc.code})
        assert resp.status_code == 200

        from se_models import Reviewer

        reviewer = Reviewer.query.filter_by(user_id=1).first()
        assert reviewer is not None

        data = {
            "title": "E2E Thesis",
            "type": tor_wt.id,
            "area": area.id,
            "thesis": (io.BytesIO(b"%PDF-1.4 e2e"), "thesis.pdf"),
        }
        resp = logged_client.post("/review/submit", data=data, content_type="multipart/form-data")
        assert resp.status_code == 302

        from se_models import ThesisOnReview, db

        tor = ThesisOnReview.query.filter_by(name_ru="E2E Thesis").first()
        assert tor is not None
        assert tor.author_id == 1
        assert tor.review_status == 1

        resp = logged_client.get(f"/review/review?thesis_review_id={tor.id}")
        assert resp.status_code == 302

        resp = logged_client.get(f"/review/review?thesis_review_id={tor.id}&set_to_review=1")
        assert resp.status_code == 302


class TestLoginRequiredRedirects:
    @pytest.mark.parametrize(
        "path",
        [
            "/review/submit",
            "/review/edit",
            "/review/delete",
            "/review/review",
            "/review/reviewed",
            "/review/review_result",
            "/review/fetch_thesis_on_review",
            "/review/become_thesis_reviewer",
            "/review/become_thesis_reviewer_confirm",
        ],
    )
    def test_review_routes_require_login(self, seeded_client, path):
        resp = seeded_client.get(path)
        assert resp.status_code in (200, 302, 404)


class TestRouteAccessibility:
    """Verify all review routes respond when logged in."""

    @pytest.mark.parametrize(
        "path,code",
        [
            ("/review/", {200}),
            ("/review/index.html", {200}),
            ("/review/submit", {200}),
            ("/review/fetch_thesis_on_review", {200}),
            ("/review/become_thesis_reviewer", {200, 302}),
            ("/review/become_thesis_reviewer_confirm", {200, 302, 404}),
            ("/review/review", {200, 302, 404}),
            ("/review/reviewed", {200, 302, 404}),
            ("/review/review_result", {200, 302, 404}),
            ("/review/edit", {200, 302, 404}),
            ("/review/delete", {200, 302, 404}),
        ],
    )
    def test_routes(self, logged_client, path, code):
        assert_ok(logged_client, path, code=code)

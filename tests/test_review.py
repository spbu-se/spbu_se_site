import pytest
from conftest import assert_ok


@pytest.fixture
def thesis_on_review(seeded_client):
    from se_models import ThesisOnReview, db
    tor = ThesisOnReview(
        name_ru="Test thesis for review",
        author_id=1,
        type_id=2,
        review_status=1,
    )
    db.session.add(tor)
    db.session.commit()
    return seeded_client


@pytest.fixture
def review_with_thesis(thesis_on_review):
    from se_models import Reviewer, db
    r = Reviewer(user_id=1)
    db.session.add(r)
    db.session.commit()
    return thesis_on_review


class TestReviewPublic:
    def test_review_index(self, seeded_client):
        assert_ok(seeded_client, "/review/", code={200, 302})

    def test_review_index_html(self, seeded_client):
        assert_ok(seeded_client, "/review/index.html", code={200, 302})


class TestReviewAuthenticated:
    def test_review_submit_page(self, logged_client):
        assert_ok(logged_client, "/review/submit", code={200, 302})

    def test_review_fetch(self, logged_client):
        assert_ok(logged_client, "/review/fetch_thesis_on_review", code={200, 302})

    def test_review_become_reviewer(self, logged_client):
        assert_ok(logged_client, "/review/become_thesis_reviewer", code={200, 302})

    def test_review_become_reviewer_confirm(self, logged_client):
        assert_ok(logged_client, "/review/become_thesis_reviewer_confirm", code={200, 302})

    def test_review_page_with_id(self, thesis_on_review):
        assert_ok(thesis_on_review, "/review/review?thesis_review_id=1", code={200, 302, 404})

    def test_review_reviewed_page_with_id(self, thesis_on_review):
        assert_ok(thesis_on_review, "/review/reviewed?thesis_review_id=1", code={200, 302, 404})

    def test_review_result(self, logged_client):
        assert_ok(logged_client, "/review/review_result", code={200, 302})

    def test_review_edit_with_id(self, thesis_on_review):
        assert_ok(thesis_on_review, "/review/edit?thesis_review_id=1", code={200, 302, 404})

    def test_review_delete_with_id(self, thesis_on_review):
        assert_ok(thesis_on_review, "/review/delete?thesis_review_id=1", code={200, 302, 404})


class TestReviewSubmitFlow:
    @pytest.mark.xfail(strict=False, reason="KNOWN BUG: .get('title') returns None when form field is not present")
    def test_review_submit_post(self, logged_client):
        resp = logged_client.post("/review/submit", data={
            "title": "Test thesis",
            "author": "Test Author",
        })
        assert resp.status_code in (200, 302)

    def test_review_edit_post(self, logged_client):
        resp = logged_client.post("/review/edit", data={"name_ru": "Updated review thesis"})
        assert resp.status_code in (200, 302, 404)

    def test_review_delete_get(self, logged_client):
        assert_ok(logged_client, "/review/delete", code={200, 302, 404})


class TestReviewerFlow:
    def test_become_reviewer_ask(self, seeded_client):
        resp = seeded_client.get("/review/become_thesis_reviewer_ask")
        assert resp.status_code in (200, 302, 404)

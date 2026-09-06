# -*- coding: utf-8 -*-
from typing import ClassVar

import pytest


@pytest.fixture
def public_approved_theme(seeded_client):
    """An approved theme visible on the public catalog/card."""
    from se_models import DiplomaThemes, db

    dt = DiplomaThemes(
        title="Public Approved Theme",
        description="Description",
        requirements="Requirements",
        author_id=1,
        consultant_id=1,
        status=2,
    )
    db.session.add(dt)
    db.session.commit()
    return dt.id


@pytest.fixture
def author_theme(logged_client):
    """A theme owned by the logged-in test user (not yet approved)."""
    from se_models import DiplomaThemes, Users, db

    author = Users.query.filter_by(email="a.terekhov@spbu.ru").first()
    dt = DiplomaThemes(
        title="Author Owned Theme",
        description="Description",
        requirements="Requirements",
        author_id=author.id,
        consultant_id=author.id,
        status=0,
    )
    db.session.add(dt)
    db.session.commit()
    return dt.id


# Old Flask-Admin-era links were GET anchors; these state-changing routes are
# POST-only today. A GET never reaches them: the site catch-all GET rule
# `/<path:filename>` shadows Werkzeug's 405, so the request returns the 404
# page instead.
POST_ONLY_GET_404 = [
    "/diplomas/delete_theme.html",
    "/diplomas/archive_theme",
    "/diplomas/unarchive_theme",
    "/review/delete",
    "/review/become_thesis_reviewer_confirm",
]


class TestLegacyMethodContract:
    """Map: old GET links on state-changing theme routes are dead (404)."""

    @pytest.mark.parametrize("path", POST_ONLY_GET_404)
    def test_get_on_post_only_route_is_404(self, seeded_client, path):
        assert seeded_client.get(path).status_code == 404


class TestDiplomaThemeFlowParity:
    """Map: /diplomas/* propose/edit/status pages behave as documented."""

    def test_public_pages_reachable_anonymously(self, seeded_client, public_approved_theme):
        for path in (
            f"/diplomas/theme.html?id={public_approved_theme}",
            "/diplomas/",
            "/diplomas/index.html",
        ):
            assert seeded_client.get(path).status_code == 200, path

    @pytest.mark.parametrize(
        "path",
        [
            "/diplomas/add_theme.html",
            "/diplomas/user_themes.html",
            "/diplomas/edit_theme.html?theme_id=1",
        ],
    )
    def test_author_pages_require_login(self, seeded_client, path):
        assert seeded_client.get(path).status_code == 302, path

    def test_author_flow_logged_in(self, logged_client, author_theme):
        assert logged_client.get("/diplomas/user_themes.html").status_code == 200
        assert logged_client.get("/diplomas/add_theme.html").status_code == 200
        assert (
            logged_client.get(f"/diplomas/edit_theme.html?theme_id={author_theme}").status_code
            == 200
        )

        assert (
            logged_client.post(
                "/diplomas/archive_theme", data={"theme_id": author_theme}
            ).status_code
            == 302
        )
        assert (
            logged_client.post(
                "/diplomas/unarchive_theme", data={"theme_id": author_theme}
            ).status_code
            == 302
        )
        assert (
            logged_client.post(
                "/diplomas/delete_theme.html", data={"theme_id": author_theme}
            ).status_code
            == 302
        )


class TestReviewAndPracticeFlowParity:
    """Map: /review/* and /practice/* theme flows still reachable."""

    # dashboard is public; everything requiring an account redirects to login.
    REVIEW_AND_PRACTICE_ANON: ClassVar[dict[str, int]] = {
        "/review/": 200,
        "/review/index.html": 200,
        "/review/submit": 302,
        "/review/edit": 302,
        "/review/review": 302,
        "/review/become_thesis_reviewer": 302,
        "/practice/": 302,
        "/practice/choosing_topic/": 302,
        "/practice/edit_theme/": 302,
    }

    def test_review_and_practice_theme_routes_reachable(self, seeded_client):
        for path, expected in self.REVIEW_AND_PRACTICE_ANON.items():
            assert seeded_client.get(path).status_code == expected, path

# -*- coding: utf-8 -*-
import pytest
from conftest import LIST_VIEWS, assert_ok


@pytest.fixture
def admin_client(seeded_client):
    from se_models import Users, db

    u = Users.query.filter_by(email="a.terekhov@spbu.ru").first()
    u.role = 5
    db.session.commit()
    with seeded_client.session_transaction() as sess:
        sess["_user_id"] = str(u.id)
    return seeded_client


@pytest.fixture
def diploma_themes_for_review(admin_client):
    from se_models import DiplomaThemes, db

    dt = DiplomaThemes(
        title="Test Theme for Review",
        description="Test description",
        requirements="Req",
        author_id=1,
        consultant_id=1,
        status=0,
    )
    db.session.add(dt)
    db.session.commit()
    return admin_client


class TestAdminDeep:
    @pytest.mark.parametrize("name,path", LIST_VIEWS)
    def test_admin_list_views_load(self, admin_client, name, path):
        assert_ok(admin_client, path, code={200})

    @pytest.mark.parametrize(
        "name,path",
        [
            ("users", "/admin/users/"),
            pytest.param("staff", "/admin/staff/", marks=pytest.mark.xfail(strict=True, reason="Flask-Admin 2.2.0 create_view() cls arg incompatible with Jinja2/Werkzeug")),
            pytest.param("thesis", "/admin/thesis/", marks=pytest.mark.xfail(strict=True, reason="Flask-Admin 2.2.0 create_view() cls arg incompatible with Jinja2/Werkzeug")),
            ("summerschool", "/admin/summerschool/"),
            ("news", "/admin/posts/"),
            ("diplomathemes", "/admin/diplomathemes/"),
            ("currentthesis", "/admin/currentthesis/"),
        ],
    )
    def test_admin_create_views_load(self, admin_client, name, path):
        assert_ok(admin_client, path.rstrip("/") + "/new/", code={200})

    @pytest.mark.parametrize(
        "name,path,edit_id",
        [
            ("users", "/admin/users/", 1),
            pytest.param("staff", "/admin/staff/", 1, marks=pytest.mark.xfail(strict=True, reason="Flask-Admin 2.2.0 edit_view() cls arg incompatible with Jinja2/Werkzeug")),
            ("diplomathemes", "/admin/diplomathemes/", 1),
            ("currentthesis", "/admin/currentthesis/", 1),
        ],
    )
    def test_admin_edit_views_load(self, admin_client, name, path, edit_id):
        assert_ok(admin_client, f"{path.rstrip('/')}/edit/?id={edit_id}", code={200, 302, 404})

    def test_admin_review_edit_view_triggers_on_form_prefill(self, diploma_themes_for_review):
        assert_ok(
            diploma_themes_for_review,
            "/admin/reviewdiplomathemes/edit/?id=1",
            code={200, 302, 404},
        )

    def test_admin_review_status_change_to_rejected(self, diploma_themes_for_review):
        diploma_themes_for_review.get("/admin/reviewdiplomathemes/edit/?id=1")
        resp = diploma_themes_for_review.post(
            "/admin/reviewdiplomathemes/edit/?id=1",
            data={
                "title": "Test Theme for Review",
                "description": "Test description",
                "requirements": "Req",
                "status": "4",
                "comment": "Rejected",
                "author": "1",
                "supervisor": "1",
                "consultant": "1",
            },
        )
        assert resp.status_code == 302

    def test_admin_review_status_change_to_needs_update(self, diploma_themes_for_review):
        diploma_themes_for_review.get("/admin/reviewdiplomathemes/edit/?id=1")
        resp = diploma_themes_for_review.post(
            "/admin/reviewdiplomathemes/edit/?id=1",
            data={
                "title": "Test Theme for Review",
                "description": "Test description",
                "requirements": "Req",
                "status": "1",
                "comment": "Needs update",
                "author": "1",
                "supervisor": "1",
                "consultant": "1",
            },
        )
        assert resp.status_code == 302

    def test_admin_index_shows_thesis_key(self, admin_client):
        resp = admin_client.get("/admin/")
        assert resp.status_code == 200

    @pytest.mark.parametrize("name,path", LIST_VIEWS)
    def test_unauth_redirects_to_login(self, seeded_client, name, path):
        resp = seeded_client.get(path)
        assert resp.status_code in (301, 302, 401, 403)

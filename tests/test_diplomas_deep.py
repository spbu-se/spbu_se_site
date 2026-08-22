# -*- coding: utf-8 -*-
import pytest
from conftest import assert_ok


def _make_theme(title, **overrides):
    from se_models import DiplomaThemes, ThemesLevel, db

    defaults = {
        "description": "Desc",
        "company_id": 1,
        "consultant_id": 1,
        "author_id": 1,
        "status": 0,
    }
    defaults.update(overrides)
    theme = DiplomaThemes(title=title, **defaults)
    theme.levels = [ThemesLevel.query.filter_by(id=1).first()]
    db.session.add(theme)
    db.session.commit()
    return theme


@pytest.fixture
def diploma_theme(logged_client):
    from se_models import DiplomaThemes, ThemesLevel, db

    theme = DiplomaThemes(
        title="Test Theme for Owner",
        description="Description",
        requirements="Requirements",
        consultant_id=1,
        company_id=1,
        author_id=1,
        status=2,
    )
    theme.levels = [ThemesLevel.query.filter_by(id=1).first()]
    db.session.add(theme)
    db.session.commit()
    return logged_client


class TestDiplomasDeep:
    def test_diplomas_index(self, logged_client):
        assert_ok(logged_client, "/diplomas/", code={200})

    def test_fetch_themes(self, seeded_client):
        assert_ok(seeded_client, "/diplomas/fetch_themes", code={200})

    def test_fetch_themes_with_company(self, seeded_client):
        assert_ok(seeded_client, "/diplomas/fetch_themes?company=1", code={200})

    def test_fetch_themes_with_supervisor(self, seeded_client):
        assert_ok(seeded_client, "/diplomas/fetch_themes?supervisor=1", code={200})

    def test_fetch_themes_with_level(self, seeded_client):
        assert_ok(seeded_client, "/diplomas/fetch_themes?level=1", code={200})

    def test_get_theme_no_id(self, seeded_client):
        assert_ok(seeded_client, "/diplomas/theme.html", code={302})

    def test_theme_page_renders_markdown_unescaped(self, seeded_client):
        theme = _make_theme(
            "Markdown Theme",
            description="[Spla](https://example.org) and\n\n- one\n- two",
            requirements="- req one\n- req two",
            status=2,
        )
        resp = seeded_client.get(f"/diplomas/theme.html?id={theme.id}")
        assert resp.status_code == 200
        body = resp.data.decode("utf-8")
        assert '<a href="https://example.org"' in body
        assert "<ul>" in body
        assert "&lt;a href" not in body

    @pytest.mark.parametrize(
        "path, code, methods",
        [
            ("/diplomas/add_theme.html", {200}, {"GET"}),
            ("/diplomas/edit_theme.html", {302}, {"GET"}),
            ("/diplomas/delete_theme.html", {302}, {"POST"}),
            ("/diplomas/user_themes.html", {200, 302}, {"GET"}),
            ("/diplomas/fetch_themes?level=99999", {200}, {"GET"}),
            ("/diplomas/fetch_themes?supervisor=5", {200}, {"GET"}),
        ],
    )
    def test_route_checks(self, logged_client, path, code, methods):
        assert_ok(logged_client, path, methods=methods, code=code)

    @pytest.mark.parametrize(
        "data,code",
        [
            ({"description": "Some description"}, {200}),
            ({"title": "Some title"}, {200}),
            ({"title": "Some title", "description": "Some description"}, {200}),
            ({"title": "Some title", "description": "Some description", "levels": 1}, {200}),
            (
                {
                    "title": "New Test Theme",
                    "description": "A description for the new theme",
                    "requirements": "Some requirements",
                    "levels": 1,
                    "company": 1,
                },
                {200, 302},
            ),
        ],
    )
    def test_add_theme(self, logged_client, data, code):
        resp = logged_client.post("/diplomas/add_theme.html", data=data)
        assert resp.status_code in code

    def test_edit_theme_page(self, diploma_theme):
        assert_ok(diploma_theme, "/diplomas/edit_theme.html?theme_id=1", code={200, 302, 404})

    def test_edit_theme_success(self, diploma_theme):
        resp = diploma_theme.post(
            "/diplomas/edit_theme.html?theme_id=1",
            data={
                "title": "Updated Title",
                "description": "Updated description",
                "requirements": "Updated requirements",
                "levels": 2,
                "company": 1,
            },
        )
        assert resp.status_code in (200, 302)

    def test_delete_theme_success(self, diploma_theme):
        resp = diploma_theme.post("/diplomas/delete_theme.html", data={"theme_id": 1})
        assert resp.status_code in (200, 302)

    @pytest.mark.parametrize("endpoint", ["/diplomas/archive_theme", "/diplomas/unarchive_theme"])
    def test_archive_toggle(self, diploma_theme, endpoint):
        resp = diploma_theme.post(endpoint, data={"theme_id": 1})
        assert resp.status_code in (200, 302)

    def test_diplomas_index_with_nonexistent_supervisor(self, logged_client):
        _make_theme("Orphan Supervisor Theme", supervisor_id=99999, status=2)
        assert_ok(logged_client, "/diplomas/", code={200})

    def test_user_themes_render_with_themes(self, logged_client):
        _make_theme("User Theme for Render Test")
        assert_ok(logged_client, "/diplomas/user_themes.html", code={200})

    @pytest.mark.parametrize(
        "payload",
        [
            {
                "title": "Test Invalid Level",
                "description": "Test description",
                "levels": [99999],
                "company": 1,
            },
            {
                "title": "Test Invalid Company",
                "description": "Test description",
                "levels": [1],
                "company": 99999,
            },
        ],
    )
    def test_add_theme_invalid_field(self, logged_client, payload):
        resp = logged_client.post("/diplomas/add_theme.html", data=payload)
        assert resp.status_code in (200,)

    def test_delete_theme_created_by_user(self, logged_client):
        from se_models import DiplomaThemes

        theme = _make_theme("Theme to Delete")
        theme_id = theme.id
        resp = logged_client.post("/diplomas/delete_theme.html", data={"theme_id": theme_id})
        assert resp.status_code in (200, 302)
        assert DiplomaThemes.query.filter_by(id=theme_id).first() is None

    def test_edit_theme_post(self, logged_client):
        from se_models import DiplomaThemes

        theme = _make_theme("Theme to Edit")
        theme_id = theme.id
        resp = logged_client.post(
            f"/diplomas/edit_theme.html?theme_id={theme_id}",
            data={
                "title": "Updated Title",
                "description": "Updated description",
                "requirements": "Updated requirements",
                "levels": [1],
                "company": 1,
            },
        )
        assert resp.status_code in (200, 302)
        updated = DiplomaThemes.query.filter_by(id=theme_id).first()
        assert updated.title == "Updated Title"

    @pytest.mark.parametrize(
        "payload",
        [
            {"title": "", "description": "Desc", "levels": [1], "company": 1},
            {"title": "Title", "description": "Desc", "levels": [99999], "company": 1},
            {"title": "Title", "description": "Desc", "levels": [1], "company": 99999},
            {"title": "Title", "description": "", "levels": [1], "company": 1},
            {"title": "Title", "description": "Desc", "company": 1},
            {"title": "Title", "description": "Desc", "levels": [1]},
        ],
    )
    def test_edit_theme_validation_failure(self, logged_client, payload):
        theme = _make_theme("Theme")
        theme_id = theme.id
        resp = logged_client.post(f"/diplomas/edit_theme.html?theme_id={theme_id}", data=payload)
        assert resp.status_code in (200,)

    @pytest.mark.parametrize(
        "endpoint, initial_status, expected_status",
        [
            ("/diplomas/archive_theme", 0, 3),
            ("/diplomas/unarchive_theme", 3, 0),
        ],
    )
    def test_archive_toggle_owned_by_user(
        self, logged_client, endpoint, initial_status, expected_status
    ):
        from se_models import DiplomaThemes

        theme = _make_theme("Theme", status=initial_status)
        theme_id = theme.id
        resp = logged_client.post(endpoint, data={"theme_id": theme_id})
        assert resp.status_code in (200, 302)
        updated = DiplomaThemes.query.filter_by(id=theme_id).first()
        assert updated.status == expected_status

    def test_diplomas_index_with_null_supervisor(self, logged_client):
        _make_theme("Null Supervisor Theme", supervisor_id=None, status=2)
        assert_ok(logged_client, "/diplomas/", code={200})

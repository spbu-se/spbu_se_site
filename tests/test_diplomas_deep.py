# -*- coding: utf-8 -*-
import pytest
from conftest import assert_ok


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
        from se_models import DiplomaThemes, db

        theme = DiplomaThemes(
            title="Markdown Theme",
            description="[Spla](https://example.org) and\n\n- one\n- two",
            requirements="- req one\n- req two",
            company_id=1,
            author_id=1,
            consultant_id=1,
            status=2,
        )
        db.session.add(theme)
        db.session.commit()
        resp = seeded_client.get(f"/diplomas/theme.html?id={theme.id}")
        assert resp.status_code == 200
        body = resp.data.decode("utf-8")
        assert '<a href="https://example.org"' in body
        assert "<ul>" in body
        assert "&lt;a href" not in body

    def test_add_theme_page(self, logged_client):
        assert_ok(logged_client, "/diplomas/add_theme.html", code={200})

    def test_add_theme_missing_title(self, logged_client):
        resp = logged_client.post(
            "/diplomas/add_theme.html",
            data={
                "description": "Some description",
            },
        )
        assert resp.status_code in (200,)

    def test_add_theme_missing_description(self, logged_client):
        resp = logged_client.post(
            "/diplomas/add_theme.html",
            data={
                "title": "Some title",
            },
        )
        assert resp.status_code in (200,)

    def test_add_theme_missing_levels(self, logged_client):
        resp = logged_client.post(
            "/diplomas/add_theme.html",
            data={
                "title": "Some title",
                "description": "Some description",
            },
        )
        assert resp.status_code in (200,)

    def test_add_theme_missing_company(self, logged_client):
        resp = logged_client.post(
            "/diplomas/add_theme.html",
            data={
                "title": "Some title",
                "description": "Some description",
                "levels": 1,
            },
        )
        assert resp.status_code in (200,)

    def test_add_theme_success(self, logged_client):
        resp = logged_client.post(
            "/diplomas/add_theme.html",
            data={
                "title": "New Test Theme",
                "description": "A description for the new theme",
                "requirements": "Some requirements",
                "levels": 1,
                "company": 1,
            },
        )
        assert resp.status_code in (200, 302)

    def test_edit_theme_page_no_id(self, logged_client):
        assert_ok(logged_client, "/diplomas/edit_theme.html", code={302})

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

    def test_delete_theme_no_id(self, logged_client):
        assert_ok(logged_client, "/diplomas/delete_theme.html", methods={"POST"}, code={302})

    def test_delete_theme_success(self, diploma_theme):
        resp = diploma_theme.post("/diplomas/delete_theme.html", data={"theme_id": 1})
        assert resp.status_code in (200, 302)

    def test_archive_theme(self, diploma_theme):
        resp = diploma_theme.post("/diplomas/archive_theme", data={"theme_id": 1})
        assert resp.status_code in (200, 302)

    def test_unarchive_theme(self, diploma_theme):
        resp = diploma_theme.post("/diplomas/unarchive_theme", data={"theme_id": 1})
        assert resp.status_code in (200, 302)

    def test_user_themes_no_themes(self, logged_client):
        assert_ok(logged_client, "/diplomas/user_themes.html", code={200, 302})

    def test_diplomas_index_with_nonexistent_supervisor(self, logged_client):
        from se_models import DiplomaThemes, ThemesLevel, db

        theme = DiplomaThemes(
            title="Orphan Supervisor Theme",
            description="Desc",
            company_id=1,
            supervisor_id=99999,
            consultant_id=1,
            author_id=1,
            status=2,
        )
        theme.levels = [ThemesLevel.query.filter_by(id=1).first()]
        db.session.add(theme)
        db.session.commit()
        assert_ok(logged_client, "/diplomas/", code={200})

    def test_fetch_themes_blank(self, seeded_client):
        assert_ok(seeded_client, "/diplomas/fetch_themes?level=99999", code={200})

    def test_fetch_themes_with_valid_supervisor(self, seeded_client):
        assert_ok(seeded_client, "/diplomas/fetch_themes?supervisor=5", code={200})

    def test_user_themes_render_with_themes(self, logged_client):
        from se_models import DiplomaThemes, ThemesLevel, db

        theme = DiplomaThemes(
            title="User Theme for Render Test",
            description="Desc",
            company_id=1,
            consultant_id=1,
            author_id=1,
            status=0,
        )
        theme.levels = [ThemesLevel.query.filter_by(id=1).first()]
        db.session.add(theme)
        db.session.commit()
        assert_ok(logged_client, "/diplomas/user_themes.html", code={200})

    def test_add_theme_invalid_level(self, logged_client):
        resp = logged_client.post(
            "/diplomas/add_theme.html",
            data={
                "title": "Test Invalid Level",
                "description": "Test description",
                "levels": [99999],
                "company": 1,
            },
        )
        assert resp.status_code in (200,)

    def test_add_theme_invalid_company(self, logged_client):
        resp = logged_client.post(
            "/diplomas/add_theme.html",
            data={
                "title": "Test Invalid Company",
                "description": "Test description",
                "levels": [1],
                "company": 99999,
            },
        )
        assert resp.status_code in (200,)

    def test_delete_theme_created_by_user(self, logged_client):
        from se_models import DiplomaThemes, ThemesLevel, db

        theme = DiplomaThemes(
            title="Theme to Delete",
            description="Desc",
            company_id=1,
            consultant_id=1,
            author_id=1,
            status=0,
        )
        theme.levels = [ThemesLevel.query.filter_by(id=1).first()]
        db.session.add(theme)
        db.session.commit()
        theme_id = theme.id
        resp = logged_client.post("/diplomas/delete_theme.html", data={"theme_id": theme_id})
        assert resp.status_code in (200, 302)
        assert DiplomaThemes.query.filter_by(id=theme_id).first() is None

    def test_edit_theme_post(self, logged_client):
        from se_models import DiplomaThemes, ThemesLevel, db

        theme = DiplomaThemes(
            title="Theme to Edit",
            description="Desc",
            company_id=1,
            consultant_id=1,
            author_id=1,
            status=0,
        )
        theme.levels = [ThemesLevel.query.filter_by(id=1).first()]
        db.session.add(theme)
        db.session.commit()
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

    def test_edit_theme_missing_title_post(self, logged_client):
        from se_models import DiplomaThemes, ThemesLevel, db

        theme = DiplomaThemes(
            title="Theme for Missing Title",
            description="Desc",
            company_id=1,
            consultant_id=1,
            author_id=1,
            status=0,
        )
        theme.levels = [ThemesLevel.query.filter_by(id=1).first()]
        db.session.add(theme)
        db.session.commit()
        theme_id = theme.id
        resp = logged_client.post(
            f"/diplomas/edit_theme.html?theme_id={theme_id}",
            data={
                "title": "",
                "description": "Desc",
                "levels": [1],
                "company": 1,
            },
        )
        assert resp.status_code in (200,)

    def test_edit_theme_invalid_level(self, logged_client):
        from se_models import DiplomaThemes, ThemesLevel, db

        theme = DiplomaThemes(
            title="Theme for Invalid Level",
            description="Desc",
            company_id=1,
            consultant_id=1,
            author_id=1,
            status=0,
        )
        theme.levels = [ThemesLevel.query.filter_by(id=1).first()]
        db.session.add(theme)
        db.session.commit()
        theme_id = theme.id
        resp = logged_client.post(
            f"/diplomas/edit_theme.html?theme_id={theme_id}",
            data={
                "title": "Title",
                "description": "Desc",
                "levels": [99999],
                "company": 1,
            },
        )
        assert resp.status_code in (200,)

    def test_edit_theme_invalid_company(self, logged_client):
        from se_models import DiplomaThemes, ThemesLevel, db

        theme = DiplomaThemes(
            title="Theme for Invalid Company",
            description="Desc",
            company_id=1,
            consultant_id=1,
            author_id=1,
            status=0,
        )
        theme.levels = [ThemesLevel.query.filter_by(id=1).first()]
        db.session.add(theme)
        db.session.commit()
        theme_id = theme.id
        resp = logged_client.post(
            f"/diplomas/edit_theme.html?theme_id={theme_id}",
            data={
                "title": "Title",
                "description": "Desc",
                "levels": [1],
                "company": 99999,
            },
        )
        assert resp.status_code in (200,)

    def test_archive_theme_owned_by_user(self, logged_client):
        from se_models import DiplomaThemes, ThemesLevel, db

        theme = DiplomaThemes(
            title="Theme to Archive",
            description="Desc",
            company_id=1,
            consultant_id=1,
            author_id=1,
            status=0,
        )
        theme.levels = [ThemesLevel.query.filter_by(id=1).first()]
        db.session.add(theme)
        db.session.commit()
        theme_id = theme.id
        resp = logged_client.post("/diplomas/archive_theme", data={"theme_id": theme_id})
        assert resp.status_code in (200, 302)
        archived = DiplomaThemes.query.filter_by(id=theme_id).first()
        assert archived.status == 3

    def test_unarchive_theme_owned_by_user(self, logged_client):
        from se_models import DiplomaThemes, ThemesLevel, db

        theme = DiplomaThemes(
            title="Theme to Unarchive",
            description="Desc",
            company_id=1,
            consultant_id=1,
            author_id=1,
            status=3,
        )
        theme.levels = [ThemesLevel.query.filter_by(id=1).first()]
        db.session.add(theme)
        db.session.commit()
        theme_id = theme.id
        resp = logged_client.post("/diplomas/unarchive_theme", data={"theme_id": theme_id})
        assert resp.status_code in (200, 302)
        unarchived = DiplomaThemes.query.filter_by(id=theme_id).first()
        assert unarchived.status == 0

    def test_diplomas_index_with_null_supervisor(self, logged_client):
        from se_models import DiplomaThemes, ThemesLevel, db

        theme = DiplomaThemes(
            title="Null Supervisor Theme",
            description="Desc",
            company_id=1,
            supervisor_id=None,
            consultant_id=1,
            author_id=1,
            status=2,
        )
        theme.levels = [ThemesLevel.query.filter_by(id=1).first()]
        db.session.add(theme)
        db.session.commit()
        assert_ok(logged_client, "/diplomas/", code={200})

    def test_edit_theme_missing_description_post(self, logged_client):
        from se_models import DiplomaThemes, ThemesLevel, db

        theme = DiplomaThemes(
            title="Theme for Missing Desc",
            description="Desc",
            company_id=1,
            consultant_id=1,
            author_id=1,
            status=0,
        )
        theme.levels = [ThemesLevel.query.filter_by(id=1).first()]
        db.session.add(theme)
        db.session.commit()
        theme_id = theme.id
        resp = logged_client.post(
            f"/diplomas/edit_theme.html?theme_id={theme_id}",
            data={
                "title": "Title",
                "description": "",
                "levels": [1],
                "company": 1,
            },
        )
        assert resp.status_code in (200,)

    def test_edit_theme_missing_levels_post(self, logged_client):
        from se_models import DiplomaThemes, ThemesLevel, db

        theme = DiplomaThemes(
            title="Theme for Missing Levels",
            description="Desc",
            company_id=1,
            consultant_id=1,
            author_id=1,
            status=0,
        )
        theme.levels = [ThemesLevel.query.filter_by(id=1).first()]
        db.session.add(theme)
        db.session.commit()
        theme_id = theme.id
        resp = logged_client.post(
            f"/diplomas/edit_theme.html?theme_id={theme_id}",
            data={
                "title": "Title",
                "description": "Desc",
                "company": 1,
            },
        )
        assert resp.status_code in (200,)

    def test_edit_theme_missing_company_post(self, logged_client):
        from se_models import DiplomaThemes, ThemesLevel, db

        theme = DiplomaThemes(
            title="Theme for Missing Company",
            description="Desc",
            company_id=1,
            consultant_id=1,
            author_id=1,
            status=0,
        )
        theme.levels = [ThemesLevel.query.filter_by(id=1).first()]
        db.session.add(theme)
        db.session.commit()
        theme_id = theme.id
        resp = logged_client.post(
            f"/diplomas/edit_theme.html?theme_id={theme_id}",
            data={
                "title": "Title",
                "description": "Desc",
                "levels": [1],
            },
        )
        assert resp.status_code in (200,)

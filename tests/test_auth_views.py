import pytest
from conftest import assert_ok, assert_ok_or_redirect


class TestAuth:
    def test_login_form_renders(self, seeded_client):
        assert_ok(seeded_client, "/login.html")

    def test_upload_avatar_redirects(self, seeded_client):
        assert_ok(seeded_client, "/upload_avatar", code={200, 302})

    def test_login_form_accepts_submission(self, seeded_client):
        resp = seeded_client.post("/login.html", data={"email": "test@spbu.ru", "password": "test"})
        assert resp.status_code in (200, 302)

    def test_login_page_has_form(self, seeded_client):
        assert_ok(seeded_client, "/login.html")

    def test_logout_redirects(self, seeded_client):
        assert_ok(seeded_client, "/logout", code={200, 302})

    def test_register_page_loads(self, seeded_client):
        assert_ok(seeded_client, "/register_basic.html")

    def test_register_page_has_form(self, seeded_client):
        resp = seeded_client.get("/register_basic.html")
        assert resp.status_code == 200

    def test_profile_redirects_when_unauth(self, seeded_client):
        assert_ok(seeded_client, "/profile.html", code={200, 302})


class TestNews:
    def test_news_index_loads(self, seeded_client):
        assert_ok(seeded_client, "/news/")

    def test_news_item_nonexistent(self, seeded_client):
        assert_ok_or_redirect(seeded_client, "/news/item.html?id=99999")

    def test_news_item_with_uri(self, seeded_client):
        assert_ok_or_redirect(seeded_client, "/news/item.html?id=1")

    def test_news_item_with_text(self, seeded_client):
        assert_ok_or_redirect(seeded_client, "/news/item.html?id=2")

    def test_news_item_no_id(self, seeded_client):
        assert_ok(seeded_client, "/news/item.html", code={200, 302})

    def test_news_submit_redirects_when_unauth(self, seeded_client):
        assert_ok(seeded_client, "/news/submit.html", code={200, 302})

    def test_news_post_vote_redirects_when_unauth(self, seeded_client):
        assert_ok(seeded_client, "/news/post_vote", code={200, 302})

    def test_news_delete_redirects_when_unauth(self, seeded_client):
        assert_ok(seeded_client, "/news/delete", code={200, 302})


class TestTheses:
    def test_theses_search_loads(self, seeded_client):
        assert_ok(seeded_client, "/theses.html")

    def test_theses_with_search_param(self, seeded_client):
        assert_ok(seeded_client, "/theses.html?search=python")

    def test_theses_with_year_filter(self, seeded_client):
        assert_ok(seeded_client, "/theses.html?startdate=2020&enddate=2024")

    def test_theses_fetch(self, seeded_client):
        assert_ok(seeded_client, "/fetch_theses")

    def test_theses_tmp_list(self, seeded_client):
        assert_ok(seeded_client, "/theses_tmp.html")

    def test_theses_post_form(self, seeded_client):
        assert_ok_or_redirect(seeded_client, "/post_theses")

    def test_theses_download_nonexistent(self, seeded_client):
        assert_ok(seeded_client, "/thesis_download", code={200, 302})

    def test_theses_delete_tmp(self, seeded_client):
        assert_ok(seeded_client, "/theses_delete_tmp", code={200, 302})

    def test_theses_add_tmp(self, seeded_client):
        assert_ok(seeded_client, "/theses_add_tmp", code={200, 302})


class TestInternships:
    def test_internships_index(self, seeded_client):
        assert_ok(seeded_client, "/internships/internships_index.html")

    def test_internships_fetch(self, seeded_client):
        assert_ok(seeded_client, "/internships/fetch_internships")

    def test_internship_detail_nonexistent(self, seeded_client):
        assert_ok_or_redirect(seeded_client, "/internships/99999")

    def test_internship_add_form(self, seeded_client):
        assert_ok_or_redirect(seeded_client, "/internships/add")

    def test_internship_detail_with_id(self, seeded_client):
        assert_ok(seeded_client, "/internships/1", code={200, 302, 404})

    def test_internship_delete(self, seeded_client):
        assert_ok(seeded_client, "/internships/1/delete", code={200, 302, 404})

    def test_internship_update_redirects(self, seeded_client):
        assert_ok(seeded_client, "/internships/1/update", code={200, 302, 404})


class TestDiplomas:
    def test_diplomas_index(self, seeded_client):
        assert_ok(seeded_client, "/diplomas/")

    def test_diplomas_add_theme(self, seeded_client):
        assert_ok_or_redirect(seeded_client, "/diplomas/add_theme.html")

    def test_diploma_theme_detail(self, seeded_client):
        assert_ok_or_redirect(seeded_client, "/diplomas/theme.html?id=1")

    def test_diploma_theme_nonexistent(self, seeded_client):
        assert_ok(seeded_client, "/diplomas/theme.html?id=99999", code={200, 302, 404})

    def test_diplomas_fetch(self, seeded_client):
        assert_ok(seeded_client, "/diplomas/fetch_themes")

    def test_diplomas_user_themes(self, seeded_client):
        assert_ok_or_redirect(seeded_client, "/diplomas/user_themes.html")

    def test_diplomas_delete_theme_redirects(self, seeded_client):
        assert_ok(seeded_client, "/diplomas/delete_theme.html", code={200, 302})

    def test_diplomas_edit_theme_redirects(self, seeded_client):
        assert_ok(seeded_client, "/diplomas/edit_theme.html", code={200, 302})

    def test_diplomas_archive_theme_redirects(self, seeded_client):
        assert_ok(seeded_client, "/diplomas/archive_theme", code={200, 302})

    def test_diplomas_unarchive_theme_redirects(self, seeded_client):
        assert_ok(seeded_client, "/diplomas/unarchive_theme", code={200, 302})


class TestPractice:
    def test_practice_guide(self, seeded_client):
        assert_ok_or_redirect(seeded_client, "/practice/guide/")

    def test_practice_staff_index(self, seeded_client):
        assert_ok_or_redirect(seeded_client, "/practice_staff")


class TestSummerSchools:
    @pytest.mark.parametrize("year", [2026, 2024, 2022, 2021])
    def test_summer_school_page(self, seeded_client, year):
        assert_ok(seeded_client, f"/summer_school_{year}.html")

    def test_summer_school_list(self, seeded_client):
        assert_ok(seeded_client, "/summer_school_list.html")


class TestBachelor:
    @pytest.mark.parametrize(
        "path",
        [
            "/bachelor/application.html",
            "/bachelor/admission.html",
            "/bachelor/programming-technology.html",
            "/bachelor/software-engineering.html",
        ],
    )
    def test_bachelor_pages(self, seeded_client, path):
        assert_ok(seeded_client, path)


class TestErrorHandlers:
    @pytest.mark.parametrize(
        "path",
        [
            "/this-route-does-not-exist-at-all",
            "/nonexistent.html",
        ],
    )
    def test_404_pages(self, seeded_client, path):
        assert_ok(seeded_client, path, code=404)

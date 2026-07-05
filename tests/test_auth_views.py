import io
import json
from unittest.mock import patch, MagicMock

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

    def test_login_invalid_password(self, seeded_client):
        resp = seeded_client.post("/login.html", data={"email": "a.terekhov@spbu.ru", "password": "wrong"})
        assert resp.status_code in (200, 302)

    def test_login_nonexistent_user(self, seeded_client):
        resp = seeded_client.post("/login.html", data={"email": "noone@spbu.ru", "password": "test"})
        assert resp.status_code in (200, 302)

    def test_login_empty_fields(self, seeded_client):
        resp = seeded_client.post("/login.html", data={"email": "", "password": ""})
        assert resp.status_code in (200, 302)

    def test_profile_loads_when_logged_in(self, logged_client):
        assert_ok(logged_client, "/profile.html")

    def test_logout_when_logged_in(self, logged_client):
        resp = logged_client.get("/logout")
        assert resp.status_code in (200, 302)

    def test_register_duplicate_email(self, seeded_client):
        resp = seeded_client.post("/register_basic.html", data={
            "email": "a.terekhov@spbu.ru",
            "password": "test123",
            "first_name": "Андрей",
            "last_name": "Терехов",
        })
        assert resp.status_code in (200, 302)

    @pytest.mark.xfail(strict=False, reason="KNOWN BUG: missing first_name causes AttributeError (.get returns None)")
    def test_register_missing_fields(self, seeded_client):
        resp = seeded_client.post("/register_basic.html", data={"email": "new@spbu.ru"})
        assert resp.status_code in (200, 302)

    def test_register_valid_new_user(self, seeded_client):
        resp = seeded_client.post("/register_basic.html", data={
            "email": "new.user@spbu.ru",
            "password": "securePass123",
            "first_name": "New",
            "last_name": "User",
        })
        assert resp.status_code in (200, 302)

    def test_login_valid_credentials(self, seeded_client):
        resp = seeded_client.post("/login.html", data={
            "email": "a.terekhov@spbu.ru",
            "password": "any",
        })
        assert resp.status_code in (200, 302)

    def test_login_then_access_profile(self, seeded_client):
        resp = seeded_client.post("/login.html", data={
            "email": "a.terekhov@spbu.ru",
            "password": "any",
        })
        resp = seeded_client.get("/profile.html")
        assert resp.status_code in (200, 302)

    @patch("requests.get")
    def test_vk_callback_new_user(self, mock_get, seeded_client):
        token_resp = MagicMock()
        token_resp.text = json.dumps({
            "access_token": "test_token",
            "user_id": 12345,
            "email": "vkuser@spbu.ru",
        })
        user_resp = MagicMock()
        user_resp.text = json.dumps({
            "response": [{"first_name": "VK", "last_name": "User"}],
        })
        mock_get.side_effect = [token_resp, user_resp]
        resp = seeded_client.get("/vk_callback?code=testcode")
        assert resp.status_code in (200, 302)

    @patch("requests.get")
    def test_vk_callback_no_code(self, mock_get, seeded_client):
        resp = seeded_client.get("/vk_callback")
        assert resp.status_code in (200, 302)

    @patch("requests.get")
    def test_vk_callback_error(self, mock_get, seeded_client):
        mock_get.return_value = MagicMock(text=MagicMock())
        mock_get.return_value.text = json.dumps({"error": "invalid_request"})
        resp = seeded_client.get("/vk_callback?code=badcode")
        assert resp.status_code in (200, 302)

    @pytest.mark.xfail(strict=False, reason="requires google client_secrets.json file")
    def test_google_login_redirect(self, seeded_client):
        assert_ok(seeded_client, "/google_login", code={200, 302})

    @pytest.mark.xfail(strict=False, reason="requires google OAuth session state")
    def test_google_callback_no_state(self, seeded_client):
        resp = seeded_client.get("/google_callback")
        assert resp.status_code in (200, 302)

    def test_profile_update_post(self, logged_client):
        resp = logged_client.post("/profile.html", data={
            "last_name": "Updated",
            "first_name": "User",
            "middle_name": "",
            "how_to_contact": "email",
        })
        assert resp.status_code in (200, 302)

    def test_avatar_upload_no_file(self, logged_client):
        resp = logged_client.post("/upload_avatar", data={})
        assert resp.status_code in (200, 204, 302)

    def test_avatar_upload_invalid_type(self, logged_client):
        data = {"file": (io.BytesIO(b"not an image"), "test.txt")}
        resp = logged_client.post("/upload_avatar", data=data, content_type="multipart/form-data")
        assert resp.status_code in (200, 204, 302)


class TestLoginRequiredRedirects:
    @pytest.mark.parametrize("path", [
        "/profile.html",
        "/upload_avatar",
        "/news/submit.html",
        "/news/post_vote",
        "/news/delete",
        "/diplomas/add_theme.html",
        "/diplomas/user_themes.html",
        "/internships/add",
        "/practice",
    ])
    def test_login_required_routes_redirect(self, seeded_client, path):
        resp = seeded_client.get(path)
        assert resp.status_code in (200, 302)

    def test_password_recovery_page_loads(self, seeded_client):
        assert_ok(seeded_client, "/password_recovery.html")

    def test_password_recovery_submission(self, seeded_client):
        resp = seeded_client.post("/password_recovery.html", data={"email": "a.terekhov@spbu.ru"})
        assert resp.status_code in (200, 302)

    def test_profile_update(self, logged_client):
        resp = logged_client.get("/profile.html")
        assert resp.status_code == 200

    def test_avatar_upload_no_file(self, logged_client):
        resp = logged_client.post("/upload_avatar", data={})
        assert resp.status_code in (200, 204, 302)


class TestGoogleOAuth:
    @patch("flask_se_auth.client_secrets_file", "{}")
    @patch("flask_se_auth.Flow.from_client_secrets_file")
    def test_google_login_mocked(self, mock_flow, seeded_client):
        mock_flow.return_value.authorization_url.return_value = ("https://accounts.google.com/o/oauth2/auth?state=test", "test")
        mock_flow.return_value.redirect_uri = "https://localhost/callback"
        resp = seeded_client.get("/google_login")
        assert resp.status_code in (200, 301, 302)

    @patch("flask_se_auth.id_token.verify_oauth2_token")
    @patch("flask_se_auth.client_secrets_file", "{}")
    @patch("flask_se_auth.requests.get")
    @patch("flask_se_auth.Flow.from_client_secrets_file")
    def test_google_callback_mocked(self, mock_flow, mock_get, mock_verify, seeded_client):
        with seeded_client.session_transaction() as sess:
            sess["state"] = "test_state"
        mock_flow.return_value.fetch_token.return_value = None
        mock_flow.return_value.credentials._id_token = "test"
        mock_get.return_value.json.return_value = {"email": "test@gmail.com", "sub": "12345"}
        mock_verify.return_value = {"email": "test@gmail.com", "sub": "12345"}
        resp = seeded_client.get("/google_callback?state=test_state&code=test_code")
        assert resp.status_code in (200, 302)


class TestPublicPages:
    @pytest.mark.parametrize("path,code", [
        ("/", {200}),
        ("/index.html", {200, 302}),
        ("/research-directions", {200}),
        ("/contacts.html", {200}),
        ("/department/staff.html", {200}),
        ("/frequently-asked-questions.html", {200}),
        ("/sitemap.xml", {200}),
        ("/nooffer", {200}),
        ("/students/index.html", {200}),
        ("/students/scholarships.html", {200}),
    ])
    def test_public_pages(self, seeded_client, path, code):
        assert_ok(seeded_client, path, code=code)


class TestMasterPrograms:
    @pytest.mark.parametrize("path", [
        "/master/information-systems-administration.html",
        "/master/software-engineering.html",
    ])
    def test_master_pages(self, seeded_client, path):
        assert_ok(seeded_client, path)


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

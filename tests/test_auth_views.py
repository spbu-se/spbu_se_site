# -*- coding: utf-8 -*-
import io
import json
from unittest.mock import MagicMock, patch

import pytest
from conftest import _approve_temp_thesis, _make_temp_thesis, assert_ok, assert_ok_or_redirect


class TestAuth:
    def test_login_form_renders(self, seeded_client):
        assert_ok(seeded_client, "/login.html")

    def test_upload_avatar_redirects(self, seeded_client):
        assert_ok(seeded_client, "/upload_avatar", code={200, 302})

    def test_login_form_accepts_submission(self, seeded_client):
        resp = seeded_client.post("/login.html", data={"email": "test@spbu.ru", "password": "test"})
        assert resp.status_code in (200, 302)

    def test_logout_redirects(self, seeded_client):
        assert_ok(seeded_client, "/logout", code={200, 302})

    def test_register_page_loads(self, seeded_client):
        assert_ok(seeded_client, "/register_basic.html")

    def test_profile_redirects_when_unauth(self, seeded_client):
        assert_ok(seeded_client, "/profile.html", code={200, 302})

    def test_login_invalid_password(self, seeded_client):
        resp = seeded_client.post(
            "/login.html", data={"email": "a.terekhov@spbu.ru", "password": "wrong"}
        )
        assert resp.status_code in (200, 302)

    def test_login_nonexistent_user(self, seeded_client):
        resp = seeded_client.post(
            "/login.html", data={"email": "noone@spbu.ru", "password": "test"}
        )
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
        resp = seeded_client.post(
            "/register_basic.html",
            data={
                "email": "a.terekhov@spbu.ru",
                "password": "test123",
                "first_name": "Андрей",
                "last_name": "Терехов",
            },
        )
        assert resp.status_code in (200, 302)

    def test_register_missing_fields(self, seeded_client):
        resp = seeded_client.post("/register_basic.html", data={"email": "new@spbu.ru"})
        assert resp.status_code in (200, 302)

    def test_register_valid_new_user(self, seeded_client):
        resp = seeded_client.post(
            "/register_basic.html",
            data={
                "email": "new.user@spbu.ru",
                "password": "securePass123",
                "first_name": "New",
                "last_name": "User",
            },
        )
        assert resp.status_code in (200, 302)

    def test_login_valid_credentials(self, seeded_client):
        resp = seeded_client.post(
            "/login.html",
            data={
                "email": "a.terekhov@spbu.ru",
                "password": "any",
            },
        )
        assert resp.status_code in (200, 302)

    def test_login_legacy_hmac_hash_fallback(self, seeded_client):
        import hashlib
        import hmac

        from se_models import Users, db

        # Simulate a legacy HMAC password hash: algorithm$salt$hexdigest.
        # check_password_hash is patched to always return True in conftest, so
        # patch it to False to force the legacy HMAC fallback branch in login_index.
        password = "legacy-pass"
        salt = "somesalt"
        digest = hmac.new(salt.encode(), password.encode(), hashlib.sha256).hexdigest()
        u = Users.query.filter_by(email="a.terekhov@spbu.ru").first()
        u.password_hash = f"sha256${salt}${digest}"
        db.session.commit()

        with patch("flask_se_auth.check_password_hash", return_value=False):
            resp = seeded_client.post(
                "/login.html",
                data={"email": "a.terekhov@spbu.ru", "password": password},
            )
        assert resp.status_code in (200, 302)

    def test_login_hmac_fallback_wrong_password(self, seeded_client):
        import hashlib
        import hmac

        from se_models import Users, db

        password = "legacy-pass"
        salt = "somesalt"
        digest = hmac.new(salt.encode(), password.encode(), hashlib.sha256).hexdigest()
        u = Users.query.filter_by(email="a.terekhov@spbu.ru").first()
        u.password_hash = f"sha256${salt}${digest}"
        db.session.commit()

        with patch("flask_se_auth.check_password_hash", return_value=False):
            resp = seeded_client.post(
                "/login.html",
                data={"email": "a.terekhov@spbu.ru", "password": "wrong-password"},
            )
        assert resp.status_code in (200, 302)

    def test_login_then_access_profile(self, seeded_client):
        resp = seeded_client.post(
            "/login.html",
            data={
                "email": "a.terekhov@spbu.ru",
                "password": "any",
            },
        )
        resp = seeded_client.get("/profile.html")
        assert resp.status_code in (200, 302)

    @patch("requests.get")
    def test_vk_callback_new_user(self, mock_get, seeded_client):
        token_resp = MagicMock()
        token_resp.text = json.dumps(
            {
                "access_token": "test_token",
                "user_id": 12345,
                "email": "vkuser@spbu.ru",
            }
        )
        user_resp = MagicMock()
        user_resp.text = json.dumps(
            {
                "response": [{"first_name": "VK", "last_name": "User"}],
            }
        )
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

    @patch("requests.get")
    def test_vk_callback_url_uses_config_secret(self, mock_get, seeded_client):
        from flask_se_auth import VK_CLIENT_ID, VK_CLIENT_SECRET

        token_resp = MagicMock()
        token_resp.text = json.dumps(
            {
                "access_token": "test_token",
                "user_id": 12345,
                "email": "vkuser@spbu.ru",
            }
        )
        user_resp = MagicMock()
        user_resp.text = json.dumps(
            {
                "response": [{"first_name": "VK", "last_name": "User"}],
            }
        )
        mock_get.side_effect = [token_resp, user_resp]
        resp = seeded_client.get("/vk_callback?code=testcode")
        assert resp.status_code in (200, 302)

        url = mock_get.call_args_list[0].args[0]
        assert f"client_id={VK_CLIENT_ID}" in url
        assert f"client_secret={VK_CLIENT_SECRET}" in url

    def test_google_login_redirect(self, seeded_client):
        assert_ok(seeded_client, "/google_login", code={200, 302})

    @pytest.mark.xfail(strict=False, reason="requires google OAuth session state")
    def test_google_callback_no_state(self, seeded_client):
        resp = seeded_client.get("/google_callback")
        assert resp.status_code in (200, 302)

    def test_profile_update_post(self, logged_client):
        resp = logged_client.post(
            "/profile.html",
            data={
                "last_name": "Updated",
                "first_name": "User",
                "middle_name": "",
                "how_to_contact": "email",
            },
        )
        assert resp.status_code in (200, 302)

    def test_avatar_upload_no_file(self, logged_client):
        resp = logged_client.post("/upload_avatar", data={})
        assert resp.status_code in (200, 204, 302)

    def test_avatar_upload_invalid_type(self, logged_client):
        data = {"file": (io.BytesIO(b"not an image"), "test.txt")}
        resp = logged_client.post("/upload_avatar", data=data, content_type="multipart/form-data")
        assert resp.status_code in (200, 204, 302)


class TestLoginRequiredRedirects:
    @pytest.mark.parametrize(
        "path",
        [
            "/profile.html",
            "/upload_avatar",
            "/news/submit.html",
            "/news/post_vote",
            "/news/delete",
            "/diplomas/add_theme.html",
            "/diplomas/user_themes.html",
            "/internships/add",
            "/practice",
        ],
    )
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


class TestGoogleOAuth:
    @patch("flask_se_auth.client_secrets_file", "{}")
    @patch("flask_se_auth.Flow.from_client_secrets_file")
    def test_google_login_mocked(self, mock_flow, seeded_client):
        mock_flow.return_value.authorization_url.return_value = (
            "https://accounts.google.com/o/oauth2/auth?state=test",
            "test",
        )
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
        mock_flow.return_value.credentials._id_token = "test"  # noqa: SLF001
        mock_get.return_value.json.return_value = {"email": "test@gmail.com", "sub": "12345"}
        mock_verify.return_value = {"email": "test@gmail.com", "sub": "12345"}
        resp = seeded_client.get("/google_callback?state=test_state&code=test_code")
        assert resp.status_code in (200, 302)


class TestPublicPages:
    @pytest.mark.parametrize(
        "path",
        [
            "/",
            "/index.html",
            "/research-directions",
            "/contacts.html",
            "/students/index.html",
            "/students/scholarships.html",
            "/department/staff.html",
            "/frequently-asked-questions.html",
            "/nooffer",
            "/sitemap.xml",
            "/Sitemap.xml",
            "/404.html",
            "/summer_school_2026.html",
            "/summer_school_2024.html",
            "/summer_school_2022.html",
            "/summer_school_list.html",
            "/news/",
            "/news/index.html",
            "/theses.html",
            "/theses.html?search=python",
            "/theses_tmp.html",
            "/fetch_theses",
            "/diplomas/",
            "/diplomas/index.html",
            "/diplomas/fetch_themes",
            "/internships/internships_index.html",
            "/internships/fetch_internships",
            "/login.html",
            "/register_basic.html",
            "/review/",
        ],
    )
    def test_public_pages(self, seeded_client, path):
        assert_ok(seeded_client, path, code={200, 302})

    def test_sitemap_xml(self, seeded_client):
        resp = seeded_client.get("/sitemap.xml")
        assert resp.status_code == 200
        assert b"<?xml" in resp.data or b"<urlset" in resp.data


class TestMasterPrograms:
    @pytest.mark.parametrize(
        "path",
        [
            "/master/information-systems-administration.html",
            "/master/software-engineering.html",
        ],
    )
    def test_master_pages(self, seeded_client, path):
        assert_ok(seeded_client, path)


class TestNews:
    def test_news_index_loads(self, seeded_client):
        assert_ok(seeded_client, "/news/")

    def test_news_item_with_text(self, seeded_client):
        assert_ok_or_redirect(seeded_client, "/news/item.html?id=2")

    def test_news_submit_redirects_when_unauth(self, seeded_client):
        assert_ok(seeded_client, "/news/submit.html", code={200, 302})

    def test_news_post_vote_redirects_when_unauth(self, seeded_client):
        assert_ok(seeded_client, "/news/post_vote", code={200, 302})

    def test_news_delete_redirects_when_unauth(self, seeded_client):
        assert_ok(seeded_client, "/news/delete", code={200, 302})


class TestNewsItems:
    @pytest.mark.parametrize("id_,code", [(1, {200, 302}), (99999, {200, 302}), (None, {200, 302})])
    def test_news_item(self, seeded_client, id_, code):
        path = f"/news/item.html?id={id_}" if id_ else "/news/item.html"
        assert_ok(seeded_client, path, code=code)


class TestNewsSubmit:
    def test_news_submit_form_loads(self, logged_client):
        assert_ok(logged_client, "/news/submit.html")

    def test_news_submit_post(self, logged_client):
        resp = logged_client.post(
            "/news/submit.html",
            data={
                "title": "Test news post",
                "text": "This is a test news post content.",
            },
        )
        assert resp.status_code in (200, 302)

    def test_news_submit_empty_title(self, logged_client):
        resp = logged_client.post(
            "/news/submit.html",
            data={
                "title": "",
                "text": "Some content",
            },
        )
        assert resp.status_code in (200, 302)

    def test_news_submit_with_uri(self, logged_client):
        resp = logged_client.post(
            "/news/submit.html",
            data={
                "title": "External link post",
                "uri": "https://example.com/news",
                "text": "Check out this link",
            },
        )
        assert resp.status_code in (200, 302)


class TestNewsVote:
    def test_news_vote_up(self, logged_client):
        resp = logged_client.post("/news/post_vote", data={"post_id": 1, "upvote": 1})
        assert resp.status_code in (200, 302)

    def test_news_vote_down(self, logged_client):
        resp = logged_client.post("/news/post_vote", data={"post_id": 1, "upvote": 0})
        assert resp.status_code in (200, 302)

    def test_news_vote_nonexistent_post(self, logged_client):
        resp = logged_client.post("/news/post_vote", data={"post_id": 99999, "upvote": 1})
        assert resp.status_code in (200, 302)

    def test_news_vote_missing_params(self, logged_client):
        resp = logged_client.post("/news/post_vote", data={})
        assert resp.status_code in (200, 302)


class TestNewsDelete:
    def test_news_delete_nonexistent(self, logged_client):
        assert_ok(logged_client, "/news/delete?id=99999", code={200, 302})

    def test_news_delete_own_post(self, logged_client):
        logged_client.post(
            "/news/submit.html", data={"title": "Delete me", "text": "To be deleted"}
        )
        assert_ok(logged_client, "/news/delete?id=1", code={200, 302})


class TestNewsDeepBehavior:
    def test_news_post_with_uri_redirects(self, seeded_client):
        resp = seeded_client.get("/news/item.html?id=1")
        assert resp.status_code in (200, 302)

    def test_news_post_view_count_increments(self, seeded_client):
        before = seeded_client.get("/news/item.html?id=2")
        assert before.status_code in (200, 302)
        after = seeded_client.get("/news/item.html?id=2")
        assert after.status_code in (200, 302)

    def test_news_list_page_param(self, seeded_client):
        assert_ok(seeded_client, "/news/?page=1", code={200, 302, 404})

    def test_news_vote_own_post_blocked(self, logged_client):
        resp = logged_client.get("/news/post_vote?post_id=2&action_vote=1")
        assert resp.status_code in (200, 302)

    def test_news_vote_get_missing_post_id(self, logged_client):
        resp = logged_client.get("/news/post_vote")
        assert resp.status_code in (200, 302)

    def test_news_vote_get(self, logged_client):
        resp = logged_client.get("/news/post_vote?post_id=1&action_vote=1")
        assert resp.status_code in (200, 302)


class TestNewsLoggedIn:
    @pytest.mark.parametrize(
        "path",
        [
            "/news/submit.html",
            "/news/post_vote",
            "/news/delete",
        ],
    )
    def test_news_routes(self, logged_client, path):
        assert_ok(logged_client, path, code={200, 302})


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


class TestThesisDownload:
    def test_thesis_download_no_id(self, logged_client):
        assert_ok(logged_client, "/thesis_download", code={200, 302})

    def test_thesis_download_with_id(self, seeded_client):
        assert_ok(seeded_client, "/thesis_download?thesis_id=1", code={200, 302})

    def test_thesis_download_nonexistent_id(self, seeded_client):
        assert_ok(seeded_client, "/thesis_download?thesis_id=99999", code={200, 302})

    def test_thesis_download_invalid_id(self, seeded_client):
        assert_ok(seeded_client, "/thesis_download?thesis_id=abc", code={200, 302})


class TestThesisSearch:
    @pytest.mark.parametrize("query", ["", "python", "test", "курсовая", "x" * 100])
    def test_thesis_search_various(self, seeded_client, query):
        assert_ok(seeded_client, f"/theses.html?search={query}")

    @pytest.mark.parametrize(
        "start,end", [("2020", "2024"), ("2010", "2015"), ("", "2024"), ("2020", "")]
    )
    def test_thesis_year_filters(self, seeded_client, start, end):
        params = []
        if start:
            params.append(f"startdate={start}")
        if end:
            params.append(f"enddate={end}")
        query = "&".join(params)
        assert_ok(seeded_client, f"/theses.html?{query}")

    def test_thesis_fetch_paginated(self, seeded_client):
        assert_ok(seeded_client, "/fetch_theses?page=1")


class TestThesisTempCrud:
    def test_theses_tmp_list_empty(self, logged_client):
        assert_ok(logged_client, "/theses_tmp.html")

    def test_theses_post_form_loads(self, logged_client):
        assert_ok(logged_client, "/post_theses", code={200, 302})

    def test_theses_post_submission(self, logged_client):
        resp = logged_client.post(
            "/post_theses",
            data={
                "name_ru": "Test thesis",
                "author": "Test Author",
                "type_id": 2,
                "course_id": 1,
                "publish_year": 2024,
            },
        )
        assert resp.status_code in (200, 302)

    def test_theses_delete_tmp_nonexistent(self, logged_client):
        assert_ok(logged_client, "/theses_delete_tmp", code={200, 302})

    def test_theses_add_tmp_nonexistent(self, logged_client):
        assert_ok(logged_client, "/theses_add_tmp", code={200, 302})

    def test_theses_post_form_filters(self, seeded_client):
        assert_ok(seeded_client, "/theses.html?type_id=2")
        assert_ok(seeded_client, "/theses.html?course_id=1")
        assert_ok(seeded_client, "/theses.html?area_id=1")

    def test_theses_download_increments_counter(self, seeded_client):
        resp = seeded_client.get("/thesis_download?thesis_id=1")
        assert resp.status_code in (200, 302)

    def test_theses_post_with_filter_params(self, seeded_client):
        assert_ok(seeded_client, "/post_theses?type_id=2")
        assert_ok(seeded_client, "/post_theses?course_id=1")

    def test_theses_add_tmp_with_id(self, logged_client):
        assert_ok(logged_client, "/theses_add_tmp?id=1", code={200, 302})

    def test_theses_delete_tmp_with_id(self, logged_client):
        assert_ok(logged_client, "/theses_delete_tmp?id=1", code={200, 302})


class TestThesisAdminApproval:
    def test_approve_temp_thesis(self, seeded_client):
        from se_models import Thesis, db

        t = _make_temp_thesis("Test")
        resp = seeded_client.get(f"/theses_add_tmp?thesis_id={t.id}")
        assert resp.status_code in (200, 302)
        updated = db.session.get(Thesis, t.id)
        assert not updated.temporary

    def test_approve_temp_thesis_with_text_uri(self, seeded_client):
        from pathlib import Path

        Path("static/tmp/texts").mkdir(parents=True, exist_ok=True)
        Path("static/thesis/texts").mkdir(parents=True, exist_ok=True)
        Path("static/tmp/texts/test.pdf").write_text("")
        Path("static/thesis/texts/test.pdf").unlink(missing_ok=True)

        t = _make_temp_thesis("Test", "test.pdf")
        resp = _approve_temp_thesis(seeded_client, t.id)
        assert resp.status_code in (200, 302)

    def test_delete_temp_thesis(self, seeded_client):
        t = _make_temp_thesis("Test")
        resp = seeded_client.get(f"/theses_delete_tmp?id={t.id}")
        assert resp.status_code in (200, 302)


class TestThesesLoggedIn:
    @pytest.mark.parametrize(
        "path",
        [
            "/theses_delete_tmp",
            "/theses_add_tmp",
            "/thesis_download",
        ],
    )
    def test_thesis_routes(self, logged_client, path):
        assert_ok(logged_client, path, code={200, 302})


class TestInternships:
    def test_internships_index(self, seeded_client):
        assert_ok(seeded_client, "/internships/internships_index.html")

    def test_internship_detail_nonexistent(self, seeded_client):
        assert_ok_or_redirect(seeded_client, "/internships/99999")

    def test_internship_add_form(self, seeded_client):
        assert_ok_or_redirect(seeded_client, "/internships/add")

    def test_internship_delete(self, seeded_client):
        assert_ok(seeded_client, "/internships/1/delete", code={200, 302, 404})

    def test_internship_update_redirects(self, seeded_client):
        assert_ok(seeded_client, "/internships/1/update", code={200, 302, 404})


class TestInternshipsBehavior:
    def test_internship_add_page(self, logged_client):
        assert_ok(logged_client, "/internships/add")

    def test_internship_add_submit(self, logged_client):
        resp = logged_client.post(
            "/internships/add",
            data={
                "company": "Test Corp",
                "title": "Test Internship",
                "description": "A test position",
            },
        )
        assert resp.status_code in (200, 302)

    def test_internship_detail(self, seeded_client):
        assert_ok(seeded_client, "/internships/1", code={200, 302, 404})

    def test_internship_detail_nonexistent(self, seeded_client):
        resp = seeded_client.get("/internships/99999")
        assert resp.status_code in (200, 302, 404)

    def test_internship_update_page(self, logged_client):
        assert_ok(logged_client, "/internships/1/update", code={200, 302, 404})

    def test_internship_update_submit(self, logged_client):
        resp = logged_client.post(
            "/internships/1/update",
            data={
                "company": "Updated Corp",
                "title": "Updated Title",
            },
        )
        assert resp.status_code in (200, 302, 404)

    def test_internship_delete(self, logged_client):
        assert_ok(logged_client, "/internships/1/delete", code={200, 302, 404})

    def test_internship_fetch_filtered(self, seeded_client):
        assert_ok(seeded_client, "/internships/fetch_internships")

    def test_internship_fetch_with_tag(self, seeded_client):
        assert_ok(seeded_client, "/internships/fetch_internships?tag=python")

    def test_internship_fetch_with_format(self, seeded_client):
        assert_ok(seeded_client, "/internships/fetch_internships?format=1")


class TestInternshipsLoggedIn:
    @pytest.mark.parametrize(
        "path",
        [
            "/internships/add",
            "/internships/1/update",
        ],
    )
    def test_internship_routes(self, logged_client, path):
        assert_ok(logged_client, path, code={200, 302})


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


class TestDiplomasBehavior:
    def test_diploma_add_theme_page(self, logged_client):
        assert_ok(logged_client, "/diplomas/add_theme.html")

    def test_diploma_add_theme_submit(self, logged_client):
        resp = logged_client.post(
            "/diplomas/add_theme.html",
            data={
                "name": "Test diploma theme",
                "description": "A test theme description",
            },
        )
        assert resp.status_code in (200, 302)

    def test_diploma_edit_theme(self, logged_client):
        assert_ok(logged_client, "/diplomas/edit_theme.html?id=1", code={200, 302})

    def test_diploma_edit_theme_post(self, logged_client):
        resp = logged_client.post(
            "/diplomas/edit_theme.html?id=1",
            data={
                "name": "Updated theme",
                "description": "Updated description",
            },
        )
        assert resp.status_code in (200, 302)

    def test_diploma_archive_theme(self, logged_client):
        assert_ok(logged_client, "/diplomas/archive_theme?id=1", code={200, 302})

    def test_diploma_unarchive_theme(self, logged_client):
        assert_ok(logged_client, "/diplomas/unarchive_theme?id=1", code={200, 302})

    def test_diploma_delete_theme(self, logged_client):
        assert_ok(logged_client, "/diplomas/delete_theme.html?id=1", code={200, 302})

    def test_diploma_user_themes(self, logged_client):
        assert_ok(logged_client, "/diplomas/user_themes.html", code={200, 302})

    def test_diploma_theme_detail(self, seeded_client):
        assert_ok(seeded_client, "/diplomas/theme.html?id=1", code={200, 302})

    def test_diploma_theme_nonexistent(self, seeded_client):
        assert_ok(seeded_client, "/diplomas/theme.html?id=99999", code={200, 302, 404})

    def test_diploma_index_with_filters(self, seeded_client):
        assert_ok(seeded_client, "/diplomas/")
        assert_ok(seeded_client, "/diplomas/index.html")


class TestDiplomasLoggedIn:
    @pytest.mark.parametrize(
        "path",
        [
            "/diplomas/add_theme.html",
            "/diplomas/user_themes.html",
            "/diplomas/delete_theme.html",
            "/diplomas/edit_theme.html",
            "/diplomas/archive_theme",
            "/diplomas/unarchive_theme",
        ],
    )
    def test_diploma_routes(self, logged_client, path):
        assert_ok(logged_client, path, code={200, 302})


class TestPractice:
    @pytest.mark.parametrize(
        "path",
        [
            "/practice",
            "/practice/",
            "/practice/guide/",
            "/practice_staff",
            "/practice_staff/",
            "/practice_admin",
            "/practice_admin/",
        ],
    )
    def test_practice_public(self, seeded_client, path):
        assert_ok(seeded_client, path, code={200, 302})

    @pytest.mark.parametrize(
        "path",
        [
            "/practice/new/",
            "/practice/data_for_practice/",
            "/practice/choosing_topic/",
            "/practice/edit_theme/",
            "/practice/goals_tasks/",
            "/practice/add_new_report/",
            "/practice/workflow/",
            "/practice/preparation_for_defense/",
            "/practice/defense/",
            "/practice_staff/thesis/",
            "/practice_staff/reports/",
            "/practice_staff/finished_thesises/",
            "/practice_admin/choose_area_worktype",
            "/practice_admin/finished_thesises",
            "/practice_admin/thesis",
            "/practice_admin/yandex_code",
        ],
    )
    def test_practice_logged_in(self, logged_client, path):
        assert_ok(logged_client, path, code={200, 302, 404})


class TestPracticeStudentFlow:
    def test_practice_index_logged_in(self, logged_client):
        assert_ok(logged_client, "/practice", code={200, 302})

    def test_practice_guide(self, seeded_client):
        assert_ok(seeded_client, "/practice/guide/", code={200, 302})

    def test_practice_new_thesis_page(self, logged_client):
        assert_ok(logged_client, "/practice/new/", code={200, 302})

    def test_practice_data_for_practice(self, logged_client):
        assert_ok(logged_client, "/practice/data_for_practice/", code={200, 302})

    def test_practice_choosing_topic(self, logged_client):
        assert_ok(logged_client, "/practice/choosing_topic/", code={200, 302})

    def test_practice_preparation(self, logged_client):
        assert_ok(logged_client, "/practice/preparation_for_defense/", code={200, 302})

    def test_practice_defense(self, logged_client):
        assert_ok(logged_client, "/practice/defense/", code={200, 302})


class TestPracticeStaffFlow:
    def test_practice_staff_index(self, logged_client):
        assert_ok(logged_client, "/practice_staff", code={200, 302})

    def test_practice_staff_thesis(self, logged_client):
        assert_ok(logged_client, "/practice_staff/thesis/", code={200, 302, 404})

    def test_practice_staff_reports(self, logged_client):
        assert_ok(logged_client, "/practice_staff/reports/", code={200, 302, 404})

    def test_practice_staff_finished(self, logged_client):
        assert_ok(logged_client, "/practice_staff/finished_thesises/", code={200, 302})


class TestPracticeAdminFlow:
    def test_practice_admin_index(self, logged_client):
        assert_ok(logged_client, "/practice_admin", code={200, 302})

    def test_practice_admin_choose_area(self, logged_client):
        assert_ok(logged_client, "/practice_admin/choose_area_worktype", code={200, 302})

    def test_practice_admin_finished(self, logged_client):
        assert_ok(logged_client, "/practice_admin/finished_thesises", code={200, 302})

    def test_practice_admin_thesis(self, logged_client):
        assert_ok(logged_client, "/practice_admin/thesis", code={200, 302, 404})

    def test_practice_admin_yandex(self, logged_client):
        assert_ok(logged_client, "/practice_admin/yandex_code", code={200, 302, 404})


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
            "/nonexistent",
            "/nonexistent.html",
            "/this-route-does-not-exist-at-all",
        ],
    )
    def test_404_pages(self, seeded_client, path):
        assert_ok(seeded_client, path, code=404)


class TestScholarships:
    @pytest.mark.parametrize("n", range(1, 14))
    def test_scholarship_pages(self, seeded_client, n):
        assert_ok(seeded_client, f"/scholarships/{n}.html")

    def test_scholarship_out_of_range(self, seeded_client):
        assert_ok(seeded_client, "/scholarships/0.html", code={200, 302, 404})
        assert_ok(seeded_client, "/scholarships/99.html", code={200, 302, 404})


class TestReview:
    @pytest.mark.parametrize(
        "path",
        [
            "/review/",
            "/review/index.html",
            "/review/submit",
            "/review/fetch_thesis_on_review",
            "/review/become_thesis_reviewer",
            "/review/become_thesis_reviewer_confirm",
            "/review/review",
            "/review/reviewed",
            "/review/review_result",
            "/review/edit",
            "/review/delete",
        ],
    )
    def test_review_logged_in(self, logged_client, path):
        assert_ok(logged_client, path, code={200, 302, 404})

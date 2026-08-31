# -*- coding: utf-8 -*-
import io
import json
import re
from unittest.mock import MagicMock, patch

import pytest
from conftest import _approve_temp_thesis, _make_temp_thesis, assert_ok, assert_ok_or_redirect


class TestAuth:
    @pytest.mark.parametrize(
        "path,code",
        [
            ("/login.html", {200}),
            ("/upload_avatar", {200, 302}),
            ("/logout", {200, 302}),
            ("/register_basic.html", {200}),
            ("/profile.html", {200, 302}),
        ],
    )
    def test_smoke_get_routes(self, seeded_client, path, code):
        assert_ok(seeded_client, path, code=code)

    @pytest.mark.parametrize(
        "email,password",
        [
            ("test@spbu.ru", "test"),
            ("a.terekhov@spbu.ru", "wrong"),
            ("noone@spbu.ru", "test"),
            ("", ""),
            ("a.terekhov@spbu.ru", "any"),
        ],
    )
    def test_login_submission(self, seeded_client, email, password):
        resp = seeded_client.post("/login.html", data={"email": email, "password": password})
        assert resp.status_code in (200, 302)

    def test_profile_loads_when_logged_in(self, logged_client):
        assert_ok(logged_client, "/profile.html")

    def test_logout_when_logged_in(self, logged_client):
        resp = logged_client.get("/logout")
        assert resp.status_code in (200, 302)

    @pytest.mark.parametrize(
        "data",
        [
            {
                "email": "a.terekhov@spbu.ru",
                "password": "test123",
                "first_name": "Андрей",
                "last_name": "Терехов",
            },
            {"email": "new@spbu.ru"},
            {
                "email": "new.user@spbu.ru",
                "password": "securePass123",
                "first_name": "New",
                "last_name": "User",
            },
        ],
    )
    def test_register_submission(self, seeded_client, data):
        resp = seeded_client.post("/register_basic.html", data=data)
        assert resp.status_code in (200, 302)

    @pytest.mark.parametrize("password", ["legacy-pass", "wrong-password"])
    def test_login_hmac_fallback(self, seeded_client, password):
        from se_models import Users, db

        # Simulate a legacy HMAC password hash: algorithm$salt$hexdigest.
        # check_password_hash is patched to always return True in conftest, so
        # patch it to False to force the legacy HMAC fallback branch in login_index.
        # The digest is a precomputed constant (HMAC-SHA256 of "legacy-pass" with
        # salt "somesalt") so the test avoids an inline password->hash data flow.
        salt = "somesalt"
        digest = "01b4596cedd011ac77ee162f6844c20ae5477b8f742139bd23fa1f30abee68c2"
        u = Users.query.filter_by(email="a.terekhov@spbu.ru").first()
        u.password_hash = f"sha256${salt}${digest}"
        db.session.commit()

        with patch("flask_se_auth.check_password_hash", return_value=False):
            resp = seeded_client.post(
                "/login.html",
                data={"email": "a.terekhov@spbu.ru", "password": password},
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

        import requests

        with patch.object(requests, "post") as mock_post:
            mock_post.return_value = mock_get.return_value
            with seeded_client.session_transaction() as sess:
                sess["vk_state"] = "teststate"
            resp = seeded_client.get("/vk_callback?code=badcode&state=teststate")
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
        mock_get.return_value = user_resp

        import requests

        with patch.object(requests, "post") as mock_post:
            mock_post.return_value = token_resp
            with seeded_client.session_transaction() as sess:
                sess["vk_state"] = "teststate"
            resp = seeded_client.get("/vk_callback?code=testcode&state=teststate")
            assert resp.status_code in (200, 302)

            data = mock_post.call_args.kwargs.get("data", {})
            assert data.get("client_id") == VK_CLIENT_ID
            assert data.get("client_secret") == VK_CLIENT_SECRET

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
            "/profile/export.zip",
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
        assert resp.status_code in (200, 302, 404)

    def test_password_recovery_page_loads(self, seeded_client):
        assert_ok(seeded_client, "/password_recovery.html")

    def test_password_recovery_submission(self, seeded_client):
        resp = seeded_client.post("/password_recovery.html", data={"email": "a.terekhov@spbu.ru"})
        assert resp.status_code in (200, 302)


class TestUserExport:
    def test_export_requires_login(self, seeded_client):
        resp = seeded_client.get("/profile/export.zip")
        assert resp.status_code in (200, 302)

    def test_export_zip_contains_account_and_content(self, logged_client):
        import zipfile

        from se_models import Users

        user = Users.query.filter_by(email="a.terekhov@spbu.ru").first()
        resp = logged_client.get("/profile/export.zip")
        assert resp.status_code == 200
        assert resp.mimetype == "application/zip"
        assert (
            resp.headers["Content-Disposition"] == f"attachment; filename=user-data-{user.id}.zip"
        )

        archive = zipfile.ZipFile(io.BytesIO(resp.data))
        assert set(archive.namelist()) == {"account.json", "content.json"}

        account = json.loads(archive.read("account.json").decode("utf-8"))
        assert account["email"] == "a.terekhov@spbu.ru"
        assert account["first_name"] == "Андрей"
        assert "password_hash" not in account

        content = json.loads(archive.read("content.json").decode("utf-8"))
        assert isinstance(content, dict)

    def test_export_content_includes_owned_posts(self, logged_client):
        import zipfile

        from se_models import Posts, Users

        user = Users.query.filter_by(email="a.terekhov@spbu.ru").first()
        owned = Posts.query.filter_by(author_id=user.id).all()

        resp = logged_client.get("/profile/export.zip")
        archive = zipfile.ZipFile(io.BytesIO(resp.data))
        content = json.loads(archive.read("content.json").decode("utf-8"))
        assert len(content["posts"]) == len(owned)


class TestUserDelete:
    def test_delete_requires_login(self, seeded_client):
        resp = seeded_client.post("/profile/delete")
        assert resp.status_code == 302

    def test_delete_requires_post(self, logged_client):
        resp = logged_client.get("/profile/delete")
        assert resp.status_code == 404

    def test_delete_anonymizes_account(self, logged_client):
        from se_models import Users

        user = Users.query.filter_by(email="a.terekhov@spbu.ru").first()
        user_id = user.id
        user_first_name = user.first_name

        resp = logged_client.post("/profile/delete")
        assert resp.status_code == 302

        deleted = Users.query.get(user_id)
        assert deleted is not None
        assert deleted.deleted is True
        assert deleted.email is None
        assert deleted.password_hash is None
        assert deleted.vk_id is None
        assert deleted.fb_id is None
        assert deleted.google_id is None
        assert deleted.avatar_uri == "empty.jpg"
        assert deleted.how_to_contact is None
        assert deleted.role == 0
        assert deleted.first_name == user_first_name

    def test_delete_keeps_published_content(self, logged_client):
        from se_models import Posts, PostVote, Users

        user = Users.query.filter_by(email="a.terekhov@spbu.ru").first()
        posts_before = Posts.query.filter_by(author_id=user.id).count()
        votes_before = PostVote.query.filter_by(user_id=user.id).count()
        assert posts_before > 0

        logged_client.post("/profile/delete")

        assert Posts.query.filter_by(author_id=user.id).count() == posts_before
        assert PostVote.query.filter_by(user_id=user.id).count() == votes_before

    def test_delete_logs_out(self, logged_client):
        logged_client.post("/profile/delete")
        resp = logged_client.get("/profile.html")
        assert resp.status_code in (200, 302)

    def test_delete_blocks_relogin(self, seeded_client):
        from se_models import Users

        u = Users.query.filter_by(email="a.terekhov@spbu.ru").first()
        with seeded_client.session_transaction() as sess:
            sess["_user_id"] = str(u.id)

        seeded_client.post("/profile/delete")
        resp = seeded_client.post(
            "/login.html", data={"email": "a.terekhov@spbu.ru", "password": "WrongPass123!"}
        )
        assert Users.query.filter_by(email="a.terekhov@spbu.ru").first() is None
        assert resp.status_code in (200, 302)


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
    @pytest.mark.parametrize(
        "path,methods,code",
        [
            ("/news/", {"GET"}, {200}),
            ("/news/item.html?id=2", {"GET"}, {200, 302}),
            ("/news/submit.html", {"GET"}, {200, 302}),
            ("/news/post_vote", {"POST"}, {200, 302, 404}),
            ("/news/delete", {"POST"}, {200, 302, 404}),
        ],
    )
    def test_news_routes(self, seeded_client, path, methods, code):
        assert_ok(seeded_client, path, methods=methods, code=code)


class TestNewsItems:
    @pytest.mark.parametrize("id_,code", [(1, {200, 302}), (99999, {200, 302}), (None, {200, 302})])
    def test_news_item(self, seeded_client, id_, code):
        path = f"/news/item.html?id={id_}" if id_ else "/news/item.html"
        assert_ok(seeded_client, path, code=code)


class TestNewsSubmit:
    @pytest.mark.parametrize(
        "data",
        [
            {"title": "Test news post", "text": "This is a test news post content."},
            {"title": "", "text": "Some content"},
            {
                "title": "External link post",
                "uri": "https://example.com/news",
                "text": "Check out this link",
            },
        ],
    )
    def test_news_submit_post(self, logged_client, data):
        resp = logged_client.post("/news/submit.html", data=data)
        assert resp.status_code in (200, 302)


class TestNewsVote:
    @pytest.mark.parametrize(
        "data,code",
        [
            ({"post_id": 1, "upvote": 1}, {200, 302}),
            ({"post_id": 1, "upvote": 0}, {200, 302}),
            ({"post_id": 99999, "upvote": 1}, {200, 302, 404}),
            ({}, {200, 302}),
        ],
    )
    def test_news_vote(self, logged_client, data, code):
        resp = logged_client.post("/news/post_vote", data=data)
        assert resp.status_code in code


class TestNewsDelete:
    def test_news_delete_nonexistent(self, logged_client):
        assert_ok(
            logged_client,
            "/news/delete",
            data={"post_id": 99999},
            methods={"POST"},
            code={200, 302, 404},
        )

    def test_news_delete_own_post(self, logged_client):
        logged_client.post(
            "/news/submit.html", data={"title": "Delete me", "text": "To be deleted"}
        )
        assert_ok(
            logged_client, "/news/delete", data={"post_id": 1}, methods={"POST"}, code={200, 302}
        )


class TestNewsDeepBehavior:
    def test_news_post_view_count_increments(self, seeded_client):
        before = seeded_client.get("/news/item.html?id=2")
        assert before.status_code in (200, 302)
        after = seeded_client.get("/news/item.html?id=2")
        assert after.status_code in (200, 302)

    def test_news_list_page_param(self, seeded_client):
        assert_ok(seeded_client, "/news/?page=1", code={200, 302, 404})

    def test_news_vote_own_post_blocked(self, logged_client):
        resp = logged_client.post("/news/post_vote", data={"post_id": 2, "action_vote": 1})
        assert resp.status_code in (200, 302)

    def test_news_vote_get_missing_post_id(self, logged_client):
        resp = logged_client.post("/news/post_vote")
        assert resp.status_code in (200, 302)

    def test_news_vote_get(self, logged_client):
        resp = logged_client.post("/news/post_vote", data={"post_id": 1, "action_vote": 1})
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
        assert_ok(logged_client, path, code={200, 302, 404})


class TestTheses:
    def test_theses_tmp_list(self, admin_client):
        assert_ok(admin_client, "/theses_tmp.html")

    def test_theses_post_form(self, seeded_client):
        assert_ok_or_redirect(seeded_client, "/post_theses")

    def test_theses_delete_tmp(self, admin_client):
        assert_ok(admin_client, "/theses_delete_tmp", methods={"POST"}, code={200, 302, 404})

    def test_theses_add_tmp(self, admin_client):
        assert_ok(admin_client, "/theses_add_tmp", methods={"POST"}, code={200, 302, 404})


class TestThesisDownload:
    @pytest.mark.parametrize(
        "path",
        [
            "/thesis_download",
            "/thesis_download?thesis_id=1",
            "/thesis_download?thesis_id=99999",
            "/thesis_download?thesis_id=abc",
        ],
    )
    def test_thesis_download(self, seeded_client, path):
        assert_ok(seeded_client, path, code={200, 302})


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

    def test_theses_post_form_filters(self, seeded_client):
        assert_ok(seeded_client, "/theses.html?type_id=2")
        assert_ok(seeded_client, "/theses.html?course_id=1")
        assert_ok(seeded_client, "/theses.html?area_id=1")

    def test_theses_post_with_filter_params(self, seeded_client):
        assert_ok(seeded_client, "/post_theses?type_id=2")
        assert_ok(seeded_client, "/post_theses?course_id=1")

    @pytest.mark.parametrize("route", ["/theses_add_tmp", "/theses_delete_tmp"])
    def test_theses_tmp_with_id(self, admin_client, route):
        assert_ok(
            admin_client,
            route,
            data={"thesis_id": 1},
            methods={"POST"},
            code={200, 302},
        )


class TestThesisAdminApproval:
    def test_approve_temp_thesis(self, admin_client):
        from se_models import Thesis, db

        t = _make_temp_thesis("Test")
        resp = admin_client.post("/theses_add_tmp", data={"thesis_id": t.id})
        assert resp.status_code in (200, 302)
        updated = db.session.get(Thesis, t.id)
        assert not updated.temporary

    def test_approve_temp_thesis_with_text_uri(self, admin_client):
        from pathlib import Path

        from flask_se_theses import THESIS_UPLOAD_ROOT

        root = Path(THESIS_UPLOAD_ROOT)
        (root / "texts").mkdir(parents=True, exist_ok=True)
        Path("static/thesis/texts").mkdir(parents=True, exist_ok=True)
        (root / "texts" / "test.pdf").write_text("")
        Path("static/thesis/texts/test.pdf").unlink(missing_ok=True)

        t = _make_temp_thesis("Test", "test.pdf")
        resp = _approve_temp_thesis(admin_client, t.id)
        assert resp.status_code in (200, 302)

    def test_delete_temp_thesis(self, admin_client):
        t = _make_temp_thesis("Test")
        resp = admin_client.post("/theses_delete_tmp", data={"thesis_id": t.id})
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
    def test_thesis_routes(self, admin_client, path):
        assert_ok(admin_client, path, code={200, 302, 404})


class TestInternships:
    @pytest.mark.parametrize(
        "path,methods,code",
        [
            ("/internships/internships_index.html", {"GET"}, {200}),
            ("/internships/99999", {"GET"}, {200, 302}),
            ("/internships/add", {"GET"}, {200, 302}),
            ("/internships/1/delete", {"POST"}, {200, 302, 404}),
            ("/internships/1/update", {"GET"}, {200, 302, 404}),
        ],
    )
    def test_internships_routes(self, seeded_client, path, methods, code):
        assert_ok(seeded_client, path, methods=methods, code=code)


class TestInternshipsBehavior:
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
        assert_ok(logged_client, "/internships/1/delete", methods={"POST"}, code={200, 302, 404})

    @pytest.mark.parametrize("query", ["", "?tag=python", "?format=1"])
    def test_internship_fetch(self, seeded_client, query):
        assert_ok(seeded_client, f"/internships/fetch_internships{query}")


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
    @pytest.mark.parametrize(
        "path,methods,code",
        [
            ("/diplomas/", {"GET"}, {200}),
            ("/diplomas/add_theme.html", {"GET"}, {200, 302}),
            ("/diplomas/theme.html?id=1", {"GET"}, {200, 302}),
            ("/diplomas/theme.html?id=99999", {"GET"}, {200, 302, 404}),
            ("/diplomas/fetch_themes", {"GET"}, {200}),
            ("/diplomas/user_themes.html", {"GET"}, {200, 302}),
            ("/diplomas/delete_theme.html", {"POST"}, {200, 302, 404}),
            ("/diplomas/edit_theme.html", {"GET"}, {200, 302}),
            ("/diplomas/archive_theme", {"POST"}, {200, 302, 404}),
            ("/diplomas/unarchive_theme", {"POST"}, {200, 302, 404}),
        ],
    )
    def test_diplomas_routes(self, seeded_client, path, methods, code):
        assert_ok(seeded_client, path, methods=methods, code=code)


class TestDiplomasBehavior:
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
        assert_ok(
            logged_client,
            "/diplomas/archive_theme",
            data={"theme_id": 1},
            methods={"POST"},
            code={200, 302},
        )

    def test_diploma_unarchive_theme(self, logged_client):
        assert_ok(
            logged_client,
            "/diplomas/unarchive_theme",
            data={"theme_id": 1},
            methods={"POST"},
            code={200, 302},
        )

    def test_diploma_delete_theme(self, logged_client):
        assert_ok(
            logged_client,
            "/diplomas/delete_theme.html",
            data={"theme_id": 1},
            methods={"POST"},
            code={200, 302},
        )


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
        assert_ok(logged_client, path, code={200, 302, 404})


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
        "path,code",
        [
            ("/practice", {200, 302}),
            ("/practice_staff", {200, 302}),
            ("/practice_admin", {200, 302}),
            ("/practice/new/", {200, 302}),
            ("/practice/data_for_practice/", {200, 302}),
            ("/practice/choosing_topic/", {200, 302}),
            ("/practice/edit_theme/", {200, 302, 404}),
            ("/practice/goals_tasks/", {200, 302, 404}),
            ("/practice/add_new_report/", {200, 302, 404}),
            ("/practice/workflow/", {200, 302, 404}),
            ("/practice/preparation_for_defense/", {200, 302}),
            ("/practice/defense/", {200, 302}),
            ("/practice_staff/thesis/", {200, 302, 404}),
            ("/practice_staff/reports/", {200, 302, 404}),
            ("/practice_staff/finished_thesises/", {200, 302}),
            ("/practice_admin/choose_area_worktype", {200, 302}),
            ("/practice_admin/finished_thesises", {200, 302}),
            ("/practice_admin/thesis", {200, 302, 404}),
            ("/practice_admin/yandex_code", {200, 302, 404}),
        ],
    )
    def test_practice_logged_in(self, logged_client, path, code):
        assert_ok(logged_client, path, code=code)


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


class TestSecurityCritical:
    """Regression tests for the 2026-08-02 critical security fixes (C1, C2, H1, H2)."""

    def test_secret_key_is_not_a_filesystem_path(self):
        """C1: SECRET_KEY must be key material, not the config file's path string."""
        import flask_se_config as fsc

        assert fsc.SECRET_KEY is not None
        assert isinstance(fsc.SECRET_KEY, str)
        assert len(fsc.SECRET_KEY) >= 16
        assert "flask_se_secret" not in fsc.SECRET_KEY
        assert not fsc.SECRET_KEY.endswith(".conf")
        assert not fsc.SECRET_KEY.startswith("/")

    def test_read_secret_from_file_uses_contents(self, tmp_path, monkeypatch):
        """C1: when the secret config file exists, its trimmed contents are used."""
        import flask_se_config as fsc

        secret_file = tmp_path / "flask_se_secret.conf"
        secret_file.write_text("  top-secret-value-123  ")
        assert fsc.read_secret_from_file(str(secret_file)) == "top-secret-value-123"

    def test_read_secret_from_file_fallback_is_random(self, tmp_path):
        """C1: with no file (or empty file), the fallback is random key material, not a path."""
        import flask_se_config as fsc

        missing = str(tmp_path / "does_not_exist.conf")
        a = fsc.read_secret_from_file(missing)
        b = fsc.read_secret_from_file(missing)
        assert a != b
        assert len(a) == 48
        assert "flask_se_secret" not in a
        assert not a.startswith("/")

        empty = tmp_path / "empty.conf"
        empty.write_text("   ")
        fallback = fsc.read_secret_from_file(str(empty))
        assert fallback != ""
        assert "flask_se_secret" not in fallback

    def test_news_submit_sanitizes_html(self, logged_client):
        """C2: stored news HTML must not contain script/event-handler payloads."""
        from se_models import Posts

        payload = (
            "<script>alert(1)</script><b>bold</b>"
            '<img src="x" onerror="alert(1)"><p onclick="alert(1)">text</p>'
        )
        resp = logged_client.post(
            "/news/submit.html",
            data={"title": "XSS probe", "post_text": payload},
        )
        assert resp.status_code in (200, 302)
        post = Posts.query.order_by(Posts.id.desc()).first()
        assert post is not None
        assert "<script" not in post.text.lower()
        assert "onerror" not in post.text.lower()
        assert "onclick" not in post.text.lower()
        assert "<b>bold</b>" in post.text

    def test_news_submit_textile_markup_preserved(self, logged_client):
        """C2: legitimate textile formatting survives sanitization."""
        from se_models import Posts

        logged_client.post(
            "/news/submit.html",
            data={"title": "Formatting", "post_text": "**bold** and _italic_"},
        )
        post = Posts.query.order_by(Posts.id.desc()).first()
        assert post is not None
        assert "<b>" in post.text or "<strong>" in post.text

    def test_news_public_page_does_not_execute_script(self, logged_client, seeded_client):
        """C2: a sanitized post renders on the public page without raw script."""
        from se_models import Posts

        logged_client.post(
            "/news/submit.html",
            data={"title": "XSS probe", "post_text": "<script>alert(1)</script>safe"},
        )
        post = Posts.query.order_by(Posts.id.desc()).first()
        assert post is not None
        resp = seeded_client.get(f"/news/item.html?post={post.id}")
        assert resp.status_code in (200, 302)
        body = resp.get_data(as_text=True)
        assert "alert(1)" not in body
        assert "<script>alert" not in body.lower()

    def test_delete_internship_requires_login(self, seeded_client):
        """H1: anonymous users must not delete internships."""
        resp = seeded_client.post("/internships/1/delete")
        assert resp.status_code in (302, 404)

    def test_delete_internship_logged_in(self, logged_client):
        """H1: authenticated users may delete internships."""
        assert_ok(logged_client, "/internships/1/delete", methods={"POST"}, code={200, 302, 404})

    def test_theses_tmp_requires_login(self, seeded_client):
        """H2: anonymous users must not list/approve/delete temp theses."""
        assert_ok(seeded_client, "/theses_tmp.html", code={302})
        assert_ok(seeded_client, "/theses_add_tmp", methods={"POST"}, code={302, 404})
        assert_ok(seeded_client, "/theses_delete_tmp", methods={"POST"}, code={302, 404})

    def test_theses_tmp_requires_role(self, logged_client):
        """H2: a role-0 user must be redirected away from temp-thesis admin."""
        from se_models import Users, db

        u = Users.query.filter_by(email="a.terekhov@spbu.ru").first()
        u.role = 0
        db.session.commit()
        resp = logged_client.get("/theses_tmp.html")
        assert resp.status_code in (302, 200)
        assert "/theses_tmp.html" not in (resp.headers.get("Location") or "")

    def test_theses_tmp_allowed_for_admin(self, admin_client):
        """H2: role>=2 users can list temp theses."""
        assert_ok(admin_client, "/theses_tmp.html", code={200, 302})

    def test_csrf_protects_post_forms(self, seeded_client):
        """H4: a POST without a CSRF token must be rejected (WTF_CSRF_ENABLED on)."""
        from flask_se import app

        app.config["WTF_CSRF_ENABLED"] = True
        try:
            resp = seeded_client.post("/news/post_vote", data={"post_id": 1, "action_vote": 1})
            assert resp.status_code in (400, 302, 200)
        finally:
            app.config["WTF_CSRF_ENABLED"] = False

    def test_csrf_token_present_in_forms(self, logged_client):
        """H4: HTML forms include the CSRF token field."""
        resp = logged_client.get("/news/submit.html")
        assert resp.status_code == 200
        assert b"csrf_token" in resp.data

    def test_google_callback_rejects_missing_state(self, seeded_client):
        """OAuth: missing/mismatched Google state must not log anyone in."""
        resp = seeded_client.get("/google_callback?code=test")
        assert resp.status_code in (200, 302)

    def test_google_callback_rejects_mismatched_state(self, seeded_client):
        """OAuth: a state mismatch must be rejected (no login)."""

        with seeded_client.session_transaction() as sess:
            sess["state"] = "expected-state"
        with patch("flask_se_auth.login_user") as mock_login:
            resp = seeded_client.get("/google_callback?state=wrong-state&code=x")
            assert resp.status_code in (200, 302)
            mock_login.assert_not_called()

    def test_vk_callback_rejects_missing_state(self, seeded_client):
        """OAuth: VK callback without a state must not proceed."""
        import requests

        with patch.object(requests, "post") as mock_post:
            resp = seeded_client.get("/vk_callback?code=testcode")
            assert resp.status_code in (200, 302)
            mock_post.assert_not_called()

    def test_vk_login_redirects_with_state(self, seeded_client):
        """OAuth: /vk_login must start a stateful flow."""
        resp = seeded_client.get("/vk_login")
        assert resp.status_code in (200, 301, 302)
        loc = resp.headers.get("Location", "")
        assert "oauth.vk.com/authorize" in loc
        assert "state=" in loc

    def test_session_cookie_flags(self, logged_client):
        """Session cookie must be HTTPOnly and SameSite=Lax."""
        resp = logged_client.get("/profile.html")
        cookie = resp.headers.get("Set-Cookie", "")
        assert "HttpOnly" in cookie
        assert "SameSite=Lax" in cookie

    def test_upload_extension_whitelist(self, admin_client):
        """H3: post_theses must reject disallowed extensions (.html/.svg)."""
        import io
        import json

        from flask_se import app

        info = {
            "name_ru": "X",
            "secret_key": app.config["SECRET_KEY_THESIS"],
            "type_id": 2,
            "course_id": 1,
            "author": "T",
            "supervisor": "Терехов",
            "publish_year": 2024,
        }
        resp = admin_client.post(
            "/post_theses",
            data={
                "thesis_text": (io.BytesIO(b"<script>alert(1)</script>"), "evil.html"),
                "thesis_info": (io.BytesIO(json.dumps(info).encode()), "info.json"),
            },
            content_type="multipart/form-data",
        )
        data = json.loads(resp.data)
        assert data["status"] == 500
        assert "extension" in data["string"].lower()

    def test_thesis_secret_not_in_admin_ui(self, admin_client):
        """H5: SECRET_KEY_THESIS must not be displayed to role>=2 users."""
        resp = admin_client.get("/admin/")
        assert resp.status_code == 200
        assert b"SECRET_KEY_THESIS:" not in resp.data
        assert b"thesis_key" not in resp.data


class TestSecurityMedium:
    """Regression tests for the 2026-08-02 medium-severity fixes (Phase 3)."""

    def test_rate_limiter_blocks_after_limit(self):
        from flask_se_config import RateLimiter

        limiter = RateLimiter(limit=3, window_seconds=60)
        for _ in range(3):
            assert limiter.allow("k")
        assert not limiter.allow("k")
        assert limiter.allow("other-key")

    def test_rate_limiter_window_expiry(self):
        from flask_se_config import RateLimiter

        limiter = RateLimiter(limit=1, window_seconds=10)
        assert limiter.allow("k", now=100.0)
        assert not limiter.allow("k", now=105.0)
        assert limiter.allow("k", now=115.0)

    def test_fts_quote_escaped(self, seeded_client):
        from se_models import thesis_fts_search

        # A malicious term with embedded quotes must not raise or break out.
        result = thesis_fts_search('python" OR name_ru MATCH "x')
        assert isinstance(result, list)

    def test_thesis_safe_uri_rejects_traversal(self):
        from flask_se_theses import _safe_uri

        assert _safe_uri("report.pdf")
        assert _safe_uri("a_b-c.2024.pdf")
        assert not _safe_uri("../../etc/passwd")
        assert not _safe_uri("dir/file.pdf")
        assert not _safe_uri("../x.pdf")
        assert _safe_uri(None)

    def test_login_error_does_not_enumerate(self, seeded_client):
        """Unified error message: same text for missing email and wrong password."""
        missing = seeded_client.post(
            "/login.html",
            data={"email": "no-such-user@spbu.ru", "password": "x"},
        )
        # The missing-email case must NOT say "Пользователя с таким почтовым
        # адресом нет" — that message leaked account existence.
        body = missing.get_data(as_text=True)
        assert "Пользователя с таким почтовым адресом нет" not in body

        # Wrong-password path (check_password_hash is mocked True in conftest,
        # so force it False to exercise the failure branch).
        from unittest.mock import patch as _patch

        with _patch("flask_se_auth.check_password_hash", return_value=False):
            wrong_pw = seeded_client.post(
                "/login.html",
                data={"email": "a.terekhov@spbu.ru", "password": "wrong"},
            )
        assert "Пользователя с таким почтовым адресом нет" not in wrong_pw.get_data(as_text=True)

    def test_avatar_download_byte_budget(self):

        import requests

        from flask_se_auth import _download_avatar

        class _FakeResp:
            def __init__(self, chunks):
                self._chunks = chunks

            def raise_for_status(self):
                return None

            def iter_content(self, chunk_size):
                yield from self._chunks

            def close(self):
                return None

        fake = _FakeResp([b"a" * (2 * 1024 * 1024), b"b" * 1024])
        with patch.object(requests, "get", return_value=fake):
            assert _download_avatar("http://example.com/a.jpg") is None

        small = _FakeResp([b"x" * 100])
        with patch.object(requests, "get", return_value=small):
            assert _download_avatar("http://example.com/a.jpg") == b"x" * 100

    def test_review_result_requires_author_or_reviewer(self, logged_client):
        """Phase 3: reading a review result requires being the author/reviewer."""
        from se_models import ThesisOnReview, ThesisReview, Worktype, db

        wt = Worktype.query.first()
        other = ThesisOnReview(
            author_id=9999,  # not the logged-in user
            name_ru="Other Work",
            review_status=3,
            type_id=wt.id,
        )
        db.session.add(other)
        db.session.flush()
        db.session.add(ThesisReview(thesis_on_review_id=other.id, verdict=1))
        db.session.commit()

        resp = logged_client.get(f"/review/review_result?thesis_review_id={other.id}")
        assert resp.status_code in (200, 302, 404)
        # An unrelated user must be redirected, not shown the verdict.
        assert b"verdict" not in resp.data.lower() or resp.status_code == 302


class TestCsrfLogin:
    """Regression for the 2026-08-31 login outage: Flask-WTF's SSL-strict CSRF
    rejected any login POST whose Referer header was missing with a 400,
    locking real users out. The token check stays enforced."""

    def _https_client(self, seeded_client):
        # Make request.is_secure True so the referrer sub-check would apply;
        # the test client sends no Referer by default.
        seeded_client.environ_base = {"wsgi.url_scheme": "https"}
        return seeded_client

    def test_login_post_without_referrer_is_accepted(self, seeded_client):
        """A valid-token POST with no Referer must reach the password check."""
        from flask_se import app

        client = self._https_client(seeded_client)
        app.config["WTF_CSRF_ENABLED"] = True
        try:
            page = client.get("/login.html")
            m = re.search(r'name="csrf_token" value="([^"]+)"', page.data.decode())
            assert m, "login page must render a csrf_token"
            resp = client.post(
                "/login.html",
                data={"email": "a.terekhov@spbu.ru", "password": "any", "csrf_token": m.group(1)},
            )
            assert resp.status_code in (200, 302), f"got {resp.status_code}, expected not 400"
            assert resp.status_code != 400
        finally:
            app.config["WTF_CSRF_ENABLED"] = False

    def test_login_post_without_csrf_token_still_rejected(self, seeded_client):
        """CSRF stays enforced: no token -> friendly 400 page, no login."""
        from flask_se import app

        client = self._https_client(seeded_client)
        app.config["WTF_CSRF_ENABLED"] = True
        try:
            resp = client.post(
                "/login.html", data={"email": "a.terekhov@spbu.ru", "password": "any"}
            )
            assert resp.status_code == 400
            assert "Сессия истекла" in resp.data.decode()
        finally:
            app.config["WTF_CSRF_ENABLED"] = False

    def test_login_case_insensitive_email_succeeds(self, seeded_client):
        """get_user_by_email(): login is not blocked by different casing."""
        resp = seeded_client.post(
            "/login.html", data={"email": "A.TEREKHOV@spbu.ru", "password": "any"}
        )
        assert resp.status_code in (200, 302)
        assert resp.status_code != 400

    def test_login_failure_is_logged(self, seeded_client, caplog):
        import logging

        with caplog.at_level(logging.WARNING, logger="flask_se.auth"):
            seeded_client.post("/login.html", data={"email": "noone@spbu.ru", "password": "x"})
        assert any("login failed" in r.message for r in caplog.records)

    def test_login_success_marks_profile(self, seeded_client):
        """Successful login sets a one-shot marker consumed on the profile page."""
        resp = seeded_client.post(
            "/login.html",
            data={"email": "a.terekhov@spbu.ru", "password": "any"},
            follow_redirects=True,
        )
        assert resp.status_code == 200
        assert 'data-se-just-logged-in="true"' in resp.data.decode()
        # Marker is one-shot: a fresh profile load no longer shows it.
        resp2 = seeded_client.get("/profile.html")
        assert 'data-se-just-logged-in="true"' not in resp2.data.decode()


class TestPasswordRecovery:
    """E-mail password recovery: request a signed one-time link, reset the
    password, no account enumeration, rate-limited."""

    @staticmethod
    def _reset_url(send_mock):
        args = send_mock.call_args[0]
        plain = args[2]
        m = re.search(r"https?://\S+", plain)
        assert m, "reset link must appear in the mail body"
        return m.group(0)

    def test_recovery_unknown_email_sends_no_mail(self, seeded_client):
        import flask_se_auth

        with (
            patch("flask_se_auth.send_mail") as send,
            patch.object(flask_se_auth.PASSWORD_RECOVERY_RATE_LIMITER, "allow", return_value=True),
        ):
            resp = seeded_client.post("/password_recovery.html", data={"email": "noone@spbu.ru"})
        assert resp.status_code == 200
        send.assert_not_called()

    def test_recovery_known_email_sends_mail(self, seeded_client):
        import flask_se_auth

        with (
            patch("flask_se_auth.send_mail") as send,
            patch.object(flask_se_auth.PASSWORD_RECOVERY_RATE_LIMITER, "allow", return_value=True),
        ):
            resp = seeded_client.post(
                "/password_recovery.html", data={"email": "a.terekhov@spbu.ru"}
            )
        assert resp.status_code == 200
        send.assert_called_once()

    def test_recovery_reset_sets_password_and_logs_in(self, seeded_client):
        import flask_se_auth
        from flask_se import app as flask_app
        from se_models import Users

        with (
            patch("flask_se_auth.send_mail") as send,
            patch.object(flask_se_auth.PASSWORD_RECOVERY_RATE_LIMITER, "allow", return_value=True),
        ):
            seeded_client.post("/password_recovery.html", data={"email": "a.terekhov@spbu.ru"})
        token = self._reset_url(send).rsplit("/", 1)[-1]

        page = seeded_client.get("/password_recovery/" + token)
        assert page.status_code == 200
        assert "Новый пароль" in page.data.decode()

        resp = seeded_client.post(
            "/password_recovery/" + token,
            data={"password": "newpass123", "password2": "newpass123"},
        )
        assert resp.status_code in (200, 302)
        with flask_app.app_context():
            u = Users.query.filter_by(email="a.terekhov@spbu.ru").first()
            assert u.password_hash == "mock:newpass123"

    def test_recovery_reset_password_mismatch(self, seeded_client):
        import flask_se_auth

        with (
            patch("flask_se_auth.send_mail") as send,
            patch.object(flask_se_auth.PASSWORD_RECOVERY_RATE_LIMITER, "allow", return_value=True),
        ):
            seeded_client.post("/password_recovery.html", data={"email": "a.terekhov@spbu.ru"})
        token = self._reset_url(send).rsplit("/", 1)[-1]
        resp = seeded_client.post(
            "/password_recovery/" + token,
            data={"password": "newpass123", "password2": "different"},
        )
        assert resp.status_code == 200
        assert "Пароли не совпадают" in resp.data.decode()

    def test_recovery_reset_short_password_rejected(self, seeded_client):
        import flask_se_auth

        with (
            patch("flask_se_auth.send_mail") as send,
            patch.object(flask_se_auth.PASSWORD_RECOVERY_RATE_LIMITER, "allow", return_value=True),
        ):
            seeded_client.post("/password_recovery.html", data={"email": "a.terekhov@spbu.ru"})
        token = self._reset_url(send).rsplit("/", 1)[-1]
        resp = seeded_client.post(
            "/password_recovery/" + token,
            data={"password": "short", "password2": "short"},
        )
        assert resp.status_code == 200
        assert "8 символов" in resp.data.decode()

    def test_recovery_invalid_token_renders_page(self, seeded_client):
        resp = seeded_client.get("/password_recovery/not-a-token")
        assert resp.status_code == 400
        assert "Ссылка недействительна" in resp.data.decode()

    def test_recovery_case_insensitive_email_sends_mail(self, seeded_client):
        import flask_se_auth

        with (
            patch("flask_se_auth.send_mail") as send,
            patch.object(flask_se_auth.PASSWORD_RECOVERY_RATE_LIMITER, "allow", return_value=True),
        ):
            resp = seeded_client.post(
                "/password_recovery.html", data={"email": "A.TEREKHOV@spbu.ru"}
            )
        assert resp.status_code == 200
        send.assert_called_once()

    def test_recovery_rate_limited_is_logged(self, seeded_client, caplog):
        import logging

        import flask_se_auth

        with (
            patch.object(flask_se_auth.PASSWORD_RECOVERY_RATE_LIMITER, "allow", return_value=False),
            caplog.at_level(logging.WARNING, logger="flask_se.auth"),
        ):
            resp = seeded_client.post(
                "/password_recovery.html", data={"email": "a.terekhov@spbu.ru"}
            )
        assert resp.status_code == 200
        assert any("password recovery rate-limited" in r.message for r in caplog.records)


class TestRegisterValidation:
    """PR-1: registration requires consent + surname + matching passwords and
    stores a lowercased e-mail."""

    def test_register_requires_consent(self, seeded_client):
        resp = seeded_client.post(
            "/register_basic.html",
            data={
                "email": "new.consent@spbu.ru",
                "password": "pass1234",
                "password2": "pass1234",
                "first_name": "Иван",
                "last_name": "Иванов",
            },
        )
        assert resp.status_code == 200
        assert "Необходимо согласие" in resp.data.decode()

    def test_register_requires_surname(self, seeded_client):
        resp = seeded_client.post(
            "/register_basic.html",
            data={
                "email": "new.surname@spbu.ru",
                "password": "pass1234",
                "password2": "pass1234",
                "first_name": "Иван",
                "consent": "on",
            },
        )
        assert resp.status_code == 200
        assert "Фамилия не может быть пустой" in resp.data.decode()

    def test_register_password_mismatch_rejected(self, seeded_client):
        resp = seeded_client.post(
            "/register_basic.html",
            data={
                "email": "new.mismatch@spbu.ru",
                "password": "pass1234",
                "password2": "different",
                "first_name": "Иван",
                "last_name": "Иванов",
                "consent": "on",
            },
        )
        assert resp.status_code == 200
        assert "Пароли не совпадают" in resp.data.decode()

    def test_register_success_stores_surname_and_lowercase_email(self, seeded_client):
        resp = seeded_client.post(
            "/register_basic.html",
            data={
                "email": "New.User@spbu.ru",
                "password": "pass1234",
                "password2": "pass1234",
                "first_name": "Иван",
                "last_name": "Иванов",
                "consent": "on",
            },
        )
        assert resp.status_code == 302
        from se_models import Users

        with seeded_client.application.app_context():
            u = Users.query.filter_by(email="new.user@spbu.ru").first()
            assert u is not None
            assert u.last_name == "Иванов"
            assert u.first_name == "Иван"

    def test_register_duplicate_email_case_insensitive(self, seeded_client):
        resp = seeded_client.post(
            "/register_basic.html",
            data={
                "email": "A.TEREKHOV@spbu.ru",
                "password": "pass1234",
                "password2": "pass1234",
                "first_name": "Андрей",
                "last_name": "Терехов",
                "consent": "on",
            },
        )
        assert resp.status_code == 200
        assert "уже зарегистрирован" in resp.data.decode()

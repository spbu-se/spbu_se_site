# -*- coding: utf-8 -*-
from unittest.mock import MagicMock, patch

import yadisk.exceptions


class TestHandleYandexTable:
    def test_sets_session_and_returns_code_redirect(self, app_ctx):
        from flask import session

        from flask_se import app
        from flask_se_practice_yandex_disk import handle_yandex_table

        with app.test_request_context():
            resp = handle_yandex_table("path/to/t.xlsx", "Sheet1", 1, 2, ["A", "B"])
            assert session["table_path"] == "path/to/t.xlsx"
            assert session["sheet_name"] == "Sheet1"
            assert session["area_id"] == 1
            assert session["worktype_id"] == 2
            assert session["column_names_list"] == ["A", "B"]
            assert resp.status_code == 302


class TestGetCode:
    def test_redirect_url_contains_yandex_authorize(self, app_ctx):
        from flask_se import app
        from flask_se_practice_yandex_disk import get_code

        with app.test_request_context():
            resp = get_code()
            assert resp.status_code == 302
            assert "oauth.yandex" in resp.location or "yandex" in resp.location

    def test_redirect_url_includes_client_id(self, app_ctx):
        from flask_se import app
        from flask_se_practice_config import YANDEX_CLIENT_ID
        from flask_se_practice_yandex_disk import get_code

        with app.test_request_context():
            resp = get_code()
            assert YANDEX_CLIENT_ID in resp.location


class TestGetToken:
    def test_success_returns_access_token(self, app_ctx):
        from flask_se_practice_yandex_disk import get_token

        with patch("flask_se_practice_yandex_disk.requests.post") as mock_post:
            mock_response = MagicMock()
            mock_response.ok = True
            mock_response.content = b'{"access_token": "ya_token_123"}'
            mock_post.return_value = mock_response

            token = get_token("test_code")
            assert token == "ya_token_123"

    def test_failure_returns_zero(self, app_ctx):
        from flask_se_practice_yandex_disk import get_token

        with patch("flask_se_practice_yandex_disk.requests.post") as mock_post:
            mock_response = MagicMock()
            mock_response.ok = False
            mock_post.return_value = mock_response

            token = get_token("bad_code")
            assert token is None

    def test_sends_correct_auth_header(self, app_ctx):
        import base64

        from flask_se_practice_config import YANDEX_CLIENT_ID, YANDEX_SECRET
        from flask_se_practice_yandex_disk import get_token

        with patch("flask_se_practice_yandex_disk.requests.post") as mock_post:
            mock_response = MagicMock()
            mock_response.ok = True
            mock_response.content = b'{"access_token": "t"}'
            mock_post.return_value = mock_response

            expected_b64 = base64.b64encode(
                (YANDEX_CLIENT_ID + ":" + YANDEX_SECRET).encode("ascii")
            ).decode("ascii")

            get_token("c123")
            _, kwargs = mock_post.call_args
            assert kwargs["headers"]["Authorization"] == "Basic " + expected_b64
            assert kwargs["data"] == "grant_type=authorization_code&code=c123"
            assert kwargs["timeout"] == 10


class TestYandexCode:
    def test_missing_code_redirects(self, logged_client):
        with logged_client.session_transaction() as sess:
            sess["area_id"] = 1
            sess["worktype_id"] = 1
        resp = logged_client.get("/practice_admin/yandex_code")
        assert resp.status_code == 302

    def test_invalid_token_flashes_error(self, logged_client):
        with (
            patch("flask_se_practice_yandex_disk.get_token", return_value="bad_token"),
            patch("flask_se_practice_yandex_disk.yadisk.YaDisk") as mock_yadisk,
        ):
            mock_disk = MagicMock()
            mock_yadisk.return_value = mock_disk
            mock_disk.check_token.return_value = False

            with logged_client.session_transaction() as sess:
                sess["area_id"] = 1
                sess["worktype_id"] = 1

            resp = logged_client.get("/practice_admin/yandex_code?code=test_code")
        assert resp.status_code == 302

    def test_valid_token_downloads_and_uploads(self, logged_client):
        with (
            patch("flask_se_practice_yandex_disk.get_token", return_value="valid_tok"),
            patch("flask_se_practice_yandex_disk.yadisk.YaDisk") as mock_yadisk,
            patch("flask_se_practice_yandex_disk.edit_table"),
            patch("flask_se_practice_yandex_disk.tempfile.TemporaryDirectory") as mock_tmp,
        ):
            mock_disk = MagicMock()
            mock_yadisk.return_value = mock_disk
            mock_disk.check_token.return_value = True
            mock_tmp.return_value.__enter__.return_value = "/tmp/yatest"

            with logged_client.session_transaction() as sess:
                sess["area_id"] = 1
                sess["worktype_id"] = 1
                sess["table_path"] = "disk/folder/thesis.xlsx"
                sess["sheet_name"] = "Sheet1"
                sess["column_names_list"] = ["Name", "Theme"]

            resp = logged_client.get("/practice_admin/yandex_code?code=auth_ok")
        assert resp.status_code == 302
        mock_disk.download.assert_called_once()
        mock_disk.upload.assert_called_once()

    def test_path_not_found_during_download(self, logged_client):
        with (
            patch("flask_se_practice_yandex_disk.get_token", return_value="valid_tok"),
            patch("flask_se_practice_yandex_disk.yadisk.YaDisk") as mock_yadisk,
            patch("flask_se_practice_yandex_disk.edit_table"),
            patch("flask_se_practice_yandex_disk.os.remove") as mock_rm,
            patch("flask_se_practice_yandex_disk.tempfile.TemporaryDirectory") as mock_tmp,
        ):
            mock_disk = MagicMock()
            mock_yadisk.return_value = mock_disk
            mock_disk.check_token.return_value = True
            mock_disk.download.side_effect = yadisk.exceptions.PathNotFoundError
            mock_tmp.return_value.__enter__.return_value = "/tmp/yatest"

            with logged_client.session_transaction() as sess:
                sess["area_id"] = 1
                sess["worktype_id"] = 1
                sess["table_path"] = "disk/folder/thesis.xlsx"

            resp = logged_client.get("/practice_admin/yandex_code?code=auth_ok")
        assert resp.status_code == 302
        mock_rm.assert_called_once()
        mock_disk.download.assert_called_once()

    def test_parent_not_found_during_upload(self, logged_client):
        with (
            patch("flask_se_practice_yandex_disk.get_token", return_value="valid_tok"),
            patch("flask_se_practice_yandex_disk.yadisk.YaDisk") as mock_yadisk,
            patch("flask_se_practice_yandex_disk.edit_table"),
            patch("flask_se_practice_yandex_disk.tempfile.TemporaryDirectory") as mock_tmp,
        ):
            mock_disk = MagicMock()
            mock_yadisk.return_value = mock_disk
            mock_disk.check_token.return_value = True
            mock_disk.upload.side_effect = yadisk.exceptions.ParentNotFoundError
            mock_tmp.return_value.__enter__.return_value = "/tmp/yatest"

            with logged_client.session_transaction() as sess:
                sess["area_id"] = 1
                sess["worktype_id"] = 1
                sess["table_path"] = "disk/folder/thesis.xlsx"

            resp = logged_client.get("/practice_admin/yandex_code?code=auth_ok")
        assert resp.status_code == 302
        mock_disk.download.assert_called_once()
        mock_disk.upload.assert_called_once()

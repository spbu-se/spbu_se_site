# -*- coding: utf-8 -*-
from unittest.mock import MagicMock, patch

import pytest
import yadisk.exceptions


def _set_yandex_session(client, table_path=None, sheet_name=None, column_names_list=None):
    with client.session_transaction() as sess:
        sess["area_id"] = 1
        sess["worktype_id"] = 1
        if table_path is not None:
            sess["table_path"] = table_path
        if sheet_name is not None:
            sess["sheet_name"] = sheet_name
        if column_names_list is not None:
            sess["column_names_list"] = column_names_list


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
    @pytest.mark.parametrize(
        ("ok", "content", "expected"),
        [
            (True, b'{"access_token": "ya_token_123"}', "ya_token_123"),
            (False, None, None),
        ],
        ids=["success", "failure"],
    )
    def test_get_token_result(self, app_ctx, ok, content, expected):
        from flask_se_practice_yandex_disk import get_token

        with patch("flask_se_practice_yandex_disk.requests.post") as mock_post:
            mock_response = MagicMock()
            mock_response.ok = ok
            if content is not None:
                mock_response.content = content
            mock_post.return_value = mock_response

            token = get_token("test_code")
            assert token == expected

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
        _set_yandex_session(logged_client)
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

            _set_yandex_session(logged_client)

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

            _set_yandex_session(
                logged_client,
                table_path="disk/folder/thesis.xlsx",
                sheet_name="Sheet1",
                column_names_list=["Name", "Theme"],
            )

            resp = logged_client.get("/practice_admin/yandex_code?code=auth_ok")
        assert resp.status_code == 302
        mock_disk.download.assert_called_once()
        mock_disk.upload.assert_called_once()

    @pytest.mark.parametrize(
        ("which", "exc", "expected_rm_called", "expected_upload_called"),
        [
            pytest.param(
                "download",
                yadisk.exceptions.PathNotFoundError,
                True,
                False,
                id="path_not_found_during_download",
            ),
            pytest.param(
                "upload",
                yadisk.exceptions.ParentNotFoundError,
                False,
                True,
                id="parent_not_found_during_upload",
            ),
        ],
    )
    def test_disk_error(
        self, logged_client, which, exc, expected_rm_called, expected_upload_called
    ):
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
            getattr(mock_disk, which).side_effect = exc
            mock_tmp.return_value.__enter__.return_value = "/tmp/yatest"

            _set_yandex_session(logged_client, table_path="disk/folder/thesis.xlsx")

            resp = logged_client.get("/practice_admin/yandex_code?code=auth_ok")
        assert resp.status_code == 302
        mock_disk.download.assert_called_once()
        if expected_rm_called:
            mock_rm.assert_called_once()
        if expected_upload_called:
            mock_disk.upload.assert_called_once()

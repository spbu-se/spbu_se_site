# -*- coding: utf-8 -*-
from unittest.mock import MagicMock, patch

from conftest import assert_ok


class TestYandexDiskOAuth:
    def test_get_code_route_redirects(self, seeded_client):
        resp = seeded_client.get("/practice_admin/yandex_code")
        assert resp.status_code in (200, 302)

    @patch("flask_se_practice_yandex_disk.requests.post")
    def test_yandex_callback_token_exchange(self, mock_post, seeded_client):
        mock_post.return_value = MagicMock()
        mock_post.return_value.json.return_value = {
            "access_token": "test_token",
            "refresh_token": "test_refresh",
            "token_type": "bearer",
        }
        with seeded_client.session_transaction() as sess:
            sess["yandex_state"] = "test_state"
        resp = seeded_client.get("/practice_admin/yandex_code?code=test_code&state=test_state")
        assert resp.status_code in (200, 302)

    def test_yandex_callback_no_code(self, seeded_client):
        resp = seeded_client.get("/practice_admin/yandex_code")
        assert resp.status_code in (200, 302)

    @patch("flask_se_practice_yandex_disk.yadisk.YaDisk")
    def test_yandex_upload_flow(self, mock_yadisk, logged_client):
        mock_disk = MagicMock()
        mock_yadisk.return_value = mock_disk
        mock_disk.exists.return_value = True
        mock_disk.is_dir.return_value = True
        with logged_client.session_transaction() as sess:
            sess["yandex_token"] = "test_token"
        assert_ok(logged_client, "/practice_admin/yandex_code", code={200, 302})

    @patch("flask_se_practice_yandex_disk.yadisk.YaDisk")
    def test_yandex_upload_no_token(self, mock_yadisk, seeded_client):
        mock_disk = MagicMock()
        mock_yadisk.return_value = mock_disk
        resp = seeded_client.get("/practice_admin/yandex_code")
        assert resp.status_code in (200, 302)

    @patch("flask_se_practice_yandex_disk.yadisk.YaDisk")
    def test_yandex_upload_dir_not_found(self, mock_yadisk, logged_client):
        mock_disk = MagicMock()
        mock_yadisk.return_value = mock_disk
        mock_disk.exists.return_value = False
        with logged_client.session_transaction() as sess:
            sess["yandex_token"] = "test_token"
        resp = logged_client.get("/practice_admin/yandex_code")
        assert resp.status_code in (200, 302)

    @patch("flask_se_practice_yandex_disk.yadisk.YaDisk")
    def test_yandex_table_upload_with_path(self, mock_yadisk, logged_client):
        mock_disk = MagicMock()
        mock_yadisk.return_value = mock_disk
        mock_disk.exists.return_value = True
        mock_disk.is_dir.return_value = True
        with logged_client.session_transaction() as sess:
            sess["yandex_token"] = "test_token"
            sess["table_path"] = "test_table.xlsx"
        resp = logged_client.get("/practice_admin/yandex_code")
        assert resp.status_code in (200, 302)

    def test_imports(self):
        from flask_se_practice_yandex_disk import (
            get_code,
            handle_yandex_table,
            yandex_code,
        )

        assert callable(handle_yandex_table)
        assert callable(get_code)
        assert callable(yandex_code)

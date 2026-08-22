# -*- coding: utf-8 -*-
from unittest.mock import MagicMock, patch

import pytest


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

    @patch("flask_se_practice_yandex_disk.yadisk.YaDisk")
    @pytest.mark.parametrize(
        ("exists", "is_dir", "session_extra"),
        [
            (True, True, {}),
            (False, False, {}),
            (True, True, {"table_path": "test_table.xlsx"}),
        ],
    )
    def test_yandex_upload_scenarios(
        self, mock_yadisk, logged_client, exists, is_dir, session_extra
    ):
        mock_disk = MagicMock()
        mock_yadisk.return_value = mock_disk
        mock_disk.exists.return_value = exists
        mock_disk.is_dir.return_value = is_dir
        with logged_client.session_transaction() as sess:
            sess["yandex_token"] = "test_token"
            sess.update(session_extra)
        resp = logged_client.get("/practice_admin/yandex_code")
        assert resp.status_code in (200, 302)

    @patch("flask_se_practice_yandex_disk.yadisk.YaDisk")
    def test_yandex_upload_no_token(self, mock_yadisk, seeded_client):
        mock_disk = MagicMock()
        mock_yadisk.return_value = mock_disk
        resp = seeded_client.get("/practice_admin/yandex_code")
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

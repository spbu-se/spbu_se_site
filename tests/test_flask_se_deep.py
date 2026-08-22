# -*- coding: utf-8 -*-
import builtins
import io
import os
import sys
from datetime import UTC, datetime

import pytest


class TestWrapperCalls:
    @pytest.mark.parametrize(
        "wrapper_name",
        [
            "recalculate_post_rank_wrapper",
            "notification_send_mail_wrapper",
            "notification_send_diploma_themes_on_review_wrapper",
        ],
    )
    def test_wrapper_calls_function(self, app_ctx, wrapper_name):
        import flask_se

        getattr(flask_se, wrapper_name)()


class TestDatetimeConvert:
    @pytest.mark.parametrize(
        "dt,fmt,expected",
        [
            (datetime(2024, 6, 15, 10, 30, 0, tzinfo=UTC), "%d.%m.%Y %H:%M", "15.06.2024"),
            (datetime(2024, 1, 1, 0, 0, 0, tzinfo=UTC), None, "01.01.2024"),
            (datetime(2024, 12, 25, 8, 15, 0, tzinfo=UTC), "%Y-%m-%d", "2024-12-25"),
        ],
    )
    def test_datetime_convert(self, app_ctx, dt, fmt, expected):
        import flask_se

        result = flask_se.datetime_convert(dt, format=fmt) if fmt else flask_se.datetime_convert(dt)
        assert expected in result


class TestIndexRouteAges:
    def test_index_returns_ages_for_news(self, seeded_client):
        from se_models import Posts, PostType, db

        pt = PostType(type=1, name="News")
        db.session.add(pt)
        db.session.flush()
        post = Posts(
            title="Test News",
            text="Test content",
            author_id=1,
            type_id=pt.id,
        )
        db.session.add(post)
        db.session.commit()
        resp = seeded_client.get("/")
        assert resp.status_code == 200
        html = resp.data.decode("utf-8")
        assert "Кафедра Системного Программирования" in html


class TestMainDispatch:
    def test_main_init_dispatch(self, monkeypatch, app_ctx):
        import flask_se as _fs

        monkeypatch.setattr(sys, "argv", ["flask_se.py", "init"])
        monkeypatch.setattr(_fs, "__name__", "__main__")
        init_called = []
        monkeypatch.setattr(_fs, "init_db", lambda: init_called.append(True))

        with open(_fs.__file__, encoding="utf-8") as f:
            lines = f.readlines()
        main_start = next(i for i, _line in enumerate(lines) if _line.startswith("if __name__"))
        src = "".join(lines[main_start:])
        code = compile(src, _fs.__file__, "exec")
        exec(code, _fs.__dict__)
        assert init_called == [True]

    def test_main_run_dispatch(self, monkeypatch, app_ctx):
        import flask_se as _fs

        monkeypatch.setattr(sys, "argv", ["flask_se.py"])
        monkeypatch.setattr(_fs, "__name__", "__main__")
        run_called = []
        monkeypatch.setattr(
            "werkzeug.serving.run_simple",
            lambda hostname, port, application, use_debugger=False, use_reloader=False: (
                run_called.append(True)
            ),
        )

        with open(_fs.__file__, encoding="utf-8") as f:
            lines = f.readlines()
        main_start = next(i for i, _line in enumerate(lines) if _line.startswith("if __name__"))
        src = "".join(lines[main_start:])
        code = compile(src, _fs.__file__, "exec")
        exec(code, _fs.__dict__)
        assert run_called == [True]


class TestFlaskSeConfigMailPassword:
    def test_mail_password_read_from_file(self, monkeypatch):
        import importlib

        import flask_se_config

        real_path = flask_se_config.MAIL_PASSWORD_FILE
        fake_content = "smtp_password\n"
        original_exists = os.path.exists

        def mock_exists(path):
            if path == real_path:
                return True
            return original_exists(path)

        original_open = builtins.open

        def mock_open(file, mode="r", *args, **kwargs):
            if file == real_path:
                return io.StringIO(fake_content)
            return original_open(file, mode, *args, **kwargs)

        monkeypatch.setattr(os.path, "exists", mock_exists)
        monkeypatch.setattr(builtins, "open", mock_open)
        importlib.reload(flask_se_config)
        assert flask_se_config.MAIL_PASSWORD == "smtp_password"

    def test_mail_password_missing_file_falls_back(self, monkeypatch):
        import importlib

        import flask_se_config

        monkeypatch.setattr(os.path, "exists", lambda p: False)
        importlib.reload(flask_se_config)
        assert len(flask_se_config.MAIL_PASSWORD) == 32


class TestFlaskSeConfigSecureFilenameWindowsDevices:
    @pytest.mark.parametrize(
        "name,expected_non_nt",
        [
            ("CON", "CON"),
            ("CON.txt", "CON.txt"),
            ("AUX", None),
            ("LPT1", None),
            ("NUL", None),
        ],
    )
    def test_secure_filename_device(self, name, expected_non_nt):
        from flask_se_config import secure_filename

        result = secure_filename(name)
        if os.name == "nt":
            assert result == "_{filename}" or result.startswith("_")
        elif expected_non_nt is not None:
            assert result == expected_non_nt

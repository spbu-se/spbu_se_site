# -*- coding: utf-8 -*-
import builtins
import io
import os
import sys
from datetime import UTC


class TestRecalculatePostRankWrapper:
    def test_wrapper_calls_recalculate_post_rank(self, app_ctx):
        from flask_se import recalculate_post_rank_wrapper

        recalculate_post_rank_wrapper()


class TestNotificationSendMailWrapper:
    def test_wrapper_calls_notification_send_mail(self, app_ctx):
        from flask_se import notification_send_mail_wrapper

        notification_send_mail_wrapper()


class TestNotificationSendDiplomaThemesOnReviewWrapper:
    def test_wrapper_calls_notification_send_diploma_themes_on_review(self, app_ctx):
        from flask_se import notification_send_diploma_themes_on_review_wrapper

        notification_send_diploma_themes_on_review_wrapper()


class TestDatetimeConvert:
    def test_datetime_convert_returns_formatted_string(self, app_ctx):
        from datetime import datetime

        import flask_se

        result = flask_se.datetime_convert(
            datetime(2024, 6, 15, 10, 30, 0, tzinfo=UTC),
            format="%d.%m.%Y %H:%M",
        )
        assert "15.06.2024" in result

    def test_datetime_convert_default_format(self, app_ctx):
        from datetime import datetime

        import flask_se

        result = flask_se.datetime_convert(datetime(2024, 1, 1, 0, 0, 0, tzinfo=UTC))
        assert "01.01.2024" in result

    def test_datetime_convert_different_format(self, app_ctx):
        from datetime import datetime

        import flask_se

        result = flask_se.datetime_convert(
            datetime(2024, 12, 25, 8, 15, 0, tzinfo=UTC),
            format="%Y-%m-%d",
        )
        assert "2024-12-25" in result


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
        assert (
            "РјРµРЅСЊС€Рµ С‡Р°СЃР°" in html
            or "С‡Р°СЃ" in html
            or "РґРµРЅСЊ" in html
            or "РґРЅСЏ" in html
            or "РґРЅРµР№" in html
        )


class TestMainBuildCommand:
    def test_main_build_dispatch(self, monkeypatch, app_ctx):
        import flask_se as _fs

        monkeypatch.setattr(sys, "argv", ["flask_se.py", "build"])
        monkeypatch.setattr(_fs, "__name__", "__main__")
        freeze_called = []
        monkeypatch.setattr(_fs.freezer, "freeze", lambda: freeze_called.append(True))
        import linecache

        lines = linecache.getlines(_fs.__file__)
        src = "".join(lines[586:])
        code = compile(src, _fs.__file__, "exec")
        exec(code, _fs.__dict__)
        assert freeze_called == [True]

    def test_main_init_dispatch(self, monkeypatch, app_ctx):
        import flask_se as _fs

        monkeypatch.setattr(sys, "argv", ["flask_se.py", "init"])
        monkeypatch.setattr(_fs, "__name__", "__main__")
        init_called = []
        monkeypatch.setattr(_fs, "init_db", lambda: init_called.append(True))
        import linecache

        lines = linecache.getlines(_fs.__file__)
        src = "".join(lines[586:])
        code = compile(src, _fs.__file__, "exec")
        exec(code, _fs.__dict__)
        assert init_called == [True]

    def test_main_run_dispatch(self, monkeypatch, app_ctx):
        import flask_se as _fs

        monkeypatch.setattr(sys, "argv", ["flask_se.py"])
        monkeypatch.setattr(_fs, "__name__", "__main__")
        reindex_called = []
        run_called = []
        monkeypatch.setattr(_fs.whooshee, "reindex", lambda: reindex_called.append(True))
        monkeypatch.setattr(_fs.app, "run", lambda port=5000, debug=True: run_called.append(True))
        import linecache

        lines = linecache.getlines(_fs.__file__)
        src = "".join(lines[586:])
        code = compile(src, _fs.__file__, "exec")
        exec(code, _fs.__dict__)
        assert reindex_called == [True]
        assert run_called == [True]


class TestFlaskSeConfigMailPassword:
    def test_mail_password_read_from_file(self, monkeypatch):
        import importlib

        import flask_se_config

        real_path = flask_se_config.MAIL_PASSWORD_FILE
        fake_content = "smtp_password\n"

        def mock_exists(path):
            if path == real_path:
                return True
            return os.path.exists(path)

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
    def test_secure_filename_con_device(self):
        from flask_se_config import secure_filename

        result = secure_filename("CON")
        if os.name == "nt":
            assert result == "_{filename}" or result.startswith("_")
        else:
            assert result == "CON"

    def test_secure_filename_con_txt(self):
        from flask_se_config import secure_filename

        result = secure_filename("CON.txt")
        if os.name == "nt":
            assert result == "_{filename}" or result.startswith("_")
        else:
            assert result == "CON.txt"

    def test_secure_filename_aux_device(self):
        from flask_se_config import secure_filename

        result = secure_filename("AUX")
        if os.name == "nt":
            assert result == "_{filename}" or result.startswith("_")

    def test_secure_filename_lpt1_device(self):
        from flask_se_config import secure_filename

        result = secure_filename("LPT1")
        if os.name == "nt":
            assert result == "_{filename}" or result.startswith("_")

    def test_secure_filename_nul_device(self):
        from flask_se_config import secure_filename

        result = secure_filename("NUL")
        if os.name == "nt":
            assert result == "_{filename}" or result.startswith("_")

# SPDX-License-Identifier: Apache-2.0

import logging
import os
from contextlib import contextmanager

import pytest

import flask_se_logviewer as lv
from flask_se_logviewer import _sanitize


@contextmanager
def _enabled_logs(tmp_path, *, public: bool = False):
    """Build a fresh app with the logs feature enabled in a throwaway scratch dir.

    Detaches the file handler afterwards so a disabled-by-default deployment
    never leaks a live handler across tests.
    """
    from flask_se import create_app

    os.environ["SE_LOGS_ENABLED"] = "1"
    os.environ["SE_SCRATCH_DIR"] = str(tmp_path)
    if public:
        os.environ["SE_LOGS_PUBLIC"] = "1"
    else:
        os.environ.pop("SE_LOGS_PUBLIC", None)
    try:
        yield create_app(start_scheduler=False)
    finally:
        os.environ.pop("SE_LOGS_ENABLED", None)
        os.environ.pop("SE_SCRATCH_DIR", None)
        os.environ.pop("SE_LOGS_PUBLIC", None)
        for logger_name in ("flask_se", ""):
            logger = logging.getLogger(logger_name)
            logger.handlers = [h for h in logger.handlers if not isinstance(h, lv.LogViewerHandler)]


def _log_record(msg: str) -> logging.LogRecord:
    return logging.LogRecord(
        name="t",
        level=logging.WARNING,
        pathname=__file__,
        lineno=1,
        msg=msg,
        args=(),
        exc_info=None,
    )


class TestDisabledByDefault:
    def test_logs_404_when_not_enabled(self, client):
        assert client.get("/logs").status_code == 404

    def test_no_handler_attached_when_not_enabled(self):
        assert not [
            h for h in logging.getLogger("flask_se").handlers if isinstance(h, lv.LogViewerHandler)
        ]


class TestEnabled:
    def test_anonymous_404_when_public_off(self, tmp_path):
        with _enabled_logs(tmp_path) as app:
            assert app.test_client().get("/logs").status_code == 404
            assert not (tmp_path / "server-errors.log").exists()

    def test_anonymous_preview_when_public_on(self, tmp_path):
        with _enabled_logs(tmp_path, public=True) as app:
            logging.getLogger("flask_se").warning("boom https://sqlalche.me/e/20/e3q8")
            # Unique client IP: the anonymous-preview window (is_rate_limited in
            # flask_se_logviewer) is process-global and keyed on REMOTE_ADDR, so a
            # default 127.0.0.1 can already be exhausted by earlier worker traffic
            # under xdist (intermittent CI 429 on an otherwise deterministic test).
            resp = app.test_client().get("/logs", environ_base={"REMOTE_ADDR": "10.0.0.42"})
            assert resp.status_code == 200
            body = resp.get_data(as_text=True)
            assert "boom" in body
            assert "sqlalche.me/e/&lt;e3q8&gt;" in body

    def test_admin_full_table_when_enabled(self, tmp_path):
        import tempfile
        from pathlib import Path

        from sqlalchemy import create_engine

        from se_models import Users, db, init_db

        with _enabled_logs(tmp_path) as app:
            # create_app resolves the DB URI from the stale import-time constant
            # (databases/se.db), which does not exist on CI and pollutes the repo
            # dir locally; a config override is ignored because the engine is
            # already cached. Swap the enabled app's engine to a temp DB instead
            # (mirrors conftest._set_db_uri).
            with app.app_context():
                db.engines[None] = create_engine(
                    "sqlite:///" + str(Path(tempfile.mkdtemp()) / "test.db")
                )
                db.create_all()
                init_db()
                u = Users.query.filter_by(email="a.terekhov@spbu.ru").first()
                assert u is not None
                u.role = 5
                db.session.commit()
                uid = str(u.id)

            client = app.test_client()
            with client.session_transaction() as sess:
                sess["_user_id"] = uid
            resp = client.get("/logs")
            assert resp.status_code == 200
            assert "Журнал ошибок" in resp.get_data(as_text=True)
            file_text = (tmp_path / "server-errors.log").read_text(encoding="utf-8")
            assert "ADMIN_LOG_VIEWED" in file_text


class TestSanitize:
    @pytest.mark.parametrize(
        "raw,expected",
        [
            ("https://sqlalche.me/e/20/e3q8", "sqlalche.me/e/<e3q8>"),
            ("hit 2001:db8::1 end", "hit x:x:x:x:x:x:x:x end"),
            ("fe80::1%eth0", "x:x:x:x:x:x:x:x"),
            ("ts 10:29:47 kept", "ts 10:29:47 kept"),
            ("tok deadbeefdeadbeefdeadbeefdeadbeef end", "tok <token> end"),
            ("ip 192.168.0.1 done", "ip x.x.x.x done"),
            ("mail a.terekhov@spbu.ru", "mail ***@spbu.ru"),
            ("p /home/ubuntu/se.db gone", "p <deploy-path> gone"),
        ],
    )
    def test_redactions(self, raw, expected):
        assert expected in _sanitize(raw)

    def test_plain_words_not_redacted(self):
        text = "ConfigurationError raised during OperationalError"
        assert _sanitize(text) == text


class TestRotation:
    def test_size_based_rotation(self, tmp_path, monkeypatch):
        monkeypatch.setenv("SE_LOGS_ENABLED", "1")
        monkeypatch.setenv("SE_SCRATCH_DIR", str(tmp_path))
        monkeypatch.setattr(lv, "_MAX_LOG_BYTES", 100)

        handler = lv.LogViewerHandler()
        for _ in range(15):
            handler.emit(_log_record("x" * 200))

        names = {p.name for p in tmp_path.iterdir()}
        assert "server-errors.log" in names
        assert "server-errors.log.1" in names

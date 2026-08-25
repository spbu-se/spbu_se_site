# SPDX-License-Identifier: Apache-2.0

from contextlib import contextmanager
from pathlib import Path

import pytest


@contextmanager
def _isolated_db(build_legacy=None):
    """Point the app at a throwaway SQLite file (engine swap), restore in finally.

    Mirrors ``conftest._set_db_uri()``. ``build_legacy`` optionally creates a
    partial/legacy schema first — the file must exist so ``ensure_schema()``
    takes the repair path instead of the fresh-init path.
    """
    import shutil
    import tempfile

    from sqlalchemy import create_engine

    import flask_se_config as fsc
    from flask_se import app, db

    _dir = tempfile.mkdtemp()
    _db_name = "schema.db"
    _uri = "sqlite:///" + str(Path(_dir, _db_name))
    with app.app_context():
        old_name, old_path = fsc.SQLITE_DATABASE_NAME, fsc.SQLITE_DATABASE_PATH
        old_uri = app.config["SQLALCHEMY_DATABASE_URI"]
        old_engine = db.engines.get(None)
        try:
            fsc.SQLITE_DATABASE_NAME = _db_name
            fsc.SQLITE_DATABASE_PATH = _dir
            app.config["SQLALCHEMY_DATABASE_URI"] = _uri
            db.engines[None] = create_engine(_uri)
            if build_legacy is not None:
                build_legacy()
            yield _dir
        finally:
            fsc.SQLITE_DATABASE_NAME, fsc.SQLITE_DATABASE_PATH = old_name, old_path
            app.config["SQLALCHEMY_DATABASE_URI"] = old_uri
            if old_engine is not None:
                db.engines[None] = old_engine
            else:
                db.engines.pop(None, None)
    shutil.rmtree(_dir, ignore_errors=True)


def _users_columns():
    from sqlalchemy import inspect

    from flask_se import db

    return {col["name"] for col in inspect(db.engine).get_columns("users")}


def _users_table_info():
    from flask_se import db

    with db.engine.connect() as conn:
        rows = conn.execute(db.text("PRAGMA table_info(users)")).fetchall()
    return {row[1]: row for row in rows}


def _legacy_users_table():
    from flask_se import db

    with db.engine.begin() as conn:
        conn.execute(db.text("CREATE TABLE users (id INTEGER PRIMARY KEY, email VARCHAR(255))"))


class TestSchemaDeltas:
    def test_fresh_db_initializes_all_tables_and_fts(self):
        from sqlalchemy import inspect

        from flask_se import db, ensure_schema

        with _isolated_db() as _dir:
            ensure_schema()
            tables = set(inspect(db.engine).get_table_names())
            assert "users" in tables
            assert "posts" in tables
            assert "thesis" in tables
            assert "thesis_fts" in tables
            assert "alembic_version" not in tables

    def test_existing_db_backs_up_then_repairs_missing_columns(self):
        import flask_se_config as fsc
        from flask_se import ensure_schema

        with _isolated_db(build_legacy=_legacy_users_table) as _dir:
            ensure_schema()
            assert Path(_dir, fsc.SQLITE_DATABASE_BACKUP_NAME).is_file()
            cols = _users_columns()
            assert {"password_hash", "first_name", "middle_name", "last_name", "role"} <= cols
            assert "deleted" in cols

    @pytest.mark.parametrize(
        "col,expected_type,not_null,default",
        [
            ("deleted", "BOOLEAN", 1, "0"),
            ("role", None, 1, "0"),
            ("first_name", None, 1, "''"),
        ],
    )
    def test_not_null_columns_repaired_with_defaults(self, col, expected_type, not_null, default):
        from flask_se import ensure_schema

        with _isolated_db(build_legacy=_legacy_users_table):
            ensure_schema()
            info = _users_table_info()[col]
            if expected_type is not None:
                assert info[2] == expected_type  # declared type
            assert info[3] == not_null  # NOT NULL
            assert info[4] == default  # server_default backfills existing rows

    def test_exotic_not_null_without_default_added_nullable(self):
        from flask_se import db, ensure_schema

        def legacy():
            with db.engine.begin() as conn:
                conn.execute(
                    db.text(
                        "CREATE TABLE notification_log (id INTEGER PRIMARY KEY, type VARCHAR(64))"
                    )
                )

        with _isolated_db(build_legacy=legacy):
            ensure_schema()
            with db.engine.connect() as conn:
                info = {
                    row[1]: row
                    for row in conn.execute(db.text("PRAGMA table_info(notification_log)"))
                }
            assert info["last_sent_at"][2] == "DATETIME"
            assert info["last_sent_at"][3] == 0  # added nullable with a logged warning

    def test_missing_unique_column_fails_loud(self):
        from flask_se import db, ensure_schema

        def legacy():
            with db.engine.begin() as conn:
                conn.execute(db.text("CREATE TABLE users (id INTEGER PRIMARY KEY)"))

        with _isolated_db(build_legacy=legacy), pytest.raises(RuntimeError, match="UNIQUE"):
            ensure_schema()

    def test_repair_is_idempotent(self):
        from flask_se import ensure_schema

        with _isolated_db(build_legacy=_legacy_users_table):
            ensure_schema()
            first = _users_columns()
            ensure_schema()
            assert _users_columns() == first

    def test_fts_index_created_for_legacy_db(self):
        from sqlalchemy import inspect

        from flask_se import db, ensure_schema

        with _isolated_db(build_legacy=_legacy_users_table):
            assert "thesis_fts" not in inspect(db.engine).get_table_names()
            ensure_schema()
            tables = set(inspect(db.engine).get_table_names())
            assert "thesis_fts" in tables
            triggers = {
                row[0]
                for row in db.session.execute(
                    db.text(
                        "SELECT name FROM sqlite_master WHERE type = 'trigger' "
                        "AND name LIKE 'thesis_fts_%'"
                    )
                )
            }
            assert {"thesis_fts_ai", "thesis_fts_ad", "thesis_fts_au"} <= triggers

    def test_db_cli_group_runs_ensure_schema(self):
        """Deploy webhook invokes ``flask db upgrade`` — it must not fail with
        "No such command 'db'" and must repair the schema like ensure_schema."""
        from flask import current_app

        with _isolated_db(build_legacy=_legacy_users_table):
            runner = current_app.test_cli_runner()
            result = runner.invoke(args=["db", "upgrade"])
            assert result.exit_code == 0, result.output
            assert "deleted" in _users_columns()

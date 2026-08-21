# SPDX-License-Identifier: Apache-2.0

from contextlib import contextmanager
from pathlib import Path


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
        from flask_se import db, ensure_schema

        def legacy():
            with db.engine.begin() as conn:
                conn.execute(
                    db.text("CREATE TABLE users (id INTEGER PRIMARY KEY, email VARCHAR(255))")
                )

        with _isolated_db(build_legacy=legacy) as _dir:
            ensure_schema()
            assert Path(_dir, fsc.SQLITE_DATABASE_BACKUP_NAME).is_file()
            cols = _users_columns()
            assert {"password_hash", "first_name", "middle_name", "last_name", "role"} <= cols
            assert "deleted" in cols

    def test_not_null_with_server_default_uses_it(self):
        from flask_se import db, ensure_schema

        def legacy():
            with db.engine.begin() as conn:
                conn.execute(
                    db.text("CREATE TABLE users (id INTEGER PRIMARY KEY, email VARCHAR(255))")
                )

        with _isolated_db(build_legacy=legacy):
            ensure_schema()
            info = _users_table_info()["deleted"]
            assert info[2] == "BOOLEAN"  # declared type
            assert info[3] == 1  # NOT NULL
            assert info[4] == "0"  # server_default backfills existing rows

    def test_not_null_without_server_default_synthesizes_constant(self):
        from flask_se import db, ensure_schema

        def legacy():
            with db.engine.begin() as conn:
                conn.execute(
                    db.text("CREATE TABLE users (id INTEGER PRIMARY KEY, email VARCHAR(255))")
                )

        with _isolated_db(build_legacy=legacy):
            ensure_schema()
            info = _users_table_info()
            assert info["role"][3] == 1 and info["role"][4] == "0"
            assert info["first_name"][3] == 1 and info["first_name"][4] == "''"

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
        import pytest

        from flask_se import db, ensure_schema

        def legacy():
            with db.engine.begin() as conn:
                conn.execute(db.text("CREATE TABLE users (id INTEGER PRIMARY KEY)"))

        with _isolated_db(build_legacy=legacy), pytest.raises(RuntimeError, match="UNIQUE"):
            ensure_schema()

    def test_repair_is_idempotent(self):
        from flask_se import db, ensure_schema

        def legacy():
            with db.engine.begin() as conn:
                conn.execute(
                    db.text("CREATE TABLE users (id INTEGER PRIMARY KEY, email VARCHAR(255))")
                )

        with _isolated_db(build_legacy=legacy):
            ensure_schema()
            first = _users_columns()
            ensure_schema()
            assert _users_columns() == first

    def test_fts_index_created_for_legacy_db(self):
        from sqlalchemy import inspect

        from flask_se import db, ensure_schema

        def legacy():
            with db.engine.begin() as conn:
                conn.execute(
                    db.text("CREATE TABLE users (id INTEGER PRIMARY KEY, email VARCHAR(255))")
                )

        with _isolated_db(build_legacy=legacy):
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

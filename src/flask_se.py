# SPDX-License-Identifier: Apache-2.0

import os
import secrets
import shutil
import sys
from datetime import UTC, date
from pathlib import Path

__all__ = ["app", "db", "scheduler"]

import markdown as _markdown
import nh3
from dateutil import tz
from flask import Flask, current_app, g, render_template, request
from flask_wtf import CSRFProtect
from flask_wtf.csrf import CSRFError
from markupsafe import Markup
from sqlalchemy import Boolean, Float, Integer, Numeric, String, Text, inspect
from sqlalchemy.dialects.sqlite import dialect as sqlite_dialect
from sqlalchemy.pool import NullPool
from sqlalchemy.schema import CreateColumn

import flask_se_config as fsc
import flask_se_theses
from flask_se_admin import (
    AdminIndexView,
    SeAdminModelViewCompany,
    SeAdminModelViewCurrentThesis,
    SeAdminModelViewDiplomaThemes,
    SeAdminModelViewNews,
    SeAdminModelViewReviewDiplomaThemes,
    SeAdminModelViewStaff,
    SeAdminModelViewSummerSchool,
    SeAdminModelViewThesis,
    SeAdminModelViewUsers,
)
from flask_se_auth import login_manager
from flask_se_auth import register_routes as register_auth_routes
from flask_se_config import (
    CONSENT_COOKIE_NAME,
    SECRET_KEY,
    SECRET_KEY_THESIS,
    SQLITE_DATABASE_PATH,
    SQLITE_DATABASE_URI,
    consent_categories,
    maps_config,
    metrica_id,
    site_deploy_date,
    smartcaptcha_enabled,
    smartcaptcha_sitekey,
)
from flask_se_csp_report import register_csp_report
from flask_se_diplomas import register_routes as register_diplomas_routes
from flask_se_headers import register_security_headers
from flask_se_internships import register_routes as register_internships_routes
from flask_se_logviewer import register_log_viewer
from flask_se_news import register_routes as register_news_routes
from flask_se_practice import register_routes as register_practice_routes
from flask_se_practice_admin import register_routes as register_practice_admin_routes
from flask_se_practice_staff import register_routes as register_practice_staff_routes
from flask_se_review import register_routes as register_review_routes
from flask_se_scheduler import (  # pyright: ignore[reportUnusedImport]  # re-exported for tests
    configure_scheduler,
    scheduler,
)
from flask_se_scholarships import register_routes as register_scholarships_routes
from flask_se_static import (
    register_content_pages,
    register_legacy_redirects,
    register_static_pages,
)
from flask_se_summer_schools import register_routes as register_summer_schools_routes
from flask_se_theses import register_routes as register_theses_routes
from se_models import (
    Company,
    CurrentThesis,
    DiplomaThemes,
    Posts,
    Staff,
    SummerSchool,
    Thesis,
    Users,
    db,
    ensure_fts5_index,
    init_db,
    recalculate_post_rank,
)
from se_sendmail import (
    notification_send_diploma_themes_on_review,
    notification_send_mail,
)
from sitemap import register_sitemap

# Extension singletons: init_app() is called inside create_app() so the same
# objects can back multiple app instances (production WSGI + tests).
csrf = CSRFProtect()


# Scheduler job wrappers: run inside an app context so db queries work. They
# reference the module-level ``app`` singleton (the WSGI entry's instance).
def recalculate_post_rank_wrapper() -> None:
    with app.app_context():
        recalculate_post_rank()


def notification_send_mail_wrapper() -> None:
    with app.app_context():
        notification_send_mail()


def notification_send_diploma_themes_on_review_wrapper() -> None:
    with app.app_context():
        notification_send_diploma_themes_on_review()


# Template filters (module-level functions registered in _configure_app so the
# names stay importable for tests: flask_se.datetime_convert, flask_se.markdown).
def render_markdown(text: str) -> Markup:
    """Render markdown to HTML, sanitize, and mark safe for Jinja.

    Sanitization happens at render time so it covers every current and future
    call site and legacy rows. It is required before marking the output safe:
    python-markdown passes raw HTML through unchanged and the source is
    user-authored (theme/report/internship content).
    """
    return Markup(nh3.clean(_markdown.markdown(text or "", extensions=["tables"])))  # noqa: S704  sanitized immediately before Markup


def render_safe_html(text: str) -> Markup:
    """Sanitize pre-rendered HTML and mark it safe for Jinja.

    Defense-in-depth for content already cleaned at write time (e.g. news
    posts) — protects legacy rows and any write path that bypasses cleaning.
    """
    return Markup(nh3.clean(text or ""))  # noqa: S704  sanitized immediately before Markup


def datetime_convert(value, format="%d.%m.%Y %H:%M"):
    return value.replace(tzinfo=UTC).astimezone(tz.tzlocal()).strftime(format)


def _configure_app(app: Flask, config_overrides: dict[str, object] | None) -> None:
    """Set every app.config key; ``config_overrides`` wins (used by tests)."""
    app.config["APPLICATION_ROOT"] = "/"

    # SQLAlchemy config
    # Absolute DB path (databases/se.db) — matches init_db(); CWD-independent.
    # Ensure the directory exists so SQLAlchemy can open the file on first run
    # (init_db() creates it too, but the dev server / Docker may connect first).
    Path(SQLITE_DATABASE_PATH).mkdir(parents=True, exist_ok=True)
    app.config["SQLALCHEMY_DATABASE_URI"] = SQLITE_DATABASE_URI
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_pre_ping": True,
        "poolclass": NullPool,
    }
    app.config["SECRET_KEY"] = SECRET_KEY
    app.config["SESSION_COOKIE_NAME"] = "se_session"

    # Secure session cookies: HTTPS-only + SameSite. Dev runs on plain HTTP, so
    # SECURE is toggled by an env flag (production deploys set it).
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SECURE"] = os.environ.get("SE_COOKIE_SECURE", "1") == "1"
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

    # CSRF stays fully enforced via the per-session token in the form, but the
    # SSL-strict referrer requirement (Flask-WTF default) is disabled. It
    # rejected any POST whose Referer header was missing (privacy browsers,
    # extensions, proxies, password-manager autofill, non-browser clients)
    # with a 400 "The referrer header is missing" — see the 2026-08-31 login
    # outage. The token comparison is the security boundary; the referrer check
    # was a redundant fragility that locked real users out of login.
    app.config["WTF_CSRF_SSL_STRICT"] = False

    # Upload/request body limit: 64 MB (thesis PDFs + presentations can be large).
    app.config["MAX_CONTENT_LENGTH"] = 64 * 1024 * 1024

    # Secret for API
    app.config["SECRET_KEY_THESIS"] = SECRET_KEY_THESIS

    # Basic auth config
    app.config["BASIC_AUTH_USERNAME"] = "se_staff"
    app.config["BASIC_AUTH_PASSWORD"] = app.config["SECRET_KEY_THESIS"]

    if config_overrides:
        app.config.update(config_overrides)


def _init_extensions(app: Flask) -> None:
    # Global CSRF protection. Tests set WTF_CSRF_ENABLED=False in conftest.
    # All POST forms must include {{ csrf_token() }}.
    csrf.init_app(app)

    @app.errorhandler(CSRFError)
    def _handle_csrf_error(exc: CSRFError):  # pyright: ignore[reportUnusedFunction]
        """Friendly page for a real CSRF rejection instead of a bare 400.

        The session token still has to match; with referrer strictness off this
        is rare (stale page, expired token) but must stay navigable — reload the
        page and retry. CSRFProtect runs before the nonce before_request, so
        the nonce is set here for both the template and the CSP header.
        """
        g.csp_nonce = secrets.token_urlsafe(16)
        current_app.logger.warning(
            "CSRF rejected path=%s reason=%s ip=%s",
            request.path,
            exc.description,
            request.remote_addr or "unknown",
        )
        return (
            render_template(
                "csrf_error.html",
                csrf_reason=str(exc.description),
            ),
            400,
        )

    db.init_app(app)
    login_manager.init_app(app)

    app.template_filter("markdown")(render_markdown)
    app.template_filter("safe_html")(render_safe_html)
    app.template_filter("datatime_convert")(datetime_convert)

    def _inject_template_globals() -> dict[str, object]:
        se_maps_provider, se_maps_key = maps_config()
        se_consent_categories = consent_categories()
        raw_consent = request.cookies.get(CONSENT_COOKIE_NAME, "").strip()
        se_consent_granted = dict.fromkeys(se_consent_categories, False)
        for _category in raw_consent.split(","):
            _category = _category.strip()
            if _category in se_consent_granted:
                se_consent_granted[_category] = True
        return {
            "current_year": date.today().year,
            "ASSET_VERSION": site_deploy_date(),
            "se_maps_provider": se_maps_provider,
            "se_maps_key": se_maps_key,
            "se_metrica_id": metrica_id(),
            "se_consent_categories": se_consent_categories,
            "se_consent_granted": se_consent_granted,
            "se_consent_decided": bool(raw_consent),
            "se_smartcaptcha_enabled": smartcaptcha_enabled(),
            "se_smartcaptcha_sitekey": smartcaptcha_sitekey(),
            "csp_nonce": lambda: g.csp_nonce,
        }

    app.context_processor(_inject_template_globals)


def _register_routes(app: Flask) -> None:
    """All app routes, registered by domain module. Endpoint names derive from
    each view function's __name__, so registering via these helpers never
    renames a URL. Adding a route means editing the module that owns it."""
    register_auth_routes(app)
    register_theses_routes(app)
    # post_theses is an authenticated-by-secret API (external upload script),
    # not a browser form — exempt from CSRF.
    csrf.exempt(flask_se_theses.post_theses)
    register_news_routes(app)
    register_scholarships_routes(app)
    register_diplomas_routes(app)
    register_review_routes(app)
    register_internships_routes(app)
    register_practice_routes(app)
    register_practice_staff_routes(app)
    register_practice_admin_routes(app)
    register_summer_schools_routes(app)


def _init_admin_views(app: Flask) -> None:
    """Custom admin CRUD views; constructors self-register their routes."""
    AdminIndexView(app)
    SeAdminModelViewUsers(app, Users, endpoint="users")
    SeAdminModelViewStaff(app, Staff, endpoint="staff")
    SeAdminModelViewThesis(app, Thesis, endpoint="thesis")
    SeAdminModelViewSummerSchool(app, SummerSchool, endpoint="summerschool")
    SeAdminModelViewNews(app, Posts, endpoint="posts")
    SeAdminModelViewDiplomaThemes(app, DiplomaThemes, endpoint="diplomathemes")
    SeAdminModelViewReviewDiplomaThemes(app, DiplomaThemes, endpoint="reviewdiplomathemes")
    SeAdminModelViewCompany(app, Company, endpoint="companies")
    SeAdminModelViewCurrentThesis(app, CurrentThesis, endpoint="currentthesis")


# Static assets are served by the app (the host nginx is a pure reverse proxy),
# so the long-term cache headers belong here, not in host nginx config. Safe
# because every css/js/libs URL carries the release date (?v=, asset() macro),
# so new releases bust the immutable cache automatically; images get 30 days so
# a replaced photo is not stuck forever.
ASSET_IMMUTABLE_PREFIXES = ("/assets/css/", "/assets/js/", "/assets/libs/")


def _register_static_cache_headers(app: Flask) -> None:
    """Immutable cache for versioned static assets, 30-day cap for images."""

    @app.after_request
    def _set_asset_cache_headers(response):  # pyright: ignore[reportUnusedFunction]
        if response.status_code != 200:
            return response
        path = request.path
        if path.startswith(ASSET_IMMUTABLE_PREFIXES):
            response.headers["Cache-Control"] = "public, max-age=31536000, immutable"
        elif path.startswith("/assets/img/"):
            response.headers["Cache-Control"] = "public, max-age=2592000"
        return response


def create_app(
    config_overrides: dict[str, object] | None = None,
    start_scheduler: bool | None = None,
) -> Flask:
    """Application factory.

    ``app = create_app()`` at module level keeps the singleton semantics the
    WSGI entry point, the import pipeline (extract_text/thesis_import) and the
    test suite rely on. ``config_overrides`` lets tests and tooling build a
    differently-configured instance without import-time monkeypatching.
    """
    app = Flask(
        __name__,
        static_url_path="",
        static_folder="static",
        template_folder="templates",
        instance_path=SQLITE_DATABASE_PATH,
    )

    _configure_app(app, config_overrides)
    _init_extensions(app)
    _register_routes(app)
    register_static_pages(app)
    register_content_pages(app)
    register_sitemap(app)
    register_legacy_redirects(app)
    _register_static_cache_headers(app)
    register_security_headers(app)
    register_csp_report(app)
    register_log_viewer(app)
    _init_admin_views(app)
    # Default: read SE_START_SCHEDULER (production leaves it unset → jobs run).
    # conftest sets it to "0" before importing so the suite never fires jobs.
    # The import pipeline (extract_text.py, thesis_import.py) imports the app
    # without starting the scheduler either way.
    if start_scheduler is None:
        start_scheduler = os.environ.get("SE_START_SCHEDULER", "1") == "1"
    configure_scheduler(
        [
            ("RecalculatePostRank", recalculate_post_rank_wrapper, 3600),
            ("SendMailNotification", notification_send_mail_wrapper, 10),
            (
                "SendDiplomaThemesOnReviewNotification",
                notification_send_diploma_themes_on_review_wrapper,
                86400,
            ),
        ],
        start_scheduler,
    )

    return app


app = create_app()


def _register_db_cli(app: Flask) -> None:
    """Provide a ``flask db ...`` CLI so the deploy webhook's migration step works.

    The production deploy webhook invokes ``flask db <subcommand>`` (Flask-Migrate
    convention). Alembic was removed in favor of the self-healing
    ``ensure_schema()``, so map the common subcommands to it instead of failing
    with "No such command 'db'".
    """

    @app.cli.group("db")
    def db_cli() -> None:
        """Database schema commands (delegate to ensure_schema)."""

    for name in ("upgrade", "migrate", "revision"):

        @db_cli.command(name)
        def _db_schema() -> None:  # pyright: ignore[reportUnusedFunction]
            with app.app_context():
                ensure_schema()


_register_db_cli(app)


class EnsureSchemaError(RuntimeError):
    """A schema delta cannot be applied automatically.

    SQLite ADD COLUMN cannot add columns carrying PK/UNIQUE/FK constraints —
    the developer fixes the model and redeploys manually, then re-runs
    ``ensure_schema``. Never an ops step.
    """

    def __init__(self, column_name: str) -> None:
        super().__init__(f"Cannot auto-add column {column_name} (PK/UNIQUE/FK)")


def ensure_schema() -> None:
    """Self-heal the SQLite schema to match the models (idempotent, no ops needed).

    Fresh DB (no file yet): ``init_db()`` builds it from the models. Existing
    DB: back it up to ``se_backup_<date>.db`` (best-effort), then
    ``db.create_all()`` for missing tables plus a per-table ``PRAGMA table_info``
    diff that adds every column the model declares and the DB lacks. Column
    presence is the version marker — there is no ``alembic_version`` table and no
    version state to drift. Entrypoint runs this unless ``SE_AUTO_MIGRATE=0``.
    """
    db_file = Path(fsc.SQLITE_DATABASE_PATH, fsc.SQLITE_DATABASE_NAME)
    if not db_file.is_file():
        init_db()
        print("[ensure-schema] Fresh DB initialized from models")
        return

    backup = Path(fsc.SQLITE_DATABASE_PATH, fsc.SQLITE_DATABASE_BACKUP_NAME)
    try:
        shutil.copyfile(db_file, backup)
        print(f"[ensure-schema] Backed up DB to {backup.name}")
    except OSError as exc:
        # Best-effort: the deploy webhook runs the migration with writable DB
        # dir, but app workers may only read it (prod hit PermissionError here,
        # which silently disabled the whole self-heal). The migration itself
        # must not be blocked by a backup we can't write.
        print(f"[ensure-schema] WARNING: DB backup to {backup.name} failed ({exc}); continuing")

    db.create_all()
    _ensure_schema_columns()
    ensure_fts5_index()
    print("[ensure-schema] Schema is up to date")


def _ensure_schema_columns() -> None:
    """Add every column the models declare but the DB lacks (idempotent)."""
    dialect = sqlite_dialect()
    inspector = inspect(db.engine)
    existing_tables = set(inspector.get_table_names())
    with db.engine.begin() as conn:
        for table in db.Model.metadata.sorted_tables:
            if table.name not in existing_tables:
                continue
            existing_columns = {column["name"] for column in inspector.get_columns(table.name)}
            for column in table.columns:
                if column.name in existing_columns:
                    continue
                _add_missing_column(conn, dialect, table, column)


def _add_missing_column(conn, dialect, table, column) -> None:
    """Emit the ``ALTER TABLE ... ADD COLUMN`` for one missing column.

    A missing column is auto-added when it is nullable or carries a
    ``server_default``; otherwise a constant default is synthesized by type
    (``Boolean/Integer → 0``, ``Float/Numeric → 0.0``, ``String/Text → ''``);
    exotic non-nullable types are added nullable with a logged warning. A
    missing column carrying UNIQUE/PK/FK cannot be added via SQLite
    ``ADD COLUMN`` — fail-loud: the developer fixes the model, never an ops step.
    """
    name = f"{table.name}.{column.name}"
    if column.primary_key or column.unique or column.foreign_keys:
        raise EnsureSchemaError(name)
    if column.nullable or column.server_default is not None:
        clause = str(CreateColumn(column).compile(dialect=dialect))
    else:
        literal = _synthesized_default_literal(column, dialect)
        if literal is None:
            print(
                f"[ensure-schema] WARNING: {name} is NOT NULL {column.type} with no "
                "server_default; adding it nullable. Set a server_default in the model."
            )
            clause = f"{column.name} {column.type.compile(dialect=dialect)}"
        else:
            clause = (
                f"{column.name} {column.type.compile(dialect=dialect)} NOT NULL DEFAULT {literal}"
            )
    print(f"[ensure-schema] ADD COLUMN {name}")
    conn.execute(db.text(f"ALTER TABLE {table.name} ADD COLUMN {clause}"))


def _synthesized_default_literal(column, dialect) -> str | None:
    """Constant literal for a NOT NULL column with no server_default, by type.

    Returns ``None`` for exotic types (DateTime, etc.) — the caller then adds
    the column nullable with a warning instead of failing the whole boot.
    """
    default: int | float | str
    if isinstance(column.type, (Boolean, Integer)):
        default = 0
    elif isinstance(column.type, (Float, Numeric)):
        default = 0.0
    elif isinstance(column.type, (String, Text)):
        default = ""
    else:
        return None
    return column.type.literal_processor(dialect)(default)


# Boot-time schema self-heal: the deploy webhook's `flask db` step is the only
# migration trigger, and it silently succeeds without actually migrating when
# the CLI group was missing. Run ensure_schema() on every boot so model↔DB drift
# (e.g. users.deleted added by PR #237) never surfaces as "no such column" 500s.
# Skip when SE_AUTO_MIGRATE=0 (tests / import pipeline).
#
# Fault-tolerant on purpose: gunicorn imports this module in every worker; a
# concurrent ensure_schema() (backup copy + create_all + FTS rebuild) can hit
# SQLite "database is locked" under multi-worker boot. The webhook's `flask db
# upgrade` runs first and performs the migration, so a here failure must never
# take down the app — log and continue.
if os.environ.get("SE_AUTO_MIGRATE", "1") != "0":
    try:
        with app.app_context():
            ensure_schema()
    except Exception:
        import logging as _logging

        _logging.getLogger("flask_se").exception("boot-time ensure_schema failed")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "init":
            with app.app_context():
                init_db()
        elif sys.argv[1] == "migrate":
            with app.app_context():
                ensure_schema()
    else:
        from werkzeug.serving import run_simple

        run_simple("127.0.0.1", 5000, app, use_debugger=True, use_reloader=True)

# SPDX-License-Identifier: Apache-2.0

import os
import sys
from datetime import UTC, date
from pathlib import Path

__all__ = ["app", "db", "scheduler"]

import markdown as _markdown
import nh3
from dateutil import tz
from flask import Flask
from flask_frozen import Freezer
from flask_migrate import Migrate
from flask_wtf import CSRFProtect
from markupsafe import Markup

import flask_se_theses
from flask_se_admin import (
    AdminIndexView,
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
    SECRET_KEY,
    SECRET_KEY_THESIS,
    SQLITE_DATABASE_PATH,
    SQLITE_DATABASE_URI,
    site_deploy_date,
)
from flask_se_diplomas import register_routes as register_diplomas_routes
from flask_se_internships import register_routes as register_internships_routes
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
    CurrentThesis,
    DiplomaThemes,
    Posts,
    Staff,
    SummerSchool,
    Thesis,
    Users,
    db,
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
migrate = Migrate()
freezer = Freezer()
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

    # Freezer config
    app.config["FREEZER_RELATIVE_URLS"] = True
    app.config["FREEZER_DESTINATION"] = "../_flask_freezed"
    app.config["FREEZER_IGNORE_MIMETYPE_WARNINGS"] = True

    # SQLAlchemy config
    # Absolute DB path (databases/se.db) — matches init_db(); CWD-independent.
    # Ensure the directory exists so SQLAlchemy can open the file on first run
    # (init_db() creates it too, but the dev server / Docker may connect first).
    Path(SQLITE_DATABASE_PATH).mkdir(parents=True, exist_ok=True)
    app.config["SQLALCHEMY_DATABASE_URI"] = SQLITE_DATABASE_URI
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
    app.config["SECRET_KEY"] = SECRET_KEY
    app.config["SESSION_COOKIE_NAME"] = "se_session"

    # Secure session cookies: HTTPS-only + SameSite. Dev runs on plain HTTP, so
    # SECURE is toggled by an env flag (production deploys set it).
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SECURE"] = os.environ.get("SE_COOKIE_SECURE", "1") == "1"
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

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
    db.init_app(app)
    migrate.init_app(app, db, render_as_batch=True)
    freezer.init_app(app)
    login_manager.init_app(app)

    app.template_filter("markdown")(render_markdown)
    app.template_filter("safe_html")(render_safe_html)
    app.template_filter("datatime_convert")(datetime_convert)

    def _inject_template_globals() -> dict[str, str | int]:
        return {"current_year": date.today().year, "ASSET_VERSION": site_deploy_date()}

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
    SeAdminModelViewCurrentThesis(app, CurrentThesis, endpoint="currentthesis")


def create_app(
    config_overrides: dict[str, object] | None = None,
    start_scheduler: bool | None = None,
) -> Flask:
    """Application factory.

    ``app = create_app()`` at module level keeps the singleton semantics the
    WSGI entry point, the import pipeline (extract_text/thesesImport) and the
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
    _init_admin_views(app)
    # Default: read SE_START_SCHEDULER (production leaves it unset → jobs run).
    # conftest sets it to "0" before importing so the suite never fires jobs.
    # The import pipeline (extract_text.py, thesesImport.py) imports the app
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


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "build":
            freezer.freeze()
        elif sys.argv[1] == "init":
            with app.app_context():
                init_db()
    else:
        from werkzeug.serving import run_simple

        run_simple("127.0.0.1", 5000, app, use_debugger=True, use_reloader=True)

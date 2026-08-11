# SPDX-License-Identifier: Apache-2.0
# pyright: reportUnusedFunction=false
# Route view functions registered via decorators inside _register_* helpers;
# basedpyright cannot see the decorator registration and would flag them unused.

import os
import sys
from datetime import UTC, datetime
from pathlib import Path

__all__ = ["app", "db"]

import markdown as _markdown
from apscheduler.schedulers.background import BackgroundScheduler
from dateutil import tz
from flask import Flask, make_response, redirect, render_template, url_for
from flask_frozen import Freezer
from flask_migrate import Migrate
from flask_wtf import CSRFProtect

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
from flask_se_auth import (
    login_manager,
)
from flask_se_auth import (
    register_routes as register_auth_routes,
)
from flask_se_bachelor import (
    bachelor_admission,
    bachelor_application,
    bachelor_programming_technology,
    bachelor_score_info,
    bachelor_software_engineering,
)
from flask_se_config import (
    SECRET_KEY,
    SECRET_KEY_THESIS,
    SQLITE_DATABASE_PATH,
    SQLITE_DATABASE_URI,
    get_hours_since,
    plural_hours,
)
from flask_se_diplomas import register_routes as register_diplomas_routes
from flask_se_internships import register_routes as register_internships_routes
from flask_se_news import register_routes as register_news_routes
from flask_se_practice import register_routes as register_practice_routes
from flask_se_practice_admin import register_routes as register_practice_admin_routes
from flask_se_practice_staff import register_routes as register_practice_staff_routes
from flask_se_review import register_routes as register_review_routes
from flask_se_scholarships import register_routes as register_scholarships_routes
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

# Extension singletons: init_app() is called inside create_app() so the same
# objects can back multiple app instances (production WSGI + tests).
migrate = Migrate()
freezer = Freezer()
csrf = CSRFProtect()
scheduler = BackgroundScheduler(timezone="UTC")

zero_days_ago = (datetime.now()).date().isoformat()


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
def render_markdown(text: str) -> str:
    return _markdown.markdown(text, extensions=["tables"])


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
    app.template_filter("datatime_convert")(datetime_convert)


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


def _register_static_pages(app: Flask) -> None:
    """Public static pages and the 404 handler."""

    @app.route("/")
    def index():
        news = Posts.query.filter(Posts.type_id > 0).order_by(Posts.rank.desc()).limit(10).all()

        ages = [plural_hours(int(get_hours_since(post.created_on))) for post in news]

        return render_template("index.html", news=news, ages=ages, score_info=bachelor_score_info)

    @app.route("/index.html")
    def index_html():
        return redirect(url_for("index"))

    @app.errorhandler(404)
    def page_not_found(e):  # noqa: ARG001
        # note that we set the 404 status explicitly
        return render_template("404.html"), 404

    @app.route("/404.html")
    def status_404():
        return render_template("404.html")

    @app.route("/contacts.html")
    def contacts():
        return render_template("contacts.html")

    @app.route("/students/index.html")
    def students():
        return render_template("students.html")

    @app.route("/students/scholarships.html")
    def scholarships():
        return render_template("students_scholarships.html")


def _register_content_pages(app: Flask) -> None:
    """Content-driven static pages (research directions, staff, programs)."""

    @app.route("/research-directions")
    def research_directions():
        directions = [
            "Языки программирования: трансляторы, реинжиниринг, синтаксический и статический анализ (Я.А. Кириленко, Д.Ю.Булычев, Д.С.Косарев, С.В.Григорьев, Д.В.Луцив), функциональное, логическое, реляционное программирование (Д.Ю.Булычев)",
            "Верификация, символьное исполнение программ (Д.Ю.Булычев, Д.А.Мордвинов)",
            "Разработка приложений для архитектуры RISC-V (К.К.Смирнов, С.В.Григорьев)",
            "Технология программирования: визуальное моделирование ПО, предметно-ориентированное моделирование, DSLs, анализ Software Data, разработка технической документации (Д.В. Кознов, Д.В. Луцив)",
            "Управление данными: архитектура данных предприятия, данные сетевых устройств, мастер-данные (Д.В.Кознов), системы хранения данных, дедупликация, менеджеры томов, SPDK (В.И.Гориховский, А.И.Васенина)",
            "Статистика, машинное обучение (В.И.Гориховский, С.В.Григорьев, К.К.Смирнов)",
            "Задачи на графах, вычислительные задачи, алгоритмы для GPU (С.В. Григорьев)",
            "Телекоммуникации (И.В.Зеленчук, Д.В.Кознов)",
            "Стохастическая оптимизация, рандомизированные алгоритмы, квантовые компьютеры (О.Н.Граничин, С.С.Сысоев)",
            "Компьютерное зрение, машинное обучение, фотограмметрия (М.Н.Смирнов)",
        ]
        return render_template("research_directions.html", directions=directions)

    app.add_url_rule("/bachelor/admission.html", view_func=bachelor_admission)
    app.add_url_rule(
        "/bachelor/programming-technology.html", view_func=bachelor_programming_technology
    )
    app.add_url_rule("/bachelor/software-engineering.html", view_func=bachelor_software_engineering)
    app.add_url_rule("/bachelor/application.html", view_func=bachelor_application)

    @app.route("/master/information-systems-administration.html")
    def master_information_systems_administration():
        return render_template("master_information-systems-administration.html")

    @app.route("/master/software-engineering.html")
    def master_software_engineering():
        return render_template("master_software-engineering.html")

    @app.route("/department/staff.html")
    def department_staff():
        records = Staff.query.filter_by(still_working=True).all()
        staff = []

        for s in records:
            position = s.position
            if s.science_degree:
                position = position + ", " + s.science_degree

            staff.append(
                {
                    "name": s.user.get_name(),
                    "position": position,
                    "contacts": s.official_email,
                    "avatar": s.user.avatar_uri,
                    "id": s.id,
                },
            )

        return render_template("department_staff.html", staff=staff)

    @app.route("/frequently-asked-questions.html")
    def frequently_asked_questions():
        return render_template("frequently_asked_questions.html")

    @app.route("/nooffer")
    def nooffer():
        return render_template("nooffer.html")


def _register_sitemap(app: Flask) -> None:
    @app.route("/sitemap.xml", methods=["GET"])
    @app.route("/Sitemap.xml", methods=["GET"])
    def sitemap():
        """Generate sitemap.xml. Makes a list of urls and date modified."""
        pages = []
        skip_pages = [
            "/nooffer",
            "/fetch_theses",
            "/Sitemap.xml",
            "/sitemap.xml",
            "/404.html",
            "/post_theses",
            "/theses_tmp.html",
            "/theses_delete_tmp",
            "/theses_add_tmp",
            "/thesis_download",
            "/thesis_card",
            "/google_callback",
            "/vk_callback",
        ]

        # static pages
        for rule in app.url_map.iter_rules():
            if rule.rule in skip_pages:
                continue

            # Skip admin URL
            if "admin/" in rule.rule:
                continue

            if "GET" in (rule.methods or set()) and len(rule.arguments) == 0:
                pages.append(["https://se.math.spbu.ru" + str(rule.rule), zero_days_ago])

        sitemap_xml = render_template("sitemap_template.xml", pages=pages)
        response = make_response(sitemap_xml)
        response.headers["Content-Type"] = "application/xml"
        return response


LEGACY_REDIRECTS = {
    "/auth/login": "login_index",
    "/auth/profile": "user_profile",
    "/auth/logout": "logout",
    "/department_staff": "department_staff",
    "/department_staff.html": "department_staff",
    "/students.html": "students",
    "/students_scholarships.html": "scholarships",
    "/frequently_asked_questions.html": "frequently_asked_questions",
    "/news.html": "list_news",
    "/staff.html": "department_staff",
    "/faq": "frequently_asked_questions",
    "/scholarships": "scholarships",
    "/internships": "internships_index",
    "/practice/student/index.html": "practice_index",
    "/summer_school.html": "summer_school_list",
    "/master_software-engineering.html": "master_software_engineering",
    "/master_information-systems-administration.html": "master_information_systems_administration",
    "/research.html": "research_directions",
    "/directions.html": "research_directions",
    "/thesis_review": "thesis_review_index",
    "/thesis_review/index.html": "thesis_review_index",
}


def _register_legacy_redirects(app: Flask) -> None:
    """Legacy URL redirects (301) — preserve backwards compatibility."""
    for legacy_path, endpoint in LEGACY_REDIRECTS.items():
        ep_name = "legacy_" + legacy_path.strip("/").replace("/", "_").replace(".", "_").replace(
            "-", "_"
        )
        app.add_url_rule(
            legacy_path,
            endpoint=ep_name,
            view_func=lambda endpoint=endpoint: redirect(url_for(endpoint), 301),
        )


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


def _configure_scheduler(start_scheduler: bool) -> None:
    """Register APScheduler jobs on the module-level ``scheduler``.

    Start is explicit: ``create_app`` defaults to off, so the import pipeline
    (extract_text.py, thesesImport.py) and the test suite never fire jobs.
    Production (wsgi.py) sets ``SE_START_SCHEDULER=1`` in its unit, or the
    callers may pass ``start_scheduler=True`` explicitly.
    """
    scheduler.add_job(
        id="RecalculatePostRank",
        func=recalculate_post_rank_wrapper,
        trigger="interval",
        seconds=3600,
    )
    scheduler.add_job(
        id="SendMailNotification",
        func=notification_send_mail_wrapper,
        trigger="interval",
        seconds=10,
    )
    scheduler.add_job(
        id="SendDiplomaThemesOnReviewNotification",
        func=notification_send_diploma_themes_on_review_wrapper,
        trigger="interval",
        seconds=86400,
    )
    if start_scheduler:
        scheduler.start()


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
    _register_static_pages(app)
    _register_content_pages(app)
    _register_sitemap(app)
    _register_legacy_redirects(app)
    _init_admin_views(app)
    # Default: read SE_START_SCHEDULER (production leaves it unset → jobs run).
    # conftest sets it to "0" before importing so the suite never fires jobs.
    # The import pipeline (extract_text.py, thesesImport.py) imports the app
    # without starting the scheduler either way.
    if start_scheduler is None:
        start_scheduler = os.environ.get("SE_START_SCHEDULER", "1") == "1"
    _configure_scheduler(start_scheduler)

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

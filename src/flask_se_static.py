# SPDX-License-Identifier: Apache-2.0
# pyright: reportUnusedFunction=false
# Route view functions registered via decorators inside _register_* helpers;
# basedpyright cannot see the decorator registration and would flag them unused.

import logging

from flask import Flask, redirect, render_template, request, url_for

from flask_se_bachelor import (
    bachelor_admission,
    bachelor_application,
    bachelor_programming_technology,
    bachelor_score_info,
    bachelor_software_engineering,
)
from flask_se_config import get_hours_since, plural_hours
from se_models import Posts, Staff

log = logging.getLogger("flask_se.static")

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
    # Section directory indexes: agents/crawlers that traverse directories get
    # a 301 to the section's representative page instead of a 404.
    "/bachelor/": "bachelor_software_engineering",
    "/master/": "master_software_engineering",
    "/department/": "department_staff",
    "/students/": "students",
}


def register_static_pages(app: Flask) -> None:
    """Public static pages and the 404 handler."""

    @app.route("/")
    def index():
        news = Posts.query.filter(Posts.type_id > 0).order_by(Posts.rank.desc()).limit(10).all()

        ages = [plural_hours(int(get_hours_since(post.created_on))) for post in news]

        return render_template("index.html", news=news, ages=ages, score_info=bachelor_score_info)

    @app.route("/index.html")
    def index_html():
        return redirect(url_for("index"), 301)

    @app.route("/.well-known/llms.txt")
    def well_known_llms():
        # Some tooling probes only the .well-known path; single-source 301 to
        # the canonical root llms.txt (served from static/ at site root).
        return redirect(url_for("static", filename="llms.txt"), 301)

    @app.route("/security.txt")
    def security_txt():
        # RFC 9116 root alias -> canonical .well-known location.
        return redirect("/.well-known/security.txt", 301)

    @app.errorhandler(404)
    def page_not_found(e):  # noqa: ARG001
        # note that we set the 404 status explicitly
        return render_template("404.html"), 404

    @app.errorhandler(500)
    def internal_error(e):
        exc = getattr(e, "original_exception", e)
        log.error("500 on %s", request.url, exc_info=(type(exc), exc, exc.__traceback__))
        return render_template("500.html"), 500

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


def register_content_pages(app: Flask) -> None:
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

    @app.route("/privacy.html")
    def privacy():
        return render_template("privacy.html")


def register_legacy_redirects(app: Flask) -> None:
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

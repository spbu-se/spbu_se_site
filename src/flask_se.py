# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0

import sys
from datetime import UTC, datetime

__all__ = ["app", "db", "whooshee"]

from dateutil import tz
from flask import Flask, make_response, redirect, render_template, url_for
from flask_admin import Admin
from flask_admin.theme import Bootstrap4Theme
from flask_apscheduler import APScheduler
from flask_frozen import Freezer
from flask_migrate import Migrate
from flask_simplemde import SimpleMDE
from flaskext.markdown import Markdown

import flask_se_theses
from flask_se_admin import (
    SeAdminIndexView,
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
    google_callback,
    google_login,
    login_index,
    login_manager,
    logout,
    password_recovery,
    register_basic,
    upload_avatar,
    user_profile,
    vk_callback,
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
    SQLITE_DATABASE_NAME,
    SQLITE_DATABASE_PATH,
    WHOOSHEE_DIR,
    get_hours_since,
    plural_hours,
)
from flask_se_diplomas import (
    add_user_theme,
    archive_theme,
    delete_theme,
    diplomas_index,
    edit_user_theme,
    fetch_themes,
    get_theme,
    unarchive_theme,
    user_diplomas_index,
)
from flask_se_internships import (
    add_internship,
    delete_internship,
    fetch_internships,
    internships_index,
    old_internships_index,
    page_internship,
    update_internship,
)
from flask_se_news import delete_post, get_post, list_news, post_vote, submit_post
from flask_se_practice import (
    practice_add_new_report,
    practice_choosing_topic,
    practice_data_for_practice,
    practice_edit_theme,
    practice_goals_tasks,
    practice_guide,
    practice_index,
    practice_new_thesis,
    practice_preparation,
    practice_thesis_defense,
    practice_workflow,
)
from flask_se_practice_admin import (
    archive_thesis,
    choose_area_and_worktype_admin,
    finished_thesises_admin,
    index_admin,
    thesis_admin,
)
from flask_se_practice_staff import (
    finished_thesises_staff,
    index_staff,
    reports_staff,
    thesis_staff,
)
from flask_se_practice_yandex_disk import yandex_code
from flask_se_review import (
    delete_thesis_on_review,
    edit_thesis_on_review,
    fetch_thesis_on_review,
    review_become_thesis_reviewer_ask,
    review_become_thesis_reviewer_confirm,
    review_result_thesis_on_review,
    review_submit_review,
    review_thesis_on_review,
    submit_thesis_on_review,
    thesis_review_index,
)
from flask_se_scholarships import (
    get_scholarships_1,
    get_scholarships_2,
    get_scholarships_3,
    get_scholarships_4,
    get_scholarships_5,
    get_scholarships_6,
    get_scholarships_7,
    get_scholarships_8,
    get_scholarships_9,
    get_scholarships_10,
    get_scholarships_11,
    get_scholarships_12,
    get_scholarships_13,
)
from flask_se_summer_schools import create_summer_school_view, summer_school_list
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
    whooshee,
)
from se_sendmail import (
    notification_send_diploma_themes_on_review,
    notification_send_mail,
)

app = Flask(
    __name__,
    static_url_path="",
    static_folder="static",
    template_folder="templates",
    instance_path=SQLITE_DATABASE_PATH,
)

# Flask configs
app.config["APPLICATION_ROOT"] = "/"

# Freezer config
app.config["FREEZER_RELATIVE_URLS"] = True
app.config["FREEZER_DESTINATION"] = "../_flask_freezed"
app.config["FREEZER_IGNORE_MIMETYPE_WARNINGS"] = True

# SQLAlchimy config
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + SQLITE_DATABASE_NAME
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.config["SECRET_KEY"] = SECRET_KEY
app.config["SESSION_COOKIE_NAME"] = "se_session"

# Secret for API
app.config["SECRET_KEY_THESIS"] = SECRET_KEY_THESIS

# Basic auth config
app.config["BASIC_AUTH_USERNAME"] = "se_staff"
app.config["BASIC_AUTH_PASSWORD"] = app.config["SECRET_KEY_THESIS"]


# App add_url_rule
# Login
app.add_url_rule("/login.html", methods=["GET", "POST"], view_func=login_index)
app.add_url_rule("/register_basic.html", methods=["GET", "POST"], view_func=register_basic)
app.add_url_rule("/password_recovery.html", methods=["GET", "POST"], view_func=password_recovery)
app.add_url_rule("/profile.html", methods=["GET", "POST"], view_func=user_profile)
app.add_url_rule("/upload_avatar", methods=["GET", "POST"], view_func=upload_avatar)
app.add_url_rule("/logout", methods=["GET"], view_func=logout)
app.add_url_rule("/vk_callback", methods=["GET"], view_func=vk_callback)
app.add_url_rule("/google_login", methods=["GET"], view_func=google_login)
app.add_url_rule("/google_callback", methods=["GET"], view_func=google_callback)


# Theses
app.add_url_rule("/theses.html", view_func=flask_se_theses.theses_search)
app.add_url_rule("/fetch_theses", view_func=flask_se_theses.fetch_theses)
app.add_url_rule("/post_theses", methods=["GET", "POST"], view_func=flask_se_theses.post_theses)
app.add_url_rule("/theses_tmp.html", view_func=flask_se_theses.theses_tmp)
app.add_url_rule("/theses_delete_tmp", view_func=flask_se_theses.theses_delete_tmp)
app.add_url_rule("/theses_add_tmp", view_func=flask_se_theses.theses_add_tmp)
app.add_url_rule("/thesis_download", view_func=flask_se_theses.download_thesis)


# News
app.add_url_rule("/news/", view_func=list_news)
app.add_url_rule("/news/index.html", view_func=list_news)
app.add_url_rule("/news/item.html", view_func=get_post)
app.add_url_rule("/news/submit.html", methods=["GET", "POST"], view_func=submit_post)
app.add_url_rule("/news/post_vote", methods=["GET", "POST"], view_func=post_vote)
app.add_url_rule("/news/delete", view_func=delete_post)


# Scholarships
app.add_url_rule("/scholarships/1.html", view_func=get_scholarships_1)
app.add_url_rule("/scholarships/2.html", view_func=get_scholarships_2)
app.add_url_rule("/scholarships/3.html", view_func=get_scholarships_3)
app.add_url_rule("/scholarships/4.html", view_func=get_scholarships_4)
app.add_url_rule("/scholarships/5.html", view_func=get_scholarships_5)
app.add_url_rule("/scholarships/6.html", view_func=get_scholarships_6)
app.add_url_rule("/scholarships/7.html", view_func=get_scholarships_7)
app.add_url_rule("/scholarships/8.html", view_func=get_scholarships_8)
app.add_url_rule("/scholarships/9.html", view_func=get_scholarships_9)
app.add_url_rule("/scholarships/10.html", view_func=get_scholarships_10)
app.add_url_rule("/scholarships/11.html", view_func=get_scholarships_11)
app.add_url_rule("/scholarships/12.html", view_func=get_scholarships_12)
app.add_url_rule("/scholarships/13.html", view_func=get_scholarships_13)


# Diplomas
app.add_url_rule("/diplomas/", view_func=diplomas_index)
app.add_url_rule("/diplomas/index.html", view_func=diplomas_index)
app.add_url_rule("/diplomas/theme.html", view_func=get_theme)
app.add_url_rule("/diplomas/add_theme.html", methods=["GET", "POST"], view_func=add_user_theme)
app.add_url_rule("/diplomas/user_themes.html", view_func=user_diplomas_index)
app.add_url_rule("/diplomas/delete_theme.html", view_func=delete_theme)
app.add_url_rule("/diplomas/edit_theme.html", methods=["GET", "POST"], view_func=edit_user_theme)
app.add_url_rule("/diplomas/fetch_themes", view_func=fetch_themes)
app.add_url_rule("/diplomas/archive_theme", view_func=archive_theme)
app.add_url_rule("/diplomas/unarchive_theme", view_func=unarchive_theme)


# Review thesis
app.add_url_rule("/review/", methods=["GET"], view_func=thesis_review_index)
app.add_url_rule("/review/index.html", methods=["GET"], view_func=thesis_review_index)
app.add_url_rule("/review/submit", methods=["GET", "POST"], view_func=submit_thesis_on_review)
app.add_url_rule("/review/edit", methods=["GET", "POST"], view_func=edit_thesis_on_review)
app.add_url_rule("/review/delete", methods=["GET"], view_func=delete_thesis_on_review)
app.add_url_rule("/review/review", methods=["GET"], view_func=review_thesis_on_review)
app.add_url_rule("/review/reviewed", methods=["GET", "POST"], view_func=review_submit_review)
app.add_url_rule("/review/review_result", methods=["GET"], view_func=review_result_thesis_on_review)
app.add_url_rule(
    "/review/fetch_thesis_on_review", methods=["GET"], view_func=fetch_thesis_on_review
)
app.add_url_rule(
    "/review/become_thesis_reviewer",
    methods=["GET"],
    view_func=review_become_thesis_reviewer_ask,
)
app.add_url_rule(
    "/review/become_thesis_reviewer_confirm",
    methods=["GET"],
    view_func=review_become_thesis_reviewer_confirm,
)


# Internships
app.add_url_rule("/internships/index", methods=["GET"], view_func=old_internships_index)
app.add_url_rule(
    "/internships/internships_index.html", methods=["GET"], view_func=internships_index
)
app.add_url_rule("/internships/fetch_internships", methods=["GET"], view_func=fetch_internships)
app.add_url_rule("/internships/add", methods=["GET", "POST"], view_func=add_internship)
app.add_url_rule("/internships/<int:id>", methods=["GET", "POST"], view_func=page_internship)
app.add_url_rule("/internships/<int:id>/delete", view_func=delete_internship)
app.add_url_rule(
    "/internships/<int:id>/update", methods=["GET", "POST"], view_func=update_internship
)


# Practice
app.add_url_rule("/practice", methods=["GET", "POST"], view_func=practice_index)
app.add_url_rule("/practice/", methods=["GET", "POST"], view_func=practice_index)
app.add_url_rule("/practice/guide/", methods=["GET"], view_func=practice_guide)
app.add_url_rule("/practice/new/", methods=["GET", "POST"], view_func=practice_new_thesis)
app.add_url_rule(
    "/practice/data_for_practice/",
    methods=["GET", "POST"],
    view_func=practice_data_for_practice,
)
app.add_url_rule(
    "/practice/choosing_topic/",
    methods=["GET", "POST"],
    view_func=practice_choosing_topic,
)
app.add_url_rule("/practice/edit_theme/", methods=["GET", "POST"], view_func=practice_edit_theme)
app.add_url_rule("/practice/goals_tasks/", methods=["GET", "POST"], view_func=practice_goals_tasks)
app.add_url_rule(
    "/practice/add_new_report/",
    methods=["GET", "POST"],
    view_func=practice_add_new_report,
)
app.add_url_rule("/practice/workflow/", methods=["GET", "POST"], view_func=practice_workflow)
app.add_url_rule(
    "/practice/preparation_for_defense/",
    methods=["GET", "POST"],
    view_func=practice_preparation,
)
app.add_url_rule("/practice/defense/", methods=["GET"], view_func=practice_thesis_defense)

# Practice staff
app.add_url_rule("/practice_staff", methods=["GET"], view_func=index_staff)
app.add_url_rule("/practice_staff/", methods=["GET"], view_func=index_staff)
app.add_url_rule("/practice_staff/thesis/", methods=["GET", "POST"], view_func=thesis_staff)
app.add_url_rule("/practice_staff/reports/", methods=["GET", "POST"], view_func=reports_staff)
app.add_url_rule(
    "/practice_staff/finished_thesises/",
    methods=["GET"],
    view_func=finished_thesises_staff,
)

# Practice admin
app.add_url_rule("/practice_admin", methods=["GET", "POST"], view_func=index_admin)
app.add_url_rule("/practice_admin/", methods=["GET", "POST"], view_func=index_admin)
app.add_url_rule(
    "/practice_admin/choose_area_worktype",
    methods=["GET"],
    view_func=choose_area_and_worktype_admin,
)
app.add_url_rule(
    "/practice_admin/finished_thesises",
    methods=["GET"],
    view_func=finished_thesises_admin,
)
app.add_url_rule("/practice_admin/thesis", methods=["GET", "POST"], view_func=thesis_admin)
app.add_url_rule("/practice_admin/yandex_code", methods=["GET"], view_func=yandex_code)
app.add_url_rule(
    "/practice_admin/thesis_to_archive",
    methods=["GET", "POST"],
    view_func=archive_thesis,
)


# Summer schools
app.add_url_rule("/summer_school_2021.html", view_func=create_summer_school_view(2021))
app.add_url_rule("/summer_school_2022.html", view_func=create_summer_school_view(2022))
app.add_url_rule("/summer_school_2024.html", view_func=create_summer_school_view(2024))
app.add_url_rule("/summer_school_2026.html", view_func=create_summer_school_view(2026))
app.add_url_rule("/summer_school_list.html", view_func=summer_school_list)

# Init Database
db.app = app  # pyright: ignore[reportAttributeAccessIssue]
db.init_app(app)
app.config["WHOOSHEE_DIR"] = WHOOSHEE_DIR
whooshee.init_app(app)

# Init Migrate
migrate = Migrate(app, db, render_as_batch=True)

app.logger.debug("SECRET_KEY_THESIS: %s", str(app.config["SECRET_KEY_THESIS"]))

# Init Freezer
freezer = Freezer(app)

# Init Sitemap
zero_days_ago = (datetime.now()).date().isoformat()

# Init LoginManager
login_manager.init_app(app)

# Init markdown
Markdown(app, extensions=["tables"])


def recalculate_post_rank_wrapper():
    with app.app_context():
        recalculate_post_rank()


def notification_send_mail_wrapper():
    with app.app_context():
        notification_send_mail()


def notification_send_diploma_themes_on_review_wrapper():
    with app.app_context():
        notification_send_diploma_themes_on_review()


# Init APScheduler
app.config["SCHEDULER_TIMEZONE"] = "UTC"
scheduler = APScheduler()
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
scheduler.start()

# Init Flask-admin
admin = Admin(app, index_view=SeAdminIndexView(), theme=Bootstrap4Theme())
# Add views to the Flask-admin
admin.add_view(SeAdminModelViewUsers(Users, db.session))
admin.add_view(SeAdminModelViewStaff(Staff, db.session))
admin.add_view(SeAdminModelViewThesis(Thesis, db.session))
admin.add_view(SeAdminModelViewSummerSchool(SummerSchool, db.session))
admin.add_view(SeAdminModelViewNews(Posts, db.session))
admin.add_view(SeAdminModelViewDiplomaThemes(DiplomaThemes, db.session, endpoint="diplomathemes"))
admin.add_view(
    SeAdminModelViewReviewDiplomaThemes(
        DiplomaThemes,
        db.session,
        endpoint="reviewdiplomathemes",
        name="Review DiplomaThemes",
    )
)
admin.add_view(SeAdminModelViewCurrentThesis(CurrentThesis, db.session))

# Init SimpleMDE
app.config["SIMPLEMDE_JS_IIFE"] = True
app.config["SIMPLEMDE_USE_CDN"] = False
SimpleMDE(app)


@app.template_filter("datatime_convert")
def datetime_convert(value, format="%d.%m.%Y %H:%M"):
    return value.replace(tzinfo=UTC).astimezone(tz.tzlocal()).strftime(format)


# Flask routes goes
@app.route("/")
def index():
    ages = []
    news = Posts.query.filter(Posts.type_id > 0).order_by(Posts.rank.desc()).limit(10).all()

    for post in news:
        ages.append(plural_hours(int(get_hours_since(post.created_on))))

    return render_template("index.html", news=news, ages=ages, score_info=bachelor_score_info)


@app.route("/index.html")
def index_html():
    return redirect(url_for("index"))


@app.route("/research-directions")
def research_directions():
    directions = [
        "РЇР·С‹РєРё РїСЂРѕРіСЂР°РјРјРёСЂРѕРІР°РЅРёСЏ: С‚СЂР°РЅСЃР»СЏС‚РѕСЂС‹, СЂРµРёРЅР¶РёРЅРёСЂРёРЅРі, СЃРёРЅС‚Р°РєСЃРёС‡РµСЃРєРёР№ Рё СЃС‚Р°С‚РёС‡РµСЃРєРёР№ Р°РЅР°Р»РёР· (РЇ.Рђ. РљРёСЂРёР»РµРЅРєРѕ, Р”.Р®.Р‘СѓР»С‹С‡РµРІ, Р”.РЎ.РљРѕСЃР°СЂРµРІ, РЎ.Р’.Р“СЂРёРіРѕСЂСЊРµРІ, Р”.Р’.Р›СѓС†РёРІ), С„СѓРЅРєС†РёРѕРЅР°Р»СЊРЅРѕРµ, Р»РѕРіРёС‡РµСЃРєРѕРµ, СЂРµР»СЏС†РёРѕРЅРЅРѕРµ РїСЂРѕРіСЂР°РјРјРёСЂРѕРІР°РЅРёРµ (Р”.Р®.Р‘СѓР»С‹С‡РµРІ)",
        "Р’РµСЂРёС„РёРєР°С†РёСЏ, СЃРёРјРІРѕР»СЊРЅРѕРµ РёСЃРїРѕР»РЅРµРЅРёРµ РїСЂРѕРіСЂР°РјРј (Р”.Р®.Р‘СѓР»С‹С‡РµРІ, Р”.Рђ.РњРѕСЂРґРІРёРЅРѕРІ)",
        "Р Р°Р·СЂР°Р±РѕС‚РєР° РїСЂРёР»РѕР¶РµРЅРёР№ РґР»СЏ Р°СЂС…РёС‚РµРєС‚СѓСЂС‹ RISC-V (Рљ.Рљ.РЎРјРёСЂРЅРѕРІ, РЎ.Р’.Р“СЂРёРіРѕСЂСЊРµРІ)",
        "РўРµС…РЅРѕР»РѕРіРёСЏ РїСЂРѕРіСЂР°РјРјРёСЂРѕРІР°РЅРёСЏ: РІРёР·СѓР°Р»СЊРЅРѕРµ РјРѕРґРµР»РёСЂРѕРІР°РЅРёРµ РџРћ, РїСЂРµРґРјРµС‚РЅРѕ-РѕСЂРёРµРЅС‚РёСЂРѕРІР°РЅРЅРѕРµ РјРѕРґРµР»РёСЂРѕРІР°РЅРёРµ, DSLs, Р°РЅР°Р»РёР· Software Data, СЂР°Р·СЂР°Р±РѕС‚РєР° С‚РµС…РЅРёС‡РµСЃРєРѕР№ РґРѕРєСѓРјРµРЅС‚Р°С†РёРё (Р”.Р’. РљРѕР·РЅРѕРІ, Р”.Р’. Р›СѓС†РёРІ)",
        "РЈРїСЂР°РІР»РµРЅРёРµ РґР°РЅРЅС‹РјРё: Р°СЂС…РёС‚РµРєС‚СѓСЂР° РґР°РЅРЅС‹С… РїСЂРµРґРїСЂРёСЏС‚РёСЏ, РґР°РЅРЅС‹Рµ СЃРµС‚РµРІС‹С… СѓСЃС‚СЂРѕР№СЃС‚РІ, РјР°СЃС‚РµСЂ-РґР°РЅРЅС‹Рµ (Р”.Р’.РљРѕР·РЅРѕРІ), СЃРёСЃС‚РµРјС‹ С…СЂР°РЅРµРЅРёСЏ РґР°РЅРЅС‹С…, РґРµРґСѓРїР»РёРєР°С†РёСЏ, РјРµРЅРµРґР¶РµСЂС‹ С‚РѕРјРѕРІ, SPDK (Р’.Р.Р“РѕСЂРёС…РѕРІСЃРєРёР№, Рђ.Р.Р’Р°СЃРµРЅРёРЅР°)",
        "РЎС‚Р°С‚РёСЃС‚РёРєР°, РјР°С€РёРЅРЅРѕРµ РѕР±СѓС‡РµРЅРёРµ (Р’.Р.Р“РѕСЂРёС…РѕРІСЃРєРёР№, РЎ.Р’.Р“СЂРёРіРѕСЂСЊРµРІ, Рљ.Рљ.РЎРјРёСЂРЅРѕРІ)",
        "Р—Р°РґР°С‡Рё РЅР° РіСЂР°С„Р°С…, РІС‹С‡РёСЃР»РёС‚РµР»СЊРЅС‹Рµ Р·Р°РґР°С‡Рё, Р°Р»РіРѕСЂРёС‚РјС‹ РґР»СЏ GPU (РЎ.Р’. Р“СЂРёРіРѕСЂСЊРµРІ)",
        "РўРµР»РµРєРѕРјРјСѓРЅРёРєР°С†РёРё (Р.Р’.Р—РµР»РµРЅС‡СѓРє, Р”.Р’.РљРѕР·РЅРѕРІ)",
        "РЎС‚РѕС…Р°СЃС‚РёС‡РµСЃРєР°СЏ РѕРїС‚РёРјРёР·Р°С†РёСЏ, СЂР°РЅРґРѕРјРёР·РёСЂРѕРІР°РЅРЅС‹Рµ Р°Р»РіРѕСЂРёС‚РјС‹, РєРІР°РЅС‚РѕРІС‹Рµ РєРѕРјРїСЊСЋС‚РµСЂС‹ (Рћ.Рќ.Р“СЂР°РЅРёС‡РёРЅ, РЎ.РЎ.РЎС‹СЃРѕРµРІ)",
        "РљРѕРјРїСЊСЋС‚РµСЂРЅРѕРµ Р·СЂРµРЅРёРµ, РјР°С€РёРЅРЅРѕРµ РѕР±СѓС‡РµРЅРёРµ, С„РѕС‚РѕРіСЂР°РјРјРµС‚СЂРёСЏ (Рњ.Рќ.РЎРјРёСЂРЅРѕРІ)",
    ]
    return render_template("research_directions.html", directions=directions)


@app.errorhandler(404)
def page_not_found(e):
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


app.add_url_rule("/bachelor/admission.html", view_func=bachelor_admission)
app.add_url_rule("/bachelor/programming-technology.html", view_func=bachelor_programming_technology)
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

    # TODO: no need loop
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
            }
        )

    return render_template("department_staff.html", staff=staff)


@app.route("/frequently-asked-questions.html")
def frequently_asked_questions():
    return render_template("frequently_asked_questions.html")


@app.route("/nooffer")
def nooffer():
    return render_template("nooffer.html")


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


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "build":
            freezer.freeze()
        elif sys.argv[1] == "init":
            with app.app_context():
                init_db()
    else:
        with app.app_context():
            whooshee.reindex()
        app.run(port=5000, debug=True)

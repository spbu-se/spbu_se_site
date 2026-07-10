# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0

from flask import redirect, render_template, session, url_for
from flask_admin import AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_admin.contrib.sqla.fields import QuerySelectField
from flask_login import current_user
from wtforms import SelectField, TextAreaField

from flask_se_config import SECRET_KEY_THESIS
from se_models import (
    AreasOfStudy,
    Courses,
    DiplomaThemes,
    Staff,
    Users,
    Worktype,
    add_mail_notification,
    db,
)
from templates.notification.templates import NotificationTemplates

ADMIN_ROLE_LEVEL = 5
REVIEW_ROLE_LEVEL = 3
THESIS_ROLE_LEVEL = 2


# Base model view with access and inaccess methods
class SeAdminModelView(ModelView):
    can_set_page_size = True

    def is_accessible(self):
        return current_user.is_authenticated and current_user.role >= ADMIN_ROLE_LEVEL

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for("login_index"))


class SeAdminModelViewThesis(SeAdminModelView):
    column_list = (
        "name_ru",
        "name_en",
        "author",
        "supervisor",
        "publish_year",
        "recomended",
        "temporary",
        "review_status",
        "download_thesis",
        "download_presentation",
    )
    form_extra_fields = {
        "supervisor": QuerySelectField(
            "РќР°СѓС‡РЅС‹Р№ СЂСѓРєРѕРІРѕРґРёС‚РµР»СЊ",
            query_factory=lambda: Staff.query.all(),
            get_pk=lambda staff: staff.id,
        ),
        "owner": QuerySelectField(
            "Author user",
            query_factory=lambda: Users.query.all(),
            get_pk=lambda user: user.id,
        ),
        "type": QuerySelectField(
            "РўРёРї СЂР°Р±РѕС‚С‹",
            query_factory=lambda: Worktype.query.all(),
            get_pk=lambda t: t.id,
        ),
        "course": QuerySelectField(
            "РљСѓСЂСЃ",
            query_factory=lambda: Courses.query.all(),
            get_label=lambda c: c.name,
            get_pk=lambda c: c.id,
        ),
        "area": QuerySelectField(
            "РќР°РїСЂР°РІР»РµРЅРёРµ РѕР±СѓС‡РµРЅРёСЏ",
            query_factory=lambda: AreasOfStudy.query.all(),
            get_pk=lambda c: c.id,
        ),
    }


class SeAdminModelViewReviewer(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.role >= REVIEW_ROLE_LEVEL

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for("login_index"))

    pass


class SeAdminIndexView(AdminIndexView):
    @expose("/")
    def index(self):
        thesis_key = SECRET_KEY_THESIS
        return self.render("admin/index.html", thesis_key=thesis_key)

    def is_accessible(self):
        return current_user.is_authenticated and current_user.role >= THESIS_ROLE_LEVEL

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for("login_index"))


class SeAdminModelViewUsers(SeAdminModelView):
    column_exclude_list = [
        "password_hash",
        "internship_author",
        "current_thesises",
        "diploma_themes_author",
        "diploma_themes_consultant",
        "diploma_themes_thesis_supervisor",
        "diploma_themes_supervisor",
        "news",
        "staff",
        "all_user_votes",
        "reviewer",
        "thesis_on_review_author",
        "thesises",
    ]
    form_excluded_columns = [
        "password_hash",
        "internship_author",
        "current_thesises",
        "diploma_themes_author",
        "diploma_themes_consultant",
        "diploma_themes_thesis_supervisor",
        "diploma_themes_supervisor",
        "news",
        "staff",
        "all_user_votes",
        "reviewer",
        "thesis_on_review_author",
        "thesises",
    ]
    column_display_pk = True

    pass


class SeAdminModelViewSummerSchool(SeAdminModelView):
    form_overrides = {
        "description": TextAreaField,
        "repo": TextAreaField,
        "demos": TextAreaField,
    }

    form_widget_args = {
        "description": {"rows": 10, "style": "font-family: monospace; width: 680px;"},
        "project_name": {"style": "width: 680px;"},
        "tech": {"rows": 3, "style": "font-family: monospace; width: 680px;"},
        "repo": {"rows": 3, "style": "font-family: monospace; width: 680px;"},
        "demos": {"rows": 3, "style": "font-family: monospace; width: 680px;"},
        "advisors": {"rows": 2, "style": "font-family: monospace; width: 680px;"},
        "requirements": {"rows": 3, "style": "font-family: monospace; width: 680px;"},
    }

    pass


class SeAdminModelViewStaff(SeAdminModelView):
    column_list = (
        "user",
        "official_email",
        "position",
        "science_degree",
        "still_working",
    )
    form_columns = (
        "user",
        "official_email",
        "position",
        "science_degree",
        "still_working",
    )
    form_choices = {
        "science_degree": [
            ("", ""),
            ("Рґ.С„.-Рј.РЅ.", "Рґ.С„.-Рј.РЅ."),
            ("Рґ.С‚.РЅ.", "Рґ.С‚.РЅ."),
            ("Рє.С„.-Рј.РЅ.", "Рє.С„.-Рј.РЅ."),
            ("Рє.С‚.РЅ.", "Рє.С‚.РЅ."),
        ]
    }
    form_extra_fields = {
        "user": QuerySelectField(
            "User",
            query_factory=lambda: Users.query.all(),
            get_pk=lambda user: user.id,
        )
    }


class SeAdminModelViewNews(SeAdminModelView):
    pass


class SeAdminModelViewDiplomaThemes(SeAdminModelView):
    column_labels = dict(  # pyright: ignore[reportAssignmentType]
        supervisor_thesis="РќР°СѓС‡РЅС‹Р№ СЂСѓРєРѕРІРѕРґРёС‚РµР»СЊ Р’РљР ",
        supervisor="РќР°СѓС‡РЅС‹Р№ СЂСѓРєРѕРІРѕРґРёС‚РµР»СЊ СѓС‡РµР±РЅС‹С… РїСЂР°РєС‚РёРє",
        comment="РљРѕРјРјРµРЅС‚Р°СЂРёР№ (С‡С‚Рѕ РЅРµРѕР±С…РѕРґРёРјРѕ РёСЃРїСЂР°РІРёС‚СЊ)",
        status="РЎС‚Р°С‚СѓСЃ С‚РµРјС‹",
        requirements="РўСЂРµР±РѕРІР°РЅРёСЏ Рє СЃС‚СѓРґРµРЅС‚Сѓ",
        title="РќР°Р·РІР°РЅРёРµ С‚РµРјС‹",
        description="РћРїРёСЃР°РЅРёРµ С‚РµРјС‹",
        company="РљС‚Рѕ РїСЂРµРґСЃС‚Р°РІР»СЏРµС‚ С‚РµРјСѓ",
        levels="РЈСЂРѕРІРµРЅСЊ С‚РµРјС‹",
        consultant="РљРѕРЅСЃСѓР»СЊС‚Р°РЅС‚",
        author="РђРІС‚РѕСЂ С‚РµРјС‹ (РєС‚Рѕ РїСЂРµРґР»РѕР¶РёР»)",
    )
    column_choices = {  # pyright: ignore[reportAssignmentType]
        "status": [
            (0, "РќР° РїСЂРѕРІРµСЂРєРµ"),
            (1, "РўСЂРµР±СѓРµС‚СЃСЏ РґРѕСЂР°Р±РѕС‚РєР°"),
            (2, "РћРґРѕР±СЂРµРЅР°"),
            (4, "РћС‚РєР»РѕРЅРµРЅР°"),
        ]
    }

    form_overrides = {
        "description": TextAreaField,
        "requirements": TextAreaField,
        "comment": TextAreaField,
        "status": SelectField,
    }
    form_args = dict(  # pyright: ignore[reportAssignmentType]
        status=dict(
            choices=[
                (0, "РќР° РїСЂРѕРІРµСЂРєРµ"),
                (1, "РўСЂРµР±СѓРµС‚СЃСЏ РґРѕСЂР°Р±РѕС‚РєР°"),
                (2, "РћРґРѕР±СЂРµРЅР°"),
                (4, "РћС‚РєР»РѕРЅРµРЅР°"),
            ],
            coerce=int,
        )
    )
    form_widget_args = {
        "description": {"rows": 10, "style": "width: 100%;"},
        "comment": {"rows": 4, "style": "width: 100%;"},
        "requirements": {"rows": 4, "style": "width: 100%;"},
    }

    pass


class SeAdminModelViewReviewDiplomaThemes(SeAdminModelViewReviewer):
    can_delete = False
    column_list = (
        "status",
        "comment",
        "title",
        "description",
        "requirements",
        "levels",
        "company",
    )
    column_labels = dict(  # pyright: ignore[reportAssignmentType]
        supervisor_thesis="РќР°СѓС‡РЅС‹Р№ СЂСѓРєРѕРІРѕРґРёС‚РµР»СЊ Р’РљР ",
        supervisor="РќР°СѓС‡РЅС‹Р№ СЂСѓРєРѕРІРѕРґРёС‚РµР»СЊ СѓС‡РµР±РЅС‹С… РїСЂР°РєС‚РёРє",
        comment="РљРѕРјРјРµРЅС‚Р°СЂРёР№ (С‡С‚Рѕ РЅСѓР¶РЅРѕ РёСЃРїСЂР°РІРёС‚СЊ, РµСЃР»Рё С‚СЂРµР±СѓРµС‚СЃСЏ РґРѕСЂР°Р±РѕС‚РєР°, РёР»Рё РїРѕС‡РµРјСѓ С‚РµРјР° РѕС‚РєР»РѕРЅРµРЅР°)",
        status="РЎС‚Р°С‚СѓСЃ С‚РµРјС‹",
        requirements="РўСЂРµР±РѕРІР°РЅРёСЏ Рє СЃС‚СѓРґРµРЅС‚Сѓ",
        title="РќР°Р·РІР°РЅРёРµ С‚РµРјС‹",
        description="РћРїРёСЃР°РЅРёРµ С‚РµРјС‹",
        company="РљС‚Рѕ РїСЂРµРґСЃС‚Р°РІР»СЏРµС‚ С‚РµРјСѓ",
        levels="РЈСЂРѕРІРµРЅСЊ С‚РµРјС‹",
        consultant="РљРѕРЅСЃСѓР»СЊС‚Р°РЅС‚",
        author="РђРІС‚РѕСЂ С‚РµРјС‹ (РєС‚Рѕ РїСЂРµРґР»РѕР¶РёР»)",
    )

    form_overrides = {
        "description": TextAreaField,
        "requirements": TextAreaField,
        "comment": TextAreaField,
        "status": SelectField,
    }

    form_args = dict(  # pyright: ignore[reportAssignmentType]
        status=dict(
            choices=[
                (0, "РќР° РїСЂРѕРІРµСЂРєРµ"),
                (1, "РўСЂРµР±СѓРµС‚СЃСЏ РґРѕСЂР°Р±РѕС‚РєР°"),
                (2, "РћРґРѕР±СЂРµРЅР°"),
                (4, "РћС‚РєР»РѕРЅРµРЅР°"),
            ],
            coerce=int,
        )
    )
    column_choices = {  # pyright: ignore[reportAssignmentType]
        "status": [
            (0, "РќР° РїСЂРѕРІРµСЂРєРµ"),
            (1, "РўСЂРµР±СѓРµС‚СЃСЏ РґРѕСЂР°Р±РѕС‚РєР°"),
            (2, "РћРґРѕР±СЂРµРЅР°"),
        ]
    }

    form_widget_args = {
        "description": {
            "rows": 10,
            "style": "width: 100%;",
        },
        "requirements": {"rows": 3, "style": "width: 100%;"},
        "title": {"readonly": False},
        "level": {"disabled": True},
        "company": {"disabled": False},
        "author": {"readonly": True},
        "comment": {
            "rows": 5,
            "style": "width: 100%;",
        },
    }

    def on_form_prefill(self, form, id):
        model = DiplomaThemes.query.filter_by(id=id).first()
        if model is not None:
            session["previous_status"] = model.status

    def on_model_change(self, form, model, is_created):
        previous_status = session.get("previous_status")
        if previous_status != model.status and model.status == 4:  # pyright: ignore[reportAttributeAccessIssue]
            add_mail_notification(
                model.author_id,  # pyright: ignore[reportAttributeAccessIssue]
                "[SE site] Р’Р°С€Р° С‚РµРјР° РѕС‚РєР»РѕРЅРµРЅР°",
                render_template(
                    NotificationTemplates.DIPLOMA_THEMES_REJECTED.value,
                    title=model.title,  # pyright: ignore[reportAttributeAccessIssue]
                    comment=model.comment,  # pyright: ignore[reportAttributeAccessIssue]
                ),
            )
        if previous_status != model.status and model.status == 1:  # pyright: ignore[reportAttributeAccessIssue]
            add_mail_notification(
                model.author_id,  # pyright: ignore[reportAttributeAccessIssue]
                "[SE site] РўСЂРµР±СѓРµС‚СЃСЏ РґРѕСЂР°Р±РѕС‚РєР° РґР»СЏ Р’Р°С€РµР№ С‚РµРјС‹",
                render_template(
                    NotificationTemplates.DIPLOMA_THEMES_NEED_UPDATE.value,
                    title=model.title,  # pyright: ignore[reportAttributeAccessIssue]
                    comment=model.comment,  # pyright: ignore[reportAttributeAccessIssue]
                ),
            )

    def get_query(self):  # pyright: ignore[reportIncompatibleMethodOverride]
        if self.model is None:  # pyright: ignore[reportAttributeAccessIssue]
            return self.session.query(DiplomaThemes).filter(DiplomaThemes.status < 2)  # pyright: ignore[reportAttributeAccessIssue]
        return self.session.query(self.model).filter(self.model.status < 2)  # pyright: ignore[reportAttributeAccessIssue]

    def get_count_query(self):  # pyright: ignore[reportIncompatibleMethodOverride]
        if self.model is None:  # pyright: ignore[reportAttributeAccessIssue]
            return self.session.query(db.func.count("*")).filter(DiplomaThemes.status < 2)  # pyright: ignore[reportAttributeAccessIssue]
        return self.session.query(db.func.count("*")).filter(self.model.status < 2)  # pyright: ignore[reportAttributeAccessIssue]

    pass


class SeAdminModelViewCurrentThesis(SeAdminModelView):
    column_list = (
        "title",
        "user",
        "area",
        "worktype",
        "supervisor",
        "deleted",
        "status",
    )
    column_labels = dict(  # pyright: ignore[reportAssignmentType]
        title="РќР°Р·РІР°РЅРёРµ С‚РµРјС‹",
        user="РЎС‚СѓРґРµРЅС‚",
        area="РќР°РїСЂР°РІР»РµРЅРёРµ РѕР±СѓС‡РµРЅРёСЏ",
        worktype="РўРёРї СЂР°Р±РѕС‚С‹",
        supervisor="РќР°СѓС‡РЅС‹Р№ СЂСѓРєРѕРІРѕРґРёС‚РµР»СЊ",
        deleted="РЈРґР°Р»РµРЅР°",
        status="РЎС‚Р°С‚СѓСЃ",
    )
    column_choices = {  # pyright: ignore[reportAssignmentType]
        "status": [(1, "РўРµРєСѓС‰Р°СЏ СЂР°Р±РѕС‚Р°"), (2, "Р—Р°РІРµСЂС€РµРЅРЅР°СЏ СЂР°Р±РѕС‚Р°")]
    }

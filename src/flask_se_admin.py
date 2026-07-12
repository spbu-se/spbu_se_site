# SPDX-License-Identifier: Apache-2.0

from flask import redirect, render_template, session, url_for
from flask_login import current_user
from wtforms import SelectField, TextAreaField

from flask_se_config import SECRET_KEY_THESIS
from flask_se_crud import CrudView
from se_models import (
    DiplomaThemes,
    Users,
    add_mail_notification,
)
from templates.notification.templates import NotificationTemplates

ADMIN_ROLE_LEVEL = 5
REVIEW_ROLE_LEVEL = 3
THESIS_ROLE_LEVEL = 2


def _accessible(level):
    return current_user.is_authenticated and current_user.role >= level


def _inaccessible():
    return redirect(url_for("login_index"))


class AdminIndexView(CrudView):
    def __init__(self, app):
        super().__init__(app, None, endpoint="admin")
        app.add_url_rule("/admin/", endpoint="admin.index", view_func=self.index, methods=["GET"])

    def index(self):
        if not _accessible(THESIS_ROLE_LEVEL):
            return _inaccessible()
        return render_template("admin/index.html", thesis_key=SECRET_KEY_THESIS)


class RestrictedCrudView(CrudView):
    role_level = ADMIN_ROLE_LEVEL

    def _check_access(self):
        if not _accessible(self.role_level):
            return _inaccessible()
        return None

    def index_view(self):
        r = self._check_access()
        return r if r else super().index_view()

    def create_view(self):
        r = self._check_access()
        return r if r else super().create_view()

    def edit_view(self):
        r = self._check_access()
        return r if r else super().edit_view()

    def delete_view(self):
        r = self._check_access()
        return r if r else super().delete_view()

    def details_view(self):
        r = self._check_access()
        return r if r else super().details_view()

    def action_view(self):
        r = self._check_access()
        return r if r else super().action_view()

    def export_view(self, export_type):
        r = self._check_access()
        return r if r else super().export_view(export_type)


class SeAdminModelViewUsers(RestrictedCrudView):
    column_display_pk = True
    _exclude = [
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

    def _get_columns(self):
        mapper = __import__("sqlalchemy", fromlist=["inspect"]).inspect(Users)
        return [c.key for c in mapper.columns if c.key not in self._exclude]


class SeAdminModelViewStaff(RestrictedCrudView):
    column_list = ("user", "official_email", "position", "science_degree", "still_working")
    form_columns = ("official_email", "position", "science_degree", "still_working")
    form_args = {
        "science_degree": {
            "choices": [
                ("", ""),
                ("д.ф.-м.н.", "д.ф.-м.н."),
                ("д.т.н.", "д.т.н."),
                ("к.ф.-м.н.", "к.ф.-м.н."),
                ("к.т.н.", "к.т.н."),
            ],
        },
    }


class SeAdminModelViewThesis(RestrictedCrudView):
    column_list = (
        "name_ru",
        "name_en",
        "author",
        "supervisor_id",
        "publish_year",
        "recomended",
        "temporary",
        "review_status",
        "download_thesis",
        "download_presentation",
    )


class SeAdminModelViewSummerSchool(RestrictedCrudView):
    form_overrides = {"description": TextAreaField, "repo": TextAreaField, "demos": TextAreaField}
    form_widget_args = {
        "description": {"rows": 10, "style": "font-family: monospace; width: 680px;"},
        "project_name": {"style": "width: 680px;"},
        "tech": {"rows": 3, "style": "font-family: monospace; width: 680px;"},
        "repo": {"rows": 3, "style": "font-family: monospace; width: 680px;"},
        "demos": {"rows": 3, "style": "font-family: monospace; width: 680px;"},
        "advisors": {"rows": 2, "style": "font-family: monospace; width: 680px;"},
        "requirements": {"rows": 3, "style": "font-family: monospace; width: 680px;"},
    }


class SeAdminModelViewNews(RestrictedCrudView):
    pass


class SeAdminModelViewDiplomaThemes(RestrictedCrudView):
    column_labels = {
        "supervisor_thesis": "Научный руководитель ВКР",
        "supervisor": "Научный руководитель учебных практик",
        "comment": "Комментарий (что необходимо исправить)",
        "status": "Статус темы",
        "requirements": "Требования к студенту",
        "title": "Название темы",
        "description": "Описание темы",
        "company": "Кто представляет тему",
        "levels": "Уровень темы",
        "consultant": "Консультант",
        "author": "Автор темы (кто предложил)",
    }
    column_choices = {
        "status": [
            (0, "На проверке"),
            (1, "Требуется доработка"),
            (2, "Одобрена"),
            (4, "Отклонена"),
        ],
    }
    form_overrides = {
        "description": TextAreaField,
        "requirements": TextAreaField,
        "comment": TextAreaField,
        "status": SelectField,
    }
    form_args = {
        "status": {
            "choices": [
                (0, "На проверке"),
                (1, "Требуется доработка"),
                (2, "Одобрена"),
                (4, "Отклонена"),
            ],
            "coerce": int,
        },
    }
    form_widget_args = {
        "description": {"rows": 10, "style": "width: 100%;"},
        "comment": {"rows": 4, "style": "width: 100%;"},
        "requirements": {"rows": 4, "style": "width: 100%;"},
    }


class SeAdminModelViewReviewDiplomaThemes(CrudView):
    can_delete = False
    can_create = False
    role_level = REVIEW_ROLE_LEVEL
    column_list = ("status", "comment", "title", "description", "requirements", "levels", "company")
    column_labels = {
        "comment": "Комментарий (что нужно исправить, если требуется доработка, или почему тема отклонена)",
        "status": "Статус темы",
        "requirements": "Требования к студенту",
        "title": "Название темы",
        "description": "Описание темы",
        "company": "Кто представляет тему",
        "levels": "Уровень темы",
        "consultant": "Консультант",
        "author": "Автор темы (кто предложил)",
    }
    column_choices = {"status": [(0, "На проверке"), (1, "Требуется доработка"), (2, "Одобрена")]}
    form_overrides = {
        "description": TextAreaField,
        "requirements": TextAreaField,
        "comment": TextAreaField,
        "status": SelectField,
    }
    form_args = {
        "status": {
            "choices": [
                (0, "На проверке"),
                (1, "Требуется доработка"),
                (2, "Одобрена"),
                (4, "Отклонена"),
            ],
            "coerce": int,
        },
    }
    form_widget_args = {
        "description": {"rows": 10, "style": "width: 100%;"},
        "requirements": {"rows": 3, "style": "width: 100%;"},
        "title": {"readonly": False},
        "company": {"disabled": False},
        "comment": {"rows": 5, "style": "width: 100%;"},
    }

    def _check_access(self):
        if not _accessible(self.role_level):
            return _inaccessible()
        return None

    def index_view(self):
        r = self._check_access()
        return r if r else super().index_view()

    def edit_view(self):
        r = self._check_access()
        return r if r else super().edit_view()

    def details_view(self):
        r = self._check_access()
        return r if r else super().details_view()

    def action_view(self):
        r = self._check_access()
        return r if r else super().action_view()

    def export_view(self, export_type):
        r = self._check_access()
        return r if r else super().export_view(export_type)

    def _list_query(self):
        return DiplomaThemes.query.filter(DiplomaThemes.status < 2)

    def on_form_prefill(self, obj, obj_id):  # noqa: ARG002
        if obj is not None:
            session["previous_status"] = obj.status

    def on_model_change(self, form, model, is_created):  # noqa: ARG002
        previous_status = session.get("previous_status")
        if previous_status != model.status:
            if model.status == 4:
                add_mail_notification(
                    model.author_id,
                    "[SE site] Ваша тема отклонена",
                    render_template(
                        NotificationTemplates.DIPLOMA_THEMES_REJECTED.value,
                        title=model.title,
                        comment=model.comment,
                    ),
                )
            elif model.status == 1:
                add_mail_notification(
                    model.author_id,
                    "[SE site] Требуется доработка для Вашей темы",
                    render_template(
                        NotificationTemplates.DIPLOMA_THEMES_NEED_UPDATE.value,
                        title=model.title,
                        comment=model.comment,
                    ),
                )


class SeAdminModelViewCurrentThesis(RestrictedCrudView):
    column_list = (
        "title",
        "user_id",
        "area_id",
        "worktype_id",
        "supervisor_id",
        "deleted",
        "status",
    )
    column_labels = {
        "title": "Название темы",
        "user_id": "Студент",
        "area_id": "Направление обучения",
        "worktype_id": "Тип работы",
        "supervisor_id": "Научный руководитель",
        "deleted": "Удалена",
        "status": "Статус",
    }
    column_choices = {"status": [(1, "Текущая работа"), (2, "Завершенная работа")]}

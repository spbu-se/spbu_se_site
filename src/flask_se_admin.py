# SPDX-License-Identifier: Apache-2.0

from flask import abort, flash, redirect, render_template, request, session, url_for
from flask_login import current_user
from wtforms import SelectField, TextAreaField

from flask_se_crud import CrudView
from se_models import (
    DiplomaThemes,
    Reviewer,
    Users,
    add_mail_notification,
    db,
)
from templates.notification.templates import NotificationTemplates

ADMIN_ROLE_LEVEL = 5
REVIEW_ROLE_LEVEL = 3
THESIS_ROLE_LEVEL = 2


def _theme_archived(theme) -> bool:
    """Move a theme to the archive preserving its previous status. No-op if already archived."""
    if theme.status == 3:
        return False
    theme.prev_status = theme.status
    theme.status = 3
    return True


def _theme_reopened(theme) -> bool:
    """Restore an archived theme to its preserved status. No-op if not archived."""
    if theme.status != 3:
        return False
    theme.status = theme.prev_status if theme.prev_status is not None else 0
    theme.prev_status = None
    return True


def _notify_theme_archived(theme) -> None:
    add_mail_notification(
        theme.author_id,
        "[SE site] Ваша тема архивирована",
        render_template(
            NotificationTemplates.DIPLOMA_THEMES_ARCHIVED.value,
            title=theme.title,
        ),
    )


def _notify_themes_archived(author_id: int, titles: list[str]) -> None:
    """One notification per author listing every theme archived in a bulk run."""
    if not titles:
        return
    single = len(titles) == 1
    add_mail_notification(
        author_id,
        "[SE site] Ваша тема архивирована" if single else "[SE site] Ваши темы архивированы",
        render_template(
            NotificationTemplates.DIPLOMA_THEMES_ARCHIVED.value,
            title=", ".join(titles),
        ),
    )


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
        return render_template("admin/index.html")


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
    form_overrides = {"science_degree": SelectField}
    form_args = {
        "science_degree": {
            "choices": [
                ("", ""),
                ("д.ф.-м.н.", "д.ф.-м.н."),
                ("д.т.н.", "д.т.н."),
                ("к.ф.-м.н.", "к.ф.-м.н."),
                ("к.т.н.", "к.т.н."),
            ],
            "coerce": str,
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
    archive_enabled = True
    bulk_archive_enabled = True
    form_exclude_columns = ("prev_status",)
    form_multi_select_relationships = ("levels",)
    list_filter_columns = ("status",)
    list_filter_choices = {
        "status": [
            (0, "На проверке"),
            (1, "Требуется доработка"),
            (2, "Одобрена"),
            (3, "В архиве"),
            (4, "Отклонена"),
        ],
    }
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
            (3, "В архиве"),
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

    def __init__(self, app, model, endpoint, name=None):
        super().__init__(app, model, endpoint, name)
        app.add_url_rule(
            f"/admin/{endpoint}/archive/",
            endpoint=f"{endpoint}.archive_view",
            view_func=self.archive_view,
            methods=["POST"],
        )
        app.add_url_rule(
            f"/admin/{endpoint}/reopen/",
            endpoint=f"{endpoint}.reopen_view",
            view_func=self.reopen_view,
            methods=["POST"],
        )
        app.add_url_rule(
            f"/admin/{endpoint}/bulk-archive/",
            endpoint=f"{endpoint}.bulk_archive_view",
            view_func=self.bulk_archive_view,
            methods=["POST"],
        )
        app.add_url_rule(
            f"/admin/{endpoint}/bulk-reopen/",
            endpoint=f"{endpoint}.bulk_reopen_view",
            view_func=self.bulk_reopen_view,
            methods=["POST"],
        )

    def archive_view(self):
        r = self._check_access()
        if r:
            return r
        theme_id = request.form.get("id", type=int)
        theme = self._get_obj(theme_id) if theme_id else None
        if theme is None:
            abort(404)
        previous = theme.status
        if _theme_archived(theme):
            if previous in (0, 1, 2):
                _notify_theme_archived(theme)
            db.session.commit()
        return redirect(url_for(f"{self.endpoint}.index_view"))

    def reopen_view(self):
        r = self._check_access()
        if r:
            return r
        theme_id = request.form.get("id", type=int)
        theme = self._get_obj(theme_id) if theme_id else None
        if theme is None:
            abort(404)
        if _theme_reopened(theme):
            db.session.commit()
        return redirect(url_for(f"{self.endpoint}.index_view"))

    def bulk_archive_view(self):
        r = self._check_access()
        if r:
            return r
        changed_by_author = {}
        for theme in self.model.query.all():
            if theme.status in (0, 1, 2) and _theme_archived(theme):
                changed_by_author.setdefault(theme.author_id, []).append(theme.title)
        for author_id, titles in changed_by_author.items():
            _notify_themes_archived(author_id, titles)
        db.session.commit()
        return redirect(url_for(f"{self.endpoint}.index_view"))

    def bulk_reopen_view(self):
        r = self._check_access()
        if r:
            return r
        for theme in self.model.query.all():
            _theme_reopened(theme)
        db.session.commit()
        return redirect(url_for(f"{self.endpoint}.index_view"))

    def extend_form_choices(self, col_key, obj):
        """Preserve status 3 (В архиве) as a selectable value while editing an
        already-archived theme; new/non-archived rows never offer it."""
        if col_key == "status" and getattr(obj, "status", None) == 3:
            return [(3, "В архиве")]
        return None

    def form_change_error(self, obj, form):
        """Archival transitions belong to the dedicated archive/reopen actions
        (they own ``prev_status``). The form must never reach or leave status 3."""
        if not hasattr(form, "status"):
            return None
        old = getattr(obj, "status", None)
        new = form.status.data
        if old == 3 and new != 3:
            return "Нельзя снять тему с архива через форму — используйте «Вернуть из архива»."
        if old != 3 and new == 3:
            return "Нельзя архивировать тему через форму — используйте «В архив»."
        return None


class SeAdminModelViewReviewDiplomaThemes(CrudView):
    can_delete = False
    can_create = False
    role_level = REVIEW_ROLE_LEVEL
    link_column = "title"
    form_exclude_columns = ("prev_status",)
    search_fields = ("title", "description", "requirements")
    list_filter_columns = ("status",)
    list_filter_choices = {"status": [(0, "На проверке"), (1, "Требуется доработка")]}
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
        "consultant_id": "Консультант",
        "author": "Автор темы (кто предложил)",
        "author_id": "Автор темы (кто предложил)",
        "supervisor": "Научный руководитель учебных практик",
        "supervisor_id": "Научный руководитель учебных практик",
        "supervisor_thesis": "Научный руководитель ВКР",
        "supervisor_thesis_id": "Научный руководитель ВКР",
        "company_id": "Кто представляет тему",
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


class SeAdminModelViewCompany(RestrictedCrudView):
    link_column = "name"
    column_display_pk = True
    search_fields = ("name",)
    column_list = ("id", "name", "logo_uri", "status")
    column_labels = {
        "name": "Компания",
        "logo_uri": "Логотип (uri)",
        "status": "Статус",
    }

    def delete_view(self):
        r = self._check_access()
        if r:
            return r
        company_id = request.form.get("id", type=int)
        company = self._get_obj(company_id) if company_id else None
        if company is None:
            abort(404)
        referenced = DiplomaThemes.query.filter_by(company_id=company.id).first() is not None
        referenced = (
            referenced or Reviewer.query.filter_by(company_id=company.id).first() is not None
        )
        if referenced:
            flash(
                "Компания используется темами или рецензентами — удаление заблокировано.",
                "danger",
            )
            return redirect(url_for(f"{self.endpoint}.index_view"))
        db.session.delete(company)
        db.session.commit()
        return redirect(url_for(f"{self.endpoint}.index_view"))


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
    form_overrides = {"status": SelectField}
    form_args = {
        "status": {
            "choices": [(1, "Текущая работа"), (2, "Завершенная работа")],
            "coerce": int,
        },
    }

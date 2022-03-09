# -*- coding: utf-8 -*-

from flask import redirect, url_for
from flask_admin import AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user

from wtforms import TextAreaField, SelectField

from flask_se_config import SECRET_KEY_THESIS
from se_models import db, ThemesLevel


# Base model view with access and inaccess methods
class SeAdminModelView(ModelView):

    def is_accessible(self):
        if current_user.is_authenticated:
            if current_user.role > 1:
                return True
        else:
            return False

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login_index'))


class SeAdminModelViewThesis(SeAdminModelView):
    pass


class SeAdminIndexView(AdminIndexView):

    @expose('/')
    def index(self):
        thesis_key = SECRET_KEY_THESIS
        return self.render('admin/index.html', thesis_key=thesis_key)

    def is_accessible(self):
        if current_user.is_authenticated:
            if current_user.role > 1:
                return True
        else:
            return False

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login_index'))


class SeAdminModelViewUsers(SeAdminModelView):

    column_exclude_list = ['password_hash']

    pass


class SeAdminModelViewSummerSchool(SeAdminModelView):

    form_overrides = {
        'description': TextAreaField,
        'repo': TextAreaField,
        'demos': TextAreaField
    }

    form_widget_args = {
        'description': {
            'rows': 10,
            'style': 'font-family: monospace; width: 680px;'
        },
        'project_name': {
            'style': 'width: 680px;'
        },
        'tech': {
            'rows': 3,
            'style': 'font-family: monospace; width: 680px;'
        },
        'repo': {
            'rows': 3,
            'style': 'font-family: monospace; width: 680px;'
        },
        'demos': {
            'rows': 3,
            'style': 'font-family: monospace; width: 680px;'
        },
        'advisors': {
            'rows': 2,
            'style': 'font-family: monospace; width: 680px;'
        },
        'requirements': {
            'rows': 3,
            'style': 'font-family: monospace; width: 680px;'
        },
    }

    pass


class SeAdminModelViewStaff(SeAdminModelView):

    form_choices = {
        'science_degree': [
            ('', ''),
            ('д.ф.-м.н.', 'д.ф.-м.н.'),
            ('д.т.н.', 'д.т.н.'),
            ('к.ф.-м.н.', 'к.ф.-м.н.'),
            ('к.т.н.', 'к.т.н.')
        ]
    }

    column_exclude_list = ['supervisor', 'adviser']
    form_excluded_columns = ['supervisor', 'adviser']

    pass


class SeAdminModelViewNews(SeAdminModelView):

    pass


class SeAdminModelViewDiplomaThemes(SeAdminModelView):

    column_labels = dict(supervisor_thesis='Научный руководитель ВКР',
                         supervisor="Научный руководитель учебных практик",
                         comment="Комментарий (что необходимо исправить)",
                         status="Статус темы",
                         requirements="Требования к студенту",
                         title='Название темы',
                         description='Описание темы',
                         company='Кто представляет тему',
                         levels='Уровень темы',
                         consultant="Консультант",
                         author="Автор темы (кто предложил)")

    form_overrides = {
        'description': TextAreaField,
        'requirements': TextAreaField,
        'comment': TextAreaField
    }

    form_widget_args = {
        'description': {
            'rows': 10,
            'style': 'width: 100%;'
        },
        'comment': {
            'rows': 4,
            'style': 'width: 100%;'
        },
        'requirements': {
            'rows': 4,
            'style': 'width: 100%;'
        }
    }


    pass


class SeAdminModelViewReviewDiplomaThemes(SeAdminModelView):

    can_delete = False
    column_list = ('status', 'comment', 'title', 'description', 'requirements', 'levels', 'company')
    column_labels = dict(supervisor_thesis='Научный руководитель ВКР',
                         supervisor="Научный руководитель учебных практик",
                         comment="Комментарий (что нужно исправить)",
                         status="Статус темы",
                         requirements="Требования к студенту",
                         title='Название темы',
                         description='Описание темы',
                         company='Кто представляет тему',
                         levels='Уровень темы',
                         consultant="Консультант",
                         author="Автор темы (кто предложил)")

    form_overrides = {
        'description': TextAreaField,
        'requirements': TextAreaField,
        'comment': TextAreaField,
        'status': SelectField
    }

    form_args = dict(
        status=dict(choices=[(0, 'На проверке'), (1, 'Требуется доработка'), (2, 'Одобрена')], coerce=int)
    )

    column_choices = {'status': [
        (0, 'На проверке'),
        (1, 'Требуется доработка'),
        (2, 'Одобрена')
    ]}

    form_widget_args = {
        'description': {
            'rows': 10,
            'style': 'width: 100%;',
            'readonly': True
        },
        'requirements': {
            'rows': 3,
            'style': 'width: 100%;',
            'readonly': True
        },
        'title': {
            'readonly': True
        },
        'level': {
            'disabled': True
        },
        'company': {
            'disabled': True
        },
        'author': {
            'readonly': True
        },
        'comment': {
            'rows': 5,
            'style': 'width: 100%;',
        }
    }

    def get_query(self):
        return self.session.query(self.model).filter(self.model.status < 2)

    def get_count_query(self):
        return self.session.query(db.func.count('*')).filter(self.model.status < 2)

    pass

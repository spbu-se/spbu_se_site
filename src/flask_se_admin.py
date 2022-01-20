# -*- coding: utf-8 -*-

from flask import redirect, url_for
from flask_admin import AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user

from wtforms import TextAreaField

from flask_se_config import SECRET_KEY_THESIS


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

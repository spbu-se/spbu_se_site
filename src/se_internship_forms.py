# -*- coding: utf-8 -*-

from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, SelectMultipleField, widgets
from wtforms.widgets import TextArea


# Diplomas forms
class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class AddInternship(FlaskForm):
    requirements = StringField('requirements', widget=TextArea())
    company = StringField('company')
    name_vacancy = StringField('name_vacancy')
    salary = StringField('salary')
    location = StringField('location')
    more_inf = StringField('more_inf')
    description = StringField('description', widget=TextArea())
    format = MultiCheckboxField('format', coerce=int)


class InternshipsFilter(FlaskForm):
    format = SelectField('format', choices=[])
    company = SelectField('company', choices=[])
    language = SelectField('language', choices=[])
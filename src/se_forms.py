# -*- coding: utf-8 -*-

from flask_wtf import FlaskForm
from wtforms import SelectField, StringField
from wtforms.widgets import TextArea
from wtforms.validators import DataRequired

class ThesisFilter(FlaskForm):
    worktype = SelectField('worktype', choices=[])
    course = SelectField('course', choices=[])
    supervisor = SelectField('supervisor', choices=[])
    startdate = SelectField('worktype', choices=[])
    enddate = SelectField('worktype', choices=[])


class UserAddTheme(FlaskForm):
    title = StringField('title', validators=[DataRequired()])
    description = StringField('description', widget=TextArea(), validators=[DataRequired()])
    level = SelectField('level', choices=[])
    consultant = StringField('consultant')
    company = SelectField('company', choices=[])


class UserEditTheme(FlaskForm):
    comment = StringField('comment')
    title = StringField('title', validators=[DataRequired()])
    description = StringField('description', widget=TextArea(), validators=[DataRequired()])
    level = SelectField('level', choices=[])
    consultant = StringField('consultant')
    company = SelectField('company', choices=[])
    supervisor = StringField('supervisor')
    theme_id = StringField('theme_id')
    status = StringField('status')


class Lecture(FlaskForm):
    worktype = SelectField('worktype', choices=[])
    course = SelectField('course', choices=[])
    supervisor = SelectField('supervisor', choices=[])
    startdate = SelectField('worktype', choices=[])
    enddate = SelectField('worktype', choices=[])

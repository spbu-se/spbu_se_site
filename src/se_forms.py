# -*- coding: utf-8 -*-

from flask_wtf import FlaskForm

from wtforms import SelectField, StringField, SelectMultipleField, widgets
from flask_wtf.file import FileField, FileRequired
from wtforms import SelectField, StringField, SelectMultipleField, RadioField, widgets
from wtforms.widgets import TextArea
from wtforms.validators import DataRequired

from se_models import Worktype, AreasOfStudy

# Thesis forms
class ThesisFilter(FlaskForm):
    worktype = SelectField('worktype', choices=[])
    course = SelectField('course', choices=[])
    supervisor = SelectField('supervisor', choices=[])
    startdate = SelectField('worktype', choices=[])
    enddate = SelectField('worktype', choices=[])


# Diplomas forms
class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class UserAddTheme(FlaskForm):
    title = StringField('title', description='Например, реализация алгоритма контекстно-свободной достижимости на OpenCL', validators=[DataRequired()])
    description = StringField('description', description='Например, необходимо адаптировать библиотеку CLSparse для работы с булевыми матрицами и реализовать алгоритм поиска путей с КС ограничениями, используя результаты адаптации. Провести сравнение с аналогами на существующих данных, проанализировать результаты.', widget=TextArea())
    requirements = StringField('requirements', description='Например, умение программировать на OpenCL C. Умение читать и понимать код на OpenCL C.', widget=TextArea())
    levels = MultiCheckboxField('levels', coerce=int)
    consultant = StringField('consultant')
    company = SelectField('company', choices=[])


class UserEditTheme(FlaskForm):
    comment = StringField('comment')
    title = StringField('title', validators=[DataRequired()])
    description = StringField('description', widget=TextArea(), validators=[DataRequired()])
    requirements = StringField('requirements', widget=TextArea())
    levels = MultiCheckboxField('Levels', coerce=int)
    consultant = StringField('consultant')
    company = SelectField('company', choices=[])
    supervisor = StringField('supervisor')
    theme_id = StringField('theme_id')
    status = StringField('status')


class DiplomaThemesFilter(FlaskForm):
    company = SelectField('company', choices=[])
    level = SelectField('level', choices=[])
    supervisor = SelectField('supervisor', choices=[])


# Thesis review forms
class ThesisReviewFilter(FlaskForm):
    status = SelectField('status', choices=[])
    worktype = SelectField('worktype', choices=[])
    areasofstudy = SelectField('areasofstudy', choices=[])


class AddThesisOnReview(FlaskForm):
    title = StringField('title', description='Укажите название загружаемой работы', validators=[DataRequired()])
    thesis = FileField()
    author = StringField('author', description='Ваше полное ФИО. Например, Иванов Иван Иванович')
    supervisor = SelectField('supervisor', choices=[])
    type = SelectField('type', choices=[])
    area = SelectField('area', choices=[])


class EditThesisOnReview(FlaskForm):
    name_ru = StringField('title', description='Укажите название загружаемой работы', validators=[DataRequired()])
    text_uri = FileField()
    author = StringField('author', description='Ваше полное ФИО. Например, Иванов Иван Иванович')
    supervisor = SelectField('supervisor', choices=[])
    type = SelectField('type', coerce=int, choices=[])
    area = SelectField('area', coerce=int, choices=[])


# Misc
class Lecture(FlaskForm):
    worktype = SelectField('worktype', choices=[])
    course = SelectField('course', choices=[])
    supervisor = SelectField('supervisor', choices=[])
    startdate = SelectField('worktype', choices=[])


class AddInternship(FlaskForm):
    requirements = StringField('requirements', widget=TextArea())
    company = SelectField('company', choices=[])
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


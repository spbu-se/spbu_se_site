# SPDX-License-Identifier: Apache-2.0
from datetime import datetime

from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import (
    DateTimeField,
    SelectField,
    SelectMultipleField,
    StringField,
    validators,
    widgets,
)
from wtforms.validators import DataRequired
from wtforms.widgets import TextArea


# Thesis forms
class ThesisFilter(FlaskForm):
    worktype = SelectField("worktype", choices=[])
    course = SelectField("course", choices=[])
    supervisor = SelectField("supervisor", choices=[])
    startdate = SelectField("worktype", choices=[])
    enddate = SelectField("worktype", choices=[])


# Diplomas forms
class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class UserAddTheme(FlaskForm):
    title = StringField(
        "title",
        description="РќР°РїСЂРёРјРµСЂ, СЂРµР°Р»РёР·Р°С†РёСЏ Р°Р»РіРѕСЂРёС‚РјР° РєРѕРЅС‚РµРєСЃС‚РЅРѕ-СЃРІРѕР±РѕРґРЅРѕР№ РґРѕСЃС‚РёР¶РёРјРѕСЃС‚Рё РЅР° OpenCL",
        validators=[DataRequired()],
    )
    description = StringField(
        "description",
        description="РќР°РїСЂРёРјРµСЂ, РЅРµРѕР±С…РѕРґРёРјРѕ Р°РґР°РїС‚РёСЂРѕРІР°С‚СЊ Р±РёР±Р»РёРѕС‚РµРєСѓ CLSparse РґР»СЏ СЂР°Р±РѕС‚С‹ СЃ Р±СѓР»РµРІС‹РјРё РјР°С‚СЂРёС†Р°РјРё Рё СЂРµР°Р»РёР·РѕРІР°С‚СЊ Р°Р»РіРѕСЂРёС‚Рј РїРѕРёСЃРєР° РїСѓС‚РµР№ СЃ РљРЎ РѕРіСЂР°РЅРёС‡РµРЅРёСЏРјРё, РёСЃРїРѕР»СЊР·СѓСЏ СЂРµР·СѓР»СЊС‚Р°С‚С‹ Р°РґР°РїС‚Р°С†РёРё. РџСЂРѕРІРµСЃС‚Рё СЃСЂР°РІРЅРµРЅРёРµ СЃ Р°РЅР°Р»РѕРіР°РјРё РЅР° СЃСѓС‰РµСЃС‚РІСѓСЋС‰РёС… РґР°РЅРЅС‹С…, РїСЂРѕР°РЅР°Р»РёР·РёСЂРѕРІР°С‚СЊ СЂРµР·СѓР»СЊС‚Р°С‚С‹.",
        widget=TextArea(),
    )
    requirements = StringField(
        "requirements",
        description="РќР°РїСЂРёРјРµСЂ, СѓРјРµРЅРёРµ РїСЂРѕРіСЂР°РјРјРёСЂРѕРІР°С‚СЊ РЅР° OpenCL C. РЈРјРµРЅРёРµ С‡РёС‚Р°С‚СЊ Рё РїРѕРЅРёРјР°С‚СЊ РєРѕРґ РЅР° OpenCL C.",
        widget=TextArea(),
    )
    levels = MultiCheckboxField("levels", coerce=int)
    consultant = StringField("consultant")
    company = SelectField("company", choices=[])


class UserEditTheme(FlaskForm):
    comment = StringField("comment")
    title = StringField("title", validators=[DataRequired()])
    description = StringField("description", widget=TextArea(), validators=[DataRequired()])
    requirements = StringField("requirements", widget=TextArea())
    levels = MultiCheckboxField("Levels", coerce=int)
    consultant = StringField("consultant")
    company = SelectField("company", choices=[])
    supervisor = StringField("supervisor")
    theme_id = StringField("theme_id")
    status = StringField("status")


class DiplomaThemesFilter(FlaskForm):
    company = SelectField("company", choices=[])
    level = SelectField("level", choices=[])
    supervisor = SelectField("supervisor", choices=[])


class UserDiplomaThemesFilter(FlaskForm):
    archived = SelectField("archived", choices=[])


# Thesis review forms
class ThesisReviewFilter(FlaskForm):
    status = SelectField("status", choices=[])
    worktype = SelectField("worktype", choices=[])
    areasofstudy = SelectField("areasofstudy", choices=[])


class AddThesisOnReview(FlaskForm):
    title = StringField(
        "title",
        description="РЈРєР°Р¶РёС‚Рµ РЅР°Р·РІР°РЅРёРµ Р·Р°РіСЂСѓР¶Р°РµРјРѕР№ СЂР°Р±РѕС‚С‹",
        validators=[DataRequired()],
    )
    thesis = FileField()
    author = StringField(
        "author",
        description="Р’Р°С€Рµ РїРѕР»РЅРѕРµ Р¤РРћ. РќР°РїСЂРёРјРµСЂ, РРІР°РЅРѕРІ РРІР°РЅ РРІР°РЅРѕРІРёС‡",
    )
    supervisor = SelectField("supervisor", choices=[])
    type = SelectField("type", choices=[])
    area = SelectField("area", choices=[])


class EditThesisOnReview(FlaskForm):
    name_ru = StringField(
        "title",
        description="РЈРєР°Р¶РёС‚Рµ РЅР°Р·РІР°РЅРёРµ Р·Р°РіСЂСѓР¶Р°РµРјРѕР№ СЂР°Р±РѕС‚С‹",
        validators=[DataRequired()],
    )
    text_uri = FileField()
    author = StringField(
        "author",
        description="Р’Р°С€Рµ РїРѕР»РЅРѕРµ Р¤РРћ. РќР°РїСЂРёРјРµСЂ, РРІР°РЅРѕРІ РРІР°РЅ РРІР°РЅРѕРІРёС‡",
    )
    supervisor = SelectField("supervisor", choices=[])
    type = SelectField("type", coerce=int, choices=[])
    area = SelectField("area", coerce=int, choices=[])


# Misc
class Lecture(FlaskForm):
    worktype = SelectField("worktype", choices=[])
    course = SelectField("course", choices=[])
    supervisor = SelectField("supervisor", choices=[])
    startdate = SelectField("worktype", choices=[])
    enddate = SelectField("worktype", choices=[])


class AddInternship(FlaskForm):
    requirements = StringField("requirements", widget=TextArea())
    company = SelectField("company", choices=[])
    name_vacancy = StringField("name_vacancy")
    salary = StringField("salary")
    location = StringField("location")
    more_inf = StringField("more_inf")
    description = StringField("description", widget=TextArea())
    format = MultiCheckboxField("format", coerce=int)
    tag = StringField("tag")


class InternshipsFilter(FlaskForm):
    format = SelectField("format", choices=[])
    company = SelectField("company", choices=[])
    language = SelectField("language", choices=[])
    tag = SelectField("tag", choices=[])


# Practice forms
class CurrentWorktypeArea(FlaskForm):
    worktype = SelectField("worktype", choices=[])
    area = SelectField("area", choices=[])


class ChooseTopic(FlaskForm):
    topic = StringField(
        "topic",
        description="РќР°РїСЂРёРјРµСЂ, СЂРµР°Р»РёР·Р°С†РёСЏ Р°Р»РіРѕСЂРёС‚РјР° РєРѕРЅС‚РµРєСЃС‚РЅРѕ-СЃРІРѕР±РѕРґРЅРѕР№ РґРѕСЃС‚РёР¶РёРјРѕСЃС‚Рё РЅР° OpenCL",
    )
    staff = SelectField("staff", choices=[])
    consultant = StringField(
        "consultant",
        description="Р¤РРћ РєРѕРЅСЃСѓР»СЊС‚Р°РЅС‚Р°, РґРѕР»Р¶РЅРѕСЃС‚СЊ Рё РєРѕРјРїР°РЅРёСЏ",
    )


class DeadlineTemp(FlaskForm):
    area = SelectField("area", choices=[], validators=[validators.Optional()])
    worktype = SelectField("worktype", choices=[], validators=[validators.Optional()])
    choose_topic = DateTimeField("choose_topic")
    submit_work_for_review = DateTimeField("submit_work_for_review")
    upload_reviews = DateTimeField("upload_reviews")
    pre_defense = DateTimeField("pre_defense")
    defense = DateTimeField("defense")


class AddGoal(FlaskForm):
    goal = StringField(
        "goal",
        description="РќР°РїСЂРёРјРµСЂ, РјРѕРґРёС„РёРєР°С†РёСЏ Р±РёР±Р»РёРѕС‚РµРєРё COLMAP РѕРїС‚РёРјР°Р»СЊРЅС‹Рј Р°Р»РіРѕСЂРёС‚РјРѕРј Р»РѕРєР°Р»РёР·Р°С†РёРё РЅРµРєР°Р»РёР±СЂРѕРІР°РЅРЅРѕР№ РєР°РјРµСЂС‹ РѕС‚РЅРѕСЃРёС‚РµР»СЊРЅРѕ РѕР±Р»Р°РєР° 3D С‚РѕС‡РµРє.",
    )


class AddTask(FlaskForm):
    task_text = StringField(
        "task_text",
        description="РќР°РїСЂРёРјРµСЂ, РЅР°СѓС‡РёС‚СЊСЃСЏ СЂР°Р±РѕС‚Р°С‚СЊ СЃ ajax.",
    )


class UserAddReport(FlaskForm):
    was_done = StringField(
        "was_done",
        description="РќР°РїСЂРёРјРµСЂ: РџСЂРѕРІРµР» СЃСЂР°РІРЅРµРЅРёРµ РјРѕРµРіРѕ РїСЂРѕРµРєС‚Р° СЃ Р°РЅР°Р»РѕРіР°РјРё. "
        "РЎРѕСЃС‚Р°РІРёР» С‚Р°Р±Р»РёС†Сѓ, РїСЂРѕР°РЅР°Р»РёР·РёСЂРѕРІР°Р» СЂРµР·СѓР»СЊС‚Р°С‚С‹. РЎС„РѕСЂРјСѓР»РёСЂРѕРІР°Р», С‡РµРј "
        "РјРѕР№ РїСЂРѕРµРєС‚ Р»СѓС‡С€Рµ РѕСЃС‚Р°Р»СЊРЅС‹С…. Рё Р·Р°РЅРµСЃ РІ С‚РµРєСЃС‚ РІРІРµРґРµРЅРёСЏ РїРѕР»СѓС‡РµРЅРЅСѓСЋ"
        " РёРЅС„РѕСЂРјР°С†РёСЋ.",
        widget=TextArea(),
    )
    planned_to_do = StringField(
        "planned_to_do",
        description="РќР°РїСЂРёРјРµСЂ: Р’ Р±Р»РёР¶Р°Р№С€РµРµ РІСЂРµРјСЏ РїР»Р°РЅРёСЂСѓСЋ РґРѕРїРёСЃР°С‚СЊ РІРІРµРґРµРЅРёРµ, "
        "РёР·СѓС‡РёС‚СЊ MySQL РїРѕ РєСѓСЂСЃР°Рј РЅР° Stepik, СЃРѕСЃС‚Р°РІРёС‚СЊ СЃС…РµРјСѓ Р±Р°Р· "
        "РґР°РЅРЅС‹С… РґР»СЏ РјРѕРµРіРѕ РїСЂРѕРµРєС‚Р°.",
        widget=TextArea(),
    )


class StaffAddCommentToReport(FlaskForm):
    comment = StringField(
        "comment",
        description="РњРѕР¶РµС‚Рµ РґР°С‚СЊ СЃС‚СѓРґРµРЅС‚Сѓ РѕР±СЂР°С‚РЅСѓСЋ СЃРІСЏР·СЊ РїРѕ РѕС‚С‡С‘С‚Сѓ",
        widget=TextArea(),
    )


class ChooseCourseAndYear(FlaskForm):
    course = SelectField("course", choices=[])

    current_year = datetime.now().year
    years = tuple((str(year), str(year)) for year in range(current_year - 5, current_year + 3))
    publish_year = SelectField("publish_year", choices=years, default=str(current_year))

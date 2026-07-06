# -*- coding: utf-8 -*-
import pytest
from flask_wtf.file import FileField
from wtforms import DateTimeField, SelectField, SelectMultipleField, StringField, validators
from wtforms.validators import DataRequired
from wtforms.widgets import TextArea


@pytest.fixture(autouse=True)
def _form_ctx():
    from flask_se import app

    app.config["WTF_CSRF_ENABLED"] = False
    with app.app_context():
        yield


class TestThesisFilter:
    def test_field_worktype_is_select(self):
        from se_forms import ThesisFilter

        f = ThesisFilter()
        assert isinstance(f.worktype, SelectField)
        assert f.worktype.name == "worktype"
        assert f.worktype.choices == []

    def test_field_course_is_select(self):
        from se_forms import ThesisFilter

        f = ThesisFilter()
        assert isinstance(f.course, SelectField)
        assert f.course.choices == []

    def test_field_supervisor_is_select(self):
        from se_forms import ThesisFilter

        f = ThesisFilter()
        assert isinstance(f.supervisor, SelectField)
        assert f.supervisor.choices == []

    def test_field_startdate_is_select(self):
        from se_forms import ThesisFilter

        f = ThesisFilter()
        assert isinstance(f.startdate, SelectField)
        assert f.startdate.choices == []

    def test_field_enddate_is_select(self):
        from se_forms import ThesisFilter

        f = ThesisFilter()
        assert isinstance(f.enddate, SelectField)
        assert f.enddate.choices == []


class TestMultiCheckboxField:
    def test_is_select_multiple_subclass(self):
        from se_forms import MultiCheckboxField

        assert issubclass(MultiCheckboxField, SelectMultipleField)

    def test_widget_is_list_with_checkboxes(self):
        from se_forms import MultiCheckboxField

        assert MultiCheckboxField.widget.__class__.__name__ == "ListWidget"
        assert MultiCheckboxField.option_widget.__class__.__name__ == "CheckboxInput"

    def test_coerce_is_int(self):
        from wtforms.fields.choices import SelectMultipleField

        from se_forms import MultiCheckboxField

        assert issubclass(MultiCheckboxField, SelectMultipleField)


class TestUserAddTheme:
    def test_field_title_required_string(self):
        from se_forms import UserAddTheme

        f = UserAddTheme()
        assert isinstance(f.title, StringField)
        assert any(isinstance(v, DataRequired) for v in f.title.validators)

    def test_field_description_is_textarea(self):
        from se_forms import UserAddTheme

        f = UserAddTheme()
        assert isinstance(f.description, StringField)
        assert isinstance(f.description.widget, TextArea)

    def test_field_requirements_is_textarea(self):
        from se_forms import UserAddTheme

        f = UserAddTheme()
        assert isinstance(f.requirements, StringField)
        assert isinstance(f.requirements.widget, TextArea)

    def test_field_levels_is_multicheckbox(self):
        from se_forms import UserAddTheme

        f = UserAddTheme()
        assert isinstance(f.levels, SelectMultipleField)
        assert f.levels.coerce is int

    def test_field_consultant_is_string(self):
        from se_forms import UserAddTheme

        f = UserAddTheme()
        assert isinstance(f.consultant, StringField)

    def test_field_company_is_select(self):
        from se_forms import UserAddTheme

        f = UserAddTheme()
        assert isinstance(f.company, SelectField)
        assert f.company.choices == []


class TestUserEditTheme:
    def test_field_title_required_string(self):
        from se_forms import UserEditTheme

        f = UserEditTheme()
        assert isinstance(f.title, StringField)
        assert any(isinstance(v, DataRequired) for v in f.title.validators)

    def test_field_description_required_textarea(self):
        from se_forms import UserEditTheme

        f = UserEditTheme()
        assert isinstance(f.description, StringField)
        assert isinstance(f.description.widget, TextArea)
        assert any(isinstance(v, DataRequired) for v in f.description.validators)

    def test_field_requirements_is_textarea(self):
        from se_forms import UserEditTheme

        f = UserEditTheme()
        assert isinstance(f.requirements, StringField)
        assert isinstance(f.requirements.widget, TextArea)

    def test_field_comment_is_string(self):
        from se_forms import UserEditTheme

        f = UserEditTheme()
        assert isinstance(f.comment, StringField)

    def test_field_levels_is_multicheckbox(self):
        from se_forms import UserEditTheme

        f = UserEditTheme()
        assert isinstance(f.levels, SelectMultipleField)
        assert f.levels.coerce is int

    def test_field_consultant_is_string(self):
        from se_forms import UserEditTheme

        f = UserEditTheme()
        assert isinstance(f.consultant, StringField)

    def test_field_company_is_select(self):
        from se_forms import UserEditTheme

        f = UserEditTheme()
        assert isinstance(f.company, SelectField)

    def test_field_supervisor_is_string(self):
        from se_forms import UserEditTheme

        f = UserEditTheme()
        assert isinstance(f.supervisor, StringField)

    def test_field_theme_id_is_string(self):
        from se_forms import UserEditTheme

        f = UserEditTheme()
        assert isinstance(f.theme_id, StringField)

    def test_field_status_is_string(self):
        from se_forms import UserEditTheme

        f = UserEditTheme()
        assert isinstance(f.status, StringField)


class TestDiplomaThemesFilter:
    def test_field_company_is_select(self):
        from se_forms import DiplomaThemesFilter

        f = DiplomaThemesFilter()
        assert isinstance(f.company, SelectField)

    def test_field_level_is_select(self):
        from se_forms import DiplomaThemesFilter

        f = DiplomaThemesFilter()
        assert isinstance(f.level, SelectField)

    def test_field_supervisor_is_select(self):
        from se_forms import DiplomaThemesFilter

        f = DiplomaThemesFilter()
        assert isinstance(f.supervisor, SelectField)


class TestUserDiplomaThemesFilter:
    def test_field_archived_is_select(self):
        from se_forms import UserDiplomaThemesFilter

        f = UserDiplomaThemesFilter()
        assert isinstance(f.archived, SelectField)
        assert f.archived.choices == []


class TestThesisReviewFilter:
    def test_field_status_is_select(self):
        from se_forms import ThesisReviewFilter

        f = ThesisReviewFilter()
        assert isinstance(f.status, SelectField)

    def test_field_worktype_is_select(self):
        from se_forms import ThesisReviewFilter

        f = ThesisReviewFilter()
        assert isinstance(f.worktype, SelectField)

    def test_field_areasofstudy_is_select(self):
        from se_forms import ThesisReviewFilter

        f = ThesisReviewFilter()
        assert isinstance(f.areasofstudy, SelectField)


class TestAddThesisOnReview:
    def test_field_title_required_string(self):
        from se_forms import AddThesisOnReview

        f = AddThesisOnReview()
        assert isinstance(f.title, StringField)
        assert any(isinstance(v, DataRequired) for v in f.title.validators)

    def test_field_thesis_is_file(self):
        from se_forms import AddThesisOnReview

        f = AddThesisOnReview()
        assert isinstance(f.thesis, FileField)

    def test_field_author_is_string(self):
        from se_forms import AddThesisOnReview

        f = AddThesisOnReview()
        assert isinstance(f.author, StringField)

    def test_field_supervisor_is_select(self):
        from se_forms import AddThesisOnReview

        f = AddThesisOnReview()
        assert isinstance(f.supervisor, SelectField)

    def test_field_type_is_select(self):
        from se_forms import AddThesisOnReview

        f = AddThesisOnReview()
        assert isinstance(f.type, SelectField)

    def test_field_area_is_select(self):
        from se_forms import AddThesisOnReview

        f = AddThesisOnReview()
        assert isinstance(f.area, SelectField)


class TestEditThesisOnReview:
    def test_field_name_ru_required_string(self):
        from se_forms import EditThesisOnReview

        f = EditThesisOnReview()
        assert isinstance(f.name_ru, StringField)
        assert any(isinstance(v, DataRequired) for v in f.name_ru.validators)

    def test_field_text_uri_is_file(self):
        from se_forms import EditThesisOnReview

        f = EditThesisOnReview()
        assert isinstance(f.text_uri, FileField)

    def test_field_author_is_string(self):
        from se_forms import EditThesisOnReview

        f = EditThesisOnReview()
        assert isinstance(f.author, StringField)

    def test_field_supervisor_is_select(self):
        from se_forms import EditThesisOnReview

        f = EditThesisOnReview()
        assert isinstance(f.supervisor, SelectField)

    def test_field_type_is_select_with_coerce_int(self):
        from se_forms import EditThesisOnReview

        f = EditThesisOnReview()
        assert isinstance(f.type, SelectField)
        assert f.type.coerce is int

    def test_field_area_is_select_with_coerce_int(self):
        from se_forms import EditThesisOnReview

        f = EditThesisOnReview()
        assert isinstance(f.area, SelectField)
        assert f.area.coerce is int


class TestLecture:
    def test_field_worktype_is_select(self):
        from se_forms import Lecture

        f = Lecture()
        assert isinstance(f.worktype, SelectField)

    def test_field_course_is_select(self):
        from se_forms import Lecture

        f = Lecture()
        assert isinstance(f.course, SelectField)

    def test_field_supervisor_is_select(self):
        from se_forms import Lecture

        f = Lecture()
        assert isinstance(f.supervisor, SelectField)

    def test_field_startdate_is_select(self):
        from se_forms import Lecture

        f = Lecture()
        assert isinstance(f.startdate, SelectField)

    def test_field_enddate_is_select(self):
        from se_forms import Lecture

        f = Lecture()
        assert isinstance(f.enddate, SelectField)


class TestAddInternship:
    def test_field_requirements_is_textarea(self):
        from se_forms import AddInternship

        f = AddInternship()
        assert isinstance(f.requirements, StringField)
        assert isinstance(f.requirements.widget, TextArea)

    def test_field_company_is_select(self):
        from se_forms import AddInternship

        f = AddInternship()
        assert isinstance(f.company, SelectField)

    def test_field_name_vacancy_is_string(self):
        from se_forms import AddInternship

        f = AddInternship()
        assert isinstance(f.name_vacancy, StringField)

    def test_field_salary_is_string(self):
        from se_forms import AddInternship

        f = AddInternship()
        assert isinstance(f.salary, StringField)

    def test_field_location_is_string(self):
        from se_forms import AddInternship

        f = AddInternship()
        assert isinstance(f.location, StringField)

    def test_field_more_inf_is_string(self):
        from se_forms import AddInternship

        f = AddInternship()
        assert isinstance(f.more_inf, StringField)

    def test_field_description_is_textarea(self):
        from se_forms import AddInternship

        f = AddInternship()
        assert isinstance(f.description, StringField)
        assert isinstance(f.description.widget, TextArea)

    def test_field_format_is_multicheckbox(self):
        from se_forms import AddInternship

        f = AddInternship()
        assert isinstance(f.format, SelectMultipleField)
        assert f.format.coerce is int

    def test_field_tag_is_string(self):
        from se_forms import AddInternship

        f = AddInternship()
        assert isinstance(f.tag, StringField)


class TestInternshipsFilter:
    def test_field_format_is_select(self):
        from se_forms import InternshipsFilter

        f = InternshipsFilter()
        assert isinstance(f.format, SelectField)

    def test_field_company_is_select(self):
        from se_forms import InternshipsFilter

        f = InternshipsFilter()
        assert isinstance(f.company, SelectField)

    def test_field_language_is_select(self):
        from se_forms import InternshipsFilter

        f = InternshipsFilter()
        assert isinstance(f.language, SelectField)

    def test_field_tag_is_select(self):
        from se_forms import InternshipsFilter

        f = InternshipsFilter()
        assert isinstance(f.tag, SelectField)


class TestCurrentWorktypeArea:
    def test_field_worktype_is_select(self):
        from se_forms import CurrentWorktypeArea

        f = CurrentWorktypeArea()
        assert isinstance(f.worktype, SelectField)

    def test_field_area_is_select(self):
        from se_forms import CurrentWorktypeArea

        f = CurrentWorktypeArea()
        assert isinstance(f.area, SelectField)


class TestChooseTopic:
    def test_field_topic_is_string(self):
        from se_forms import ChooseTopic

        f = ChooseTopic()
        assert isinstance(f.topic, StringField)

    def test_field_staff_is_select(self):
        from se_forms import ChooseTopic

        f = ChooseTopic()
        assert isinstance(f.staff, SelectField)

    def test_field_consultant_is_string(self):
        from se_forms import ChooseTopic

        f = ChooseTopic()
        assert isinstance(f.consultant, StringField)


class TestDeadlineTemp:
    def test_field_area_is_optional_select(self):
        from se_forms import DeadlineTemp

        f = DeadlineTemp()
        assert isinstance(f.area, SelectField)
        assert any(isinstance(v, validators.Optional) for v in f.area.validators)

    def test_field_worktype_is_optional_select(self):
        from se_forms import DeadlineTemp

        f = DeadlineTemp()
        assert isinstance(f.worktype, SelectField)
        assert any(isinstance(v, validators.Optional) for v in f.worktype.validators)

    def test_field_choose_topic_is_datetime(self):
        from se_forms import DeadlineTemp

        f = DeadlineTemp()
        assert isinstance(f.choose_topic, DateTimeField)

    def test_field_submit_work_for_review_is_datetime(self):
        from se_forms import DeadlineTemp

        f = DeadlineTemp()
        assert isinstance(f.submit_work_for_review, DateTimeField)

    def test_field_upload_reviews_is_datetime(self):
        from se_forms import DeadlineTemp

        f = DeadlineTemp()
        assert isinstance(f.upload_reviews, DateTimeField)

    def test_field_pre_defense_is_datetime(self):
        from se_forms import DeadlineTemp

        f = DeadlineTemp()
        assert isinstance(f.pre_defense, DateTimeField)

    def test_field_defense_is_datetime(self):
        from se_forms import DeadlineTemp

        f = DeadlineTemp()
        assert isinstance(f.defense, DateTimeField)


class TestAddGoal:
    def test_field_goal_is_string(self):
        from se_forms import AddGoal

        f = AddGoal()
        assert isinstance(f.goal, StringField)


class TestAddTask:
    def test_field_task_text_is_string(self):
        from se_forms import AddTask

        f = AddTask()
        assert isinstance(f.task_text, StringField)


class TestUserAddReport:
    def test_field_was_done_is_textarea(self):
        from se_forms import UserAddReport

        f = UserAddReport()
        assert isinstance(f.was_done, StringField)
        assert isinstance(f.was_done.widget, TextArea)

    def test_field_planned_to_do_is_textarea(self):
        from se_forms import UserAddReport

        f = UserAddReport()
        assert isinstance(f.planned_to_do, StringField)
        assert isinstance(f.planned_to_do.widget, TextArea)


class TestStaffAddCommentToReport:
    def test_field_comment_is_textarea(self):
        from se_forms import StaffAddCommentToReport

        f = StaffAddCommentToReport()
        assert isinstance(f.comment, StringField)
        assert isinstance(f.comment.widget, TextArea)


class TestChooseCourseAndYear:
    def test_field_course_is_select(self):
        from se_forms import ChooseCourseAndYear

        f = ChooseCourseAndYear()
        assert isinstance(f.course, SelectField)

    def test_field_publish_year_is_select_with_default_current(self):
        from datetime import datetime

        from se_forms import ChooseCourseAndYear

        f = ChooseCourseAndYear()
        assert isinstance(f.publish_year, SelectField)
        assert f.publish_year.default == str(datetime.now().year)

    def test_field_publish_year_choices_span_eight_years(self):
        from datetime import datetime

        from se_forms import ChooseCourseAndYear

        f = ChooseCourseAndYear()
        current = datetime.now().year
        assert (str(current), str(current)) in f.publish_year.choices
        assert (str(current - 5), str(current - 5)) in f.publish_year.choices
        assert (str(current + 2), str(current + 2)) in f.publish_year.choices

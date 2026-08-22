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
    @pytest.mark.parametrize(
        ("field", "check_name"),
        [
            ("worktype", True),
            ("course", False),
            ("supervisor", False),
            ("startdate", False),
            ("enddate", False),
        ],
    )
    def test_field_is_select(self, field, check_name):
        from se_forms import ThesisFilter

        f = ThesisFilter()
        field_obj = getattr(f, field)
        assert isinstance(field_obj, SelectField)
        assert field_obj.choices == []
        if check_name:
            assert field_obj.name == field


class TestMultiCheckboxField:
    def test_is_select_multiple_subclass(self):
        from se_forms import MultiCheckboxField

        assert issubclass(MultiCheckboxField, SelectMultipleField)

    def test_widget_is_list_with_checkboxes(self):
        from se_forms import MultiCheckboxField

        assert MultiCheckboxField.widget.__class__.__name__ == "ListWidget"
        assert MultiCheckboxField.option_widget.__class__.__name__ == "CheckboxInput"


class TestUserAddTheme:
    @pytest.mark.parametrize(
        ("field", "required"),
        [("title", True), ("consultant", False)],
    )
    def test_field_is_string(self, field, required):
        from se_forms import UserAddTheme

        f = UserAddTheme()
        field_obj = getattr(f, field)
        assert isinstance(field_obj, StringField)
        if required:
            assert any(isinstance(v, DataRequired) for v in field_obj.validators)

    @pytest.mark.parametrize("field", ["description", "requirements"])
    def test_field_is_textarea(self, field):
        from se_forms import UserAddTheme

        f = UserAddTheme()
        field_obj = getattr(f, field)
        assert isinstance(field_obj, StringField)
        assert isinstance(field_obj.widget, TextArea)

    def test_field_levels_is_multicheckbox(self):
        from se_forms import UserAddTheme

        f = UserAddTheme()
        assert isinstance(f.levels, SelectMultipleField)
        assert f.levels.coerce is int

    def test_field_company_is_select(self):
        from se_forms import UserAddTheme

        f = UserAddTheme()
        assert isinstance(f.company, SelectField)
        assert f.company.choices == []


class TestUserEditTheme:
    @pytest.mark.parametrize(
        ("field", "required"),
        [
            ("title", True),
            ("comment", False),
            ("consultant", False),
            ("supervisor", False),
            ("theme_id", False),
            ("status", False),
        ],
    )
    def test_field_is_string(self, field, required):
        from se_forms import UserEditTheme

        f = UserEditTheme()
        field_obj = getattr(f, field)
        assert isinstance(field_obj, StringField)
        if required:
            assert any(isinstance(v, DataRequired) for v in field_obj.validators)

    @pytest.mark.parametrize(
        ("field", "required"),
        [("description", True), ("requirements", False)],
    )
    def test_field_is_textarea(self, field, required):
        from se_forms import UserEditTheme

        f = UserEditTheme()
        field_obj = getattr(f, field)
        assert isinstance(field_obj, StringField)
        assert isinstance(field_obj.widget, TextArea)
        if required:
            assert any(isinstance(v, DataRequired) for v in field_obj.validators)

    def test_field_levels_is_multicheckbox(self):
        from se_forms import UserEditTheme

        f = UserEditTheme()
        assert isinstance(f.levels, SelectMultipleField)
        assert f.levels.coerce is int

    def test_field_company_is_select(self):
        from se_forms import UserEditTheme

        f = UserEditTheme()
        assert isinstance(f.company, SelectField)


class TestDiplomaThemesFilter:
    @pytest.mark.parametrize("field", ["company", "level", "supervisor"])
    def test_field_is_select(self, field):
        from se_forms import DiplomaThemesFilter

        f = DiplomaThemesFilter()
        assert isinstance(getattr(f, field), SelectField)


class TestUserDiplomaThemesFilter:
    def test_field_archived_is_select(self):
        from se_forms import UserDiplomaThemesFilter

        f = UserDiplomaThemesFilter()
        assert isinstance(f.archived, SelectField)
        assert f.archived.choices == []


class TestThesisReviewFilter:
    @pytest.mark.parametrize("field", ["status", "worktype", "areasofstudy"])
    def test_field_is_select(self, field):
        from se_forms import ThesisReviewFilter

        f = ThesisReviewFilter()
        assert isinstance(getattr(f, field), SelectField)


class TestAddThesisOnReview:
    @pytest.mark.parametrize(
        ("field", "required"),
        [("title", True), ("author", False)],
    )
    def test_field_is_string(self, field, required):
        from se_forms import AddThesisOnReview

        f = AddThesisOnReview()
        field_obj = getattr(f, field)
        assert isinstance(field_obj, StringField)
        if required:
            assert any(isinstance(v, DataRequired) for v in field_obj.validators)

    def test_field_thesis_is_file(self):
        from se_forms import AddThesisOnReview

        f = AddThesisOnReview()
        assert isinstance(f.thesis, FileField)

    @pytest.mark.parametrize("field", ["supervisor", "type", "area"])
    def test_field_is_select(self, field):
        from se_forms import AddThesisOnReview

        f = AddThesisOnReview()
        assert isinstance(getattr(f, field), SelectField)


class TestEditThesisOnReview:
    @pytest.mark.parametrize(
        ("field", "required"),
        [("name_ru", True), ("author", False)],
    )
    def test_field_is_string(self, field, required):
        from se_forms import EditThesisOnReview

        f = EditThesisOnReview()
        field_obj = getattr(f, field)
        assert isinstance(field_obj, StringField)
        if required:
            assert any(isinstance(v, DataRequired) for v in field_obj.validators)

    def test_field_text_uri_is_file(self):
        from se_forms import EditThesisOnReview

        f = EditThesisOnReview()
        assert isinstance(f.text_uri, FileField)

    @pytest.mark.parametrize(
        ("field", "coerce_is_int"),
        [("supervisor", False), ("type", True), ("area", True)],
    )
    def test_field_is_select(self, field, coerce_is_int):
        from se_forms import EditThesisOnReview

        f = EditThesisOnReview()
        field_obj = getattr(f, field)
        assert isinstance(field_obj, SelectField)
        if coerce_is_int:
            assert field_obj.coerce is int


class TestLecture:
    @pytest.mark.parametrize("field", ["worktype", "course", "supervisor", "startdate", "enddate"])
    def test_field_is_select(self, field):
        from se_forms import Lecture

        f = Lecture()
        assert isinstance(getattr(f, field), SelectField)


class TestAddInternship:
    @pytest.mark.parametrize("field", ["requirements", "description"])
    def test_field_is_textarea(self, field):
        from se_forms import AddInternship

        f = AddInternship()
        field_obj = getattr(f, field)
        assert isinstance(field_obj, StringField)
        assert isinstance(field_obj.widget, TextArea)

    def test_field_company_is_select(self):
        from se_forms import AddInternship

        f = AddInternship()
        assert isinstance(f.company, SelectField)

    @pytest.mark.parametrize("field", ["name_vacancy", "salary", "location", "more_inf", "tag"])
    def test_field_is_string(self, field):
        from se_forms import AddInternship

        f = AddInternship()
        assert isinstance(getattr(f, field), StringField)

    def test_field_format_is_multicheckbox(self):
        from se_forms import AddInternship

        f = AddInternship()
        assert isinstance(f.format, SelectMultipleField)
        assert f.format.coerce is int


class TestInternshipsFilter:
    @pytest.mark.parametrize("field", ["format", "company", "language", "tag"])
    def test_field_is_select(self, field):
        from se_forms import InternshipsFilter

        f = InternshipsFilter()
        assert isinstance(getattr(f, field), SelectField)


class TestCurrentWorktypeArea:
    @pytest.mark.parametrize("field", ["worktype", "area"])
    def test_field_is_select(self, field):
        from se_forms import CurrentWorktypeArea

        f = CurrentWorktypeArea()
        assert isinstance(getattr(f, field), SelectField)


class TestChooseTopic:
    @pytest.mark.parametrize("field", ["topic", "consultant"])
    def test_field_is_string(self, field):
        from se_forms import ChooseTopic

        f = ChooseTopic()
        assert isinstance(getattr(f, field), StringField)

    def test_field_staff_is_select(self):
        from se_forms import ChooseTopic

        f = ChooseTopic()
        assert isinstance(f.staff, SelectField)


class TestDeadlineTemp:
    @pytest.mark.parametrize("field", ["area", "worktype"])
    def test_field_is_optional_select(self, field):
        from se_forms import DeadlineTemp

        f = DeadlineTemp()
        field_obj = getattr(f, field)
        assert isinstance(field_obj, SelectField)
        assert any(isinstance(v, validators.Optional) for v in field_obj.validators)

    @pytest.mark.parametrize(
        "field",
        ["choose_topic", "submit_work_for_review", "upload_reviews", "pre_defense", "defense"],
    )
    def test_field_is_datetime(self, field):
        from se_forms import DeadlineTemp

        f = DeadlineTemp()
        assert isinstance(getattr(f, field), DateTimeField)


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
    @pytest.mark.parametrize("field", ["was_done", "planned_to_do"])
    def test_field_is_textarea(self, field):
        from se_forms import UserAddReport

        f = UserAddReport()
        field_obj = getattr(f, field)
        assert isinstance(field_obj, StringField)
        assert isinstance(field_obj.widget, TextArea)


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

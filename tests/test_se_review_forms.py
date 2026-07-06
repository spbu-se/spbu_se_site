# -*- coding: utf-8 -*-
import pytest
from flask_wtf.file import FileField
from wtforms import RadioField, StringField
from wtforms.widgets import TextArea


@pytest.fixture(autouse=True)
def _form_ctx():
    from flask_se import app

    app.config["WTF_CSRF_ENABLED"] = False
    with app.app_context():
        yield


class TestReviewForm:
    def test_field_review_o1_radio_has_six_choices(self):
        from se_review_forms import ReviewForm

        f = ReviewForm()
        assert isinstance(f.review_o1_radio_switcher, RadioField)
        assert len(f.review_o1_radio_switcher.choices) == 6

    def test_field_review_o1_choices_are_strings_0_to_5(self):
        from se_review_forms import ReviewForm

        f = ReviewForm()
        keys = [k for k, _ in f.review_o1_radio_switcher.choices]
        assert keys == ["5", "4", "3", "2", "1", "0"]

    def test_field_review_o1_comment_is_textarea(self):
        from se_review_forms import ReviewForm

        f = ReviewForm()
        assert isinstance(f.review_o1_comment, StringField)
        assert isinstance(f.review_o1_comment.widget, TextArea)

    def test_field_review_o2_radio_has_six_choices(self):
        from se_review_forms import ReviewForm

        f = ReviewForm()
        assert isinstance(f.review_o2_radio_switcher, RadioField)
        assert len(f.review_o2_radio_switcher.choices) == 6

    def test_field_review_o2_choices_are_strings_0_to_5(self):
        from se_review_forms import ReviewForm

        f = ReviewForm()
        keys = [k for k, _ in f.review_o2_radio_switcher.choices]
        assert keys == ["5", "4", "3", "2", "1", "0"]

    def test_field_review_o2_comment_is_textarea(self):
        from se_review_forms import ReviewForm

        f = ReviewForm()
        assert isinstance(f.review_o2_comment, StringField)
        assert isinstance(f.review_o2_comment.widget, TextArea)

    def test_field_review_t1_radio_has_six_choices(self):
        from se_review_forms import ReviewForm

        f = ReviewForm()
        assert isinstance(f.review_t1_radio_switcher, RadioField)
        assert len(f.review_t1_radio_switcher.choices) == 6

    def test_field_review_t1_choices_are_strings_0_to_5(self):
        from se_review_forms import ReviewForm

        f = ReviewForm()
        keys = [k for k, _ in f.review_t1_radio_switcher.choices]
        assert keys == ["5", "4", "3", "2", "1", "0"]

    def test_field_review_t1_comment_is_textarea(self):
        from se_review_forms import ReviewForm

        f = ReviewForm()
        assert isinstance(f.review_t1_comment, StringField)
        assert isinstance(f.review_t1_comment.widget, TextArea)

    def test_field_review_t2_radio_has_six_choices(self):
        from se_review_forms import ReviewForm

        f = ReviewForm()
        assert isinstance(f.review_t2_radio_switcher, RadioField)
        assert len(f.review_t2_radio_switcher.choices) == 6

    def test_field_review_t2_choices_are_strings_0_to_5(self):
        from se_review_forms import ReviewForm

        f = ReviewForm()
        keys = [k for k, _ in f.review_t2_radio_switcher.choices]
        assert keys == ["5", "4", "3", "2", "1", "0"]

    def test_field_review_t2_comment_is_textarea(self):
        from se_review_forms import ReviewForm

        f = ReviewForm()
        assert isinstance(f.review_t2_comment, StringField)
        assert isinstance(f.review_t2_comment.widget, TextArea)

    def test_field_review_p1_radio_has_seven_choices(self):
        from se_review_forms import ReviewForm

        f = ReviewForm()
        assert isinstance(f.review_p1_radio_switcher, RadioField)
        assert len(f.review_p1_radio_switcher.choices) == 7

    def test_field_review_p1_choices_include_x(self):
        from se_review_forms import ReviewForm

        f = ReviewForm()
        keys = [k for k, _ in f.review_p1_radio_switcher.choices]
        assert keys == ["5", "4", "3", "2", "1", "0", "x"]

    def test_field_review_p1_comment_is_textarea(self):
        from se_review_forms import ReviewForm

        f = ReviewForm()
        assert isinstance(f.review_p1_comment, StringField)
        assert isinstance(f.review_p1_comment.widget, TextArea)

    def test_field_review_p2_radio_has_seven_choices(self):
        from se_review_forms import ReviewForm

        f = ReviewForm()
        assert isinstance(f.review_p2_radio_switcher, RadioField)
        assert len(f.review_p2_radio_switcher.choices) == 7

    def test_field_review_p2_choices_include_x(self):
        from se_review_forms import ReviewForm

        f = ReviewForm()
        keys = [k for k, _ in f.review_p2_radio_switcher.choices]
        assert keys == ["5", "4", "3", "2", "1", "0", "x"]

    def test_field_review_p2_comment_is_textarea(self):
        from se_review_forms import ReviewForm

        f = ReviewForm()
        assert isinstance(f.review_p2_comment, StringField)
        assert isinstance(f.review_p2_comment.widget, TextArea)

    def test_field_review_overall_comment_is_textarea(self):
        from se_review_forms import ReviewForm

        f = ReviewForm()
        assert isinstance(f.review_overall_comment, StringField)
        assert isinstance(f.review_overall_comment.widget, TextArea)

    def test_field_review_verdict_has_two_choices(self):
        from se_review_forms import ReviewForm

        f = ReviewForm()
        assert isinstance(f.review_verdict_radio_switcher, RadioField)
        assert len(f.review_verdict_radio_switcher.choices) == 2

    def test_field_review_verdict_choices_are_1_and_0(self):
        from se_review_forms import ReviewForm

        f = ReviewForm()
        keys = [k for k, _ in f.review_verdict_radio_switcher.choices]
        assert keys == ["1", "0"]

    def test_field_review_file_is_filefield(self):
        from se_review_forms import ReviewForm

        f = ReviewForm()
        assert isinstance(f.review_file, FileField)

# -*- coding: utf-8 -*-
from typing import cast

import pytest
from flask_wtf.file import FileField
from wtforms import RadioField, StringField
from wtforms.widgets import TextArea

# Field-name prefixes whose review grades are 0..5; p1/p2 add an "x" grade.
_SCORE_FIELDS = ("o1", "o2", "t1", "t2", "p1", "p2")


@pytest.fixture(autouse=True)
def _form_ctx():
    from flask_se import app

    app.config["WTF_CSRF_ENABLED"] = False
    with app.app_context():
        yield


class TestReviewForm:
    @pytest.mark.parametrize("prefix", _SCORE_FIELDS)
    def test_score_radio_choice_count(self, prefix):
        from se_review_forms import ReviewForm

        f = ReviewForm()
        field = cast(RadioField, getattr(f, f"review_{prefix}_radio_switcher"))
        assert isinstance(field, RadioField)
        assert len(cast(list[tuple[str, str]], field.choices)) == (
            7 if prefix.startswith("p") else 6
        )

    @pytest.mark.parametrize("prefix", _SCORE_FIELDS)
    def test_score_radio_choice_keys(self, prefix):
        from se_review_forms import ReviewForm

        f = ReviewForm()
        field = cast(RadioField, getattr(f, f"review_{prefix}_radio_switcher"))
        assert isinstance(field, RadioField)
        choices = cast(list[tuple[str, str]], field.choices)
        keys = [k for k, _ in choices]
        expected = ["5", "4", "3", "2", "1", "0"]
        if prefix.startswith("p"):
            expected.append("x")
        assert keys == expected

    @pytest.mark.parametrize("prefix", (*_SCORE_FIELDS, "overall"))
    def test_comment_is_textarea(self, prefix):
        from se_review_forms import ReviewForm

        f = ReviewForm()
        field = getattr(f, f"review_{prefix}_comment")
        assert isinstance(field, StringField)
        assert isinstance(field.widget, TextArea)

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

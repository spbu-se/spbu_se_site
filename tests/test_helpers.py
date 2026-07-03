import pytest


class TestSecureFilename:
    def test_normal_filename(self):
        from flask_se_config import secure_filename
        assert secure_filename("hello.pdf") == "hello.pdf"

    def test_spaces_replaced(self):
        from flask_se_config import secure_filename
        assert secure_filename("my file.txt") == "my_file.txt"

    def test_path_separators_removed(self):
        from flask_se_config import secure_filename
        result = secure_filename("../etc/passwd")
        assert ".." not in result
        assert "/" not in result
        assert result != ""

    def test_special_chars_stripped(self):
        from flask_se_config import secure_filename
        result = secure_filename("hello<world>.pdf")
        assert "<" not in result
        assert ">" not in result
        assert result != ""

    def test_unicode_normalized(self):
        from flask_se_config import secure_filename
        result = secure_filename("café.pdf")
        assert result != ""
        assert " " not in result

    def test_empty_after_strip_returns_empty(self):
        from flask_se_config import secure_filename
        result = secure_filename("...")
        assert result == ""

    def test_leading_trailing_dots_stripped(self):
        from flask_se_config import secure_filename
        result = secure_filename(".hidden.")
        assert not result.startswith(".")
        assert not result.endswith(".")


class TestPostRankingScore:
    def test_default_scores(self):
        from flask_se_config import post_ranking_score
        score = post_ranking_score()
        assert score > 0

    def test_zero_upvotes(self):
        from flask_se_config import post_ranking_score
        score = post_ranking_score(upvotes=0)
        assert score == 0

    def test_more_upvotes_higher_score(self):
        from flask_se_config import post_ranking_score
        low = post_ranking_score(upvotes=1, age=0, views=1)
        high = post_ranking_score(upvotes=10, age=0, views=1)
        assert high > low

    def test_older_posts_lower_score(self):
        from flask_se_config import post_ranking_score
        new = post_ranking_score(upvotes=5, age=1, views=1)
        old = post_ranking_score(upvotes=5, age=100, views=1)
        assert old < new

    def test_more_views_lower_score(self):
        from flask_se_config import post_ranking_score
        few = post_ranking_score(upvotes=5, age=1, views=1)
        many = post_ranking_score(upvotes=5, age=1, views=1000)
        assert many < few


class TestPluralHours:
    def test_less_than_hour(self):
        from flask_se_config import plural_hours
        assert plural_hours(0) == "меньше часа"

    def test_one_hour(self):
        from flask_se_config import plural_hours
        assert plural_hours(1) == "1 час"

    def test_two_hours(self):
        from flask_se_config import plural_hours
        assert plural_hours(2) == "2 часа"

    def test_five_hours(self):
        from flask_se_config import plural_hours
        assert plural_hours(5) == "5 часов"

    def test_21_hours(self):
        from flask_se_config import plural_hours
        assert plural_hours(21) == "21 час"

    def test_exactly_24_hours_returns_one_day(self):
        from flask_se_config import plural_hours
        assert plural_hours(24) == "1 день"

    def test_48_hours_returns_two_days(self):
        from flask_se_config import plural_hours
        assert plural_hours(48) == "2 дня"

    def test_72_hours_returns_three_days(self):
        from flask_se_config import plural_hours
        assert plural_hours(72) == "3 дня"

    def test_100_hours_returns_four_days(self):
        from flask_se_config import plural_hours
        assert plural_hours(100) == "4 дня"

    def test_120_hours_returns_five_days(self):
        from flask_se_config import plural_hours
        assert plural_hours(120) == "5 дней"


class TestGetThesisTypeIdString:
    def test_valid_id(self):
        from flask_se_config import get_thesis_type_id_string
        assert get_thesis_type_id_string(1) == "Bachelor_Report"

    def test_another_valid_id(self):
        from flask_se_config import get_thesis_type_id_string
        assert get_thesis_type_id_string(3) == "Master_Thesis"

    def test_last_valid_id(self):
        from flask_se_config import get_thesis_type_id_string
        assert get_thesis_type_id_string(9) == "Pre_graduate_practice"


class TestAllowedFile:
    def test_pdf_allowed(self):
        from flask_se_practice_config import allowed_file
        assert allowed_file("document.pdf") is True

    def test_uppercase_extension(self):
        from flask_se_practice_config import allowed_file
        assert allowed_file("document.PDF") is True

    def test_no_extension(self):
        from flask_se_practice_config import allowed_file
        assert allowed_file("document") is False

    def test_empty_filename(self):
        from flask_se_practice_config import allowed_file
        assert allowed_file("") is False

    def test_dot_only(self):
        from flask_se_practice_config import allowed_file
        assert allowed_file(".") is False

    def test_wrong_extension(self):
        from flask_se_practice_config import allowed_file
        assert allowed_file("document.exe") is False

    def test_multiple_dots(self):
        from flask_se_practice_config import allowed_file
        assert allowed_file("file.backup.pdf") is True

    def test_avatar_png_allowed(self):
        from flask_se_auth import allowed_file as auth_allowed_file
        assert auth_allowed_file("avatar.png") is True

    def test_avatar_pdf_not_allowed(self):
        from flask_se_auth import allowed_file as auth_allowed_file
        assert auth_allowed_file("avatar.pdf") is False

    def test_review_pdf_allowed(self):
        from flask_se_review import allowed_file as review_allowed_file
        assert review_allowed_file("review.pdf") is True

    def test_review_exe_not_allowed(self):
        from flask_se_review import allowed_file as review_allowed_file
        assert review_allowed_file("review.exe") is False

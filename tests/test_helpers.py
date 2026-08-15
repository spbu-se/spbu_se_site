# -*- coding: utf-8 -*-
import pytest

from flask_se_auth import allowed_file as auth_allowed
from flask_se_config import (
    get_thesis_type_id_string,
    plural_hours,
    post_ranking_score,
    secure_filename,
)
from flask_se_practice_config import allowed_file as practice_allowed
from flask_se_review import allowed_file as review_allowed


class TestSecureFilename:
    def test_normal_filename(self):
        assert secure_filename("hello.pdf") == "hello.pdf"

    def test_spaces_replaced(self):
        assert secure_filename("my file.txt") == "my_file.txt"

    def test_path_separators_removed(self):
        result = secure_filename("../etc/passwd")
        assert ".." not in result
        assert "/" not in result
        assert result != ""

    def test_special_chars_stripped(self):
        result = secure_filename("hello<world>.pdf")
        assert "<" not in result
        assert ">" not in result
        assert result != ""

    def test_unicode_normalized(self):
        result = secure_filename("cafГ©.pdf")
        assert result != ""
        assert " " not in result

    def test_empty_after_strip_returns_empty(self):
        assert secure_filename("...") == ""

    def test_leading_trailing_dots_stripped(self):
        result = secure_filename(".hidden.")
        assert not result.startswith(".")
        assert not result.endswith(".")

    @pytest.mark.parametrize("name", ["", ".", "..", "...", " ", "  "])
    def test_edge_empty_or_dots(self, name):
        assert secure_filename(name) == ""

    @pytest.mark.parametrize("name", ["a" * 256, "a" * 1024])
    def test_very_long_filename(self, name):
        result = secure_filename(name)
        assert isinstance(result, str)

    def test_oversized_unicode_filename_bounded(self):
        result = secure_filename("\u2101" * 5_000_000 + ".bmp")
        assert isinstance(result, str)

    def test_normalize_receives_truncated_input(self, monkeypatch):
        from flask_se_config import normalize as config_normalize

        calls = []
        real_normalize = config_normalize

        def spy(form, string):
            calls.append(len(string))
            return real_normalize(form, string)

        monkeypatch.setattr("flask_se_config.normalize", spy)
        secure_filename("\u2101" * 1_000_000 + ".bmp")
        assert calls
        assert calls[0] <= 255

    @pytest.mark.parametrize("name", ["file\u0000.txt", "file\n.txt", "file\t.txt"])
    def test_null_and_control_chars(self, name):
        result = secure_filename(name)
        assert "\u0000" not in result
        assert isinstance(result, str)

    def test_only_special_chars(self):
        assert secure_filename('<>:"/\\|?*') == ""


class TestPostRankingScore:
    def test_default_scores(self):
        assert post_ranking_score() > 0

    def test_zero_upvotes(self):
        assert post_ranking_score(upvotes=0) == 0

    def test_more_upvotes_higher_score(self):
        low = post_ranking_score(upvotes=1, age=0, views=1)
        high = post_ranking_score(upvotes=10, age=0, views=1)
        assert high > low

    def test_older_posts_lower_score(self):
        new = post_ranking_score(upvotes=5, age=1, views=1)
        old = post_ranking_score(upvotes=5, age=100, views=1)
        assert old < new

    def test_more_views_lower_score(self):
        few = post_ranking_score(upvotes=5, age=1, views=1)
        many = post_ranking_score(upvotes=5, age=1, views=1000)
        assert many < few

    @pytest.mark.parametrize(
        "upvotes,age,views",
        [
            (-1, 0, 0),
            (0, -1, 0),
            (0, 0, -1),
            (-100, -100, -100),
        ],
    )
    def test_negative_values(self, upvotes, age, views):
        result = post_ranking_score(upvotes=upvotes, age=age, views=views)
        assert result >= 0

    @pytest.mark.parametrize(
        "upvotes,views",
        [
            (10**6, 1),
            (1, 10**6),
            (10**9, 10**9),
        ],
    )
    def test_large_values(self, upvotes, views):
        result = post_ranking_score(upvotes=upvotes, age=0, views=views)
        assert result >= 0


class TestPluralHours:
    @pytest.mark.parametrize(
        "hours,expected",
        [
            (0, "меньше часа"),
            (1, "1 час"),
            (2, "2 часа"),
            (5, "5 часов"),
            (21, "21 час"),
            (24, "24 часа"),
            (25, "1 день"),
            (48, "2 дня"),
            (72, "3 дня"),
            (100, "4 дня"),
            (120, "5 дней"),
        ],
    )
    def test_plural_hours(self, hours, expected):
        assert plural_hours(hours) == expected

    @pytest.mark.parametrize("hours", [-1, -24, -100])
    def test_negative_hours(self, hours):
        result = plural_hours(hours)
        assert isinstance(result, str)
        assert len(result) > 0

    @pytest.mark.parametrize("hours", [168, 720, 8760])
    def test_large_hours(self, hours):
        result = plural_hours(hours)
        assert isinstance(result, str)
        assert len(result) > 0


class TestGetThesisTypeIdString:
    def test_id_1_returns_empty(self):
        assert get_thesis_type_id_string(1) == ""

    def test_id_2_returns_bachelor_report(self):
        assert get_thesis_type_id_string(2) == "Bachelor_Report"

    def test_id_4_returns_master_thesis(self):
        assert get_thesis_type_id_string(4) == "Master_Thesis"

    def test_id_10_returns_pre_graduate(self):
        assert get_thesis_type_id_string(10) == "Pre_graduate_practice"

    @pytest.mark.parametrize("tid", [0, -1, 999, -999])
    def test_edge_ids(self, tid):
        assert get_thesis_type_id_string(tid) == ""


class TestAllowedFile:
    @pytest.mark.parametrize(
        "func,name,expected",
        [
            (practice_allowed, "document.pdf", True),
            (practice_allowed, "document.PDF", True),
            (practice_allowed, "document", False),
            (practice_allowed, "", False),
            (practice_allowed, ".", False),
            (practice_allowed, "document.exe", False),
            (practice_allowed, "file.backup.pdf", True),
            (auth_allowed, "avatar.png", True),
            (auth_allowed, "avatar.pdf", False),
            (review_allowed, "review.pdf", True),
            (review_allowed, "review.exe", False),
        ],
    )
    def test_allowed_file(self, func, name, expected):
        assert func(name) is expected

    @pytest.mark.parametrize("name", [".pdf", ".PDF", ".png", ".PNG"])
    def test_extension_only(self, name):
        result = practice_allowed(name)
        assert isinstance(result, bool)

    @pytest.mark.parametrize("name", ["a" * 256 + ".pdf", "a.b.c.d.e.pdf"])
    def test_long_and_deep_paths(self, name):
        result = practice_allowed(name)
        assert isinstance(result, bool)

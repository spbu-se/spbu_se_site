# -*- coding: utf-8 -*-
import pytest
from conftest import assert_ok

PAGES = [
    "/bachelor/application.html",
    "/bachelor/programming-technology.html",
    "/bachelor/software-engineering.html",
    "/bachelor/admission.html",
]
SEEDED_PAGES = PAGES[1:]


class TestBachelorPages:
    @pytest.mark.parametrize("path", PAGES)
    def test_page_loads_without_db(self, client, path):
        assert_ok(client, path)

    @pytest.mark.parametrize("path", SEEDED_PAGES)
    def test_page_loads_with_seeded_db(self, seeded_client, path):
        assert_ok(seeded_client, path)


class TestBachelorScoreInfo:
    def test_score_dataclass_has_expected_fields(self):
        from flask_se_bachelor import Score

        s = Score(
            pass_rate=250,
            budget_count=30,
            contract_count=10,
            cost_year="300 000",
            min_score_computer_science=60,
            min_score_math=55,
            min_score_russian_language=45,
        )
        assert s.pass_rate == 250
        assert s.budget_count == 30
        assert s.contract_count == 10
        assert s.cost_year == "300 000"
        assert s.min_score_computer_science == 60
        assert s.min_score_math == 55
        assert s.min_score_russian_language == 45

    def test_bachelor_info_dataclass_has_expected_fields(self):
        from flask_se_bachelor import BachelorInfo, Score

        se = Score(
            pass_rate=282,
            budget_count=45,
            contract_count=12,
            cost_year="396 500",
            min_score_computer_science=55,
            min_score_math=55,
            min_score_russian_language=50,
        )
        info = BachelorInfo(
            score_url="https://example.com/score.pdf",
            cost_url="https://example.com/cost.pdf",
            min_score_and_count_url="https://example.com/min.pdf",
            year=2025,
            se=se,
            tp=se,
        )
        assert info.score_url == "https://example.com/score.pdf"
        assert info.cost_url == "https://example.com/cost.pdf"
        assert info.min_score_and_count_url == "https://example.com/min.pdf"
        assert info.year == 2025

    @pytest.mark.parametrize(
        ("attr", "expected"),
        [
            ("year", 2025),
            ("se.pass_rate", 282),
            ("tp.pass_rate", 252),
        ],
    )
    def test_bachelor_score_info(self, attr, expected):
        from flask_se_bachelor import bachelor_score_info

        value = bachelor_score_info
        for part in attr.split("."):
            value = getattr(value, part)
        assert value == expected

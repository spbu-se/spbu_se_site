# -*- coding: utf-8 -*-
from conftest import assert_ok


class TestBachelorApplication:
    def test_application_page_loads(self, client):
        assert_ok(client, "/bachelor/application.html")


class TestBachelorProgrammingTechnology:
    def test_programming_technology_page_loads_without_db(self, client):
        assert_ok(client, "/bachelor/programming-technology.html")

    def test_programming_technology_page_loads_with_seeded_db(self, seeded_client):
        assert_ok(seeded_client, "/bachelor/programming-technology.html")


class TestBachelorSoftwareEngineering:
    def test_software_engineering_page_loads_without_db(self, client):
        assert_ok(client, "/bachelor/software-engineering.html")

    def test_software_engineering_page_loads_with_seeded_db(self, seeded_client):
        assert_ok(seeded_client, "/bachelor/software-engineering.html")


class TestBachelorAdmission:
    def test_admission_page_loads_without_db(self, client):
        assert_ok(client, "/bachelor/admission.html")

    def test_admission_page_loads_with_seeded_db(self, seeded_client):
        assert_ok(seeded_client, "/bachelor/admission.html")


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

    def test_bachelor_score_info_module_level_has_correct_year(self):
        from flask_se_bachelor import bachelor_score_info

        assert bachelor_score_info.year == 2025

    def test_bachelor_score_info_se_has_correct_pass_rate(self):
        from flask_se_bachelor import bachelor_score_info

        assert bachelor_score_info.se.pass_rate == 282

    def test_bachelor_score_info_tp_has_correct_pass_rate(self):
        from flask_se_bachelor import bachelor_score_info

        assert bachelor_score_info.tp.pass_rate == 252

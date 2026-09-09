# -*- coding: utf-8 -*-
import re


def _select_block(html, name):
    match = re.search(rf'<select[^>]*name="{re.escape(name)}".*?</select>', html, re.S)
    return match.group(0) if match else ""


class TestCurrentThesisFkLabels:
    """FK dropdowns to Staff/lookup tables must show names, not #<id> fallbacks."""

    def test_supervisor_area_worktype_options_are_named(self, admin_client):
        html = admin_client.get("/admin/currentthesis/new/").get_data(as_text=True)
        for name in ("supervisor_id", "area_id", "worktype_id"):
            block = _select_block(html, name)
            assert block, f"{name} is not rendered as a select"
            assert not re.search(r"<option[^>]*>\s*#[0-9]+\s*</option>", block), (
                f"{name} contains #<id> label fallbacks"
            )
            assert block.count("<option") >= 3, f"{name} has too few options"

    def test_supervisor_options_are_full_names_not_emails(self, admin_client):
        html = admin_client.get("/admin/currentthesis/new/").get_data(as_text=True)
        block = _select_block(html, "supervisor_id")
        assert re.search(r"[А-ЯЁ][а-яё-]+ [А-ЯЁ]\. [А-ЯЁ]\.", block), (
            "staff options must be Фамилия И.О. labels"
        )

    def test_duplicate_areas_are_disambiguated(self, admin_client):
        html = admin_client.get("/admin/currentthesis/new/").get_data(as_text=True)
        block = _select_block(html, "area_id")
        assert "Программная инженерия (бак)" in block
        assert "Программная инженерия (маг)" in block
        assert "Технологии программирования" in block


class TestCurrentThesisStatusSelect:
    def test_status_is_a_select_with_both_choices(self, admin_client):
        html = admin_client.get("/admin/currentthesis/new/").get_data(as_text=True)
        block = _select_block(html, "status")
        assert block, "status must render as a select"
        assert 'value="1"' in block and 'value="2"' in block
        assert "Текущая работа" in block and "Завершенная работа" in block


class TestStaffScienceDegreeSelect:
    def test_science_degree_renders_as_select(self, admin_client):
        html = admin_client.get("/admin/staff/new/").get_data(as_text=True)
        assert html, "staff create form must render (no crash)"
        block = _select_block(html, "science_degree")
        assert block, "science_degree must render as a select"
        assert "д.ф.-м.н." in block

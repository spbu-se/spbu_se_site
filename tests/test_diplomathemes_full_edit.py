# -*- coding: utf-8 -*-
import re

import pytest


@pytest.fixture
def level_ids():
    from se_models import ThemesLevel

    ids = [level.id for level in ThemesLevel.query.order_by(ThemesLevel.id).all()]
    if len(ids) < 2:
        pytest.skip("seed data has fewer than two ThemesLevel rows")
    return ids


def _get_theme(theme_id):
    from se_models import DiplomaThemes

    return DiplomaThemes.query.filter_by(id=theme_id).first()


def _levels(theme):
    return [row.id for row in theme.levels]


def _edit_data(title, levels, status="2"):
    return {
        "title": title,
        "description": "D",
        "requirements": "R",
        "comment": "",
        "status": status,
        "author_id": "1",
        "consultant_id": "1",
        "levels": [str(level_id) for level_id in levels],
    }


class TestLevelsMultiSelect:
    def test_levels_render_as_multi_select_with_current_values(
        self, admin_client, make_theme, level_ids
    ):
        theme_id = make_theme(levels=[level_ids[0]])
        html = admin_client.get(f"/admin/diplomathemes/edit/?id={theme_id}").get_data(as_text=True)
        block = re.search(r'<select[^>]*name="levels".*?</select>', html, re.S)
        assert block, "levels multi-select missing on the edit form"
        assert f'value="{level_ids[0]}"' in block.group(0)
        assert re.search(
            rf'<option(?=[^>]*\bselected\b)[^>]*value="{level_ids[0]}"', block.group(0)
        )

    def test_levels_save_round_trip_without_duplicates(self, admin_client, make_theme, level_ids):
        theme_id = make_theme(levels=[level_ids[0]])
        resp = admin_client.post(
            f"/admin/diplomathemes/edit/?id={theme_id}",
            data=_edit_data("Updated Levels", levels=[level_ids[0], level_ids[1]]),
        )
        assert resp.status_code == 302
        theme = _get_theme(theme_id)
        assert set(_levels(theme)) == {level_ids[0], level_ids[1]}

        resp = admin_client.post(
            f"/admin/diplomathemes/edit/?id={theme_id}",
            data=_edit_data("Updated Levels Again", levels=[level_ids[0]]),
        )
        assert resp.status_code == 302
        theme = _get_theme(theme_id)
        assert _levels(theme) == [level_ids[0]]

    def test_review_edit_view_has_no_levels_field(self, reviewer_client, make_theme, level_ids):
        theme_id = make_theme(status=0, levels=[level_ids[0]])
        html = reviewer_client.get(f"/admin/reviewdiplomathemes/edit/?id={theme_id}").get_data(
            as_text=True
        )
        assert 'name="levels"' not in html, "reviewer queue form must stay minimal"


class TestApprovedReachabilityAndStatusFilter:
    def test_status_filter(self, admin_client, make_theme):
        make_theme(title="Approved Only", status=2)
        make_theme(title="Archived Only", status=3)
        make_theme(title="Queued Only", status=0)

        html2 = admin_client.get("/admin/diplomathemes/?status=2").get_data(as_text=True)
        assert (
            "Approved Only" in html2 and "Archived Only" not in html2 and "Queued Only" not in html2
        )
        html3 = admin_client.get("/admin/diplomathemes/?status=3").get_data(as_text=True)
        assert "Archived Only" in html3 and "Approved Only" not in html3
        html0 = admin_client.get("/admin/diplomathemes/?status=0").get_data(as_text=True)
        assert "Queued Only" in html0 and "Approved Only" not in html0

    def test_approved_theme_fully_editable(self, admin_client, make_theme, level_ids):
        theme_id = make_theme(title="Approved Old", status=2, levels=[level_ids[0]])
        resp = admin_client.post(
            f"/admin/diplomathemes/edit/?id={theme_id}",
            data=_edit_data("Approved New Title", levels=[level_ids[0], level_ids[1]]),
        )
        assert resp.status_code == 302
        theme = _get_theme(theme_id)
        assert theme.title == "Approved New Title"
        assert theme.status == 2, "editing must not change the approved status"
        assert set(_levels(theme)) == {level_ids[0], level_ids[1]}

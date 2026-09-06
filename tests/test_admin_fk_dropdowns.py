# -*- coding: utf-8 -*-
import re

import pytest


@pytest.fixture
def make_theme():
    def _make(title, status=0, company_id=None, author_id=1, consultant_id=1):
        from se_models import DiplomaThemes, db

        dt = DiplomaThemes(
            title=title,
            description="Desc",
            requirements="Req",
            author_id=author_id,
            consultant_id=consultant_id,
            company_id=company_id,
            status=status,
        )
        db.session.add(dt)
        db.session.commit()
        return dt.id

    return _make


def _get_theme(theme_id):
    from se_models import DiplomaThemes

    return DiplomaThemes.query.filter_by(id=theme_id).first()


def _edit_url(theme_id):
    return f"/admin/reviewdiplomathemes/edit/?id={theme_id}"


def _select_block(html, name):
    match = re.search(rf'<select[^>]*name="{name}".*?</select>', html, re.S)
    return match.group(0) if match else ""


class TestFkFieldsRenderAsSelects:
    """Issue #276: FK columns render as dropdowns, not raw integer inputs."""

    def test_fk_fields_are_selects_not_raw_inputs(self, reviewer_client, make_theme):
        theme_id = make_theme("Select Theme", status=0, company_id=None)
        resp = reviewer_client.get(_edit_url(theme_id))
        assert resp.status_code == 200
        html = resp.get_data(as_text=True)

        for fk in (
            "author_id",
            "consultant_id",
            "company_id",
            "supervisor_id",
            "supervisor_thesis_id",
        ):
            assert re.search(rf'<select[^>]*name="{fk}"', html), f"{fk} is not a select"
        assert not re.search(
            r'<input[^>]*name="(author_id|consultant_id|supervisor_id|supervisor_thesis_id|company_id)"',
            html,
        )

    def test_current_value_is_present_and_nullable_gets_empty_option(
        self, reviewer_client, make_theme
    ):
        theme_id = make_theme("Select Values", status=0, company_id=None)
        html = reviewer_client.get(_edit_url(theme_id)).get_data(as_text=True)

        author_select = _select_block(html, "author_id")
        assert author_select and 'value="1"' in author_select, "current author not among options"

        company_select = _select_block(html, "company_id")
        assert company_select and "—" in company_select, "nullable FK lacks empty option"

    def test_empty_non_null_fk_shows_validation_error(self, reviewer_client, make_theme):
        theme_id = make_theme("Empty FK Theme", status=0)
        resp = reviewer_client.post(
            _edit_url(theme_id),
            data={
                "title": "Empty FK Theme",
                "description": "D",
                "requirements": "R",
                "author_id": "",
            },
        )
        assert resp.status_code == 200, "empty non-null FK must not crash with 500"
        theme = _get_theme(theme_id)
        assert theme.author_id == 1 and theme.status == 0, "failed validation must not commit"

    def test_fk_select_submit_persists(self, reviewer_client, make_theme):
        theme_id = make_theme("Change Company", status=0, company_id=None)
        resp = reviewer_client.post(
            _edit_url(theme_id),
            data={
                "title": "Change Company",
                "description": "D",
                "requirements": "R",
                "status": "2",
                "author_id": "1",
                "consultant_id": "1",
                "company_id": "1",
            },
        )
        assert resp.status_code == 302
        theme = _get_theme(theme_id)
        assert theme.company_id == 1 and theme.status == 2


class TestQueueSearchAndFilter:
    """Issue #276: queue keeps status<2 and supports search + status filter."""

    def test_search_filters_queued_and_excludes_approved(self, reviewer_client, make_theme):
        make_theme("Alpha SearchUnique", status=0)
        make_theme("Approved SearchUniqueButApproved", status=2)

        resp = reviewer_client.get("/admin/reviewdiplomathemes/?search=SearchUnique")
        assert resp.status_code == 200
        html = resp.get_data(as_text=True)
        assert "Alpha SearchUnique" in html
        assert "Approved SearchUniqueButApproved" not in html, (
            "approved theme leaked into the queue"
        )

    def test_status_filter(self, reviewer_client, make_theme):
        make_theme("Alpha StatusZero", status=0)
        make_theme("Beta NeedsWork", status=1)

        resp = reviewer_client.get("/admin/reviewdiplomathemes/?status=1")
        html = resp.get_data(as_text=True)
        assert "Beta NeedsWork" in html
        assert "Alpha StatusZero" not in html

    def test_combined_search_and_status(self, reviewer_client, make_theme):
        make_theme("Gamma Shared status-zero", status=0)
        make_theme("Delta Shared needs-work", status=1)

        resp = reviewer_client.get("/admin/reviewdiplomathemes/?search=Shared&status=1")
        html = resp.get_data(as_text=True)
        assert "Delta Shared needs-work" in html
        assert "Gamma Shared status-zero" not in html

    def test_filter_form_shows_reset_and_keeps_value(self, reviewer_client, make_theme):
        make_theme("Alpha SearchUnique", status=0)
        resp = reviewer_client.get("/admin/reviewdiplomathemes/?search=SearchUnique")
        html = resp.get_data(as_text=True)
        assert 'name="search"' in html and 'value="SearchUnique"' in html
        assert "Сброс" in html, "reset link missing when a filter is active"

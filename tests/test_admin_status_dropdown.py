# -*- coding: utf-8 -*-
import re
from types import SimpleNamespace


def _get_theme(theme_id):
    from se_models import DiplomaThemes

    return DiplomaThemes.query.filter_by(id=theme_id).first()


def _status_block(html):
    match = re.search(r'<select[^>]*name="status".*?</select>', html, re.S)
    return match.group(0) if match else ""


def _status_option_values(html):
    block = _status_block(html)
    return re.findall(r'value="(\d+)"', block)


class TestDiplomaStatusEditDropdown:
    """Status 3 (В архиве) is a display/transition value, not a free-form choice.

    It appears in the edit form only when editing an already-archived theme
    (so the current value prefills and an unchanged save does not reset it);
    new/non-archived rows must never offer it.
    """

    def test_archived_row_offers_and_preselects_3(self, admin_client, make_theme):
        theme_id = make_theme(status=2)
        assert (
            admin_client.post("/admin/diplomathemes/archive/", data={"id": theme_id}).status_code
            == 302
        )
        theme = _get_theme(theme_id)
        assert theme.status == 3 and theme.prev_status == 2

        html = admin_client.get(f"/admin/diplomathemes/edit/?id={theme_id}").get_data(as_text=True)
        values = _status_option_values(html)
        assert "3" in values, "archived row edit form must offer status 3"

    def test_non_archived_form_never_offers_3(self, admin_client, make_theme):
        theme_id = make_theme(status=2)
        html = admin_client.get(f"/admin/diplomathemes/edit/?id={theme_id}").get_data(as_text=True)
        assert "3" not in _status_option_values(html)

    def test_create_form_never_offers_3(self, admin_client):
        html = admin_client.get("/admin/diplomathemes/new/").get_data(as_text=True)
        assert "3" not in _status_option_values(html)


class TestDiplomaStatusGuard:
    """Archive/reopen transitions belong to the dedicated actions (prev_status
    bookkeeping); the edit form must never reach or leave status 3."""

    def _view(self):
        from flask_se_admin import SeAdminModelViewDiplomaThemes

        return object.__new__(SeAdminModelViewDiplomaThemes)

    def _data(self, value):
        return SimpleNamespace(status=SimpleNamespace(data=value))

    def test_staying_archived_is_allowed(self):
        assert self._view().form_change_error(SimpleNamespace(status=3), self._data(3)) is None

    def test_normal_transition_between_workflow_states_is_allowed(self):
        assert self._view().form_change_error(SimpleNamespace(status=2), self._data(1)) is None

    def test_form_cannot_archive_a_theme(self):
        assert self._view().form_change_error(SimpleNamespace(status=2), self._data(3))

    def test_form_cannot_unarchive_a_theme(self):
        assert self._view().form_change_error(SimpleNamespace(status=3), self._data(1))

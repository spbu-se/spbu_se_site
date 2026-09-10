# -*- coding: utf-8 -*-
"""Admin supervisor dropdowns list only active staff (SSOT eligibility).

Guards the prod defect where ``DiplomaThemes.supervisor_id`` /
``supervisor_thesis_id`` (FK -> ``users.id``) offered every account, and
``CurrentThesis.supervisor_id`` (FK -> ``staff.id``) offered inactive staff.
Eligibility is the single-source ``Staff.active_query`` /
``Users.eligible_supervisors_query`` rule, and an already-stored supervisor is
preserved even when no longer eligible.
"""

import re

from se_models import CurrentThesis, DiplomaThemes, Staff, Users, db


def _select_block(html, name):
    match = re.search(rf'<select[^>]*name="{re.escape(name)}".*?</select>', html, re.S)
    return match.group(0) if match else ""


def _option_values(block):
    return {int(value) for value in re.findall(r'<option value="(\d+)"', block)}


def _active_staff():
    return Staff.query.filter_by(still_working=True).first()


def _inactive_staff():
    return Staff.query.filter_by(still_working=False).first()


def _non_staff_user_id():
    return Users.query.filter_by(email="user@se.dev").first().id


def _review_edit_url(theme_id):
    return f"/admin/reviewdiplomathemes/edit/?id={theme_id}"


def _theme(theme_id):
    theme = db.session.get(DiplomaThemes, theme_id)
    assert theme is not None
    return theme


class TestReviewSupervisorDropdownEligibility:
    def test_only_active_staff_users_are_offered(self, reviewer_client, make_theme):
        theme_id = make_theme("Eligibility Theme", status=0, company_id=None)
        html = reviewer_client.get(_review_edit_url(theme_id)).get_data(as_text=True)
        for field in ("supervisor_id", "supervisor_thesis_id"):
            block = _select_block(html, field)
            assert block, f"{field} is not rendered as a select"
            values = _option_values(block)
            assert _non_staff_user_id() not in values, f"{field} offers a non-staff account"
            assert _inactive_staff().user_id not in values, f"{field} offers inactive staff"
            assert _active_staff().user_id in values, f"{field} is missing active staff"

    def test_consultant_and_author_stay_open(self, reviewer_client, make_theme):
        theme_id = make_theme("Open Fields Theme", status=0, company_id=None)
        html = reviewer_client.get(_review_edit_url(theme_id)).get_data(as_text=True)
        non_staff = _non_staff_user_id()
        assert non_staff in _option_values(_select_block(html, "consultant_id"))
        assert non_staff in _option_values(_select_block(html, "author_id"))

    def test_existing_inactive_supervisor_is_preserved_with_label(
        self, reviewer_client, make_theme
    ):
        inactive = _inactive_staff()
        theme_id = make_theme("Preserve Theme", status=0, company_id=None)
        theme = _theme(theme_id)
        theme.supervisor_id = inactive.user_id
        db.session.commit()

        block = _select_block(
            reviewer_client.get(_review_edit_url(theme_id)).get_data(as_text=True),
            "supervisor_id",
        )
        assert f'value="{inactive.user_id}"' in block
        assert "(не найден)" not in block
        assert inactive.user.last_name in block

    def test_edit_rejects_change_to_ineligible_supervisor(self, reviewer_client, make_theme):
        theme_id = make_theme("Reject Theme", status=0, company_id=None)
        db.session.expire_all()
        before = _theme(theme_id).supervisor_id
        resp = reviewer_client.post(
            _review_edit_url(theme_id),
            data={
                "title": "Reject Theme",
                "description": "D",
                "requirements": "R",
                "status": "0",
                "author_id": "1",
                "consultant_id": "1",
                "supervisor_id": str(_non_staff_user_id()),
            },
        )
        assert resp.status_code == 200
        db.session.expire_all()
        assert _theme(theme_id).supervisor_id == before

    def test_keeping_existing_inactive_supervisor_is_allowed(self, reviewer_client, make_theme):
        inactive = _inactive_staff()
        theme_id = make_theme("Keep Theme", status=0, company_id=None)
        theme = _theme(theme_id)
        theme.supervisor_id = inactive.user_id
        db.session.commit()

        resp = reviewer_client.post(
            _review_edit_url(theme_id),
            data={
                "title": "Keep Theme",
                "description": "D",
                "requirements": "R",
                "status": "0",
                "author_id": "1",
                "consultant_id": "1",
                "supervisor_id": str(inactive.user_id),
            },
        )
        assert resp.status_code == 302
        db.session.expire_all()
        assert _theme(theme_id).supervisor_id == inactive.user_id


class TestCurrentThesisSupervisorDropdownEligibility:
    def test_inactive_staff_excluded(self, admin_client):
        html = admin_client.get("/admin/currentthesis/new/").get_data(as_text=True)
        values = _option_values(_select_block(html, "supervisor_id"))
        assert _inactive_staff().id not in values
        assert _active_staff().id in values

    def test_create_rejects_ineligible_supervisor(self, admin_client):
        resp = admin_client.post(
            "/admin/currentthesis/new/",
            data={
                "title": "Bad Supervisor Thesis",
                "author_id": "1",
                "worktype_id": "1",
                "area_id": "1",
                "status": "1",
                "supervisor_id": str(_inactive_staff().id),
            },
        )
        assert resp.status_code == 200
        assert CurrentThesis.query.filter_by(title="Bad Supervisor Thesis").first() is None

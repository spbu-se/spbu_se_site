# -*- coding: utf-8 -*-
import se_seed_data
from se_models import Staff, Users


def test_seed_accounts_roles_and_staff(seeded_client):
    for account in se_seed_data.ROLE_ACCOUNTS + se_seed_data.STAFF_ACCOUNTS:
        user = Users.query.filter_by(email=account["email"]).first()
        assert user is not None
        assert user.role == account["role"]
        has_staff = Staff.query.filter_by(user_id=user.id).first() is not None
        assert has_staff == bool(account.get("staff"))


def test_admin_can_open_admin_users(admin_client):
    assert admin_client.get("/admin/users/").status_code == 200


def test_reviewer_cannot_open_admin_users(reviewer_client):
    assert reviewer_client.get("/admin/users/").status_code == 302


def test_thesis_cannot_open_admin_users(thesis_client):
    assert thesis_client.get("/admin/users/").status_code == 302


def test_user_cannot_open_admin_users(user_client):
    assert user_client.get("/admin/users/").status_code == 302


def test_reviewer_can_open_review_queue(reviewer_client):
    assert reviewer_client.get("/admin/reviewdiplomathemes/").status_code == 200


def test_thesis_cannot_open_review_queue(thesis_client):
    assert thesis_client.get("/admin/reviewdiplomathemes/").status_code == 302


def test_user_cannot_open_review_queue(user_client):
    assert user_client.get("/admin/reviewdiplomathemes/").status_code == 302

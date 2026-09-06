# -*- coding: utf-8 -*-


def _get_theme(theme_id):
    from se_models import DiplomaThemes

    return DiplomaThemes.query.filter_by(id=theme_id).first()


def _notifications(user_id):
    from se_models import Notification

    return Notification.query.filter_by(recipient=user_id).all()


class TestAuthorArchivePreservesStatus:
    """Author self archive/unarchive must not destroy approved/rejected status."""

    def test_approved_theme_returns_to_catalog_on_unarchive(self, logged_client, make_theme):
        theme_id = make_theme(status=2)
        assert (
            logged_client.post("/diplomas/archive_theme", data={"theme_id": theme_id}).status_code
            == 302
        )
        theme = _get_theme(theme_id)
        assert theme.status == 3 and theme.prev_status == 2
        assert (
            logged_client.post("/diplomas/unarchive_theme", data={"theme_id": theme_id}).status_code
            == 302
        )
        theme = _get_theme(theme_id)
        assert theme.status == 2, "approved theme must return to the catalog, not the queue"
        assert theme.prev_status is None

    def test_unreviewed_theme_still_reenters_the_queue(self, logged_client, make_theme):
        theme_id = make_theme(status=0)
        logged_client.post("/diplomas/archive_theme", data={"theme_id": theme_id})
        logged_client.post("/diplomas/unarchive_theme", data={"theme_id": theme_id})
        theme = _get_theme(theme_id)
        assert theme.status == 0 and theme.prev_status is None


class TestAdminSingleArchiveReopen:
    def test_admin_archive_approved_mails_author_once(self, admin_client, make_theme):
        theme_id = make_theme(status=2)
        resp = admin_client.post("/admin/diplomathemes/archive/", data={"id": theme_id})
        assert resp.status_code == 302
        theme = _get_theme(theme_id)
        assert theme.status == 3 and theme.prev_status == 2
        mails = _notifications(1)
        assert len(mails) == 1 and mails[0].title == "[SE site] Ваша тема архивирована"

    def test_admin_reopen_restores_approved(self, admin_client, make_theme):
        theme_id = make_theme(status=2)
        admin_client.post("/admin/diplomathemes/archive/", data={"id": theme_id})
        resp = admin_client.post("/admin/diplomathemes/reopen/", data={"id": theme_id})
        assert resp.status_code == 302
        theme = _get_theme(theme_id)
        assert theme.status == 2 and theme.prev_status is None

    def test_admin_reopen_legacy_archived_falls_back_to_queue(self, admin_client, make_theme):
        from se_models import db

        theme_id = make_theme(status=3)
        theme = _get_theme(theme_id)
        theme.prev_status = None
        db.session.commit()
        admin_client.post("/admin/diplomathemes/reopen/", data={"id": theme_id})
        theme = _get_theme(theme_id)
        assert theme.status == 0 and theme.prev_status is None

    def test_reviewer_cannot_archive(self, reviewer_client, make_theme):
        theme_id = make_theme(status=2)
        resp = reviewer_client.post("/admin/diplomathemes/archive/", data={"id": theme_id})
        assert resp.status_code in (301, 302, 401, 403)
        theme = _get_theme(theme_id)
        assert theme.status == 2, "role 3 must not archive on the role >= 5 view"

    def test_archive_buttons_render_on_list_and_prev_status_not_editable(
        self, admin_client, make_theme
    ):
        queued_id = make_theme(status=0, title="Queued For Archive")
        make_theme(status=3, title="Archived To Reopen")
        html = admin_client.get("/admin/diplomathemes/").get_data(as_text=True)
        assert "/admin/diplomathemes/archive/" in html
        assert "/admin/diplomathemes/reopen/" in html
        assert "В архив" in html and "Вернуть" in html

        edit_html = admin_client.get(f"/admin/diplomathemes/edit/?id={queued_id}").get_data(
            as_text=True
        )
        assert 'name="prev_status"' not in edit_html, "prev_status must not be a raw editable field"
        review_html = admin_client.get(f"/admin/reviewdiplomathemes/edit/?id={queued_id}").get_data(
            as_text=True
        )
        assert 'name="prev_status"' not in review_html

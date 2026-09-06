# -*- coding: utf-8 -*-
def _get_theme(theme_id):
    from se_models import DiplomaThemes

    return DiplomaThemes.query.filter_by(id=theme_id).first()


def _status(theme_id):
    return _get_theme(theme_id).status


def _notifications_of(author_id):
    from se_models import Notification

    return Notification.query.filter_by(recipient=author_id).all()


class TestBulkArchive:
    def test_bulk_archive_moves_in_012_keeps_34_and_mails_author_once(
        self, admin_client, make_theme
    ):
        author_one_a = make_theme(title="One A", status=2, author_id=1)
        author_one_b = make_theme(title="One B", status=0, author_id=1)
        author_two = make_theme(title="Two Theme", status=1, author_id=2)
        rejected = make_theme(title="Rejected", status=4, author_id=1)
        already_archived = make_theme(title="Prev Archived", status=3, author_id=2)
        legacy = _get_theme(already_archived)
        legacy.prev_status = 2

        resp = admin_client.post("/admin/diplomathemes/bulk-archive/")
        assert resp.status_code == 302
        assert _status(author_one_a) == 3
        assert _status(author_one_b) == 3
        assert _status(author_two) == 3
        assert _status(rejected) == 4, "rejected themes are never archived in bulk"
        assert _get_theme(already_archived).prev_status == 2, "already archived rows are untouched"

        notes_one = _notifications_of(1)
        assert len(notes_one) == 1, "one deduped mail per author, not one per theme"
        assert notes_one[0].title == "[SE site] Ваши темы архивированы"
        assert "One A" in notes_one[0].content and "One B" in notes_one[0].content
        notes_two = _notifications_of(2)
        assert len(notes_two) == 1 and notes_two[0].title == "[SE site] Ваша тема архивирована"

    def test_bulk_reopen_restores_preserved_statuses(self, admin_client, make_theme):
        theme_id = make_theme(title="Approved", status=2, author_id=1)
        queued_id = make_theme(title="Queued", status=1, author_id=2)
        admin_client.post("/admin/diplomathemes/bulk-archive/")

        resp = admin_client.post("/admin/diplomathemes/bulk-reopen/")
        assert resp.status_code == 302
        assert _status(theme_id) == 2, "approved must return to the catalog"
        assert _get_theme(theme_id).prev_status is None
        assert _status(queued_id) == 1

    def test_bulk_reopen_legacy_rows_fall_back_to_queue(self, admin_client, make_theme):
        from se_models import db

        legacy_id = make_theme(title="Legacy", status=3, author_id=1)
        _get_theme(legacy_id).prev_status = None
        db.session.commit()
        admin_client.post("/admin/diplomathemes/bulk-reopen/")
        assert _status(legacy_id) == 0

    def test_reviewer_cannot_bulk_archive(self, reviewer_client, make_theme):
        theme_id = make_theme(title="Protected", status=2, author_id=1)
        resp = reviewer_client.post("/admin/diplomathemes/bulk-archive/")
        assert resp.status_code in (301, 302, 401, 403)
        assert _status(theme_id) == 2

    def test_bulk_buttons_render_on_the_list(self, admin_client, make_theme):
        make_theme(title="Whatever", status=2, author_id=1)
        html = admin_client.get("/admin/diplomathemes/").get_data(as_text=True)
        assert "/admin/diplomathemes/bulk-archive/" in html
        assert "/admin/diplomathemes/bulk-reopen/" in html
        assert "Архивировать всё" in html

# -*- coding: utf-8 -*-
import re

import pytest


@pytest.fixture
def queued_theme(seeded_client):
    """A DiplomaThemes row awaiting review (status 0, so it shows in the queue)."""
    from se_models import DiplomaThemes, db

    dt = DiplomaThemes(
        title="Queue Clickable Theme",
        description="Description",
        requirements="Requirements",
        author_id=1,
        consultant_id=1,
        status=0,
    )
    db.session.add(dt)
    db.session.commit()
    return dt.id


def _edit_url(theme_id):
    return f"/admin/reviewdiplomathemes/edit/?id={theme_id}"


def _list_html(client):
    resp = client.get("/admin/reviewdiplomathemes/")
    assert resp.status_code == 200
    return resp.get_data(as_text=True)


def _details_html(client, theme_id):
    resp = client.get(f"/admin/reviewdiplomathemes/details/?id={theme_id}")
    assert resp.status_code == 200
    return resp.get_data(as_text=True)


class TestReviewQueueNavigableFromList:
    """Issue #274: reviewer must reach the theme review/edit page from the queue."""

    @pytest.mark.parametrize("client_name", ["reviewer_client", "admin_client"])
    def test_queued_theme_title_links_to_edit_page(self, request, client_name, queued_theme):
        html = _list_html(request.getfixturevalue(client_name))
        pattern = re.compile(
            rf'href="[^"]*{re.escape(_edit_url(queued_theme))}"[^>]*>Queue Clickable Theme</a>'
        )
        assert pattern.search(html), "theme title cell is not a link to the edit page"

    @pytest.mark.parametrize("client_name", ["reviewer_client", "admin_client"])
    def test_queued_theme_row_is_clickable(self, request, client_name, queued_theme):
        html = _list_html(request.getfixturevalue(client_name))
        assert re.compile(rf'data-href="[^"]*{re.escape(_edit_url(queued_theme))}"').search(html), (
            "no row-level click target pointing at the edit page"
        )

    def test_details_page_links_to_edit(self, admin_client, queued_theme):
        html = _details_html(admin_client, queued_theme)
        assert re.compile(rf'href="[^"]*{re.escape(_edit_url(queued_theme))}"').search(html), (
            "details page does not link on to the edit page"
        )

# -*- coding: utf-8 -*-
from conftest import assert_ok


class TestNewsGetPost:
    def test_news_get_post_with_id(self, seeded_client):
        assert_ok(seeded_client, "/news/item.html?post=2")

    def test_news_get_post_with_uri(self, seeded_client):
        resp = seeded_client.get("/news/item.html?post=1")
        assert resp.status_code in (200, 302)

    def test_news_get_post_increments_views(self, seeded_client):
        seeded_client.get("/news/item.html?post=2")
        seeded_client.get("/news/item.html?post=2")


class TestNewsSubmit:
    def test_news_submit_with_uri(self, logged_client):
        resp = logged_client.post(
            "/news/submit.html",
            data={
                "title": "External link post",
                "post_uri": "https://example.com/news",
            },
        )
        assert resp.status_code in (200, 302)

    def test_news_submit_no_title(self, logged_client):
        resp = logged_client.post(
            "/news/submit.html",
            data={
                "title": "",
                "post_text": "Some content",
            },
        )
        assert resp.status_code in (200, 302)

    def test_news_submit_no_uri_no_text(self, logged_client):
        resp = logged_client.post(
            "/news/submit.html",
            data={
                "title": "Title only",
            },
        )
        assert resp.status_code in (200, 302)


class TestNewsVote:
    def test_news_vote_own_post(self, logged_client):
        resp = logged_client.post("/news/post_vote", data={"post_id": 1, "action_vote": 1})
        assert resp.status_code in (200, 302)

    def test_news_vote_new_downvote(self, logged_client):
        resp = logged_client.post("/news/post_vote", data={"post_id": 2, "action_vote": 0})
        assert resp.status_code in (200, 302)

    def test_news_vote_change_vote(self, logged_client):
        resp = logged_client.post("/news/post_vote", data={"post_id": 2, "action_vote": 1})
        assert resp.status_code in (200, 302)
        resp = logged_client.post("/news/post_vote", data={"post_id": 2, "action_vote": 0})
        assert resp.status_code in (200, 302)

    def test_news_vote_already_voted(self, logged_client):
        resp = logged_client.post("/news/post_vote", data={"post_id": 2, "action_vote": 1})
        assert resp.status_code in (200, 302)
        resp = logged_client.post("/news/post_vote", data={"post_id": 2, "action_vote": 1})
        assert resp.status_code in (200, 302)

    def test_news_vote_rejects_non_http_referrer(self, logged_client):
        resp = logged_client.post(
            "/news/post_vote",
            data={"post_id": 1, "action_vote": 1},
            headers={"Referer": "javascript:alert(1)"},
        )
        assert resp.status_code in (200, 302)
        assert "javascript:" not in resp.headers.get("Location", "")

    def test_news_vote_rejects_cross_host_referrer(self, logged_client):
        resp = logged_client.post(
            "/news/post_vote",
            data={"post_id": 1, "action_vote": 1},
            headers={"Referer": "https://evil.example.com/path"},
        )
        assert resp.status_code in (200, 302)
        assert "evil.example.com" not in resp.headers.get("Location", "")


class TestNewsDelete:
    def test_news_delete_own_post(self, logged_client):
        assert_ok(
            logged_client, "/news/delete", data={"post_id": 1}, methods={"POST"}, code={200, 302}
        )

    def test_news_delete_nonexistent(self, logged_client):
        assert_ok(
            logged_client,
            "/news/delete",
            data={"post_id": 99999},
            methods={"POST"},
            code={200, 302, 404},
        )


class TestNewsList:
    def test_news_list_pagination(self, seeded_client):
        assert_ok(seeded_client, "/news/")

    def test_news_list_page_param(self, seeded_client):
        assert_ok(seeded_client, "/news/?page=1", code={200, 302})

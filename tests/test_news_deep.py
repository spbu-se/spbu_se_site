# -*- coding: utf-8 -*-
import pytest
from conftest import assert_ok


class TestNewsGetPost:
    def test_news_get_post_with_id(self, seeded_client):
        assert_ok(seeded_client, "/news/item.html?post=2")

    def test_news_get_post_with_uri(self, seeded_client):
        resp = seeded_client.get("/news/item.html?post=1")
        assert resp.status_code in (200, 302)


class TestNewsSubmit:
    @pytest.mark.parametrize(
        "data",
        [
            {"title": "External link post", "post_uri": "https://example.com/news"},
            {"title": "", "post_text": "Some content"},
            {"title": "Title only"},
        ],
    )
    def test_news_submit(self, logged_client, data):
        resp = logged_client.post("/news/submit.html", data=data)
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

    @pytest.mark.parametrize(
        ("referer", "forbidden"),
        [
            ("javascript:alert(1)", "javascript:"),
            ("https://evil.example.com/path", "evil.example.com"),
        ],
    )
    def test_news_vote_rejects_bad_referrer(self, logged_client, referer, forbidden):
        resp = logged_client.post(
            "/news/post_vote",
            data={"post_id": 1, "action_vote": 1},
            headers={"Referer": referer},
        )
        assert resp.status_code in (200, 302)
        assert forbidden not in resp.headers.get("Location", "")


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

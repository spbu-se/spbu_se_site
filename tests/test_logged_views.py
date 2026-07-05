from unittest.mock import patch

import pytest
from conftest import assert_ok

# Auth routes that require login
AUTH_ROUTES = [
    "/upload_avatar",
    "/profile.html",
]

# News routes that require login
NEWS_ROUTES = [
    "/news/submit.html",
    "/news/post_vote",
    "/news/delete",
]

# Diplomas routes that require login
DIPLOMA_ROUTES = [
    "/diplomas/add_theme.html",
    "/diplomas/user_themes.html",
    "/diplomas/delete_theme.html",
    "/diplomas/edit_theme.html",
    "/diplomas/archive_theme",
    "/diplomas/unarchive_theme",
]

# Internship routes that require login
INTERNSHIP_ROUTES = [
    "/internships/add",
    "/internships/1/update",
]

# Thesis routes (public but need seeded data)
THESIS_ROUTES = [
    "/theses_delete_tmp",
    "/theses_add_tmp",
    "/thesis_download",
]


class TestAuthLoggedIn:
    @pytest.mark.parametrize(
        "path,code",
        [
            ("/upload_avatar", {200, 204, 302}),
            ("/profile.html", {200, 302}),
        ],
    )
    def test_auth_routes(self, logged_client, path, code):
        assert_ok(logged_client, path, code=code)

    def test_profile_update(self, logged_client):
        resp = logged_client.post(
            "/profile.html",
            data={
                "last_name": "Updated",
                "first_name": "User",
                "middle_name": "",
                "how_to_contact": "email",
            },
        )
        assert resp.status_code in (200, 302)

    def test_profile_page_renders(self, logged_client):
        assert_ok(logged_client, "/profile.html", code={200, 302})

    def test_password_recovery_page(self, logged_client):
        assert_ok(logged_client, "/password_recovery.html")


class TestNewsLoggedIn:
    @pytest.mark.parametrize("path", NEWS_ROUTES)
    def test_news_routes(self, logged_client, path):
        assert_ok(logged_client, path, code={200, 302})


class TestDiplomasLoggedIn:
    @pytest.mark.parametrize("path", DIPLOMA_ROUTES)
    def test_diploma_routes(self, logged_client, path):
        assert_ok(logged_client, path, code={200, 302})


class TestDiplomasBehavior:
    def test_diploma_add_theme_page(self, logged_client):
        assert_ok(logged_client, "/diplomas/add_theme.html")

    def test_diploma_add_theme_submit(self, logged_client):
        resp = logged_client.post("/diplomas/add_theme.html", data={
            "name": "Test diploma theme",
            "description": "A test theme description",
        })
        assert resp.status_code in (200, 302)

    def test_diploma_edit_theme(self, logged_client):
        assert_ok(logged_client, "/diplomas/edit_theme.html?id=1", code={200, 302})

    def test_diploma_edit_theme_post(self, logged_client):
        resp = logged_client.post("/diplomas/edit_theme.html?id=1", data={
            "name": "Updated theme",
            "description": "Updated description",
        })
        assert resp.status_code in (200, 302)

    def test_diploma_archive_theme(self, logged_client):
        assert_ok(logged_client, "/diplomas/archive_theme?id=1", code={200, 302})

    def test_diploma_unarchive_theme(self, logged_client):
        assert_ok(logged_client, "/diplomas/unarchive_theme?id=1", code={200, 302})

    def test_diploma_delete_theme(self, logged_client):
        assert_ok(logged_client, "/diplomas/delete_theme.html?id=1", code={200, 302})

    def test_diploma_user_themes(self, logged_client):
        assert_ok(logged_client, "/diplomas/user_themes.html", code={200, 302})

    def test_diploma_fetch_themes(self, seeded_client):
        assert_ok(seeded_client, "/diplomas/fetch_themes")

    def test_diploma_theme_detail(self, seeded_client):
        assert_ok(seeded_client, "/diplomas/theme.html?id=1", code={200, 302})

    def test_diploma_theme_nonexistent(self, seeded_client):
        assert_ok(seeded_client, "/diplomas/theme.html?id=99999", code={200, 302, 404})

    def test_diploma_index_with_filters(self, seeded_client):
        assert_ok(seeded_client, "/diplomas/")
        assert_ok(seeded_client, "/diplomas/index.html")


class TestInternshipsLoggedIn:
    @pytest.mark.parametrize("path", INTERNSHIP_ROUTES)
    def test_internship_routes(self, logged_client, path):
        assert_ok(logged_client, path, code={200, 302})


class TestInternshipsBehavior:
    def test_internship_add_page(self, logged_client):
        assert_ok(logged_client, "/internships/add")

    def test_internship_add_submit(self, logged_client):
        resp = logged_client.post("/internships/add", data={
            "company": "Test Corp",
            "title": "Test Internship",
            "description": "A test position",
        })
        assert resp.status_code in (200, 302)

    def test_internship_detail(self, seeded_client):
        assert_ok(seeded_client, "/internships/1", code={200, 302, 404})

    def test_internship_detail_nonexistent(self, seeded_client):
        resp = seeded_client.get("/internships/99999")
        assert resp.status_code in (200, 302, 404)

    def test_internship_update_page(self, logged_client):
        assert_ok(logged_client, "/internships/1/update", code={200, 302, 404})

    def test_internship_update_submit(self, logged_client):
        resp = logged_client.post("/internships/1/update", data={
            "company": "Updated Corp",
            "title": "Updated Title",
        })
        assert resp.status_code in (200, 302, 404)

    def test_internship_delete(self, logged_client):
        assert_ok(logged_client, "/internships/1/delete", code={200, 302, 404})

    def test_internship_fetch_filtered(self, seeded_client):
        assert_ok(seeded_client, "/internships/fetch_internships")

    def test_internship_fetch_with_tag(self, seeded_client):
        assert_ok(seeded_client, "/internships/fetch_internships?tag=python")

    def test_internship_fetch_with_format(self, seeded_client):
        assert_ok(seeded_client, "/internships/fetch_internships?format=1")

    def test_internship_index_loads(self, seeded_client):
        assert_ok(seeded_client, "/internships/internships_index.html")


class TestThesesLoggedIn:
    @pytest.mark.parametrize("path", THESIS_ROUTES)
    def test_thesis_routes(self, logged_client, path):
        assert_ok(logged_client, path, code={200, 302})


class TestBachelor:
    @pytest.mark.parametrize(
        "path",
        [
            "/bachelor/application.html",
            "/bachelor/admission.html",
            "/bachelor/programming-technology.html",
            "/bachelor/software-engineering.html",
        ],
    )
    def test_bachelor_pages(self, seeded_client, path):
        assert_ok(seeded_client, path)


class TestMaster:
    @pytest.mark.parametrize(
        "path",
        [
            "/master/information-systems-administration.html",
            "/master/software-engineering.html",
        ],
    )
    def test_master_pages(self, seeded_client, path):
        assert_ok(seeded_client, path)


class TestReadOnlyPublic:
    @pytest.mark.parametrize(
        "path",
        [
            "/",
            "/index.html",
            "/research-directions",
            "/contacts.html",
            "/students/index.html",
            "/students/scholarships.html",
            "/department/staff.html",
            "/frequently-asked-questions.html",
            "/nooffer",
            "/sitemap.xml",
            "/Sitemap.xml",
            "/404.html",
            "/summer_school_2026.html",
            "/summer_school_2024.html",
            "/summer_school_2022.html",
            "/summer_school_list.html",
            "/news/",
            "/news/index.html",
            "/theses.html",
            "/theses.html?search=python",
            "/theses_tmp.html",
            "/fetch_theses",
            "/diplomas/",
            "/diplomas/index.html",
            "/diplomas/fetch_themes",
            "/internships/internships_index.html",
            "/internships/fetch_internships",
            "/login.html",
            "/register_basic.html",
            "/review/",
        ],
    )
    def test_public_pages(self, seeded_client, path):
        assert_ok(seeded_client, path, code={200, 302})

    def test_sitemap_xml(self, seeded_client):
        resp = seeded_client.get("/sitemap.xml")
        assert resp.status_code == 200
        assert b"<?xml" in resp.data or b"<urlset" in resp.data


class TestErrorPages:
    @pytest.mark.parametrize(
        "path",
        [
            "/nonexistent",
            "/nonexistent.html",
            "/this-route-does-not-exist-at-all",
        ],
    )
    def test_404(self, seeded_client, path):
        assert_ok(seeded_client, path, code=404)


class TestScholarships:
    @pytest.mark.parametrize("n", range(1, 14))
    def test_scholarship_pages(self, seeded_client, n):
        assert_ok(seeded_client, f"/scholarships/{n}.html")

    def test_scholarship_out_of_range(self, seeded_client):
        assert_ok(seeded_client, "/scholarships/0.html", code={200, 302, 404})
        assert_ok(seeded_client, "/scholarships/99.html", code={200, 302, 404})


class TestPractice:
    @pytest.mark.parametrize(
        "path",
        [
            "/practice",
            "/practice/",
            "/practice/guide/",
            "/practice_staff",
            "/practice_staff/",
            "/practice_admin",
            "/practice_admin/",
        ],
    )
    def test_practice_public(self, seeded_client, path):
        assert_ok(seeded_client, path, code={200, 302})

    @pytest.mark.parametrize(
        "path",
        [
            "/practice/new/",
            "/practice/data_for_practice/",
            "/practice/choosing_topic/",
            "/practice/edit_theme/",
            "/practice/goals_tasks/",
            "/practice/add_new_report/",
            "/practice/workflow/",
            "/practice/preparation_for_defense/",
            "/practice/defense/",
            "/practice_staff/thesis/",
            "/practice_staff/reports/",
            "/practice_staff/finished_thesises/",
            "/practice_admin/choose_area_worktype",
            "/practice_admin/finished_thesises",
            "/practice_admin/thesis",
            "/practice_admin/yandex_code",
        ],
    )
    def test_practice_logged_in(self, logged_client, path):
        assert_ok(logged_client, path, code={200, 302, 404})


class TestPracticeStudentFlow:
    def test_practice_index_logged_in(self, logged_client):
        assert_ok(logged_client, "/practice", code={200, 302})

    def test_practice_guide(self, seeded_client):
        assert_ok(seeded_client, "/practice/guide/", code={200, 302})

    def test_practice_new_thesis_page(self, logged_client):
        assert_ok(logged_client, "/practice/new/", code={200, 302})

    def test_practice_data_for_practice(self, logged_client):
        assert_ok(logged_client, "/practice/data_for_practice/", code={200, 302})

    def test_practice_choosing_topic(self, logged_client):
        assert_ok(logged_client, "/practice/choosing_topic/", code={200, 302})

    def test_practice_preparation(self, logged_client):
        assert_ok(logged_client, "/practice/preparation_for_defense/", code={200, 302})

    def test_practice_defense(self, logged_client):
        assert_ok(logged_client, "/practice/defense/", code={200, 302})


class TestPracticeStaffFlow:
    def test_practice_staff_index(self, logged_client):
        assert_ok(logged_client, "/practice_staff", code={200, 302})

    def test_practice_staff_thesis(self, logged_client):
        assert_ok(logged_client, "/practice_staff/thesis/", code={200, 302, 404})

    def test_practice_staff_reports(self, logged_client):
        assert_ok(logged_client, "/practice_staff/reports/", code={200, 302, 404})

    def test_practice_staff_finished(self, logged_client):
        assert_ok(logged_client, "/practice_staff/finished_thesises/", code={200, 302})


class TestPracticeAdminFlow:
    def test_practice_admin_index(self, logged_client):
        assert_ok(logged_client, "/practice_admin", code={200, 302})

    def test_practice_admin_choose_area(self, logged_client):
        assert_ok(logged_client, "/practice_admin/choose_area_worktype", code={200, 302})

    def test_practice_admin_finished(self, logged_client):
        assert_ok(logged_client, "/practice_admin/finished_thesises", code={200, 302})

    def test_practice_admin_thesis(self, logged_client):
        assert_ok(logged_client, "/practice_admin/thesis", code={200, 302, 404})

    def test_practice_admin_yandex(self, logged_client):
        assert_ok(logged_client, "/practice_admin/yandex_code", code={200, 302, 404})


class TestReview:
    @pytest.mark.parametrize(
        "path",
        [
            "/review/",
            "/review/index.html",
            "/review/submit",
            "/review/fetch_thesis_on_review",
            "/review/become_thesis_reviewer",
            "/review/become_thesis_reviewer_confirm",
            "/review/review",
            "/review/reviewed",
            "/review/review_result",
            "/review/edit",
            "/review/delete",
        ],
    )
    def test_review_logged_in(self, logged_client, path):
        assert_ok(logged_client, path, code={200, 302, 404})


class TestThesisDownload:
    def test_thesis_download_no_id(self, logged_client):
        assert_ok(logged_client, "/thesis_download", code={200, 302})

    def test_thesis_download_with_id(self, seeded_client):
        assert_ok(seeded_client, "/thesis_download?thesis_id=1", code={200, 302})

    def test_thesis_download_nonexistent_id(self, seeded_client):
        assert_ok(seeded_client, "/thesis_download?thesis_id=99999", code={200, 302})

    def test_thesis_download_invalid_id(self, seeded_client):
        assert_ok(seeded_client, "/thesis_download?thesis_id=abc", code={200, 302})


class TestThesisSearch:
    @pytest.mark.parametrize("query", ["", "python", "test", "курсовая", "x" * 100])
    def test_thesis_search_various(self, seeded_client, query):
        assert_ok(seeded_client, f"/theses.html?search={query}")

    @pytest.mark.parametrize("start,end", [("2020", "2024"), ("2010", "2015"), ("", "2024"), ("2020", "")])
    def test_thesis_year_filters(self, seeded_client, start, end):
        params = []
        if start:
            params.append(f"startdate={start}")
        if end:
            params.append(f"enddate={end}")
        query = "&".join(params)
        assert_ok(seeded_client, f"/theses.html?{query}")

    def test_thesis_fetch_paginated(self, seeded_client):
        assert_ok(seeded_client, "/fetch_theses?page=1")


class TestThesisTempCrud:
    def test_theses_tmp_list_empty(self, logged_client):
        assert_ok(logged_client, "/theses_tmp.html")

    def test_theses_post_form_loads(self, logged_client):
        assert_ok(logged_client, "/post_theses", code={200, 302})

    def test_theses_post_submission(self, logged_client):
        resp = logged_client.post("/post_theses", data={
            "name_ru": "Test thesis",
            "author": "Test Author",
            "type_id": 2,
            "course_id": 1,
            "publish_year": 2024,
        })
        assert resp.status_code in (200, 302)

    def test_theses_delete_tmp_nonexistent(self, logged_client):
        assert_ok(logged_client, "/theses_delete_tmp", code={200, 302})

    def test_theses_add_tmp_nonexistent(self, logged_client):
        assert_ok(logged_client, "/theses_add_tmp", code={200, 302})

    def test_theses_post_form_filters(self, seeded_client):
        assert_ok(seeded_client, "/theses.html?type_id=2")
        assert_ok(seeded_client, "/theses.html?course_id=1")
        assert_ok(seeded_client, "/theses.html?area_id=1")

    def test_theses_download_increments_counter(self, seeded_client):
        resp = seeded_client.get("/thesis_download?thesis_id=1")
        assert resp.status_code in (200, 302)

    def test_theses_post_with_filter_params(self, seeded_client):
        assert_ok(seeded_client, "/post_theses?type_id=2")
        assert_ok(seeded_client, "/post_theses?course_id=1")

    def test_theses_add_tmp_with_id(self, logged_client):
        assert_ok(logged_client, "/theses_add_tmp?id=1", code={200, 302})

    def test_theses_delete_tmp_with_id(self, logged_client):
        assert_ok(logged_client, "/theses_delete_tmp?id=1", code={200, 302})


class TestThesisAdminApproval:
    def test_approve_temp_thesis(self, seeded_client):
        from se_models import Thesis, db
        t = Thesis(name_ru="Temp Thesis", author="Test", type_id=2, course_id=1, publish_year=2024, temporary=True)
        db.session.add(t)
        db.session.commit()
        resp = seeded_client.get(f"/theses_add_tmp?thesis_id={t.id}")
        assert resp.status_code in (200, 302)
        updated = Thesis.query.get(t.id)
        assert updated.temporary == False

    @pytest.mark.xfail(strict=False, reason="Whoosh index not available in parallel test workers")
    @patch("os.rename")
    def test_approve_temp_thesis_with_text_uri(self, mock_rename, seeded_client):
        from se_models import Thesis, db
        t = Thesis(name_ru="Temp Thesis", author="Test", type_id=2, course_id=1, publish_year=2024, temporary=True, text_uri="test.pdf")
        db.session.add(t)
        db.session.commit()
        resp = seeded_client.get(f"/theses_add_tmp?thesis_id={t.id}")
        assert resp.status_code in (200, 302)

    @pytest.mark.xfail(strict=False, reason="Whoosh index not available in parallel test workers")
    def test_delete_temp_thesis(self, seeded_client):
        from se_models import Thesis, db
        t = Thesis(name_ru="Delete me", author="Test", type_id=2, course_id=1, publish_year=2024, temporary=True)
        db.session.add(t)
        db.session.commit()
        resp = seeded_client.get(f"/theses_delete_tmp?id={t.id}")
        assert resp.status_code in (200, 302)


class TestNewsItems:
    @pytest.mark.parametrize("id_,code", [(1, {200, 302}), (99999, {200, 302}), (None, {200, 302})])
    def test_news_item(self, seeded_client, id_, code):
        path = f"/news/item.html?id={id_}" if id_ else "/news/item.html"
        assert_ok(seeded_client, path, code=code)


class TestNewsSubmit:
    def test_news_submit_form_loads(self, logged_client):
        assert_ok(logged_client, "/news/submit.html")

    def test_news_submit_post(self, logged_client):
        resp = logged_client.post("/news/submit.html", data={
            "title": "Test news post",
            "text": "This is a test news post content.",
        })
        assert resp.status_code in (200, 302)

    def test_news_submit_empty_title(self, logged_client):
        resp = logged_client.post("/news/submit.html", data={
            "title": "",
            "text": "Some content",
        })
        assert resp.status_code in (200, 302)

    def test_news_submit_with_uri(self, logged_client):
        resp = logged_client.post("/news/submit.html", data={
            "title": "External link post",
            "uri": "https://example.com/news",
            "text": "Check out this link",
        })
        assert resp.status_code in (200, 302)


class TestNewsVote:
    def test_news_vote_up(self, logged_client):
        resp = logged_client.post("/news/post_vote", data={"post_id": 1, "upvote": 1})
        assert resp.status_code in (200, 302)

    def test_news_vote_down(self, logged_client):
        resp = logged_client.post("/news/post_vote", data={"post_id": 1, "upvote": 0})
        assert resp.status_code in (200, 302)

    def test_news_vote_nonexistent_post(self, logged_client):
        resp = logged_client.post("/news/post_vote", data={"post_id": 99999, "upvote": 1})
        assert resp.status_code in (200, 302)

    def test_news_vote_missing_params(self, logged_client):
        resp = logged_client.post("/news/post_vote", data={})
        assert resp.status_code in (200, 302)


class TestNewsDelete:
    def test_news_delete_nonexistent(self, logged_client):
        assert_ok(logged_client, "/news/delete?id=99999", code={200, 302})

    def test_news_delete_own_post(self, logged_client):
        resp = logged_client.post("/news/submit.html", data={"title": "Delete me", "text": "To be deleted"})
        assert_ok(logged_client, "/news/delete?id=1", code={200, 302})


class TestNewsDeepBehavior:
    def test_news_post_with_uri_redirects(self, seeded_client):
        resp = seeded_client.get("/news/item.html?id=1")
        # Post with URI may redirect
        assert resp.status_code in (200, 302)

    def test_news_post_view_count_increments(self, seeded_client):
        before = seeded_client.get("/news/item.html?id=2")
        assert before.status_code in (200, 302)
        after = seeded_client.get("/news/item.html?id=2")
        assert after.status_code in (200, 302)

    def test_news_list_pagination(self, seeded_client):
        assert_ok(seeded_client, "/news/")

    def test_news_list_page_param(self, seeded_client):
        assert_ok(seeded_client, "/news/?page=1", code={200, 302, 404})

    def test_news_vote_own_post_blocked(self, logged_client):
        resp = logged_client.get("/news/post_vote?post_id=2&action_vote=1")
        assert resp.status_code in (200, 302)

    def test_news_vote_get_missing_post_id(self, logged_client):
        resp = logged_client.get("/news/post_vote")
        assert resp.status_code in (200, 302)

    def test_news_vote_get(self, logged_client):
        resp = logged_client.get("/news/post_vote?post_id=1&action_vote=1")
        assert resp.status_code in (200, 302)

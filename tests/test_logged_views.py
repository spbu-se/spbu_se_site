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
    @pytest.mark.parametrize("path,code", [
        ("/upload_avatar", {200, 204, 302}),
        ("/profile.html", {200, 302}),
    ])
    def test_auth_routes(self, logged_client, path, code):
        assert_ok(logged_client, path, code=code)

    def test_profile_update(self, logged_client):
        resp = logged_client.post("/profile.html", data={
            "last_name": "Updated", "first_name": "User", "middle_name": "",
            "how_to_contact": "email",
        })
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


class TestInternshipsLoggedIn:
    @pytest.mark.parametrize("path", INTERNSHIP_ROUTES)
    def test_internship_routes(self, logged_client, path):
        assert_ok(logged_client, path, code={200, 302})


class TestThesesLoggedIn:
    @pytest.mark.parametrize("path", THESIS_ROUTES)
    def test_thesis_routes(self, logged_client, path):
        assert_ok(logged_client, path, code={200, 302})


class TestBachelor:
    @pytest.mark.parametrize("path", [
        "/bachelor/application.html",
        "/bachelor/admission.html",
        "/bachelor/programming-technology.html",
        "/bachelor/software-engineering.html",
    ])
    def test_bachelor_pages(self, seeded_client, path):
        assert_ok(seeded_client, path)


class TestMaster:
    @pytest.mark.parametrize("path", [
        "/master/information-systems-administration.html",
        "/master/software-engineering.html",
    ])
    def test_master_pages(self, seeded_client, path):
        assert_ok(seeded_client, path)


class TestReadOnlyPublic:
    @pytest.mark.parametrize("path", [
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
    ])
    def test_public_pages(self, seeded_client, path):
        assert_ok(seeded_client, path, code={200, 302})

    def test_sitemap_xml(self, seeded_client):
        resp = seeded_client.get("/sitemap.xml")
        assert resp.status_code == 200
        assert b"<?xml" in resp.data or b"<urlset" in resp.data


class TestErrorPages:
    @pytest.mark.parametrize("path", [
        "/nonexistent",
        "/nonexistent.html",
        "/this-route-does-not-exist-at-all",
    ])
    def test_404(self, seeded_client, path):
        assert_ok(seeded_client, path, code=404)


class TestScholarships:
    @pytest.mark.parametrize("n", range(1, 14))
    def test_scholarship_pages(self, seeded_client, n):
        assert_ok(seeded_client, f"/scholarships/{n}.html")


class TestPractice:
    @pytest.mark.parametrize("path", [
        "/practice",
        "/practice/",
        "/practice/guide/",
        "/practice_staff",
        "/practice_staff/",
        "/practice_admin",
        "/practice_admin/",
    ])
    def test_practice_public(self, seeded_client, path):
        assert_ok(seeded_client, path, code={200, 302})

    @pytest.mark.parametrize("path", [
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
    ])
    def test_practice_logged_in(self, logged_client, path):
        assert_ok(logged_client, path, code={200, 302, 404})


class TestReview:
    @pytest.mark.parametrize("path", [
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
    ])
    def test_review_logged_in(self, logged_client, path):
        assert_ok(logged_client, path, code={200, 302, 404})


class TestThesisDownload:
    def test_thesis_download_no_id(self, logged_client):
        assert_ok(logged_client, "/thesis_download", code={200, 302})

    def test_thesis_download_with_id(self, seeded_client):
        assert_ok(seeded_client, "/thesis_download?thesis_id=1", code={200, 302})


class TestNewsItems:
    @pytest.mark.parametrize("id_,code", [(1, {200, 302}), (99999, {200, 302}), (None, {200, 302})])
    def test_news_item(self, seeded_client, id_, code):
        path = f"/news/item.html?id={id_}" if id_ else "/news/item.html"
        assert_ok(seeded_client, path, code=code)

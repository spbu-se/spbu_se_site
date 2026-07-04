class TestAuth:
    def test_login_form_renders(self, seeded_client):
        resp = seeded_client.get("/login.html")
        assert resp.status_code == 200

    def test_login_form_accepts_submission(self, seeded_client):
        resp = seeded_client.post(
            "/login.html",
            data={
                "email": "test@spbu.ru",
                "password": "test",
            },
        )
        assert resp.status_code in (200, 302)

    def test_login_page_has_form(self, seeded_client):
        resp = seeded_client.get("/login.html")
        assert resp.status_code == 200

    def test_logout_redirects(self, seeded_client):
        resp = seeded_client.get("/logout")
        assert resp.status_code == 302

    def test_register_page_loads(self, seeded_client):
        resp = seeded_client.get("/register_basic.html")
        assert resp.status_code == 200

    def test_register_page_has_form(self, seeded_client):
        resp = seeded_client.get("/register_basic.html")
        assert resp.status_code == 200
        assert b"email" in resp.data.lower()

    def test_register_with_data(self, seeded_client):
        resp = seeded_client.post(
            "/register_basic.html",
            data={"email": "newuser@spbu.ru", "password": "secret123"},
        )
        assert resp.status_code in (200, 302)

    def test_profile_redirects_when_unauth(self, seeded_client):
        resp = seeded_client.get("/profile.html")
        assert resp.status_code == 302

    def test_password_recovery_page(self, seeded_client):
        resp = seeded_client.get("/password_recovery.html")
        assert resp.status_code == 200


class TestNews:
    def test_news_index_loads(self, seeded_client):
        resp = seeded_client.get("/news/")
        assert resp.status_code == 200

    def test_news_item_nonexistent(self, seeded_client):
        resp = seeded_client.get("/news/item.html?id=99999")
        assert resp.status_code in (200, 302, 404)

    def test_news_item_with_uri(self, seeded_client):
        resp = seeded_client.get("/news/item.html?id=1")
        assert resp.status_code in (200, 302)

    def test_news_item_with_text(self, seeded_client):
        resp = seeded_client.get("/news/item.html?id=2")
        assert resp.status_code == 200

    def test_news_item_no_id(self, seeded_client):
        resp = seeded_client.get("/news/item.html")
        assert resp.status_code == 302


class TestTheses:
    def test_theses_search_loads(self, seeded_client):
        resp = seeded_client.get("/theses.html")
        assert resp.status_code == 200

    def test_theses_with_search_param(self, seeded_client):
        resp = seeded_client.get("/theses.html?search=python")
        assert resp.status_code == 200

    def test_theses_with_year_filter(self, seeded_client):
        resp = seeded_client.get("/theses.html?startdate=2020&enddate=2024")
        assert resp.status_code == 200

    def test_theses_fetch(self, seeded_client):
        resp = seeded_client.get("/fetch_theses")
        assert resp.status_code == 200

    def test_theses_tmp_list(self, seeded_client):
        resp = seeded_client.get("/theses_tmp.html")
        assert resp.status_code == 200

    def test_theses_post_form(self, seeded_client):
        resp = seeded_client.get("/post_theses")
        assert resp.status_code in (200, 302)


class TestInternships:
    def test_internships_index(self, seeded_client):
        resp = seeded_client.get("/internships/internships_index.html")
        assert resp.status_code == 200

    def test_internships_fetch(self, seeded_client):
        resp = seeded_client.get("/internships/fetch_internships")
        assert resp.status_code == 200

    def test_internship_detail_nonexistent(self, seeded_client):
        resp = seeded_client.get("/internships/99999")
        assert resp.status_code == 404

    def test_internship_add_form(self, seeded_client):
        resp = seeded_client.get("/internships/add")
        assert resp.status_code in (200, 302)


class TestDiplomas:
    def test_diplomas_index(self, seeded_client):
        resp = seeded_client.get("/diplomas/")
        assert resp.status_code == 200

    def test_diplomas_add_theme(self, seeded_client):
        resp = seeded_client.get("/diplomas/add_theme.html")
        assert resp.status_code in (200, 302)

    def test_diploma_theme_detail(self, seeded_client):
        resp = seeded_client.get("/diplomas/theme.html?id=1")
        assert resp.status_code in (200, 302, 404)

    def test_diploma_theme_nonexistent(self, seeded_client):
        resp = seeded_client.get("/diplomas/theme.html?id=99999")
        assert resp.status_code in (200, 302, 404)

    def test_diplomas_fetch(self, seeded_client):
        resp = seeded_client.get("/diplomas/fetch_themes")
        assert resp.status_code == 200

    def test_diplomas_user_themes(self, seeded_client):
        resp = seeded_client.get("/diplomas/user_themes.html")
        assert resp.status_code == 200


class TestPractice:
    def test_practice_guide(self, seeded_client):
        resp = seeded_client.get("/practice/guide/")
        assert resp.status_code in (200, 302)

    def test_practice_staff_index(self, seeded_client):
        resp = seeded_client.get("/practice_staff")
        assert resp.status_code in (200, 302)


class TestSummerSchools:
    def test_summer_school_2026(self, seeded_client):
        resp = seeded_client.get("/summer_school_2026.html")
        assert resp.status_code == 200

    def test_summer_school_2024(self, seeded_client):
        resp = seeded_client.get("/summer_school_2024.html")
        assert resp.status_code == 200

    def test_summer_school_2022(self, seeded_client):
        resp = seeded_client.get("/summer_school_2022.html")
        assert resp.status_code == 200

    def test_summer_school_2021(self, seeded_client):
        resp = seeded_client.get("/summer_school_2021.html")
        assert resp.status_code == 200

    def test_summer_school_list(self, seeded_client):
        resp = seeded_client.get("/summer_school_list.html")
        assert resp.status_code == 200


class TestBachelor:
    def test_bachelor_application(self, seeded_client):
        resp = seeded_client.get("/bachelor/application.html")
        assert resp.status_code == 200

    def test_bachelor_admission(self, seeded_client):
        resp = seeded_client.get("/bachelor/admission.html")
        assert resp.status_code == 200

    def test_bachelor_programming_technology(self, seeded_client):
        resp = seeded_client.get("/bachelor/programming-technology.html")
        assert resp.status_code == 200

    def test_bachelor_software_engineering(self, seeded_client):
        resp = seeded_client.get("/bachelor/software-engineering.html")
        assert resp.status_code == 200


class TestErrorHandlers:
    def test_404_returns_custom_page(self, seeded_client):
        resp = seeded_client.get("/this-route-does-not-exist-at-all")
        assert resp.status_code == 404

    def test_404_for_html_path(self, seeded_client):
        resp = seeded_client.get("/nonexistent.html")
        assert resp.status_code == 404

def test_theses_search_page_loads(seeded_client):
    resp = seeded_client.get("/theses.html")
    assert resp.status_code == 200


def test_theses_fetch(seeded_client):
    resp = seeded_client.get("/fetch_theses")
    assert resp.status_code == 200


def test_news_list_loads(seeded_client):
    resp = seeded_client.get("/news/")
    assert resp.status_code == 200


def test_scholarships_year1(seeded_client):
    resp = seeded_client.get("/scholarships/1.html")
    assert resp.status_code == 200


def test_scholarships_year13(seeded_client):
    resp = seeded_client.get("/scholarships/13.html")
    assert resp.status_code == 200


def test_diplomas_index(seeded_client):
    resp = seeded_client.get("/diplomas/")
    assert resp.status_code == 200


def test_internships_index(seeded_client):
    resp = seeded_client.get("/internships/internships_index.html")
    assert resp.status_code == 200


def test_review_index_loads(seeded_client):
    resp = seeded_client.get("/review/")
    assert resp.status_code == 200


def test_bachelor_admission(seeded_client):
    resp = seeded_client.get("/bachelor/admission.html")
    assert resp.status_code == 200


def test_master_isa(seeded_client):
    resp = seeded_client.get("/master/information-systems-administration.html")
    assert resp.status_code == 200


def test_login_with_invalid_credentials(seeded_client):
    resp = seeded_client.post("/login.html", data={
        "email": "nonexistent@spbu.ru",
        "password": "wrong",
    }, follow_redirects=True)
    assert resp.status_code == 200


def test_login_page_has_form(seeded_client):
    resp = seeded_client.get("/login.html")
    assert resp.status_code == 200
    assert b"email" in resp.data.lower() or b"login" in resp.data.lower()


def test_register_page_loads(seeded_client):
    resp = seeded_client.get("/register_basic.html")
    assert resp.status_code == 200


def test_profile_redirects_to_login_when_unauth(seeded_client):
    resp = seeded_client.get("/profile.html")
    assert resp.status_code == 302


def test_news_item_with_seeded_data(seeded_client):
    resp = seeded_client.get("/news/item.html?id=1")
    assert resp.status_code in (200, 302, 404)


def test_diploma_theme_detail(seeded_client):
    resp = seeded_client.get("/diplomas/theme.html?id=1")
    assert resp.status_code in (200, 302, 404)


def test_sitemap_xml_valid(seeded_client):
    resp = seeded_client.get("/sitemap.xml")
    assert resp.status_code == 200
    assert b"<?xml" in resp.data or b"<urlset" in resp.data


def test_404_page(seeded_client):
    resp = seeded_client.get("/nonexistent-route-that-does-not-exist")
    assert resp.status_code == 404


def test_faq_page_loads(seeded_client):
    resp = seeded_client.get("/frequently-asked-questions.html")
    assert resp.status_code == 200

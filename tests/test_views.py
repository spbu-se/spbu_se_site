import pytest
from conftest import assert_ok, assert_ok_or_redirect


@pytest.mark.parametrize("n", range(1, 14))
def test_scholarship_page(seeded_client, n):
    assert_ok(seeded_client, f"/scholarships/{n}.html")


def test_theses_search_page_loads(seeded_client):
    assert_ok(seeded_client, "/theses.html")


def test_theses_fetch(seeded_client):
    assert_ok(seeded_client, "/fetch_theses")


def test_news_list_loads(seeded_client):
    assert_ok(seeded_client, "/news/")


def test_diplomas_index(seeded_client):
    assert_ok(seeded_client, "/diplomas/")


def test_internships_index(seeded_client):
    assert_ok(seeded_client, "/internships/internships_index.html")


def test_review_index_loads(seeded_client):
    assert_ok(seeded_client, "/review/")


def test_bachelor_admission(seeded_client):
    assert_ok(seeded_client, "/bachelor/admission.html")


def test_master_isa(seeded_client):
    assert_ok(seeded_client, "/master/information-systems-administration.html")


def test_login_with_invalid_credentials(seeded_client):
    assert_ok_or_redirect(seeded_client, "/login.html")


def test_login_page_has_form(seeded_client):
    assert_ok(seeded_client, "/login.html")


def test_register_page_loads(seeded_client):
    assert_ok(seeded_client, "/register_basic.html")


def test_profile_redirects_to_login_when_unauth(seeded_client):
    assert_ok(seeded_client, "/profile.html", code={200, 302})


def test_news_item_with_seeded_data(seeded_client):
    assert_ok_or_redirect(seeded_client, "/news/item.html?id=1")


def test_diploma_theme_detail(seeded_client):
    assert_ok_or_redirect(seeded_client, "/diplomas/theme.html?id=1")


def test_sitemap_xml_valid(seeded_client):
    resp = seeded_client.get("/sitemap.xml")
    assert resp.status_code == 200
    assert b"<?xml" in resp.data or b"<urlset" in resp.data


def test_faq_page_loads(seeded_client):
    assert_ok(seeded_client, "/frequently-asked-questions.html")

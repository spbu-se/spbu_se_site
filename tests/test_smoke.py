def test_app_exists():
    from flask_se import app

    assert app is not None


def test_index_returns_200(client):
    resp = client.get("/")
    assert resp.status_code == 200


def test_index_html_redirects_to_root(client):
    resp = client.get("/index.html")
    assert resp.status_code == 302
    assert resp.location == "/"


def test_nonexistent_returns_404(client):
    resp = client.get("/nonexistent-page")
    assert resp.status_code == 404


def test_login_page_loads(client):
    resp = client.get("/login.html")
    assert resp.status_code == 200


def test_contacts_page_loads(client):
    resp = client.get("/contacts.html")
    assert resp.status_code == 200


def test_students_index_loads(client):
    resp = client.get("/students/index.html")
    assert resp.status_code == 200


def test_sitemap_returns_200(client):
    resp = client.get("/sitemap.xml")
    assert resp.status_code == 200


def test_research_directions_loads(client):
    resp = client.get("/research-directions")
    assert resp.status_code == 200

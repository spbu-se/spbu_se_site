# -*- coding: utf-8 -*-
def _company(name):
    from se_models import Company, db

    c = Company(name=name)
    db.session.add(c)
    db.session.commit()
    return c.id


def _get_company(company_id):
    from se_models import Company

    return Company.query.filter_by(id=company_id).first()


class TestCompanyCrud:
    def test_list_shows_companies_and_nav(self, admin_client):
        _company("ACME Ltd")
        html = admin_client.get("/admin/companies/").get_data(as_text=True)
        assert "ACME Ltd" in html
        master = admin_client.get("/admin/diplomathemes/").get_data(as_text=True)
        assert "/admin/companies/" in master, "companies nav link missing on admin pages"

    def test_create_company(self, admin_client):
        resp = admin_client.post(
            "/admin/companies/new/",
            data={"name": "NewCo", "logo_uri": "https://example.com/logo.png", "status": "0"},
        )
        assert resp.status_code == 302
        company = _company_by_name("NewCo")
        assert company is not None and company.logo_uri.endswith("logo.png")

    def test_edit_company(self, admin_client):
        company_id = _company("Old Name")
        resp = admin_client.post(
            f"/admin/companies/edit/?id={company_id}",
            data={"name": "Renamed Ltd", "logo_uri": "", "status": "0"},
        )
        assert resp.status_code == 302
        assert _get_company(company_id).name == "Renamed Ltd"

    def test_delete_referenced_company_blocked(self, admin_client, make_theme):
        company_id = _company("Used By Theme")
        theme_id = make_theme(title="Theme With Company", status=2, company_id=company_id)
        resp = admin_client.post("/admin/companies/delete/", data={"id": company_id})
        assert resp.status_code == 302
        assert _get_company(company_id) is not None, "referenced company must not be deleted"
        assert _get_theme_row(theme_id) is not None

    def test_delete_unreferenced_company_succeeds(self, admin_client):
        company_id = _company("Orphan Co")
        resp = admin_client.post("/admin/companies/delete/", data={"id": company_id})
        assert resp.status_code == 302
        assert _get_company(company_id) is None

    def test_reviewer_cannot_access(self, reviewer_client):
        resp = reviewer_client.get("/admin/companies/")
        assert resp.status_code in (301, 302, 401, 403)


def _company_by_name(name):
    from se_models import Company

    return Company.query.filter_by(name=name).first()


def _get_theme_row(theme_id):
    from se_models import DiplomaThemes

    return DiplomaThemes.query.filter_by(id=theme_id).first()

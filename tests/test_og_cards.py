# -*- coding: utf-8 -*-
import re


def _seed_internship(client):
    from se_models import InternshipCompany, InternshipFormat, Internships, InternshipTag, db

    company = InternshipCompany(name="OG Card Co")
    db.session.add(company)
    db.session.flush()

    fmt = db.session.get(InternshipFormat, 1)
    tag = db.session.get(InternshipTag, 1)

    internship = Internships(
        name_vacancy="OG Card Vacancy",
        salary="50000",
        description="OG card description",
        location="SPb",
        company_id=company.id,
        requirements="Some requirements text for the og card",
        more_inf="https://example.com",
        author_id=1,
    )
    internship.format = [fmt]
    internship.tag = [tag]
    db.session.add(internship)
    db.session.commit()
    return internship.id


def _head_html(resp) -> str:
    html = resp.get_data(as_text=True)
    head = html[: html.find("</head>")]
    return re.sub(r"\s+", " ", head)


def _meta_content(head: str, prop: str) -> str | None:
    m = re.search(rf'(?:property|name)="{re.escape(prop)}"\s+content="([^"]*)"', head)
    return m.group(1).strip() if m else None


def _assert_og_card(resp, title, description):
    head = _head_html(resp)
    assert resp.status_code == 200
    assert _meta_content(head, "og:title") == title
    assert _meta_content(head, "og:description") == description
    assert 'property="og:image" content="http://localhost/assets/img/main-back.jpg"' in head
    assert 'name="twitter:card" content="summary_large_image"' in head


class TestOgBaseDefaults:
    def test_theses_archive(self, seeded_client):
        resp = seeded_client.get("/theses.html")
        _assert_og_card(
            resp,
            "Курсовые, учебные практики и ВКР студентов Кафедры Системного Программирования",
            "Готовые дипломные работы по программированию, курсовые по программированию, ВКР бакалавров и магистров Кафедры Системного программирования Математико-механического факультета СПбГУ.",
        )

    def test_scholarship_light_base(self, seeded_client):
        resp = seeded_client.get("/scholarships/1.html")
        head = _head_html(resp)
        assert resp.status_code == 200
        assert 'property="og:title"' in head
        assert 'property="og:description"' in head
        assert 'property="og:image"' in head
        assert 'name="twitter:card" content="summary_large_image"' in head


class TestOgNewsItem:
    def test_news_post_og(self, seeded_client):
        resp = seeded_client.get("/news/item.html?post=2")
        head = _head_html(resp)
        assert resp.status_code == 200
        assert 'property="og:type" content="article"' in head
        assert 'property="og:title"' in head
        assert 'property="og:description"' in head


class TestOgInternship:
    def test_internship_og_and_canonical(self, seeded_client):
        internship_id = _seed_internship(seeded_client)
        resp = seeded_client.get(f"/internships/{internship_id}")
        head = _head_html(resp)
        assert resp.status_code == 200
        assert 'property="og:type" content="article"' in head
        canonical = re.search(r'rel="canonical" href="([^"]+)"', head)
        assert canonical is not None
        assert canonical.group(1) == f"https://se.math.spbu.ru/internships/{internship_id}"
        assert "/diplomas/index.html" not in canonical.group(1)
        assert 'property="og:title" content="OG Card Vacancy"' in head
        assert 'property="og:description" content="OG card description"' in head


class TestOgDiplomaTheme:
    def test_theme_og(self, seeded_client):
        from se_models import DiplomaThemes

        theme = DiplomaThemes.query.filter_by(status=2).first()
        if theme is None:
            theme = DiplomaThemes.query.first()
        assert theme is not None
        resp = seeded_client.get(f"/diplomas/theme.html?id={theme.id}")
        head = _head_html(resp)
        assert resp.status_code == 200
        assert 'property="og:type" content="article"' in head
        assert 'property="og:title"' in head
        assert 'property="og:description"' in head

    def test_theme_og_description_falls_back_to_title(self, seeded_client):
        from se_models import DiplomaThemes

        theme = DiplomaThemes.query.filter(DiplomaThemes.description.is_(None)).first()
        if theme is None:
            theme = DiplomaThemes.query.first()
        assert theme is not None
        resp = seeded_client.get(f"/diplomas/theme.html?id={theme.id}")
        head = _head_html(resp)
        assert _meta_content(head, "og:description") in (theme.title, theme.description)


class TestOgThesisCard:
    def _make_published_thesis(self):
        from se_models import Thesis, db

        thesis = Thesis(
            name_ru="Published Thesis OG",
            author="OG Author",
            type_id=2,
            course_id=1,
            publish_year=2024,
            temporary=False,
        )
        db.session.add(thesis)
        db.session.commit()
        return thesis

    def test_card_valid_thesis(self, seeded_client):
        thesis = self._make_published_thesis()
        resp = seeded_client.get(f"/thesis_card?thesis_id={thesis.id}")
        head = _head_html(resp)
        assert resp.status_code == 200
        assert _meta_content(head, "og:title") == f"{thesis.name_ru} [{thesis.publish_year}]"
        assert 'property="og:type" content="article"' in head
        canonical = re.search(r'rel="canonical" href="([^"]+)"', head)
        assert canonical is not None
        assert canonical.group(1) == f"https://se.math.spbu.ru/thesis_card?thesis_id={thesis.id}"

    def test_card_title_links_to_card(self, seeded_client):
        thesis = self._make_published_thesis()
        html = seeded_client.get(f"/thesis_card?thesis_id={thesis.id}").get_data(as_text=True)
        assert f'href="/thesis_card?thesis_id={thesis.id}"' in html
        assert f'data-copy-url="http://localhost/thesis_card?thesis_id={thesis.id}"' in html
        assert 'data-content="Скопировать ссылку"' in html

    def test_card_missing_id(self, seeded_client):
        resp = seeded_client.get("/thesis_card")
        assert resp.status_code == 302

    def test_card_zero_id(self, seeded_client):
        resp = seeded_client.get("/thesis_card?thesis_id=0")
        assert resp.status_code == 302

    def test_card_nonexistent(self, seeded_client):
        resp = seeded_client.get("/thesis_card?thesis_id=99999")
        assert resp.status_code == 302

    def test_card_temporary_thesis_redirects(self, seeded_client):
        from conftest import _make_temp_thesis

        thesis = _make_temp_thesis(author="TempCard")
        resp = seeded_client.get(f"/thesis_card?thesis_id={thesis.id}")
        assert resp.status_code == 302

    def test_fetch_theses_contains_card_link(self, seeded_client):
        self._make_published_thesis()
        resp = seeded_client.get("/fetch_theses")
        assert resp.status_code == 200
        assert "/thesis_card?thesis_id=" in resp.get_data(as_text=True)


class TestOgThesisSearch:
    def test_search_query_og_title(self, seeded_client):
        resp = seeded_client.get("/theses.html?search=android+performance")
        head = _head_html(resp)
        assert resp.status_code == 200
        assert "Результаты поиска" in (_meta_content(head, "og:title") or "")

    def test_no_search_uses_static_title(self, seeded_client):
        resp = seeded_client.get("/theses.html")
        head = _head_html(resp)
        assert _meta_content(head, "og:title") == (
            "Курсовые, учебные практики и ВКР студентов Кафедры Системного Программирования"
        )

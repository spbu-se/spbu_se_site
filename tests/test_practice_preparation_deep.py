# -*- coding: utf-8 -*-
import io

import pytest


class TestPracticePreparation:
    def test_get(self, practice_thesis):
        resp = practice_thesis.get("/practice/preparation_for_defense/?id=1")
        assert resp.status_code in (200, 302)

    @pytest.mark.parametrize(
        "button,link_field,url",
        [
            ("submit_text_button", "text_link", "https://example.com/thesis.pdf"),
            ("submit_presentation_button", "presentation_link", "https://example.com/slides.pdf"),
        ],
    )
    def test_post_valid_link(self, practice_thesis, button, link_field, url):
        from se_models import CurrentThesis, db

        resp = practice_thesis.post(
            "/practice/preparation_for_defense/?id=1",
            data={button: "1", link_field: url},
        )
        assert resp.status_code in (200, 302)
        db.session.refresh(CurrentThesis.query.filter_by(author_id=1).first())
        ct = CurrentThesis.query.filter_by(author_id=1).first()
        assert getattr(ct, link_field) == url

    @pytest.mark.parametrize(
        "button,field,filename",
        [
            ("submit_text_button", "text", "thesis.txt"),
            ("submit_review_button", "supervisor_review", "review.txt"),
            ("submit_presentation_button", "presentation", "slides.txt"),
        ],
    )
    def test_post_invalid_file_type(self, practice_thesis, button, field, filename):
        resp = practice_thesis.post(
            "/practice/preparation_for_defense/?id=1",
            data={
                button: "1",
                field: (io.BytesIO(b"bad"), filename, "text/plain"),
            },
        )
        assert resp.status_code in (200, 302)
        with practice_thesis.session_transaction() as sess:
            flashes = sess["_flashes"]
            assert any(".PDF" in str(msg) for _, msg in flashes)

    @pytest.mark.parametrize(
        "button,field,filename,uri_attr",
        [
            ("submit_text_button", "text", "thesis.pdf", "text_uri"),
            ("submit_review_button", "supervisor_review", "review.pdf", "supervisor_review_uri"),
            ("submit_review_button", "consultant_review", "consult.pdf", "reviewer_review_uri"),
            ("submit_presentation_button", "presentation", "slides.pdf", "presentation_uri"),
        ],
    )
    def test_post_valid_pdf(self, practice_thesis, button, field, filename, uri_attr):
        from se_models import CurrentThesis, db

        pdf_bytes = b"%PDF-1.4 fake pdf content"
        resp = practice_thesis.post(
            "/practice/preparation_for_defense/?id=1",
            data={
                button: "1",
                field: (io.BytesIO(pdf_bytes), filename, "application/pdf"),
            },
        )
        assert resp.status_code in (200, 302)
        db.session.refresh(CurrentThesis.query.filter_by(author_id=1).first())
        ct = CurrentThesis.query.filter_by(author_id=1).first()
        assert getattr(ct, uri_attr) is not None
        assert getattr(ct, uri_attr).endswith(".pdf")

    def test_post_review_both_none(self, practice_thesis):
        resp = practice_thesis.post(
            "/practice/preparation_for_defense/?id=1",
            data={"submit_review_button": "1"},
        )
        assert resp.status_code in (200, 302)

    @pytest.mark.parametrize(
        "data,flash_substring",
        [
            ({"submit_text_button": "1", "text_link": ""}, "Вы не указали ссылку"),
            (
                {
                    "submit_text_button": "1",
                    "text": (io.BytesIO(b""), "", ""),
                    "text_link": "",
                },
                "не загрузили текст",
            ),
            (
                {"submit_text_button": "1", "text": (io.BytesIO(b""), "", "")},
                "не загрузили текст",
            ),
            (
                {
                    "submit_review_button": "1",
                    "supervisor_review": (io.BytesIO(b""), "", ""),
                    "consultant_review": (io.BytesIO(b""), "", ""),
                },
                "не загрузили",
            ),
        ],
    )
    def test_post_empty_upload_flash(self, practice_thesis, data, flash_substring):
        resp = practice_thesis.post("/practice/preparation_for_defense/?id=1", data=data)
        assert resp.status_code in (200, 302)
        with practice_thesis.session_transaction() as sess:
            flashes = sess["_flashes"]
            assert any(flash_substring in str(msg) for _, msg in flashes)

    def test_post_presentation_no_file_empty_link(self, practice_thesis):
        resp = practice_thesis.post(
            "/practice/preparation_for_defense/?id=1",
            data={"submit_presentation_button": "1", "presentation_link": ""},
        )
        assert resp.status_code in (200, 302)
        with practice_thesis.session_transaction() as sess:
            flashes = sess["_flashes"]
            assert any("не указали ссылку" in str(msg) for _, msg in flashes)

    def test_post_code_both_empty(self, practice_thesis):
        resp = practice_thesis.post(
            "/practice/preparation_for_defense/?id=1",
            data={"submit_code_button": "1", "code_link": "", "account_name": ""},
        )
        assert resp.status_code in (200, 302)
        with practice_thesis.session_transaction() as sess:
            flashes = sess["_flashes"]
            assert any("не указали" in str(msg) for _, msg in flashes)

    @pytest.mark.parametrize(
        "data,field_asserts",
        [
            (
                {"submit_code_button": "1", "code_link": "https://github.com/user/repo"},
                [("code_link", "https://github.com/user/repo")],
            ),
            (
                {"submit_code_button": "1", "account_name": "testuser"},
                [("account_name", "testuser")],
            ),
            (
                {
                    "submit_code_button": "1",
                    "code_link": "https://github.com/user/repo",
                    "account_name": "testuser",
                },
                [("code_link", "https://github.com/user/repo"), ("account_name", "testuser")],
            ),
        ],
    )
    def test_post_code(self, practice_thesis, data, field_asserts):
        from se_models import CurrentThesis, db

        resp = practice_thesis.post("/practice/preparation_for_defense/?id=1", data=data)
        assert resp.status_code in (200, 302)
        db.session.refresh(CurrentThesis.query.filter_by(author_id=1).first())
        ct = CurrentThesis.query.filter_by(author_id=1).first()
        for attr, expected in field_asserts:
            assert getattr(ct, attr) == expected

    @pytest.mark.parametrize(
        "field,seed_value,button_name",
        [
            ("text_uri", "some_text.pdf", "delete_text_button"),
            ("text_link", "https://example.com/thesis.pdf", "delete_text_link_button"),
            ("presentation_uri", "some_slides.pdf", "delete_presentation_button"),
            (
                "presentation_link",
                "https://example.com/slides.pdf",
                "delete_presentation_link_button",
            ),
            ("reviewer_review_uri", "consultant_review.pdf", "delete_reviewer_review_button"),
            ("supervisor_review_uri", "supervisor_review.pdf", "delete_supervisor_review_button"),
            ("code_link", "https://github.com/user/repo", "delete_code_link_button"),
            ("account_name", "testuser", "delete_account_name_button"),
        ],
    )
    def test_post_delete_field(self, practice_thesis, field, seed_value, button_name):
        from se_models import CurrentThesis, db

        ct = CurrentThesis.query.filter_by(author_id=1).first()
        setattr(ct, field, seed_value)
        db.session.commit()
        resp = practice_thesis.post(
            "/practice/preparation_for_defense/?id=1",
            data={button_name: "1"},
        )
        assert resp.status_code in (200, 302)
        db.session.refresh(ct)
        assert getattr(ct, field) is None

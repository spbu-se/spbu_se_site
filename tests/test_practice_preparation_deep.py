# -*- coding: utf-8 -*-
import io

import pytest


class TestPracticePreparation:
    def test_get(self, practice_thesis):
        resp = practice_thesis.get("/practice/preparation_for_defense/?id=1")
        assert resp.status_code in (200, 302)

    def test_post_text_no_file_empty_link(self, practice_thesis):
        resp = practice_thesis.post(
            "/practice/preparation_for_defense/?id=1",
            data={"submit_text_button": "1", "text_link": ""},
        )
        assert resp.status_code in (200, 302)
        with practice_thesis.session_transaction() as sess:
            flashes = sess["_flashes"]
            assert any("Р’С‹ РЅРµ СѓРєР°Р·Р°Р»Рё СЃСЃС‹Р»РєСѓ" in str(msg) for _, msg in flashes)

    def test_post_text_empty_file_and_empty_link(self, practice_thesis):
        resp = practice_thesis.post(
            "/practice/preparation_for_defense/?id=1",
            data={
                "submit_text_button": "1",
                "text": (io.BytesIO(b""), "", ""),
                "text_link": "",
            },
        )
        assert resp.status_code in (200, 302)
        with practice_thesis.session_transaction() as sess:
            flashes = sess["_flashes"]
            assert any("РЅРµ Р·Р°РіСЂСѓР·РёР»Рё С‚РµРєСЃС‚" in str(msg) for _, msg in flashes)

    def test_post_text_empty_file_no_link_field(self, practice_thesis):
        resp = practice_thesis.post(
            "/practice/preparation_for_defense/?id=1",
            data={
                "submit_text_button": "1",
                "text": (io.BytesIO(b""), "", ""),
            },
        )
        assert resp.status_code in (200, 302)
        with practice_thesis.session_transaction() as sess:
            flashes = sess["_flashes"]
            assert any("РЅРµ Р·Р°РіСЂСѓР·РёР»Рё С‚РµРєСЃС‚" in str(msg) for _, msg in flashes)

    def test_post_text_valid_link(self, practice_thesis):
        from se_models import CurrentThesis, db

        resp = practice_thesis.post(
            "/practice/preparation_for_defense/?id=1",
            data={
                "submit_text_button": "1",
                "text_link": "https://example.com/thesis.pdf",
            },
        )
        assert resp.status_code in (200, 302)
        db.session.refresh(CurrentThesis.query.filter_by(author_id=1).first())
        ct = CurrentThesis.query.filter_by(author_id=1).first()
        assert ct.text_link == "https://example.com/thesis.pdf"

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

    def test_post_text_valid_pdf(self, practice_thesis):
        from se_models import CurrentThesis, db

        pdf_bytes = b"%PDF-1.4 fake pdf content"
        resp = practice_thesis.post(
            "/practice/preparation_for_defense/?id=1",
            data={
                "submit_text_button": "1",
                "text": (io.BytesIO(pdf_bytes), "thesis.pdf", "application/pdf"),
            },
        )
        assert resp.status_code in (200, 302)
        db.session.refresh(CurrentThesis.query.filter_by(author_id=1).first())
        ct = CurrentThesis.query.filter_by(author_id=1).first()
        assert ct.text_uri is not None
        assert ct.text_uri.endswith(".pdf")

    def test_post_review_both_none(self, practice_thesis):
        resp = practice_thesis.post(
            "/practice/preparation_for_defense/?id=1",
            data={"submit_review_button": "1"},
        )
        assert resp.status_code in (200, 302)

    def test_post_review_empty_filenames(self, practice_thesis):
        resp = practice_thesis.post(
            "/practice/preparation_for_defense/?id=1",
            data={
                "submit_review_button": "1",
                "supervisor_review": (io.BytesIO(b""), "", ""),
                "consultant_review": (io.BytesIO(b""), "", ""),
            },
        )
        assert resp.status_code in (200, 302)
        with practice_thesis.session_transaction() as sess:
            flashes = sess["_flashes"]
            assert any("РЅРµ Р·Р°РіСЂСѓР·РёР»Рё" in str(msg) for _, msg in flashes)

    def test_post_review_supervisor_valid(self, practice_thesis):
        from se_models import CurrentThesis, db

        pdf_bytes = b"%PDF-1.4 fake supervisor review"
        resp = practice_thesis.post(
            "/practice/preparation_for_defense/?id=1",
            data={
                "submit_review_button": "1",
                "supervisor_review": (
                    io.BytesIO(pdf_bytes),
                    "review.pdf",
                    "application/pdf",
                ),
            },
        )
        assert resp.status_code in (200, 302)
        db.session.refresh(CurrentThesis.query.filter_by(author_id=1).first())
        ct = CurrentThesis.query.filter_by(author_id=1).first()
        assert ct.supervisor_review_uri is not None
        assert ct.supervisor_review_uri.endswith(".pdf")

    def test_post_review_reviewer_valid(self, practice_thesis):
        from se_models import CurrentThesis, db

        pdf_bytes = b"%PDF-1.4 fake reviewer review"
        resp = practice_thesis.post(
            "/practice/preparation_for_defense/?id=1",
            data={
                "submit_review_button": "1",
                "consultant_review": (
                    io.BytesIO(pdf_bytes),
                    "consult.pdf",
                    "application/pdf",
                ),
            },
        )
        assert resp.status_code in (200, 302)
        db.session.refresh(CurrentThesis.query.filter_by(author_id=1).first())
        ct = CurrentThesis.query.filter_by(author_id=1).first()
        assert ct.reviewer_review_uri is not None
        assert ct.reviewer_review_uri.endswith(".pdf")

    def test_post_presentation_no_file_empty_link(self, practice_thesis):
        resp = practice_thesis.post(
            "/practice/preparation_for_defense/?id=1",
            data={"submit_presentation_button": "1", "presentation_link": ""},
        )
        assert resp.status_code in (200, 302)
        with practice_thesis.session_transaction() as sess:
            flashes = sess["_flashes"]
            assert any("РЅРµ СѓРєР°Р·Р°Р»Рё СЃСЃС‹Р»РєСѓ" in str(msg) for _, msg in flashes)

    def test_post_presentation_valid_link(self, practice_thesis):
        from se_models import CurrentThesis, db

        resp = practice_thesis.post(
            "/practice/preparation_for_defense/?id=1",
            data={
                "submit_presentation_button": "1",
                "presentation_link": "https://example.com/slides.pdf",
            },
        )
        assert resp.status_code in (200, 302)
        db.session.refresh(CurrentThesis.query.filter_by(author_id=1).first())
        ct = CurrentThesis.query.filter_by(author_id=1).first()
        assert ct.presentation_link == "https://example.com/slides.pdf"

    def test_post_presentation_valid_pdf(self, practice_thesis):
        from se_models import CurrentThesis, db

        pdf_bytes = b"%PDF-1.4 fake presentation"
        resp = practice_thesis.post(
            "/practice/preparation_for_defense/?id=1",
            data={
                "submit_presentation_button": "1",
                "presentation": (
                    io.BytesIO(pdf_bytes),
                    "slides.pdf",
                    "application/pdf",
                ),
            },
        )
        assert resp.status_code in (200, 302)
        db.session.refresh(CurrentThesis.query.filter_by(author_id=1).first())
        ct = CurrentThesis.query.filter_by(author_id=1).first()
        assert ct.presentation_uri is not None
        assert ct.presentation_uri.endswith(".pdf")

    def test_post_code_both_empty(self, practice_thesis):
        resp = practice_thesis.post(
            "/practice/preparation_for_defense/?id=1",
            data={"submit_code_button": "1", "code_link": "", "account_name": ""},
        )
        assert resp.status_code in (200, 302)
        with practice_thesis.session_transaction() as sess:
            flashes = sess["_flashes"]
            assert any("РЅРµ СѓРєР°Р·Р°Р»Рё" in str(msg) for _, msg in flashes)

    def test_post_code_link_only(self, practice_thesis):
        from se_models import CurrentThesis, db

        resp = practice_thesis.post(
            "/practice/preparation_for_defense/?id=1",
            data={
                "submit_code_button": "1",
                "code_link": "https://github.com/user/repo",
            },
        )
        assert resp.status_code in (200, 302)
        db.session.refresh(CurrentThesis.query.filter_by(author_id=1).first())
        ct = CurrentThesis.query.filter_by(author_id=1).first()
        assert ct.code_link == "https://github.com/user/repo"

    def test_post_code_account_only(self, practice_thesis):
        from se_models import CurrentThesis, db

        resp = practice_thesis.post(
            "/practice/preparation_for_defense/?id=1",
            data={"submit_code_button": "1", "account_name": "testuser"},
        )
        assert resp.status_code in (200, 302)
        db.session.refresh(CurrentThesis.query.filter_by(author_id=1).first())
        ct = CurrentThesis.query.filter_by(author_id=1).first()
        assert ct.account_name == "testuser"

    def test_post_code_both_valid(self, practice_thesis):
        from se_models import CurrentThesis, db

        resp = practice_thesis.post(
            "/practice/preparation_for_defense/?id=1",
            data={
                "submit_code_button": "1",
                "code_link": "https://github.com/user/repo",
                "account_name": "testuser",
            },
        )
        assert resp.status_code in (200, 302)
        db.session.refresh(CurrentThesis.query.filter_by(author_id=1).first())
        ct = CurrentThesis.query.filter_by(author_id=1).first()
        assert ct.code_link == "https://github.com/user/repo"
        assert ct.account_name == "testuser"

    def test_post_delete_text_button(self, practice_thesis):
        from se_models import CurrentThesis, db

        ct = CurrentThesis.query.filter_by(author_id=1).first()
        ct.text_uri = "some_text.pdf"
        db.session.commit()
        resp = practice_thesis.post(
            "/practice/preparation_for_defense/?id=1",
            data={"delete_text_button": "1"},
        )
        assert resp.status_code in (200, 302)
        db.session.refresh(ct)
        assert ct.text_uri is None

    def test_post_delete_text_link_button(self, practice_thesis):
        from se_models import CurrentThesis, db

        ct = CurrentThesis.query.filter_by(author_id=1).first()
        ct.text_link = "https://example.com/thesis.pdf"
        db.session.commit()
        resp = practice_thesis.post(
            "/practice/preparation_for_defense/?id=1",
            data={"delete_text_link_button": "1"},
        )
        assert resp.status_code in (200, 302)
        db.session.refresh(ct)
        assert ct.text_link is None

    def test_post_delete_presentation_button(self, practice_thesis):
        from se_models import CurrentThesis, db

        ct = CurrentThesis.query.filter_by(author_id=1).first()
        ct.presentation_uri = "some_slides.pdf"
        db.session.commit()
        resp = practice_thesis.post(
            "/practice/preparation_for_defense/?id=1",
            data={"delete_presentation_button": "1"},
        )
        assert resp.status_code in (200, 302)
        db.session.refresh(ct)
        assert ct.presentation_uri is None

    def test_post_delete_presentation_link_button(self, practice_thesis):
        from se_models import CurrentThesis, db

        ct = CurrentThesis.query.filter_by(author_id=1).first()
        ct.presentation_link = "https://example.com/slides.pdf"
        db.session.commit()
        resp = practice_thesis.post(
            "/practice/preparation_for_defense/?id=1",
            data={"delete_presentation_link_button": "1"},
        )
        assert resp.status_code in (200, 302)
        db.session.refresh(ct)
        assert ct.presentation_link is None

    def test_post_delete_reviewer_review_button(self, practice_thesis):
        from se_models import CurrentThesis, db

        ct = CurrentThesis.query.filter_by(author_id=1).first()
        ct.reviewer_review_uri = "consultant_review.pdf"
        db.session.commit()
        resp = practice_thesis.post(
            "/practice/preparation_for_defense/?id=1",
            data={"delete_reviewer_review_button": "1"},
        )
        assert resp.status_code in (200, 302)
        db.session.refresh(ct)
        assert ct.reviewer_review_uri is None

    def test_post_delete_supervisor_review_button(self, practice_thesis):
        from se_models import CurrentThesis, db

        ct = CurrentThesis.query.filter_by(author_id=1).first()
        ct.supervisor_review_uri = "supervisor_review.pdf"
        db.session.commit()
        resp = practice_thesis.post(
            "/practice/preparation_for_defense/?id=1",
            data={"delete_supervisor_review_button": "1"},
        )
        assert resp.status_code in (200, 302)
        db.session.refresh(ct)
        assert ct.supervisor_review_uri is None

    def test_post_delete_code_link_button(self, practice_thesis):
        from se_models import CurrentThesis, db

        ct = CurrentThesis.query.filter_by(author_id=1).first()
        ct.code_link = "https://github.com/user/repo"
        db.session.commit()
        resp = practice_thesis.post(
            "/practice/preparation_for_defense/?id=1",
            data={"delete_code_link_button": "1"},
        )
        assert resp.status_code in (200, 302)
        db.session.refresh(ct)
        assert ct.code_link is None

    def test_post_delete_account_name_button(self, practice_thesis):
        from se_models import CurrentThesis, db

        ct = CurrentThesis.query.filter_by(author_id=1).first()
        ct.account_name = "testuser"
        db.session.commit()
        resp = practice_thesis.post(
            "/practice/preparation_for_defense/?id=1",
            data={"delete_account_name_button": "1"},
        )
        assert resp.status_code in (200, 302)
        db.session.refresh(ct)
        assert ct.account_name is None

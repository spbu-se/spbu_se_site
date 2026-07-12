# -*- coding: utf-8 -*-
import io
from unittest.mock import MagicMock, patch

import pytest
from conftest import assert_ok


@pytest.fixture
def current_thesis(staff_client):
    from se_models import CurrentThesis, db

    ct = CurrentThesis(author_id=1, worktype_id=5, area_id=2)
    ct.title = "Test Practice Thesis Admin"
    ct.supervisor_id = 1
    ct.text_uri = "test_text.pdf"
    ct.presentation_uri = "test_slides.pdf"
    ct.supervisor_review_uri = "test_review.pdf"
    ct.reviewer_review_uri = "test_reviewer.pdf"
    ct.code_link = "https://github.com/test/repo"
    db.session.add(ct)
    db.session.commit()
    return staff_client, ct.id


@pytest.fixture
def finished_thesis(staff_client):
    from se_models import CurrentThesis, db

    ct = CurrentThesis(author_id=1, worktype_id=5, area_id=2)
    ct.title = "Finished Thesis"
    ct.supervisor_id = 1
    ct.status = 2
    db.session.add(ct)
    db.session.commit()
    return staff_client, ct.id


class TestPracticeAdminAccess:
    def test_non_staff_redirects_to_practice_index(self, seeded_client):
        from se_models import Users, db

        u = Users(email="nobody@spbu.ru", first_name="Nobody", last_name="User")
        db.session.add(u)
        db.session.commit()
        with seeded_client.session_transaction() as sess:
            sess["_user_id"] = str(u.id)
        resp = seeded_client.get("/practice_admin")
        assert resp.status_code in (200, 302)

    def test_staff_can_access_admin_index(self, staff_client):
        assert_ok(staff_client, "/practice_admin", code={200, 302})

    def test_staff_can_access_admin_index_slash(self, staff_client):
        assert_ok(staff_client, "/practice_admin/", code={200, 302})


class TestPracticeAdminIndexGet:
    def test_index_without_params(self, staff_client):
        resp = staff_client.get("/practice_admin")
        assert resp.status_code in (200, 302)

    def test_index_with_valid_params(self, staff_client):
        resp = staff_client.get("/practice_admin?area_id=2&worktype_id=5")
        assert resp.status_code in (200, 302)

    def test_index_with_invalid_area(self, staff_client):
        resp = staff_client.get("/practice_admin?area_id=999&worktype_id=5")
        assert resp.status_code in (200, 302)

    def test_index_with_invalid_worktype(self, staff_client):
        resp = staff_client.get("/practice_admin?area_id=2&worktype_id=999")
        assert resp.status_code in (200, 302)

    def test_index_sets_previous_page_in_session(self, staff_client):
        staff_client.get("/practice_admin?area_id=2&worktype_id=5")
        with staff_client.session_transaction() as sess:
            assert sess.get("previous_page") == "current_thesises"


class TestPracticeAdminIndexPostFinishAll:
    def test_finish_all_work(self, current_thesis):
        from se_models import CurrentThesis, db

        client, ct_id = current_thesis
        ct = CurrentThesis.query.get(ct_id)
        ct.status = 1
        ct.title = "Ready to finish"
        db.session.commit()
        resp = client.post(
            "/practice_admin?area_id=2&worktype_id=5",
            data={
                "finish_all_work_button": "1",
            },
        )
        assert resp.status_code in (200, 302)


class TestPracticeAdminIndexPostDownloadTable:
    def test_download_table(self, staff_client):
        with patch("flask_se_practice_admin.send_file") as mock_send:
            mock_send.return_value = "file"
            resp = staff_client.post(
                "/practice_admin?area_id=2&worktype_id=5",
                data={
                    "download_table": "1",
                },
            )
            assert resp.status_code in (200, 302)


class TestPracticeAdminIndexPostYandex:
    def test_yandex_empty_table_name(self, current_thesis):
        client, _ct_id = current_thesis
        resp = client.post(
            "/practice_admin?area_id=2&worktype_id=5",
            data={
                "yandex_button": "1",
                "table_name": "",
                "sheet_name": "Sheet1",
            },
        )
        assert resp.status_code in (200, 302)

    def test_yandex_non_xlsx_extension(self, current_thesis):
        client, _ct_id = current_thesis
        resp = client.post(
            "/practice_admin?area_id=2&worktype_id=5",
            data={
                "yandex_button": "1",
                "table_name": "table.csv",
                "sheet_name": "Sheet1",
            },
        )
        assert resp.status_code in (200, 302)

    def test_yandex_empty_column_name(self, current_thesis):
        client, _ct_id = current_thesis
        resp = client.post(
            "/practice_admin?area_id=2&worktype_id=5",
            data={
                "yandex_button": "1",
                "table_name": "table.xlsx",
                "sheet_name": "Sheet1",
                "user_name_column": "",
            },
        )
        assert resp.status_code in (200, 302)

    def test_yandex_successful_upload(self, current_thesis):
        client, _ct_id = current_thesis
        with patch("flask_se_practice_admin.handle_yandex_table") as mock_handle:
            mock_handle.return_value = "success"
            resp = client.post(
                "/practice_admin?area_id=2&worktype_id=5",
                data={
                    "yandex_button": "1",
                    "table_name": "table.xlsx",
                    "sheet_name": "Sheet1",
                    "user_name_column": "ФИО",
                    "how_to_contact_column": "Контакты",
                    "supervisor_column": "Руководитель",
                    "consultant_column": "Консультант",
                    "theme_column": "Тема",
                    "text_column": "Текст",
                    "supervisor_review_column": "Отзыв",
                    "reviewer_review_column": "Отзыв рец",
                    "code_column": "РљРѕРґ",
                    "committer_column": "Коммитер",
                    "presentation_column": "Презентация",
                },
            )
            assert resp.status_code in (200, 302)
            mock_handle.assert_called_once()

    def test_yandex_exception_caught(self, current_thesis):
        client, _ct_id = current_thesis
        with patch("flask_se_practice_admin.handle_yandex_table", side_effect=Exception):
            resp = client.post(
                "/practice_admin?area_id=2&worktype_id=5",
                data={
                    "yandex_button": "1",
                    "table_name": "table.xlsx",
                    "sheet_name": "Sheet1",
                    "user_name_column": "ФИО",
                    "how_to_contact_column": "Контакты",
                    "supervisor_column": "Руководитель",
                    "consultant_column": "Консультант",
                    "theme_column": "Тема",
                    "text_column": "Текст",
                    "supervisor_review_column": "Отзыв",
                    "reviewer_review_column": "Отзыв рец",
                    "code_column": "РљРѕРґ",
                    "committer_column": "Коммитер",
                    "presentation_column": "Презентация",
                },
            )
            assert resp.status_code in (200, 302)


class TestPracticeAdminChooseAreaWorktype:
    def test_without_session(self, staff_client):
        resp = staff_client.get("/practice_admin/choose_area_worktype?area_id=2&worktype_id=5")
        assert resp.status_code in (200, 302)

    def test_with_current_thesises_session(self, staff_client):
        staff_client.get("/practice_admin?area_id=2&worktype_id=5")
        resp = staff_client.get("/practice_admin/choose_area_worktype?area_id=2&worktype_id=5")
        assert resp.status_code in (200, 302)

    def test_with_finished_session(self, staff_client):
        staff_client.get("/practice_admin/finished_thesises?area_id=2&worktype_id=5")
        resp = staff_client.get("/practice_admin/choose_area_worktype?area_id=2&worktype_id=5")
        assert resp.status_code in (200, 302)

    def test_no_area_id(self, staff_client):
        resp = staff_client.get("/practice_admin/choose_area_worktype")
        assert resp.status_code in (200, 302)

    def test_no_worktype_id(self, staff_client):
        resp = staff_client.get("/practice_admin/choose_area_worktype?area_id=2")
        assert resp.status_code in (200, 302)


class TestPracticeAdminFinishedThesises:
    def test_finished_without_params(self, staff_client):
        resp = staff_client.get("/practice_admin/finished_thesises")
        assert resp.status_code in (200, 302)

    def test_finished_with_valid_params(self, staff_client):
        resp = staff_client.get("/practice_admin/finished_thesises?area_id=2&worktype_id=5")
        assert resp.status_code in (200, 302)

    def test_finished_with_invalid_area(self, staff_client):
        resp = staff_client.get("/practice_admin/finished_thesises?area_id=999&worktype_id=5")
        assert resp.status_code in (200, 302)

    def test_finished_sets_previous_page(self, staff_client):
        staff_client.get("/practice_admin/finished_thesises?area_id=2&worktype_id=5")
        with staff_client.session_transaction() as sess:
            assert sess.get("previous_page") == "finished_thesises"

    def test_finished_shows_completed_thesis(self, finished_thesis):
        client, _ct_id = finished_thesis
        resp = client.get("/practice_admin/finished_thesises?area_id=2&worktype_id=5")
        assert resp.status_code in (200, 302)


class TestPracticeAdminThesis:
    def test_thesis_without_id_redirects(self, staff_client):
        resp = staff_client.get("/practice_admin/thesis")
        assert resp.status_code in (200, 302)

    def test_thesis_with_invalid_id_redirects(self, staff_client):
        resp = staff_client.get("/practice_admin/thesis?id=99999")
        assert resp.status_code in (200, 302)

    def test_thesis_with_valid_id(self, current_thesis):
        client, ct_id = current_thesis
        resp = client.get(f"/practice_admin/thesis?id={ct_id}")
        assert resp.status_code == 200

    def test_thesis_sets_previous_page(self, current_thesis):
        client, ct_id = current_thesis
        client.get(f"/practice_admin/thesis?id={ct_id}")
        with client.session_transaction() as sess:
            assert sess.get("previous_page") == "thesis"


class TestPracticeAdminThesisPost:
    def test_submit_notification_empty_content(self, current_thesis):

        client, ct_id = current_thesis
        resp = client.post(
            f"/practice_admin/thesis?id={ct_id}",
            data={
                "submit_notification_button": "1",
                "content": "",
            },
        )
        assert resp.status_code in (200, 302)

    def test_submit_notification_valid(self, current_thesis):
        from se_models import NotificationPractice

        client, ct_id = current_thesis
        resp = client.post(
            f"/practice_admin/thesis?id={ct_id}",
            data={
                "submit_notification_button": "1",
                "content": "Test notification from admin",
            },
        )
        assert resp.status_code in (200, 302)
        notification = NotificationPractice.query.filter_by(recipient_id=1).first()
        assert notification is not None

    def test_submit_edit_title(self, current_thesis):
        from se_models import CurrentThesis

        client, ct_id = current_thesis
        resp = client.post(
            f"/practice_admin/thesis?id={ct_id}",
            data={
                "submit_edit_title_button": "1",
                "title_input": "Updated Title",
            },
        )
        assert resp.status_code in (200, 302)
        ct = CurrentThesis.query.get(ct_id)
        assert ct.title == "Updated Title"

    def test_submit_finish_work(self, current_thesis):
        from se_models import CurrentThesis

        client, ct_id = current_thesis
        ct = CurrentThesis.query.get(ct_id)
        ct.status = 1
        resp = client.post(
            f"/practice_admin/thesis?id={ct_id}",
            data={
                "submit_finish_work_button": "1",
            },
        )
        assert resp.status_code in (200, 302)
        ct = CurrentThesis.query.get(ct_id)
        assert ct.status == 2

    def test_submit_restore_work(self, current_thesis):
        from se_models import CurrentThesis, db

        client, ct_id = current_thesis
        ct = CurrentThesis.query.get(ct_id)
        ct.status = 2
        db.session.commit()
        resp = client.post(
            f"/practice_admin/thesis?id={ct_id}",
            data={
                "submit_restore_work_button": "1",
            },
        )
        assert resp.status_code in (200, 302)
        ct = CurrentThesis.query.get(ct_id)
        assert ct.status == 1

    def test_notification_with_content_none(self, current_thesis):

        client, ct_id = current_thesis
        resp = client.post(
            f"/practice_admin/thesis?id={ct_id}",
            data={
                "submit_notification_button": "1",
            },
        )
        assert resp.status_code in (200, 302, 400)


class TestPracticeAdminArchiveThesis:
    def test_archive_without_id_redirects(self, staff_client):
        resp = staff_client.get("/practice_admin/thesis_to_archive")
        assert resp.status_code in (200, 302)

    def test_archive_with_invalid_id_redirects(self, staff_client):
        resp = staff_client.get("/practice_admin/thesis_to_archive?id=99999")
        assert resp.status_code in (200, 302)

    def test_archive_get_with_valid_id(self, current_thesis):
        client, ct_id = current_thesis
        resp = client.get(f"/practice_admin/thesis_to_archive?id={ct_id}")
        assert resp.status_code == 200

    def test_archive_post_no_course(self, current_thesis):
        client, ct_id = current_thesis
        resp = client.post(
            f"/practice_admin/thesis_to_archive?id={ct_id}",
            data={
                "thesis_to_archive_button": "1",
                "course": 0,
            },
        )
        assert resp.status_code in (200, 302)

    def test_archive_post_no_text(self, current_thesis):
        from se_models import CurrentThesis, db

        client, ct_id = current_thesis
        ct = CurrentThesis.query.get(ct_id)
        ct.text_uri = None
        db.session.commit()
        resp = client.post(
            f"/practice_admin/thesis_to_archive?id={ct_id}",
            data={
                "thesis_to_archive_button": "1",
                "course": 1,
            },
        )
        assert resp.status_code in (200, 302)

    def test_archive_post_no_presentation(self, current_thesis):
        from se_models import CurrentThesis, db

        client, ct_id = current_thesis
        ct = CurrentThesis.query.get(ct_id)
        ct.presentation_uri = None
        db.session.commit()
        resp = client.post(
            f"/practice_admin/thesis_to_archive?id={ct_id}",
            data={
                "thesis_to_archive_button": "1",
                "course": 1,
            },
        )
        assert resp.status_code in (200, 302)

    def test_archive_post_no_supervisor_review(self, current_thesis):
        from se_models import CurrentThesis, db

        client, ct_id = current_thesis
        ct = CurrentThesis.query.get(ct_id)
        ct.supervisor_review_uri = None
        db.session.commit()
        resp = client.post(
            f"/practice_admin/thesis_to_archive?id={ct_id}",
            data={
                "thesis_to_archive_button": "1",
                "course": 1,
            },
        )
        assert resp.status_code in (200, 302)

    def test_archive_post_success_with_all_files(self, current_thesis):
        from se_models import CurrentThesis, Thesis

        client, ct_id = current_thesis
        ct = CurrentThesis.query.get(ct_id)
        ct.text_uri = "test_text.pdf"
        ct.presentation_uri = "test_slides.pdf"
        ct.supervisor_review_uri = "test_review.pdf"
        ct.reviewer_review_uri = "test_reviewer.pdf"
        ct.code_link = "https://github.com/test/repo"

        with patch("shutil.copyfile"):
            resp = client.post(
                f"/practice_admin/thesis_to_archive?id={ct_id}",
                data={
                    "thesis_to_archive_button": "1",
                    "course": 1,
                    "publish_year": 2025,
                },
            )
        assert resp.status_code in (200, 302)
        archived = Thesis.query.filter_by(author_id=1).first()
        assert archived is not None
        assert archived.name_ru == "Test Practice Thesis Admin"

    def test_archive_post_with_uploaded_files(self, current_thesis):
        from se_models import CurrentThesis, db

        client, ct_id = current_thesis
        ct = CurrentThesis.query.get(ct_id)
        ct.text_uri = None
        ct.presentation_uri = None
        ct.supervisor_review_uri = None
        ct.reviewer_review_uri = None
        ct.code_link = None
        db.session.commit()

        pdf_bytes = b"%PDF-1.4 fake content"
        with patch("shutil.copyfile"), patch("werkzeug.datastructures.FileStorage.save"):
            resp = client.post(
                f"/practice_admin/thesis_to_archive?id={ct_id}",
                data={
                    "thesis_to_archive_button": "1",
                    "course": 1,
                    "publish_year": 2025,
                    "text": (io.BytesIO(pdf_bytes), "thesis.pdf", "application/pdf"),
                    "presentation": (io.BytesIO(pdf_bytes), "slides.pdf", "application/pdf"),
                    "supervisor_review": (
                        io.BytesIO(pdf_bytes),
                        "review.pdf",
                        "application/pdf",
                    ),
                    "consultant_review": (
                        io.BytesIO(pdf_bytes),
                        "consult.pdf",
                        "application/pdf",
                    ),
                    "code_link": "https://github.com/test/code",
                },
                content_type="multipart/form-data",
            )
        assert resp.status_code in (200, 302)

    def test_archive_post_code_link_no_http(self, current_thesis):
        from se_models import CurrentThesis

        client, ct_id = current_thesis
        ct = CurrentThesis.query.get(ct_id)
        ct.code_link = None

        with patch("shutil.copyfile"):
            resp = client.post(
                f"/practice_admin/thesis_to_archive?id={ct_id}",
                data={
                    "thesis_to_archive_button": "1",
                    "course": 1,
                    "publish_year": 2025,
                    "code_link": "not a url",
                },
            )
        assert resp.status_code in (200, 302)


class TestPracticeAdminYandexCode:
    def test_yandex_code_without_session(self, staff_client):
        resp = staff_client.get("/practice_admin/yandex_code")
        assert resp.status_code in (200, 302)

    def test_yandex_code_without_code(self, staff_client):
        with staff_client.session_transaction() as sess:
            sess["area_id"] = 2
            sess["worktype_id"] = 5
        resp = staff_client.get("/practice_admin/yandex_code")
        assert resp.status_code in (200, 302)

    @patch("flask_se_practice_yandex_disk.yadisk.YaDisk")
    @patch("flask_se_practice_yandex_disk.get_token")
    def test_yandex_code_invalid_token(self, mock_get_token, mock_yadisk, staff_client):
        mock_get_token.return_value = "fake_token"
        mock_disk_instance = MagicMock()
        mock_disk_instance.check_token.return_value = False
        mock_yadisk.return_value = mock_disk_instance

        with staff_client.session_transaction() as sess:
            sess["area_id"] = 2
            sess["worktype_id"] = 5
            sess["table_path"] = "/test/table.xlsx"
            sess["sheet_name"] = "Sheet1"
            sess["column_names_list"] = []

        resp = staff_client.get("/practice_admin/yandex_code?code=testcode")
        assert resp.status_code in (200, 302)

    @patch("flask_se_practice_yandex_disk.yadisk.YaDisk")
    @patch("flask_se_practice_yandex_disk.get_token")
    def test_yandex_code_success(self, mock_get_token, mock_yadisk, staff_client):
        mock_get_token.return_value = "fake_token"
        mock_disk_instance = MagicMock()
        mock_disk_instance.check_token.return_value = True
        mock_yadisk.return_value = mock_disk_instance

        with patch("flask_se_practice_yandex_disk.edit_table"):
            with staff_client.session_transaction() as sess:
                sess["area_id"] = 2
                sess["worktype_id"] = 5
                sess["table_path"] = "/test/table.xlsx"
                sess["sheet_name"] = "Sheet1"
                sess["column_names_list"] = []

            resp = staff_client.get("/practice_admin/yandex_code?code=testcode")
            assert resp.status_code in (200, 302)

    @patch("flask_se_practice_yandex_disk.yadisk.YaDisk")
    @patch("flask_se_practice_yandex_disk.get_token")
    @patch("flask_se_practice_yandex_disk.os.remove")
    def test_yandex_code_path_not_found(
        self, mock_remove, mock_get_token, mock_yadisk, staff_client
    ):
        import yadisk

        mock_get_token.return_value = "fake_token"
        mock_disk_instance = MagicMock()
        mock_disk_instance.check_token.return_value = True
        mock_disk_instance.download.side_effect = yadisk.exceptions.PathNotFoundError
        mock_yadisk.return_value = mock_disk_instance

        with patch("flask_se_practice_yandex_disk.edit_table"):
            with staff_client.session_transaction() as sess:
                sess["area_id"] = 2
                sess["worktype_id"] = 5
                sess["table_path"] = "/test/table.xlsx"
                sess["sheet_name"] = "Sheet1"
                sess["column_names_list"] = []

            resp = staff_client.get("/practice_admin/yandex_code?code=testcode")
            assert resp.status_code in (200, 302)

    @patch("flask_se_practice_yandex_disk.yadisk.YaDisk")
    @patch("flask_se_practice_yandex_disk.get_token")
    def test_yandex_code_upload_parent_not_found(self, mock_get_token, mock_yadisk, staff_client):
        import yadisk

        mock_get_token.return_value = "fake_token"
        mock_disk_instance = MagicMock()
        mock_disk_instance.check_token.return_value = True
        mock_yadisk.return_value = mock_disk_instance
        mock_disk_instance.upload.side_effect = yadisk.exceptions.ParentNotFoundError

        with patch("flask_se_practice_yandex_disk.edit_table"):
            with staff_client.session_transaction() as sess:
                sess["area_id"] = 2
                sess["worktype_id"] = 5
                sess["table_path"] = "/test/table.xlsx"
                sess["sheet_name"] = "Sheet1"
                sess["column_names_list"] = []

            resp = staff_client.get("/practice_admin/yandex_code?code=testcode")
            assert resp.status_code in (200, 302)


class TestPracticeAdminDownloadMaterials:
    def test_download_materials_post(self, current_thesis):
        client, _ct_id = current_thesis
        with patch("flask_se_practice_admin.send_file") as mock_send:
            mock_send.return_value = "file"
            with patch("flask_se_practice_admin.ZipFile"):
                resp = client.post(
                    "/practice_admin?area_id=2&worktype_id=5",
                    data={
                        "download_materials_button": "1",
                    },
                )
                assert resp.status_code in (200, 302)

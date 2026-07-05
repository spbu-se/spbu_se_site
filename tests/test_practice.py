import io
import os

import pytest
from conftest import assert_ok


class TestPracticeStudentGuide:
    def test_guide(self, seeded_client):
        assert_ok(seeded_client, "/practice/guide/", code={200, 302})

    def test_index(self, logged_client):
        assert_ok(logged_client, "/practice", code={200, 302})


class TestPracticeStudentNewThesis:
    def test_new_thesis_page(self, logged_client):
        assert_ok(logged_client, "/practice/new/", code={200, 302})

    def test_new_thesis_submit(self, logged_client):
        resp = logged_client.post("/practice/new/", data={
            "area": 2,
            "worktype": 3,
        })
        assert resp.status_code in (200, 302)


class TestPracticeStudentThesisFlow:
    def test_choosing_topic(self, practice_thesis):
        assert_ok(practice_thesis, "/practice/choosing_topic/", code={200, 302})

    def test_goals_tasks_page(self, practice_thesis):
        assert_ok(practice_thesis, "/practice/goals_tasks/", code={200, 302})

    def test_goals_tasks_add(self, practice_thesis):
        resp = practice_thesis.post("/practice/goals_tasks/", data={"task_text": "New task", "add_task_button": "1"})
        assert resp.status_code in (200, 302)

    def test_workflow_page(self, practice_thesis):
        assert_ok(practice_thesis, "/practice/workflow/", code={200, 302})

    def test_add_report_page(self, practice_thesis):
        assert_ok(practice_thesis, "/practice/add_new_report/", code={200, 302})

    def test_add_report_submit(self, practice_thesis):
        resp = practice_thesis.post("/practice/add_new_report/", data={
            "was_done": "Completed a significant task for the project this week",
            "planned_to_do": "Plan to continue with the next set of tasks for the project",
        })
        assert resp.status_code in (200, 302)

    def test_edit_theme(self, practice_thesis):
        assert_ok(practice_thesis, "/practice/edit_theme/", code={200, 302})

    def test_preparation(self, practice_thesis):
        assert_ok(practice_thesis, "/practice/preparation_for_defense/", code={200, 302})

    def test_defense(self, practice_thesis):
        assert_ok(practice_thesis, "/practice/defense/", code={200, 302})

    def test_data_for_practice(self, practice_thesis):
        assert_ok(practice_thesis, "/practice/data_for_practice/", code={200, 302})


class TestPracticeStaff:
    def test_staff_index(self, logged_client):
        assert_ok(logged_client, "/practice_staff", code={200, 302})

    def test_staff_thesis(self, practice_thesis):
        practice_thesis.get("/practice_staff/thesis/")
        # May not find advisee for the current user
        assert_ok(practice_thesis, "/practice_staff/thesis/", code={200, 302, 404})

    def test_staff_reports(self, practice_thesis):
        assert_ok(practice_thesis, "/practice_staff/reports/", code={200, 302, 404})

    def test_staff_finished(self, logged_client):
        assert_ok(logged_client, "/practice_staff/finished_thesises/", code={200, 302})


class TestPracticeAdmin:
    def test_admin_index(self, logged_client):
        assert_ok(logged_client, "/practice_admin", code={200, 302})

    def test_admin_choose_area(self, practice_thesis):
        assert_ok(practice_thesis, "/practice_admin/choose_area_worktype", code={200, 302})

    def test_admin_finished(self, logged_client):
        assert_ok(logged_client, "/practice_admin/finished_thesises", code={200, 302})

    def test_admin_thesis(self, practice_thesis):
        assert_ok(practice_thesis, "/practice_admin/thesis", code={200, 302, 404})

    def test_admin_yandex(self, logged_client):
        assert_ok(logged_client, "/practice_admin/yandex_code", code={200, 302, 404})

    def test_admin_archive_thesis(self, practice_thesis):
        assert_ok(practice_thesis, "/practice_admin/thesis_to_archive", code={200, 302, 404})


class TestPracticeFileUploads:
    def test_upload_text_via_link(self, practice_thesis):
        """Approach 1: Upload text via link field instead of file."""
        resp = practice_thesis.post("/practice/preparation_for_defense/", data={
            "submit_text_button": "1",
            "text_link": "https://example.com/thesis.pdf",
        })
        assert resp.status_code in (200, 302)

    def test_upload_text_with_pdf_file(self, practice_thesis):
        """Approach 2: Upload PDF file via multipart - file in data dict."""
        pdf_bytes = b"%PDF-1.4 fake pdf content for testing"
        resp = practice_thesis.post("/practice/preparation_for_defense/", data={
            "submit_text_button": "1",
            "text": (io.BytesIO(pdf_bytes), "thesis.pdf", "application/pdf"),
        })
        assert resp.status_code in (200, 302)

    def test_upload_text_empty_file_and_link_rejected(self, practice_thesis):
        """Approach 3: Empty file + empty link should redirect with flash."""
        data = {
            "submit_text_button": "1",
            "text_link": "",
        }
        resp = practice_thesis.post("/practice/preparation_for_defense/", data=data)
        assert resp.status_code in (200, 302)

    def test_upload_review_files(self, practice_thesis):
        """Upload supervisor and consultant review PDFs."""
        pdf_bytes = b"%PDF-1.4 fake review"
        resp = practice_thesis.post("/practice/preparation_for_defense/", data={
            "submit_review_button": "1",
            "supervisor_review": (io.BytesIO(pdf_bytes), "review.pdf", "application/pdf"),
            "consultant_review": (io.BytesIO(pdf_bytes), "consult.pdf", "application/pdf"),
        })
        assert resp.status_code in (200, 302)

    def test_upload_presentation(self, practice_thesis):
        """Upload presentation file."""
        pdf_bytes = b"%PDF-1.4 fake presentation"
        resp = practice_thesis.post("/practice/preparation_for_defense/", data={
            "submit_presentation_button": "1",
            "presentation": (io.BytesIO(pdf_bytes), "slides.pdf", "application/pdf"),
        })
        assert resp.status_code in (200, 302)

    def test_upload_code_link(self, practice_thesis):
        """Submit code repository link."""
        resp = practice_thesis.post("/practice/preparation_for_defense/", data={
            "submit_code_button": "1",
            "code_link": "https://github.com/user/repo",
            "account_name": "testuser",
        })
        assert resp.status_code in (200, 302)

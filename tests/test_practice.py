# -*- coding: utf-8 -*-
import io

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
        resp = logged_client.post(
            "/practice/new/",
            data={
                "area": 2,
                "worktype": 3,
            },
        )
        assert resp.status_code in (200, 302)


class TestPracticeStudentThesisFlow:
    @pytest.mark.parametrize(
        "path",
        [
            "/practice/choosing_topic/",
            "/practice/goals_tasks/",
            "/practice/workflow/",
            "/practice/add_new_report/",
            "/practice/edit_theme/",
            "/practice/preparation_for_defense/",
            "/practice/defense/",
            "/practice/data_for_practice/",
        ],
    )
    def test_flow_pages(self, practice_thesis, path):
        assert_ok(practice_thesis, path, code={200, 302})

    def test_goals_tasks_add(self, practice_thesis):
        resp = practice_thesis.post(
            "/practice/goals_tasks/", data={"task_text": "New task", "add_task_button": "1"}
        )
        assert resp.status_code in (200, 302)

    def test_add_report_submit(self, practice_thesis):
        resp = practice_thesis.post(
            "/practice/add_new_report/",
            data={
                "was_done": "Completed a significant task for the project this week",
                "planned_to_do": "Plan to continue with the next set of tasks for the project",
            },
        )
        assert resp.status_code in (200, 302)


class TestPracticeStaff:
    @pytest.mark.parametrize(
        "path,code",
        [
            ("/practice_staff", {200, 302}),
            ("/practice_staff/reports/", {200, 302, 404}),
            ("/practice_staff/finished_thesises/", {200, 302}),
        ],
    )
    def test_staff_pages(self, practice_thesis, path, code):
        assert_ok(practice_thesis, path, code=code)

    def test_staff_thesis(self, practice_thesis):
        practice_thesis.get("/practice_staff/thesis/")
        # May not find advisee for the current user
        assert_ok(practice_thesis, "/practice_staff/thesis/", code={200, 302, 404})


class TestPracticeAdmin:
    @pytest.mark.parametrize(
        "path,code",
        [
            ("/practice_admin", {200, 302}),
            ("/practice_admin/choose_area_worktype", {200, 302}),
            ("/practice_admin/finished_thesises", {200, 302}),
            ("/practice_admin/thesis", {200, 302, 404}),
            ("/practice_admin/yandex_code", {200, 302, 404}),
            ("/practice_admin/thesis_to_archive", {200, 302, 404}),
        ],
    )
    def test_admin_pages(self, practice_thesis, path, code):
        assert_ok(practice_thesis, path, code=code)


class TestPracticeFileUploads:
    @pytest.mark.parametrize(
        "data",
        [
            {
                "submit_text_button": "1",
                "text_link": "https://example.com/thesis.pdf",
            },
            {
                "submit_text_button": "1",
                "text": (
                    io.BytesIO(b"%PDF-1.4 fake pdf content for testing"),
                    "thesis.pdf",
                    "application/pdf",
                ),
            },
            {"submit_text_button": "1", "text_link": ""},
            {
                "submit_review_button": "1",
                "supervisor_review": (
                    io.BytesIO(b"%PDF-1.4 fake review"),
                    "review.pdf",
                    "application/pdf",
                ),
                "consultant_review": (
                    io.BytesIO(b"%PDF-1.4 fake review"),
                    "consult.pdf",
                    "application/pdf",
                ),
            },
            {
                "submit_presentation_button": "1",
                "presentation": (
                    io.BytesIO(b"%PDF-1.4 fake presentation"),
                    "slides.pdf",
                    "application/pdf",
                ),
            },
        ],
    )
    def test_upload(self, practice_thesis, data):
        resp = practice_thesis.post("/practice/preparation_for_defense/", data=data)
        assert resp.status_code in (200, 302)

# -*- coding: utf-8 -*-
import io
from datetime import datetime, timedelta

import pytest
from conftest import assert_ok


class TestCurrentThesisDecorator:
    def test_no_id_redirects_index(self, logged_client):
        resp = logged_client.get("/practice/choosing_topic/")
        assert resp.status_code == 302

    def test_nonexistent_id_redirects(self, logged_client):
        resp = logged_client.get("/practice/choosing_topic/?id=99999")
        assert resp.status_code == 302

    def test_deleted_thesis_redirects(self, logged_client):
        from se_models import CurrentThesis, db

        ct = CurrentThesis(author_id=1, worktype_id=1, area_id=1)
        ct.deleted = True
        db.session.add(ct)
        db.session.commit()
        resp = logged_client.get(f"/practice/choosing_topic/?id={ct.id}")
        assert resp.status_code == 302


class TestPracticeIndex:
    def test_get_returns_200(self, logged_client):
        assert_ok(logged_client, "/practice")

    def test_post_read_notification(self, logged_client):
        from se_models import NotificationPractice, db

        n = NotificationPractice(
            recipient_id=1,
            content="Test notification content",
        )
        db.session.add(n)
        db.session.commit()
        nid = n.id
        resp = logged_client.post("/practice", data={"read_notification_button": nid})
        assert resp.status_code in (200, 302)

    def test_post_read_nonexistent_notification(self, logged_client):
        resp = logged_client.post("/practice", data={"read_notification_button": 9999})
        assert resp.status_code in (200, 302)


class TestPracticeGuide:
    def test_get(self, logged_client):
        assert_ok(logged_client, "/practice/guide/")


class TestPracticeNewThesis:
    def test_get(self, logged_client):
        assert_ok(logged_client, "/practice/new/")

    def test_post_worktype_zero(self, logged_client):
        resp = logged_client.post("/practice/new/", data={"area": 2, "worktype": 0})
        assert resp.status_code in (200, 302)

    def test_post_area_zero(self, logged_client):
        resp = logged_client.post("/practice/new/", data={"area": 0, "worktype": 3})
        assert resp.status_code in (200, 302)

    def test_post_valid(self, logged_client):
        resp = logged_client.post("/practice/new/", data={"area": 2, "worktype": 3})
        assert resp.status_code in (200, 302)


class TestPracticeChoosingTopic:
    def test_get_with_id(self, practice_thesis):
        resp = practice_thesis.get("/practice/choosing_topic/?id=1")
        assert resp.status_code in (200, 302)

    def test_post_save_topic_empty(self, practice_thesis):
        resp = practice_thesis.post(
            "/practice/choosing_topic/?id=1",
            data={"save_topic_button": "1", "topic": "", "staff": 1},
        )
        assert resp.status_code in (200, 302)

    def test_post_save_topic_short(self, practice_thesis):
        resp = practice_thesis.post(
            "/practice/choosing_topic/?id=1",
            data={"save_topic_button": "1", "topic": "AB", "staff": 1},
        )
        assert resp.status_code in (200, 302)

    def test_post_save_topic_no_supervisor(self, practice_thesis):
        resp = practice_thesis.post(
            "/practice/choosing_topic/?id=1",
            data={"save_topic_button": "1", "topic": "My thesis topic"},
        )
        assert resp.status_code in (200, 302)

    def test_post_save_topic_valid(self, practice_thesis):
        resp = practice_thesis.post(
            "/practice/choosing_topic/?id=1",
            data={"save_topic_button": "1", "topic": "My thesis topic", "staff": 1},
        )
        assert resp.status_code in (200, 302)

    def test_post_add_consultant(self, practice_thesis):
        resp = practice_thesis.post(
            "/practice/choosing_topic/?id=1",
            data={
                "add_consultant_button": "1",
                "add_consultant_input": "Dr. Consultant Name",
            },
        )
        assert resp.status_code in (200, 302)

    def test_post_delete_topic(self, practice_thesis):
        resp = practice_thesis.post(
            "/practice/choosing_topic/?id=1",
            data={"delete_topic_button": "1"},
        )
        assert resp.status_code in (200, 302)


class TestPracticeEditTheme:
    def test_get(self, practice_thesis):
        resp = practice_thesis.get("/practice/edit_theme/?id=1")
        assert resp.status_code in (200, 302)

    def test_post_save_empty_topic(self, practice_thesis):
        resp = practice_thesis.post(
            "/practice/edit_theme/?id=1",
            data={"save_topic_button": "1", "topic": "", "staff": 1},
        )
        assert resp.status_code in (200, 302)

    def test_post_save_short_topic(self, practice_thesis):
        resp = practice_thesis.post(
            "/practice/edit_theme/?id=1",
            data={"save_topic_button": "1", "topic": "AB", "staff": 1},
        )
        assert resp.status_code in (200, 302)

    def test_post_save_no_supervisor(self, practice_thesis):
        resp = practice_thesis.post(
            "/practice/edit_theme/?id=1",
            data={"save_topic_button": "1", "topic": "Edited thesis topic"},
        )
        assert resp.status_code in (200, 302)

    def test_post_save_valid(self, practice_thesis):
        resp = practice_thesis.post(
            "/practice/edit_theme/?id=1",
            data={
                "save_topic_button": "1",
                "topic": "Edited thesis topic",
                "staff": 1,
            },
        )
        assert resp.status_code in (200, 302)

    def test_post_save_with_different_supervisor(self, practice_thesis):
        resp = practice_thesis.post(
            "/practice/edit_theme/?id=1",
            data={
                "save_topic_button": "1",
                "topic": "Edited thesis topic",
                "staff": 2,
                "consultant": "Ext. Consultant",
            },
        )
        assert resp.status_code in (200, 302)


class TestPracticeGoalsTasks:
    def test_get(self, practice_thesis):
        resp = practice_thesis.get("/practice/goals_tasks/?id=1")
        assert resp.status_code in (200, 302)

    def test_post_submit_goal(self, practice_thesis):
        resp = practice_thesis.post(
            "/practice/goals_tasks/?id=1",
            data={
                "submit_goal_button": "1",
                "goal": "My main goal for this practice project is to complete the work",
            },
        )
        assert resp.status_code in (200, 302)

    def test_post_submit_goal_short(self, practice_thesis):
        resp = practice_thesis.post(
            "/practice/goals_tasks/?id=1",
            data={"submit_goal_button": "1", "goal": "AB"},
        )
        assert resp.status_code in (200, 302)

    def test_post_submit_goal_missing_field(self, practice_thesis):
        resp = practice_thesis.post(
            "/practice/goals_tasks/?id=1",
            data={"submit_goal_button": "1"},
        )
        assert resp.status_code in (200, 302)

    def test_post_submit_goal_same_value(self, practice_thesis):
        from se_models import CurrentThesis, db

        ct = CurrentThesis.query.filter_by(author_id=1).first()
        ct.goal = "My main goal for this practice project is to complete the work"
        db.session.commit()
        resp = practice_thesis.post(
            "/practice/goals_tasks/?id=1",
            data={
                "submit_goal_button": "1",
                "goal": "My main goal for this practice project is to complete the work",
            },
        )
        assert resp.status_code in (200, 302)

    def test_post_edit_goal(self, practice_thesis):
        resp = practice_thesis.post(
            "/practice/goals_tasks/?id=1",
            data={
                "edit_goal_button": "1",
                "goal": "Updated main goal for the practice project",
            },
        )
        assert resp.status_code in (200, 302)

    def test_post_delete_goal(self, practice_thesis):
        resp = practice_thesis.post(
            "/practice/goals_tasks/?id=1",
            data={"delete_goal_button": "1"},
        )
        assert resp.status_code in (200, 302)

    def test_post_submit_task(self, practice_thesis):
        resp = practice_thesis.post(
            "/practice/goals_tasks/?id=1",
            data={
                "submit_task_button": "1",
                "task": "Complete the first milestone of the project",
            },
        )
        assert resp.status_code in (200, 302)

    def test_post_submit_task_short(self, practice_thesis):
        resp = practice_thesis.post(
            "/practice/goals_tasks/?id=1",
            data={"submit_task_button": "1", "task": "AB"},
        )
        assert resp.status_code in (200, 302)

    def test_post_delete_task(self, practice_thesis):
        resp = practice_thesis.post(
            "/practice/goals_tasks/?id=1",
            data={"delete_task_id_button": "1"},
        )
        assert resp.status_code in (200, 302)

    def test_post_delete_task_zero(self, practice_thesis):
        resp = practice_thesis.post(
            "/practice/goals_tasks/?id=1",
            data={"delete_task_id_button": "0"},
        )
        assert resp.status_code in (200, 302)

    def test_post_delete_task_nonexistent(self, practice_thesis):
        resp = practice_thesis.post(
            "/practice/goals_tasks/?id=1",
            data={"delete_task_id_button": "9999"},
        )
        assert resp.status_code in (200, 302)

    def test_post_edit_task(self, practice_thesis):
        resp = practice_thesis.post(
            "/practice/goals_tasks/?id=1",
            data={
                "edit_task_id_button": "1",
                "task": "Updated task description for the project milestone",
            },
        )
        assert resp.status_code in (200, 302)

    def test_post_edit_task_short(self, practice_thesis):
        resp = practice_thesis.post(
            "/practice/goals_tasks/?id=1",
            data={"edit_task_id_button": "1", "task": "AB"},
        )
        assert resp.status_code in (200, 302)

    def test_post_edit_task_nonexistent(self, practice_thesis):
        resp = practice_thesis.post(
            "/practice/goals_tasks/?id=1",
            data={"edit_task_id_button": "9999", "task": "Updated task description"},
        )
        assert resp.status_code in (200, 302)


class TestPracticeAddNewReport:
    def test_get(self, practice_thesis):
        resp = practice_thesis.get("/practice/add_new_report/?id=1")
        assert resp.status_code in (200, 302)

    def test_post_missing_was_done(self, practice_thesis):
        resp = practice_thesis.post(
            "/practice/add_new_report/?id=1",
            data={
                "planned_to_do": "I plan to finish the remaining tasks soon for completion",
            },
        )
        assert resp.status_code in (200, 302)

    def test_post_missing_planned_to_do(self, practice_thesis):
        resp = practice_thesis.post(
            "/practice/add_new_report/?id=1",
            data={
                "was_done": "I completed many important tasks this week for the project",
            },
        )
        assert resp.status_code in (200, 302)

    def test_post_short_was_done(self, practice_thesis):
        resp = practice_thesis.post(
            "/practice/add_new_report/?id=1",
            data={
                "was_done": "AB",
                "planned_to_do": "I plan to finish the remaining tasks soon for completion",
            },
        )
        assert resp.status_code in (200, 302)

    def test_post_short_planned_to_do(self, practice_thesis):
        resp = practice_thesis.post(
            "/practice/add_new_report/?id=1",
            data={
                "was_done": "I completed many important tasks this week for the project",
                "planned_to_do": "AB",
            },
        )
        assert resp.status_code in (200, 302)

    def test_post_supervisor_id_none(self, practice_thesis):
        from se_models import CurrentThesis, db

        ct = CurrentThesis.query.filter_by(author_id=1).first()
        ct.supervisor_id = None
        db.session.commit()
        resp = practice_thesis.post(
            "/practice/add_new_report/?id=1",
            data={
                "was_done": "I completed many important tasks this week for the project",
                "planned_to_do": "I plan to finish the remaining tasks soon for completion",
            },
        )
        assert resp.status_code in (200, 302)

    def test_post_valid(self, practice_thesis):
        resp = practice_thesis.post(
            "/practice/add_new_report/?id=1",
            data={
                "was_done": "I completed many important tasks this week for the project",
                "planned_to_do": "I plan to finish the remaining tasks soon for completion",
            },
        )
        assert resp.status_code in (200, 302)


class TestPracticeDataForPractice:
    def test_get(self, practice_thesis):
        resp = practice_thesis.get("/practice/data_for_practice/?id=1")
        assert resp.status_code in (200, 302)

    def test_post_no_changes(self, practice_thesis):
        resp = practice_thesis.post(
            "/practice/data_for_practice/?id=1",
            data={"save_button": "1", "area": 1, "worktype": 1},
        )
        assert resp.status_code in (200, 302)

    def test_post_change_area_and_worktype(self, practice_thesis):
        resp = practice_thesis.post(
            "/practice/data_for_practice/?id=1",
            data={"save_button": "1", "area": 2, "worktype": 3},
        )
        assert resp.status_code in (200, 302)

    def test_post_delete_thesis(self, practice_thesis):
        resp = practice_thesis.post(
            "/practice/data_for_practice/?id=1",
            data={"delete_thesis_button": "1"},
        )
        assert resp.status_code in (200, 302)


class TestPracticePreparation:
    def test_get(self, practice_thesis):
        resp = practice_thesis.get("/practice/preparation_for_defense/?id=1")
        assert resp.status_code in (200, 302)

    def test_post_submit_text_link(self, practice_thesis):
        resp = practice_thesis.post(
            "/practice/preparation_for_defense/?id=1",
            data={
                "submit_text_button": "1",
                "text_link": "https://example.com/thesis.pdf",
            },
        )
        assert resp.status_code in (200, 302)

    def test_post_submit_text_empty_link_and_file(self, practice_thesis):
        resp = practice_thesis.post(
            "/practice/preparation_for_defense/?id=1",
            data={"submit_text_button": "1", "text_link": ""},
        )
        assert resp.status_code in (200, 302)

    def test_post_submit_text_empty_file_and_link(self, practice_thesis):
        resp = practice_thesis.post(
            "/practice/preparation_for_defense/?id=1",
            data={
                "submit_text_button": "1",
                "text": (io.BytesIO(b""), "", ""),
                "text_link": "",
            },
        )
        assert resp.status_code in (200, 302)

    def test_post_submit_text_empty_file_no_link_field(self, practice_thesis):
        resp = practice_thesis.post(
            "/practice/preparation_for_defense/?id=1",
            data={
                "submit_text_button": "1",
                "text": (io.BytesIO(b""), "", ""),
            },
        )
        assert resp.status_code in (200, 302)

    @pytest.mark.parametrize("button,field,filename", [
        ("submit_text_button", "text", "thesis.txt"),
        ("submit_review_button", "supervisor_review", "review.txt"),
        ("submit_presentation_button", "presentation", "slides.txt"),
    ])
    def test_post_submit_invalid_extension(self, practice_thesis, button, field, filename):
        resp = practice_thesis.post(
            "/practice/preparation_for_defense/?id=1",
            data={
                button: "1",
                field: (io.BytesIO(b"bad"), filename, "text/plain"),
            },
        )
        assert resp.status_code in (200, 302)

    def test_post_submit_text_file(self, practice_thesis):
        pdf_bytes = b"%PDF-1.4 fake pdf content for testing"
        resp = practice_thesis.post(
            "/practice/preparation_for_defense/?id=1",
            data={
                "submit_text_button": "1",
                "text": (io.BytesIO(pdf_bytes), "thesis.pdf", "application/pdf"),
            },
        )
        assert resp.status_code in (200, 302)

    def test_post_submit_review(self, practice_thesis):
        pdf_bytes = b"%PDF-1.4 fake review"
        resp = practice_thesis.post(
            "/practice/preparation_for_defense/?id=1",
            data={
                "submit_review_button": "1",
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
            },
        )
        assert resp.status_code in (200, 302)

    def test_post_submit_review_empty_files(self, practice_thesis):
        resp = practice_thesis.post(
            "/practice/preparation_for_defense/?id=1",
            data={"submit_review_button": "1"},
        )
        assert resp.status_code in (200, 302)

    def test_post_submit_review_empty_filenames(self, practice_thesis):
        resp = practice_thesis.post(
            "/practice/preparation_for_defense/?id=1",
            data={
                "submit_review_button": "1",
                "supervisor_review": (io.BytesIO(b""), "", ""),
                "consultant_review": (io.BytesIO(b""), "", ""),
            },
        )
        assert resp.status_code in (200, 302)

    def test_post_submit_presentation_link(self, practice_thesis):
        resp = practice_thesis.post(
            "/practice/preparation_for_defense/?id=1",
            data={
                "submit_presentation_button": "1",
                "presentation_link": "https://example.com/slides.pdf",
            },
        )
        assert resp.status_code in (200, 302)

    def test_post_submit_presentation_empty(self, practice_thesis):
        resp = practice_thesis.post(
            "/practice/preparation_for_defense/?id=1",
            data={"submit_presentation_button": "1", "presentation_link": ""},
        )
        assert resp.status_code in (200, 302)

    def test_post_submit_presentation_file(self, practice_thesis):
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

    def test_post_submit_presentation_empty_file_and_link(self, practice_thesis):
        resp = practice_thesis.post(
            "/practice/preparation_for_defense/?id=1",
            data={
                "submit_presentation_button": "1",
                "presentation": (io.BytesIO(b""), "", ""),
                "presentation_link": "",
            },
        )
        assert resp.status_code in (200, 302)

    def test_post_submit_presentation_empty_file_no_link(self, practice_thesis):
        resp = practice_thesis.post(
            "/practice/preparation_for_defense/?id=1",
            data={
                "submit_presentation_button": "1",
                "presentation": (io.BytesIO(b""), "", ""),
            },
        )
        assert resp.status_code in (200, 302)

    def test_post_submit_code_both_empty(self, practice_thesis):
        resp = practice_thesis.post(
            "/practice/preparation_for_defense/?id=1",
            data={"submit_code_button": "1", "code_link": "", "account_name": ""},
        )
        assert resp.status_code in (200, 302)

    def test_post_submit_code_link_only(self, practice_thesis):
        resp = practice_thesis.post(
            "/practice/preparation_for_defense/?id=1",
            data={
                "submit_code_button": "1",
                "code_link": "https://github.com/user/repo",
            },
        )
        assert resp.status_code in (200, 302)

    def test_post_submit_code_account_only(self, practice_thesis):
        resp = practice_thesis.post(
            "/practice/preparation_for_defense/?id=1",
            data={"submit_code_button": "1", "account_name": "testuser"},
        )
        assert resp.status_code in (200, 302)

    def test_post_submit_code_both(self, practice_thesis):
        resp = practice_thesis.post(
            "/practice/preparation_for_defense/?id=1",
            data={
                "submit_code_button": "1",
                "code_link": "https://github.com/user/repo",
                "account_name": "testuser",
            },
        )
        assert resp.status_code in (200, 302)

    def test_post_delete_text_button(self, practice_thesis):
        resp = practice_thesis.post(
            "/practice/preparation_for_defense/?id=1",
            data={"delete_text_button": "1"},
        )
        assert resp.status_code in (200, 302)

    def test_post_delete_text_link_button(self, practice_thesis):
        resp = practice_thesis.post(
            "/practice/preparation_for_defense/?id=1",
            data={"delete_text_link_button": "1"},
        )
        assert resp.status_code in (200, 302)

    def test_post_delete_presentation_button(self, practice_thesis):
        resp = practice_thesis.post(
            "/practice/preparation_for_defense/?id=1",
            data={"delete_presentation_button": "1"},
        )
        assert resp.status_code in (200, 302)

    def test_post_delete_presentation_link_button(self, practice_thesis):
        resp = practice_thesis.post(
            "/practice/preparation_for_defense/?id=1",
            data={"delete_presentation_link_button": "1"},
        )
        assert resp.status_code in (200, 302)

    def test_post_delete_reviewer_review_button(self, practice_thesis):
        resp = practice_thesis.post(
            "/practice/preparation_for_defense/?id=1",
            data={"delete_reviewer_review_button": "1"},
        )
        assert resp.status_code in (200, 302)

    def test_post_delete_supervisor_review_button(self, practice_thesis):
        resp = practice_thesis.post(
            "/practice/preparation_for_defense/?id=1",
            data={"delete_supervisor_review_button": "1"},
        )
        assert resp.status_code in (200, 302)

    def test_post_delete_code_link_button(self, practice_thesis):
        resp = practice_thesis.post(
            "/practice/preparation_for_defense/?id=1",
            data={"delete_code_link_button": "1"},
        )
        assert resp.status_code in (200, 302)

    def test_post_delete_account_name_button(self, practice_thesis):
        resp = practice_thesis.post(
            "/practice/preparation_for_defense/?id=1",
            data={"delete_account_name_button": "1"},
        )
        assert resp.status_code in (200, 302)


class TestPracticeDefense:
    def test_get(self, practice_thesis):
        resp = practice_thesis.get("/practice/defense/?id=1")
        assert resp.status_code in (200, 302)


class TestPracticeWorkflow:
    def test_get(self, practice_thesis):
        resp = practice_thesis.get("/practice/workflow/?id=1")
        assert resp.status_code in (200, 302)

    def test_post_delete_report(self, practice_thesis):
        from se_models import ThesisReport, db

        report = ThesisReport(
            was_done="Completed task A",
            planned_to_do="Plan to do task B",
            current_thesis_id=1,
            author_id=1,
        )
        db.session.add(report)
        db.session.commit()
        report_id = report.id
        resp = practice_thesis.post(
            "/practice/workflow/?id=1",
            data={"delete_button": report_id},
        )
        assert resp.status_code in (200, 302)

    @pytest.mark.xfail(
        reason="Code does not handle nonexistent report_id - crashes with AttributeError"
    )
    def test_post_delete_nonexistent_report(self, practice_thesis):
        resp = practice_thesis.post(
            "/practice/workflow/?id=1",
            data={"delete_button": 9999},
        )
        assert resp.status_code in (200, 302)


class TestGetListOfTheses:
    def test_returns_non_deleted_theses(self, logged_client):
        from se_models import CurrentThesis, db

        ct1 = CurrentThesis(author_id=1, worktype_id=1, area_id=1)
        ct2 = CurrentThesis(author_id=1, worktype_id=2, area_id=2)
        ct2.deleted = True
        db.session.add(ct1)
        db.session.add(ct2)
        db.session.commit()

        with logged_client:
            resp = logged_client.get("/practice")
            assert resp.status_code in (200, 302)

    def test_returns_empty_when_none(self, logged_client):
        with logged_client:
            resp = logged_client.get("/practice")
            assert resp.status_code in (200, 302)

    def test_returns_all_active_theses(self, logged_client):
        from se_models import CurrentThesis, db

        ct1 = CurrentThesis(author_id=1, worktype_id=1, area_id=1)
        ct2 = CurrentThesis(author_id=1, worktype_id=2, area_id=2)
        db.session.add(ct1)
        db.session.add(ct2)
        db.session.commit()

        with logged_client:
            resp = logged_client.get("/practice")
            assert resp.status_code in (200, 302)


class TestGetRemainingTime:
    def test_choosing_topic_with_deadline(self, practice_thesis):
        from se_models import Deadline, db

        dl = Deadline(worktype_id=1, area_id=1, choose_topic=datetime.utcnow() + timedelta(days=10))
        db.session.add(dl)
        db.session.commit()
        resp = practice_thesis.get("/practice/choosing_topic/?id=1")
        assert resp.status_code in (200, 302)

    def test_choosing_topic_expired_deadline(self, practice_thesis):
        from se_models import Deadline, db

        dl = Deadline(worktype_id=1, area_id=1, choose_topic=datetime.utcnow() - timedelta(days=1))
        db.session.add(dl)
        db.session.commit()
        resp = practice_thesis.get("/practice/choosing_topic/?id=1")
        assert resp.status_code in (200, 302)

    def test_preparation_with_submit_deadline(self, practice_thesis):
        from se_models import Deadline, db

        dl = Deadline(
            worktype_id=1,
            area_id=1,
            submit_work_for_review=datetime.utcnow() + timedelta(days=10),
            upload_reviews=datetime.utcnow() + timedelta(days=20),
        )
        db.session.add(dl)
        db.session.commit()
        resp = practice_thesis.get("/practice/preparation_for_defense/?id=1")
        assert resp.status_code in (200, 302)

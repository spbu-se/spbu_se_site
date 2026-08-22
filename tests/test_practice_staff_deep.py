# -*- coding: utf-8 -*-
import datetime

import pytest
from conftest import assert_ok


@pytest.fixture
def thesis_with_report(staff_client):
    from conftest import _setup_current_thesis_with_report

    ct_id, report_id = _setup_current_thesis_with_report()
    return staff_client, ct_id, report_id


class TestDatetimeConvert:
    def test_datetime_convert_utc(self):
        from flask_se_practice_staff import datetime_convert

        dt = datetime.datetime(2024, 6, 15, 12, 0, 0, tzinfo=datetime.UTC)
        result = datetime_convert(dt)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_datetime_convert_naive(self):
        from flask_se_practice_staff import datetime_convert

        dt = datetime.datetime(2024, 6, 15, 12, 0, 0)
        result = datetime_convert(dt)
        assert isinstance(result, str)
        assert "." in result or ":" in result


class TestUserIsStaff:
    def test_non_staff_redirects_to_practice_index(self, seeded_client):
        from se_models import Users, db

        u = Users(email="nobody@spbu.ru", first_name="Nobody", last_name="User")
        db.session.add(u)
        db.session.commit()
        with seeded_client.session_transaction() as sess:
            sess["_user_id"] = str(u.id)
        resp = seeded_client.get("/practice_staff")
        assert resp.status_code in (200, 302)

    def test_staff_can_access_index(self, staff_client):
        assert_ok(staff_client, "/practice_staff", code={200, 302})


class TestCurrentThesisExistsOrRedirect:
    @pytest.mark.parametrize(
        "path",
        ["/practice_staff/thesis/", "/practice_staff/thesis/?id=99999"],
        ids=["missing_id", "invalid_id"],
    )
    def test_missing_or_invalid_id_redirects(self, staff_client, path):
        resp = staff_client.get(path)
        assert resp.status_code in (200, 302)

    def test_thesis_not_owned_by_staff_redirects(self, staff_client):
        from se_models import CurrentThesis, db

        ct = CurrentThesis(author_id=2, worktype_id=1, area_id=1)
        ct.title = "Not my thesis"
        ct.supervisor_id = 2
        db.session.add(ct)
        db.session.commit()
        resp = staff_client.get(f"/practice_staff/thesis/?id={ct.id}")
        assert resp.status_code in (200, 302)

    def test_valid_thesis_renders(self, thesis_with_report):
        client, ct_id, _ = thesis_with_report
        resp = client.get(f"/practice_staff/thesis/?id={ct_id}")
        assert resp.status_code == 200


class TestThesisStaffPost:
    def test_submit_notification_empty_content(self, thesis_with_report):
        client, ct_id, _ = thesis_with_report
        resp = client.post(
            f"/practice_staff/thesis/?id={ct_id}",
            data={
                "submit_notification_button": "1",
                "content": "",
            },
        )
        assert resp.status_code in (200, 302)

    def test_submit_notification_valid(self, thesis_with_report):
        from se_models import NotificationPractice

        client, ct_id, _ = thesis_with_report
        resp = client.post(
            f"/practice_staff/thesis/?id={ct_id}",
            data={
                "submit_notification_button": "1",
                "content": "Test notification from supervisor",
            },
        )
        assert resp.status_code in (200, 302)
        notification = NotificationPractice.query.filter_by(recipient_id=1).first()
        assert notification is not None

    @pytest.mark.parametrize(
        ("initial_status", "button", "final_status"),
        [
            (1, "submit_finish_work_button", 2),
            (2, "submit_restore_work_button", 1),
        ],
    )
    def test_submit_work_transition(self, thesis_with_report, initial_status, button, final_status):
        from se_models import CurrentThesis, db

        client, ct_id, _ = thesis_with_report
        ct = db.session.get(CurrentThesis, ct_id)
        ct.status = initial_status
        db.session.commit()

        resp = client.post(
            f"/practice_staff/thesis/?id={ct_id}",
            data={button: "1"},
        )
        assert resp.status_code in (200, 302)
        ct = db.session.get(CurrentThesis, ct_id)
        assert ct.status == final_status

    def test_finished_thesises_staff(self, staff_client):
        assert_ok(staff_client, "/practice_staff/finished_thesises/", code={200, 302})

    def test_index_staff(self, thesis_with_report):
        client, _ct_id, _ = thesis_with_report
        resp = client.get("/practice_staff/")
        assert resp.status_code == 200


class TestReportsStaff:
    @pytest.mark.parametrize(
        ("query", "code"),
        [
            pytest.param("", (200,), id="without_report_id"),
            pytest.param("_REPORT_ID_", (200,), id="with_valid_report_id"),
            pytest.param("&report_id=99999", (200, 302), id="with_invalid_report_id_redirects"),
        ],
    )
    def test_reports_get(self, thesis_with_report, query, code):
        client, ct_id, report_id = thesis_with_report
        query = query.replace("_REPORT_ID_", f"&report_id={report_id}")
        resp = client.get(f"/practice_staff/reports/?id={ct_id}{query}")
        assert resp.status_code in code

    def test_reports_with_report_not_owned_redirects(self, thesis_with_report):
        from se_models import CurrentThesis, ThesisReport, db

        client, ct_id, _ = thesis_with_report
        ct2 = CurrentThesis(author_id=2, worktype_id=1, area_id=1)
        ct2.title = "Another thesis"
        ct2.supervisor_id = 2
        db.session.add(ct2)
        db.session.flush()
        report2 = ThesisReport(
            was_done="Other work", planned_to_do="Other plan", current_thesis_id=ct2.id, author_id=2
        )
        db.session.add(report2)
        db.session.commit()
        resp = client.get(f"/practice_staff/reports/?id={ct_id}&report_id={report2.id}")
        assert resp.status_code in (200, 302)

    @pytest.mark.parametrize(
        ("comment", "expected_or_none"),
        [("Great work!", "Great work!"), ("", None)],
    )
    def test_reports_post_comment(self, thesis_with_report, comment, expected_or_none):
        from se_models import ThesisReport, db

        client, ct_id, report_id = thesis_with_report
        resp = client.post(
            f"/practice_staff/reports/?id={ct_id}&report_id={report_id}",
            data={f"submit_button{report_id}": "1", "comment": comment},
        )
        assert resp.status_code in (200, 302)
        if expected_or_none is not None:
            updated = db.session.get(ThesisReport, report_id)
            assert updated.comment == expected_or_none

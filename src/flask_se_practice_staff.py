# -*- coding: utf-8 -*-
import datetime

import pytz
from dateutil import tz
from flask import flash, redirect, request, render_template, url_for
from sqlalchemy import desc
from functools import wraps

from flask_se_auth import login_required
from flask_login import current_user

from se_forms import StaffAddCommentToReport
from se_models import (
    db,
    Staff,
    CurrentThesis,
    ThesisReport,
    NotificationPractice,
    add_mail_notification,
)

from templates.practice.staff.templates import PracticeStaffTemplates
from templates.notification.templates import NotificationTemplates

DATE_AND_TIME_FORMAT = "%d.%m.%Y %H:%M"


def datetime_convert(value):
    return (
        value.replace(tzinfo=pytz.UTC)
        .astimezone(tz.tzlocal())
        .strftime(DATE_AND_TIME_FORMAT)
    )


def user_is_staff(func):
    @wraps(func)
    def check_user_is_staff_decorator():
        user_staff = Staff.query.filter_by(user_id=current_user.id).first()
        if not user_staff:
            return redirect(url_for("practice_index"))
        return func(user_staff)

    return check_user_is_staff_decorator


def current_thesis_exists_or_redirect(func):
    @wraps(func)
    def get_current_thesis_decorator(user_staff):
        current_thesis_id = request.args.get("id", type=int)
        if not current_thesis_id:
            return redirect(url_for("index_staff"))
        current_thesis = (
            CurrentThesis.query.filter_by(supervisor_id=user_staff.id)
            .filter_by(id=current_thesis_id)
            .first()
        )
        if not current_thesis:
            return redirect(url_for("index_staff"))
        return func(user_staff, current_thesis)

    return get_current_thesis_decorator


@login_required
@user_is_staff
def index_staff(user_staff):
    current_thesises = (
        CurrentThesis.query.filter_by(supervisor_id=user_staff.id)
        .filter_by(status=1)
        .filter_by(deleted=False)
        .outerjoin(ThesisReport, CurrentThesis.reports)
        .order_by(desc(ThesisReport.time))
        .all()
    )
    return render_template(
        PracticeStaffTemplates.CURRENT_THESISES.value, thesises=current_thesises
    )


@login_required
@user_is_staff
def finished_thesises_staff(user_staff):
    current_thesises = (
        CurrentThesis.query.filter_by(supervisor_id=user_staff.id)
        .filter_by(status=2)
        .filter_by(deleted=False)
        .all()
    )
    return render_template(
        PracticeStaffTemplates.FINISHED_THESISES.value, thesises=current_thesises
    )


@login_required
@user_is_staff
@current_thesis_exists_or_redirect
def thesis_staff(user_staff, current_thesis):
    if request.method == "POST":
        if "submit_notification_button" in request.form:
            if request.form["content"] in {None, ""}:
                flash("Нельзя отправить пустое уведомление!", category="error")
                return redirect(url_for("thesis_staff", id=current_thesis.id))

            mail_notification = render_template(
                NotificationTemplates.NOTIFICATION_FROM_SUPERVISOR.value,
                supervisor=user_staff,
                thesis=current_thesis,
                content=request.form["content"],
            )
            add_mail_notification(
                current_thesis.author_id,
                "[SE site] Уведомление от научного руководителя",
                mail_notification,
            )
            notification_content = (
                f"Научный руководитель {user_staff.user.get_name()} "
                f'отправил Вам уведомление по работе "{current_thesis.title}": '
                f"{request.form['content']}"
            )
            notification = NotificationPractice(
                recipient_id=current_thesis.author_id, content=notification_content
            )
            db.session.add(notification)
            db.session.commit()
            flash("Уведомление отправлено!", category="success")
        elif "submit_finish_work_button" in request.form:
            current_thesis.status = 2
            db.session.commit()
        elif "submit_restore_work_button" in request.form:
            current_thesis.status = 1
            db.session.commit()

    not_deleted_tasks = [task for task in current_thesis.tasks if not task.deleted]
    return render_template(
        PracticeStaffTemplates.THESIS.value,
        thesis=current_thesis,
        tasks=not_deleted_tasks,
    )


@login_required
@user_is_staff
@current_thesis_exists_or_redirect
def reports_staff(user_staff, current_thesis):
    current_report_id = request.args.get("report_id", type=int)
    reports = (
        ThesisReport.query.filter_by(current_thesis_id=current_thesis.id)
        .filter_by(deleted=False)
        .order_by(desc(ThesisReport.time))
        .all()
    )
    add_report_comment = StaffAddCommentToReport()

    if current_report_id:
        current_report = ThesisReport.query.filter_by(id=current_report_id).first()

        if not current_report or current_report.deleted:
            return redirect(url_for("index_staff"))

        if current_report.practice.supervisor_id != user_staff.id:
            return redirect(url_for("index_staff"))

        if request.method == "POST":
            if "submit_button" + str(current_report_id) in request.form:
                new_comment = request.form.get("comment", type=str)

                if not new_comment:
                    flash("Нельзя отправить пустой комментарий!", category="error")
                else:
                    current_report.comment = new_comment
                    current_report.comment_time = datetime.datetime.now()
                    db.session.commit()

                    content = (
                        f"Научный руководитель {user_staff.user.get_name()} прокомментировал "
                        + f"Ваш отчет от {datetime_convert(current_report.time)} "
                        + f'по работе "{current_thesis.title}"'
                    )

                    notification = NotificationPractice(
                        recipient_id=current_thesis.author_id, content=content
                    )

                    add_mail_notification(
                        current_thesis.author_id,
                        "[SE site] Отчёт прокомментирован",
                        render_template(
                            NotificationTemplates.SUPERVISOR_COMMENT_TO_REPORT.value,
                            user_staff=user_staff,
                            current_report=current_report,
                            current_thesis=current_thesis,
                        ),
                    )

                    db.session.add(notification)
                    db.session.commit()
                    flash("Комментарий успешно отправлен!", category="success")

                return render_template(
                    PracticeStaffTemplates.REPORTS.value,
                    thesis=current_thesis,
                    reports=reports,
                    form=add_report_comment,
                )

    return render_template(
        PracticeStaffTemplates.REPORTS.value,
        thesis=current_thesis,
        reports=reports,
        form=add_report_comment,
    )

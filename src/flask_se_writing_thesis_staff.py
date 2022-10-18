# -*- coding: utf-8 -*-
import datetime

from flask import flash, redirect, request, render_template, url_for
from sqlalchemy import desc, asc

from flask_se_auth import login_required
from flask_login import current_user

from se_forms import StaffAddCommentToReport
from se_models import db, Staff, CurrentThesis, ThesisReport


@login_required
def writing_thesis_index():
    user_staff = Staff.query.filter_by(user_id=current_user.id).first()
    if not user_staff:
        return redirect(url_for('account_index'))

    current_thesises = CurrentThesis.query.filter_by(supervisor_id=user_staff.id).all()
    return render_template('account/current_thesises_staff.html', thesises=current_thesises)

@login_required
def writing_thesis_thesis():
    user_staff = Staff.query.filter_by(user_id=current_user.id).first()
    if not user_staff:
        return redirect(url_for('account_index'))

    current_thesis_id = request.args.get('id', type=int)
    if not current_thesis_id:
        return redirect(url_for('writing_thesis_index'))

    current_thesis = CurrentThesis.query.filter_by(supervisor_id=user_staff.id).filter_by(id=current_thesis_id).first()
    if not current_thesis:
        return redirect(url_for('writing_thesis_index'))

    if current_thesis.supervisor_id != user_staff.id:
        return redirect(url_for('account_index'))

    return render_template('account/thesis_staff.html', thesis=current_thesis)


@login_required
def writing_thesis_reports():
    user_staff = Staff.query.filter_by(user_id=current_user.id).first()
    if not user_staff:
        return redirect(url_for('account_index'))

    current_thesis_id = request.args.get('id', type=int)
    if not current_thesis_id:
        return redirect(url_for('account_index'))

    current_thesis = CurrentThesis.query.filter_by(id=current_thesis_id).first()
    if not current_thesis:
        return redirect(url_for('account_index'))

    if current_thesis.supervisor_id != user_staff.id:
        return redirect(url_for('account_index'))

    current_report_id = request.args.get('report_id', type=int)
    reports = ThesisReport.query.filter_by(current_thesis_id=current_thesis_id).order_by(desc(ThesisReport.time)).all()
    add_report_comment = StaffAddCommentToReport()

    if current_report_id:
        current_report = ThesisReport.query.filter_by(id=current_report_id).first()

        if not current_report:
            return redirect(url_for('account_index'))

        if current_report.practice.supervisor_id != user_staff.id:
            return redirect(url_for('account_index'))

        if request.method == 'POST':
            if 'submit_button'+str(current_report_id) in request.form:
                new_comment = request.form.get('comment', type=str)

                if not new_comment:
                    flash('Нельзя отправить пустой комментарий!', category='error')
                else:
                    current_report.comment = new_comment
                    current_report.comment_time = datetime.datetime.now()
                    db.session.commit()
                    flash('Комментарий успешно отправлен!', category='success')
                return render_template('account/reports_staff.html', thesis=current_thesis, reports=reports,
                                        form=add_report_comment)

    return render_template('account/reports_staff.html', thesis=current_thesis, reports=reports,
                    form=add_report_comment)



# -*- coding: utf-8 -*-

from flask import flash, redirect, request, render_template, url_for
from sqlalchemy import desc, asc

from flask_se_auth import login_required
from flask_login import current_user
from se_models import db, Users, Staff, CurrentThesis, ThesisReport


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

    reports = ThesisReport.query.filter_by(current_thesis_id=current_thesis_id).order_by(desc(ThesisReport.time)).all()

    return render_template('account/thesis_staff.html', thesis=current_thesis, reports=reports)

# -*- coding: utf-8 -*-


from flask import flash, redirect, request, render_template, url_for
from flask_login import current_user

from flask_se_auth import login_required
from se_forms import CurrentCourseArea, ChooseTopic
from se_models import AreasOfStudy, Users, CurrentThesis, Staff, Worktype


@login_required
def account_profile():
    user = current_user
    form = CurrentCourseArea()
    course = form.course

    if request.method == "POST":
        currentarea = request.form.get('area', type=str)
        course = request.form.get('course', type=int)
        new_thesis = CurrentThesis()
        new_thesis.area = currentarea
        new_thesis.course = course
        new_thesis.title = "None"
        new_thesis.user_id = user.id

        db.session.add(new_thesis)
        db.session.commit()

    for area in AreasOfStudy.query.filter(AreasOfStudy.id > 1).distinct().all():
        form.area.choices.append(area.area)

    form.area.choices.sort(key=lambda tup: tup[0])

    for course in range(2, 7):
        form.course.choices.append(course)

    return render_template('account/profile.html', review_filter=form, user=user, form=form)


@login_required
def account_index():
    return render_template('account/index.html')


@login_required
def account_guide():
    return render_template('account/guide.html')


@login_required
def account_choosing_topic():
    form = ChooseTopic()

    for supervisor in Staff.query.distinct().all():
        form.staff.choices.append(supervisor.user.get_name())

    for worktype in Worktype.query.distinct().all():
        form.worktype.choices.append(worktype)

    return render_template('account/choosing_topic.html', form=form)


@login_required
def account_workflow():
    return render_template('account/account_workflow.html')


@login_required
def account_preparation():
    return render_template('account/account_preparation.html')


@login_required
def account_thesis_defense():
    return render_template('account/defense.html')


@login_required
def account_materials():
    return render_template('account/account_materials.html')
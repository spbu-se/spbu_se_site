# -*- coding: utf-8 -*-


from flask import flash, redirect, request, render_template, url_for
from flask_login import current_user

from flask_se_auth import login_required
from se_forms import CurrentCourseArea
from se_models import AreasOfStudy, Users, CurrentThesis


@login_required
def account_profile():
    user = current_user
    return render_template('account/profile.html', user=user)


@login_required
def submit_course_area():
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
def choosing_topic():
    return render_template('account/base_account.html', content_page="Hello")

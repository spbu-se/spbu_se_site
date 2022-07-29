# -*- coding: utf-8 -*-


from flask import flash, redirect, request, render_template, url_for
from flask_login import current_user

from flask_se_auth import login_required
from se_forms import CurrentCourseArea
from se_models import AreasOfStudy, Users
from se_internship_forms import AddInternship, InternshipsFilter
from se_models import db, Internships, InternshipFormat, InternshipCompany


@login_required
def account_profile():
    user = current_user
    return render_template('account/profile.html', user=user)


@login_required
def submit_course_area():
    user = current_user
    form = CurrentCourseArea()

    for area in AreasOfStudy.query.filter(AreasOfStudy.id > 1).distinct().all():
        form.area.choices.append((area.id, area.area))

    form.area.choices.sort(key=lambda tup: tup[0])

    form.fname = Users.query.filter(Users.id == user.id).distinct().first().first_name

    form.mname = Users.query.filter(Users.id == user.id).distinct().first().middle_name

    form.lname = Users.query.filter(Users.id == user.id).distinct().first().last_name

    return render_template('account/profile.html', review_filter=form, user=user, form=form)

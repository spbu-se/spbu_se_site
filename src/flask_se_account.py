# -*- coding: utf-8 -*-


from flask import flash, redirect, request, render_template, url_for
from flask_login import current_user

from flask_se_auth import login_required
from se_forms import CurrentCourseArea
from se_models import AreasOfStudy


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

    return render_template('account/profile.html', review_filter=form, user=user)


@login_required
def choosing_topic():
    return render_template('account/base_account.html', content_page="Hello")

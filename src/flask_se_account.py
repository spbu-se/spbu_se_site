# -*- coding: utf-8 -*-


from flask import flash, redirect, request, render_template, url_for
from flask_login import current_user

from flask_se_auth import login_required
from se_internship_forms import AddInternship, InternshipsFilter
from se_models import db, Internships, InternshipFormat, InternshipCompany


@login_required
def account_profile():
    user = current_user
    return render_template('account/profile.html', user=user)

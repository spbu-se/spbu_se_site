# -*- coding: utf-8 -*-


from flask import flash, redirect, request, render_template, url_for
from flask_login import current_user

from flask_se_auth import login_required
from se_forms import CurrentCourseArea, ChooseTopic
from se_models import AreasOfStudy, Users, CurrentThesis, Staff, Worktype, UserStudent, db


@login_required
def account_new_thesis():
    user = current_user
    form = CurrentCourseArea()

    if request.method == "POST":
        currentArea = request.form.get('area', type=str)
        course = request.form.get('course', type=int)
        new_thesis = CurrentThesis()
        new_thesis.course = course
        new_thesis.author_id = user.user_student[0].id
        print(user.user_student[0].id)
        currentArea_id = 0
        for area in AreasOfStudy.query.filter(AreasOfStudy.id > 1).distinct().all():
            if (area.area == currentArea):
                currentArea_id = area.id
        new_thesis.area = currentArea_id

        db.session.add(new_thesis)
        db.session.commit()

    for area in AreasOfStudy.query.filter(AreasOfStudy.id > 1).distinct().all():
        form.area.choices.append(area.area)

    form.area.choices.sort(key=lambda tup: tup[0])

    for course in range(2, 7):
        form.course.choices.append(course)

    return render_template('account/profile.html', user=user, review_filter=form, form=form)


@login_required
def account_index():
    user = current_user

    if request.method == "POST":
        user_student = UserStudent()
        user_student.user_id = user.id

        db.session.add(user_student)
        db.session.commit()

    userIsStudent = False
    if len(user.user_student) >= 1:
        userIsStudent = True

    return render_template('account/index.html', userIsStudent=userIsStudent, user=user)


@login_required
def account_guide():
    user = current_user
    return render_template('account/guide.html', user=user)


@login_required
def account_data_for_practice():

    practice_id = request.args.get('id', type=int)
    if not practice_id:
        return redirect(url_for('account_index'))

    user = current_user
    form = CurrentCourseArea()

    for area in AreasOfStudy.query.filter(AreasOfStudy.id > 1).distinct().all():
        form.area.choices.append(area.area)

    form.area.choices.sort(key=lambda tup: tup[0])

    for course in range(2, 7):
        form.course.choices.append(course)

    return render_template('account/data_for_practice.html', user=user, form=form)


@login_required
def account_choosing_topic():
    user = current_user
    form = ChooseTopic()

    if request.method == "POST":
        topic = request.form.get('topic', type=str)
        supervisor = request.form.get('staff', type=str)
        worktype = request.form.get('worktype', type=str)

        supervisor_id = 1
        for staff in Staff.query.distinct().all():
            if (staff.user.get_name() == supervisor):
                supervisor_id = staff.user.id

        print(topic)
        print(supervisor_id)
        print(worktype)

    form.staff.choices.append('Выберите научного руководителя')
    for supervisor in Staff.query.filter_by(still_working=1).all():
        form.staff.choices.append(supervisor.user.get_name())

    form.worktype.choices.append('Выберите тип работы')
    for worktype in Worktype.query.all():
        form.worktype.choices.append(worktype)

    return render_template('account/choosing_topic.html', user=user, form=form)


@login_required
def account_workflow():
    user = current_user
    return render_template('account/account_workflow.html', user=user)


@login_required
def account_preparation():
    user = current_user
    return render_template('account/account_preparation.html', user=user)


@login_required
def account_thesis_defense():
    user = current_user
    return render_template('account/defense.html', user=user)


@login_required
def account_materials():
    user = current_user
    return render_template('account/account_materials.html', user=user)
# -*- coding: utf-8 -*-


from flask import flash, redirect, request, render_template, url_for
from flask_login import current_user

from flask_se_auth import login_required
from se_forms import CurrentCourseArea, ChooseTopic
from se_models import AreasOfStudy, Users, CurrentThesis, Staff, Worktype, UserStudent, db


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

    return render_template('account/index.html', thesises=get_list_of_thesises(), userIsStudent=userIsStudent)


@login_required
def account_guide():
    return render_template('account/guide.html', thesises=get_list_of_thesises())


@login_required
def account_new_thesis():
    user = current_user
    form = CurrentCourseArea()

    if request.method == "POST":
        current_area_id = request.form.get('area', type=int)
        current_course = request.form.get('course', type=int)
        if current_area_id == 0:
            flash('Выберите направление.', category='error')
        elif current_course == 0:
            flash('Выберите курс.', category='error')
        else:
            new_thesis = CurrentThesis()
            new_thesis.course = current_course
            new_thesis.author_id = user.user_student[0].id
            new_thesis.area_id = current_area_id

            db.session.add(new_thesis)
            db.session.commit()
            return redirect(url_for('account_choosing_topic', id=new_thesis.id))

    form.area.choices.append((0, 'Выберите направление'))
    for area in AreasOfStudy.query.filter(AreasOfStudy.id > 1).order_by('id').all():
        form.area.choices.append((area.id, area.area))

    form.course.choices.append((0, 'Выберите курс'))
    for course in range(2, 7):
        form.course.choices.append((course, course))

    return render_template('account/new_practice.html', thesises=get_list_of_thesises(), user=user, review_filter=form, form=form)


@login_required
def account_choosing_topic():
    current_thesis_id = request.args.get('id', type=int)
    if not current_thesis_id:
        return redirect(url_for('account_index'))

    current_thesis = CurrentThesis.query.filter_by(id=current_thesis_id).first()
    if not current_thesis:
        return redirect(url_for('account_index'))

    form = ChooseTopic()

    if request.method == "POST":
        if request.form['submit_button'] == 'Сохранить':
            topic = request.form.get('topic', type=str)
            supervisor_id = request.form.get('staff', type=int)
            worktype_id = request.form.get('worktype', type=int)

            if not topic:
                flash('Введите название темы.', category='error')
            elif len(topic) <= 7:
                flash('Слишком короткое название темы.', category='error')
            elif not supervisor_id:
                flash('Выберите научного руководителя.', category='error')
            elif not worktype_id:
                flash('Выберите тип работы.', category='error')
            else:
                current_thesis.title = topic
                current_thesis.supervisor_id = supervisor_id
                current_thesis.worktype_id = worktype_id

                db.session.commit()

        elif request.form['submit_button'] == 'Редактировать':
            return redirect(url_for('account_edit_theme', id=current_thesis_id))

        elif request.form['submit_button'] == 'Да, отказываюсь!':
            current_thesis.title = None
            current_thesis.supervisor_id = None
            current_thesis.worktype_id = None

            db.session.commit()

    form.staff.choices.append((0, 'Выберите научного руководителя'))
    for supervisor in Staff.query.filter_by(still_working=True).all():
        form.staff.choices.append((supervisor.id, supervisor.user.get_name()))
    form.worktype.choices.append((0, 'Выберите тип работы'))
    for worktype in Worktype.query.filter(Worktype.id > 1).all():
        form.worktype.choices.append((worktype.id, worktype.type))

    return render_template('account/choosing_topic.html', thesises=get_list_of_thesises(), form=form, practice=current_thesis)


@login_required
def account_edit_theme():
    current_thesis_id = request.args.get('id', type=int)
    if not current_thesis_id:
        return redirect(url_for('account_index'))

    current_thesis = CurrentThesis.query.filter_by(id=current_thesis_id).first()
    if not current_thesis:
        return redirect(url_for('account_index'))

    form = ChooseTopic()
    if request.method == "POST":
        if request.form['submit_button'] == 'Сохранить':
            topic = request.form.get('topic', type=str)
            supervisor_id = request.form.get('staff', type=int)
            worktype_id = request.form.get('worktype', type=int)

            if not topic:
                flash('Введите название темы.', category='error')
            elif len(topic) <= 7:
                flash('Слишком короткое название темы.', category='error')
            elif not supervisor_id:
                flash('Выберите научного руководителя.', category='error')
            elif not worktype_id:
                flash('Выберите тип работы.', category='error')
            else:
                current_thesis.title = topic
                current_thesis.supervisor_id = supervisor_id
                current_thesis.worktype_id = worktype_id

                db.session.commit()
                return redirect(url_for('account_choosing_topic', id=current_thesis_id))

    form.topic.data = current_thesis.title
    form.staff.choices.append((current_thesis.supervisor_id, current_thesis.supervisor))
    form.worktype.choices.append((current_thesis.worktype_id, current_thesis.worktype))
    for supervisor in Staff.query.filter_by(still_working=True).filter(Staff.id != current_thesis.supervisor_id).all():
        form.staff.choices.append((supervisor.id, supervisor.user.get_name()))
    for worktype in Worktype.query.filter(Worktype.id > 1).filter(Worktype.id != current_thesis.worktype_id).all():
        form.worktype.choices.append((worktype.id, worktype.type))

    return render_template('account/edit_theme.html', thesises=get_list_of_thesises(), form=form,
                           practice=current_thesis)


@login_required
def account_workflow():
    current_thesis_id = request.args.get('id', type=int)
    if not current_thesis_id:
        return redirect(url_for('account_index'))

    current_thesis = CurrentThesis.query.filter_by(id=current_thesis_id).first()
    if not current_thesis:
        return redirect(url_for('account_index'))

    return render_template('account/workflow.html', thesises=get_list_of_thesises(), practice=current_thesis)


@login_required
def account_preparation():
    current_thesis_id = request.args.get('id', type=int)
    if not current_thesis_id:
        return redirect(url_for('account_index'))

    current_thesis = CurrentThesis.query.filter_by(id=current_thesis_id).first()
    if not current_thesis:
        return redirect(url_for('account_index'))

    return render_template('account/preparation.html', thesises=get_list_of_thesises(), practice=current_thesis)


@login_required
def account_thesis_defense():
    current_thesis_id = request.args.get('id', type=int)
    if not current_thesis_id:
        return redirect(url_for('account_index'))

    current_thesis = CurrentThesis.query.filter_by(id=current_thesis_id).first()
    if not current_thesis:
        return redirect(url_for('account_index'))

    return render_template('account/defense.html', thesises=get_list_of_thesises(), practice=current_thesis)


@login_required
def account_materials():
    current_thesis_id = request.args.get('id', type=int)
    if not current_thesis_id:
        return redirect(url_for('account_index'))

    current_thesis = CurrentThesis.query.filter_by(id=current_thesis_id).first()
    if not current_thesis:
        return redirect(url_for('account_index'))

    return render_template('account/materials.html', thesises=get_list_of_thesises(), practice=current_thesis)


@login_required
def account_data_for_practice():
    current_thesis_id = request.args.get('id', type=int)
    if not current_thesis_id:
        return redirect(url_for('account_index'))

    current_thesis = CurrentThesis.query.filter_by(id=current_thesis_id).first()
    if not current_thesis:
        return redirect(url_for('account_index'))

    user = current_user
    form = CurrentCourseArea()
    if request.method == "POST":
        if request.form['submit_button'] == 'Сохранить':
            current_area_id = request.form.get('area', type=int)
            current_course = request.form.get('course', type=int)

            if current_area_id == current_thesis.area_id and current_course == current_thesis.course:
                flash('Никаких изменений нет.', category='error')
            else:
                if current_area_id != current_thesis.area_id:
                    current_thesis.area_id = current_area_id
                if current_course != current_thesis.course:
                    current_thesis.course = current_course
                flash('Изменения сохранены', category='success')
                db.session.commit()

        elif request.form['submit_button'] == 'Да, удалить!':
            current_thesis.deleted = True
            db.session.commit()
            return redirect(url_for('account_index'))

    form.area.choices.append((current_thesis.area_id, current_thesis.area))
    for area in AreasOfStudy.query.filter(AreasOfStudy.id > 1).filter(AreasOfStudy.id != current_thesis.area.id). \
            order_by('id').all():
        form.area.choices.append((area.id, area.area))

    form.course.choices.append((current_thesis.course, current_thesis.course))
    for course in range(2, 7):
        if course != current_thesis.course:
            form.course.choices.append((course, course))

    return render_template('account/data_for_practice.html', thesises=get_list_of_thesises(), user=user, form=form,
                           practice=current_thesis)


def get_list_of_thesises():
    user = current_user

    if not user.user_student:
        return [] #redirect(url_for('user_profile'))

    return [thesis for thesis in user.user_student[0].thesises if thesis.deleted == False]

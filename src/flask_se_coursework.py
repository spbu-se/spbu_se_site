# -*- coding: utf-8 -*-

import os
import pytz
from datetime import date, timedelta

import werkzeug
from flask import flash, redirect, request, render_template, url_for
from flask_login import current_user
from sqlalchemy import desc, asc
from datetime import datetime
from pytz import timezone
from transliterate import translit

from flask_se_auth import login_required
from flask_se_config import get_thesis_type_id_string
from se_forms import ChooseTopic, DeadlineTemp, UserAddReport, CurrentWorktypeArea, AddGoal, AddTask
from se_models import Users, AreasOfStudy, CurrentThesis, Staff, Worktype, NotificationAccount, Deadline, db, \
    ThesisReport, ThesisTask

# Global variables
formatDateTime = "%d.%m.%Y %H:%M"
TEXT_UPLOAD_FOLDER = 'static/currentThesis/texts/'
REVIEW_UPLOAD_FOLDER = 'static/currentThesis/reviews/'
PRESENTATION_UPLOAD_FOLDER = 'static/currentThesis/slides/'
ALLOWED_EXTENSIONS = {'pdf'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@login_required
def coursework_temp_deadline():
    form = DeadlineTemp()

    if request.method == "POST":
        worktype_id = request.form.get('worktype', type=int)
        area_id = request.form.get('area', type=int)

        if area_id == 0:
            flash('Укажите направление.', category='error')
        elif worktype_id == 0:
            flash('Укажите тип работы!', category='error')
        else:
            deadline = Deadline.query.filter_by(worktype_id=worktype_id).filter_by(area_id=area_id).first()
            if not deadline:
                deadline = Deadline()
                deadline.worktype_id = worktype_id
                deadline.area_id = area_id
                db.session.add(deadline)

            current_thesises = CurrentThesis.query.filter_by(worktype_id=worktype_id).filter_by(area_id=area_id).all()

            if request.form.get('choose_topic'):
                new_deadline = datetime.strptime(request.form.get('choose_topic'), "%Y-%m-%dT%H:%M").astimezone(
                    pytz.UTC)
                if not deadline.choose_topic or deadline.choose_topic and \
                        deadline.choose_topic.replace(tzinfo=pytz.UTC) != new_deadline:
                    first_word = ""
                    if not deadline.choose_topic:
                        first_word = "Назначен"
                    elif deadline.choose_topic.replace(tzinfo=pytz.UTC) != new_deadline:
                        first_word = "Изменён"

                    deadline.choose_topic = new_deadline
                    for currentThesis in current_thesises:
                        notification = NotificationAccount()
                        notification.recipient_id = currentThesis.author_id
                        notification.content = first_word + " дедлайн на выбор темы для " + Worktype.query. \
                            filter_by(id=worktype_id).first().type + " для направления " + AreasOfStudy.query.\
                            filter_by(id=area_id).first().area + ": **" + new_deadline.replace(tzinfo=pytz.UTC).\
                            astimezone(timezone("Europe/Moscow")).strftime(formatDateTime) + " МСК**"

                        db.session.add(notification)

            if request.form.get('submit_work_for_review'):
                new_deadline = datetime.strptime(request.form.get('submit_work_for_review'),
                                                 "%Y-%m-%dT%H:%M").astimezone(pytz.UTC)
                if not deadline.submit_work_for_review or \
                        deadline.submit_work_for_review and deadline.submit_work_for_review.replace(tzinfo=pytz.UTC) \
                        != new_deadline:
                    first_word = ""
                    if not deadline.submit_work_for_review:
                        first_word = "Назначен"
                    elif deadline.submit_work_for_review.replace(tzinfo=pytz.UTC) != new_deadline:
                        first_word = "Изменён"

                    deadline.submit_work_for_review = new_deadline
                    for currentThesis in current_thesises:
                        notification = NotificationAccount()
                        notification.recipient_id = currentThesis.author_id
                        notification.content = first_word + " дедлайн на отправку работы для рецензирования для " + \
                            Worktype.query.filter_by(id=worktype_id).first().type + " для направления " + \
                            AreasOfStudy.query.filter_by(id=area_id).first().area + ": **" + new_deadline.\
                            replace(tzinfo=pytz.UTC).astimezone(timezone("Europe/Moscow")).strftime(formatDateTime) + \
                            " МСК**"

                        db.session.add(notification)

            if request.form.get('upload_reviews'):
                new_deadline = datetime.strptime(request.form.get('upload_reviews'), "%Y-%m-%dT%H:%M").astimezone(
                    pytz.UTC)
                if not deadline.upload_reviews or \
                        deadline.upload_reviews and deadline.upload_reviews.replace(tzinfo=pytz.UTC) != new_deadline:
                    first_word = ""
                    if not deadline.upload_reviews:
                        first_word = "Назначен"
                    elif deadline.upload_reviews.replace(tzinfo=pytz.UTC) != new_deadline:
                        first_word = "Изменён"

                    deadline.upload_reviews = new_deadline
                    for currentThesis in current_thesises:
                        notification = NotificationAccount()
                        notification.recipient_id = currentThesis.author_id
                        notification.content = first_word + " дедлайн на загрузку отзывов для " + Worktype.query. \
                            filter_by(id=worktype_id).first().type + " для направления " + AreasOfStudy.query.\
                            filter_by(id=area_id).first().area + ": **" + new_deadline.replace(tzinfo=pytz.UTC).\
                            astimezone(timezone("Europe/Moscow")).strftime(formatDateTime) + " МСК**"

                        db.session.add(notification)

            if request.form.get('pre_defense'):
                new_deadline = datetime.strptime(request.form.get('pre_defense'), "%Y-%m-%dT%H:%M").astimezone(pytz.UTC)
                if not deadline.pre_defense or \
                        deadline.pre_defense and deadline.pre_defense.replace(tzinfo=pytz.UTC) != new_deadline:
                    first_word = ""
                    if not deadline.pre_defense:
                        first_word = "Назначено"
                    elif deadline.pre_defense.replace(tzinfo=pytz.UTC) != new_deadline:
                        first_word = "Изменено"

                    deadline.pre_defense = new_deadline
                    for currentThesis in current_thesises:
                        notification = NotificationAccount()
                        notification.recipient_id = currentThesis.author_id
                        notification.content = first_word + " время предзащиты для " + Worktype.query.\
                            filter_by(id=worktype_id).first().type + " для направления " + AreasOfStudy.query.\
                            filter_by(id=area_id).first().area + ": **" + new_deadline.replace(tzinfo=pytz.UTC).\
                            astimezone(timezone("Europe/Moscow")).strftime(formatDateTime) + " МСК**"

                        db.session.add(notification)

            if request.form.get('defense'):
                new_deadline = datetime.strptime(request.form.get('defense'), "%Y-%m-%dT%H:%M").astimezone(pytz.UTC)
                if not deadline.defense or \
                        deadline.defense and deadline.defense.replace(tzinfo=pytz.UTC) != new_deadline:
                    first_word = ""
                    if not deadline.defense:
                        first_word = "Назначено"
                    elif deadline.defense.replace(tzinfo=pytz.UTC) != new_deadline:
                        first_word = "Изменено"

                    deadline.defense = new_deadline
                    for currentThesis in current_thesises:
                        notification = NotificationAccount()
                        notification.recipient_id = currentThesis.author_id
                        notification.content = first_word + " время защиты для " + Worktype.query.\
                            filter_by(id=worktype_id).first().type + " для направления " + AreasOfStudy.query.\
                            filter_by(id=area_id).first().area + ": **" + new_deadline.replace(tzinfo=pytz.UTC).\
                            astimezone(timezone("Europe/Moscow")).strftime(formatDateTime) + " МСК**"

                        db.session.add(notification)

            db.session.commit()

    form.area.choices.append((0, 'Выберите направление'))
    for area in AreasOfStudy.query.filter(AreasOfStudy.id > 1).order_by('id').all():
        form.area.choices.append((area.id, area.area))

    form.worktype.choices.append((0, 'Выберите тип работы'))
    for worktype in Worktype.query.filter(Worktype.id > 2).order_by('id').all():
        form.worktype.choices.append((worktype.id, worktype.type))

    return render_template('coursework/temp_deadline.html', form=form)


@login_required
def coursework_temp():
    if request.method == "POST":
        recipient_id = request.form.get('recipient')
        content = request.form.get('content')
        if recipient_id and content:
            new_notification = NotificationAccount()
            new_notification.recipient_id = recipient_id
            new_notification.content = content

            db.session.add(new_notification)
            db.session.commit()

    return render_template('coursework/temp.html')


@login_required
def coursework_index():
    user = current_user

    type_notifications = request.args.get('notifications', type=str)
    if not type_notifications:
        type_notifications = "new"

    if request.method == "POST":
        if request.form['read_button']:
            notification_id = request.form['read_button']
            notification = NotificationAccount.query.filter_by(id=notification_id).first()
            notification.viewed = True

            db.session.commit()

    notifications = NotificationAccount.query.filter_by(recipient_id=user.id) \
        .order_by(desc(NotificationAccount.time)).all()
    notifications_not_viewed = NotificationAccount.query.filter_by(recipient_id=user.id).filter_by(viewed=False). \
        order_by(desc(NotificationAccount.time)).all()

    return render_template('coursework/student/index.html', thesises=get_list_of_thesises(),
                           notifications=notifications, notifications_not_viewed=notifications_not_viewed,
                           type_notifications=type_notifications)


@login_required
def coursework_guide():
    return render_template('coursework/student/guide.html', thesises=get_list_of_thesises())


@login_required
def coursework_new_thesis():
    user = current_user
    form = CurrentWorktypeArea()

    if request.method == "POST":
        current_area_id = request.form.get('area', type=int)
        current_worktype_id = request.form.get('worktype', type=int)
        if current_worktype_id == 0:
            flash('Выберите тип работы.', category='error')
        elif current_area_id == 0:
            flash('Выберите направление.', category='error')
        else:
            new_thesis = CurrentThesis()
            new_thesis.author_id = user.id
            new_thesis.worktype_id = current_worktype_id
            new_thesis.area_id = current_area_id

            db.session.add(new_thesis)
            db.session.commit()
            return redirect(url_for('coursework_choosing_topic', id=new_thesis.id))

    form.area.choices.append((0, 'Выберите направление'))
    for area in AreasOfStudy.query.filter(AreasOfStudy.id > 1).order_by('id').all():
        form.area.choices.append((area.id, area.area))

    form.worktype.choices.append((0, 'Выберите тип работы'))
    for worktype in Worktype.query.filter(Worktype.id > 2).all():
        form.worktype.choices.append((worktype.id, worktype.type))

    return render_template('coursework/student/new_practice.html', thesises=get_list_of_thesises(), user=user,
                           review_filter=form,
                           form=form)


@login_required
def coursework_choosing_topic():
    current_thesis_id = request.args.get('id', type=int)
    if not current_thesis_id:
        return redirect(url_for('coursework_index'))

    current_thesis = CurrentThesis.query.filter_by(author_id=current_user.id).filter_by(id=current_thesis_id).first()
    if not current_thesis or current_thesis.deleted:
        return redirect(url_for('coursework_index'))

    if request.method == "POST":
        if request.form['submit_button'] == 'Сохранить':
            topic = request.form.get('topic', type=str)
            supervisor_id = request.form.get('staff', type=int)

            if not topic:
                flash('Введите название темы.', category='error')
            elif len(topic) <= 7:
                flash('Слишком короткое название темы.', category='error')
            elif not supervisor_id:
                flash('Выберите научного руководителя.', category='error')
            else:
                current_thesis.title = topic
                current_thesis.supervisor_id = supervisor_id
                db.session.commit()

        elif request.form['submit_button'] == 'Да, отказываюсь!':
            current_thesis.title = None
            current_thesis.supervisor_id = None

            db.session.commit()

    deadline = Deadline.query.filter_by(worktype_id=current_thesis.worktype_id).filter_by(
        area_id=current_thesis.area_id).first()

    form = ChooseTopic()
    form.staff.choices.append((0, 'Выберите научного руководителя'))
    for supervisor in Staff.query.join(Users, Staff.user_id == Users.id).order_by(asc(Users.last_name)).all():
        form.staff.choices.append((supervisor.id, supervisor.user.get_name()))

    return render_template('coursework/student/choosing_topic.html', thesises=get_list_of_thesises(), form=form,
                           practice=current_thesis, deadline=deadline,
                           remaining_time=get_remaining_time(deadline, "choose_topic"))


@login_required
def coursework_edit_theme():
    current_thesis_id = request.args.get('id', type=int)
    if not current_thesis_id:
        return redirect(url_for('coursework_index'))

    current_thesis = CurrentThesis.query.filter_by(author_id=current_user.id).filter_by(id=current_thesis_id).first()
    if not current_thesis or current_thesis.deleted:
        return redirect(url_for('coursework_index'))

    form = ChooseTopic()
    if request.method == "POST":
        if request.form['submit_button'] == 'Сохранить':
            topic = request.form.get('topic', type=str)
            supervisor_id = request.form.get('staff', type=int)

            if not topic:
                flash('Введите название темы.', category='error')
            elif len(topic) <= 7:
                flash('Слишком короткое название темы.', category='error')
            elif not supervisor_id:
                flash('Выберите научного руководителя.', category='error')
            else:
                current_thesis.title = topic
                current_thesis.supervisor_id = supervisor_id

                db.session.commit()
                return redirect(url_for('coursework_choosing_topic', id=current_thesis_id))

    form.topic.data = current_thesis.title
    form.staff.choices.append((current_thesis.supervisor_id, current_thesis.supervisor))
    for supervisor in Staff.query.join(Users, Staff.user_id == Users.id).filter(
            Staff.id != current_thesis.supervisor_id) \
            .order_by(asc(Users.last_name)).all():
        form.staff.choices.append((supervisor.id, supervisor.user.get_name()))

    return render_template('coursework/student/edit_theme.html', thesises=get_list_of_thesises(), form=form,
                           practice=current_thesis)


@login_required
def coursework_goals_tasks():
    current_thesis_id = request.args.get('id', type=int)
    if not current_thesis_id:
        return redirect(url_for('coursework_index'))

    current_thesis = CurrentThesis.query.filter_by(author_id=current_user.id).filter_by(id=current_thesis_id).first()
    if not current_thesis or current_thesis.deleted:
        return redirect(url_for('coursework_index'))

    formGoal = AddGoal()
    formTask = AddTask()
    if request.method == "POST":
        if 'submit_goal_button' in request.form and request.form['submit_goal_button'] == 'Сохранить' \
                and request.form['goal']:
            goal = request.form.get('goal', type=str)
            if len(goal) <= 20:
                flash("Напишите подробнее!", category='error')
            else:
                current_thesis.goal = goal
                db.session.commit()
                flash('Цель добавлена!', category='success')

        if 'submit_goal_button' in request.form and request.form['submit_goal_button'] == 'Сохранить изменения' \
                and request.form['goal']:
            goal = request.form.get('goal', type=str)
            if len(goal) <= 20:
                flash("Напишите подробнее!", category='error')
            else:
                current_thesis.goal = goal
                db.session.commit()
                flash('Цель изменена!', category='success')
        if 'submit_task_button' in request.form:
            if 'submit_task_button' in request.form:
                task = request.form.get('task_text', type=str)
                same = False
                for existedTask in current_thesis.tasks:
                    if not existedTask.deleted and existedTask.task_text == task:
                        same = True
                if same:
                    flash("Такая задача уже существует!", category='error')
                elif len(task) <= 15:
                    flash("Опишите задачу подробнее!", category='error')
                else:
                    new_task = ThesisTask(task_text=task, current_thesis_id=current_thesis_id)
                    db.session.add(new_task)
                    db.session.commit()
                    flash('Задача успешно добавлена!', category='success')

        for task in current_thesis.tasks:
            if 'delete_task_' + str(task.id) in request.form:
                task.deleted = True
                db.session.commit()
                flash('Задача удалена!', category='success')

    return render_template('coursework/student/goals_tasks.html', thesises=get_list_of_thesises(),
                           practice=current_thesis, formGoal=formGoal, formTask=formTask)


@login_required
def coursework_workflow():
    current_thesis_id = request.args.get('id', type=int)
    if not current_thesis_id:
        return redirect(url_for('coursework_index'))

    current_thesis = CurrentThesis.query.filter_by(author_id=current_user.id).filter_by(id=current_thesis_id).first()
    if not current_thesis or current_thesis.deleted:
        return redirect(url_for('coursework_index'))

    if request.method == "POST":
        if request.form['delete_button']:
            report_id = request.form['delete_button']
            report = ThesisReport.query.filter_by(id=report_id).first()
            report.deleted = True
            db.session.commit()
            flash('Отчёт удален!', category='success')

    reports = ThesisReport.query.filter_by(current_thesis_id=current_thesis_id).filter_by(deleted=False). \
        order_by(desc(ThesisReport.time)).all()
    return render_template('coursework/student/workflow.html', thesises=get_list_of_thesises(), practice=current_thesis,
                           reports=reports)


@login_required
def coursework_add_new_report():
    current_thesis_id = request.args.get('id', type=int)
    if not current_thesis_id:
        return redirect(url_for('coursework_index'))

    current_thesis = CurrentThesis.query.filter_by(author_id=current_user.id).filter_by(id=current_thesis_id).first()
    if not current_thesis or current_thesis.deleted:
        return redirect(url_for('coursework_index'))

    user = current_user
    add_thesis_report_form = UserAddReport()

    if request.method == 'POST':
        was_done = request.form.get('was_done', type=str)
        planned_to_do = request.form.get('planned_to_do', type=str)

        if not was_done:
            flash('Поле "Что было сделано?" является обязательным!', category='error')
        elif not planned_to_do:
            flash('Поле "Что планируется сделать?" является обязательным!', category='error')
        elif len(was_done) <= 10:
            flash("Слишком короткое описание проделанной работы, напишите подробнее!", category='error')
        elif len(planned_to_do) <= 10:
            flash("Слишком короткое описание дальнейших планов, напишите подробнее!", category='error')
        else:
            new_report = ThesisReport(was_done=was_done, planned_to_do=planned_to_do,
                                      current_thesis_id=current_thesis_id, author_id=user.id)
            db.session.add(new_report)
            db.session.commit()
            flash('Отчёт успешно отправлен!', category='success')
            return redirect(url_for('coursework_workflow', id=current_thesis_id))

    return render_template('coursework/student/new_report.html', thesises=get_list_of_thesises(),
                           practice=current_thesis,
                           form=add_thesis_report_form, user=user)


@login_required
def coursework_preparation():
    current_thesis_id = request.args.get('id', type=int)
    if not current_thesis_id:
        return redirect(url_for('coursework_index'))

    current_thesis = CurrentThesis.query.filter_by(author_id=current_user.id).filter_by(id=current_thesis_id).first()
    if not current_thesis or current_thesis.deleted:
        return redirect(url_for('coursework_index'))

    if request.method == 'POST':
        if 'submit_text_button' in request.form:
            text_file = werkzeug.datastructures.FileStorage()
            if 'text' in request.files:
                text_file = request.files['text']

            if not current_thesis.text_uri and current_thesis.text_link:
                if text_file.filename:
                    if text_file and not allowed_file(text_file.filename):
                        flash("Текст должен быть в формате .PDF", category='error')
                    else:
                        if text_file:
                            author_en = translit(current_user.get_name(), 'ru', reversed=True)
                            author_en = author_en.replace(" ", "_")
                            text_filename = author_en + '_' + get_thesis_type_id_string(current_thesis.worktype_id)

                            text_filename = text_filename + '_' + str(date.today().year) + '_text'
                            text_filename_with_ext = text_filename + '.pdf'
                            full_text_filename = os.path.join(TEXT_UPLOAD_FOLDER + text_filename_with_ext)

                            # Check if file already exist
                            if os.path.isfile(full_text_filename):
                                text_filename = text_filename + '_' + str(os.urandom(8).hex())
                                text_filename_with_ext = text_filename + '.pdf'
                                full_text_filename = os.path.join(
                                    TEXT_UPLOAD_FOLDER + text_filename_with_ext)

                            text_file.save(full_text_filename)

                            current_thesis.text_uri = text_filename_with_ext
                            db.session.commit()
                            flash('Текст успешно загружен!', category='success')
                else:
                    flash('Вы не загрузили текст работы.', category='error')

            elif current_thesis.text_uri and not current_thesis.text_link:
                if request.form['text_link']:
                    text_link = request.form['text_link']
                    current_thesis.text_link = text_link
                    db.session.commit()
                    flash('Ссылка на текст работы сохранена!', category='success')
                else:
                    flash('Вы не указали ссылку на текст;', category='error')

            elif not current_thesis.text_uri and not current_thesis.text_link:
                if not request.form['text_link'] and not text_file.filename:
                    flash('Вы не загрузили текст работы и не указали ссылку на текст.', category='error')
                else:
                    if request.form['text_link']:
                        text_link = request.form['text_link']
                        current_thesis.text_link = text_link
                        db.session.commit()
                        flash('Ссылка на текст работы сохранена!', category='success')

                    if text_file.filename:
                        if text_file and not allowed_file(text_file.filename):
                            flash("Текст должен быть в формате .PDF", category='error')
                        else:
                            if text_file:
                                author_en = translit(current_user.get_name(), 'ru', reversed=True)
                                author_en = author_en.replace(" ", "_")
                                text_filename = author_en + '_' + get_thesis_type_id_string(current_thesis.worktype_id)

                                text_filename = text_filename + '_' + str(date.today().year) + '_text'
                                text_filename_with_ext = text_filename + '.pdf'
                                full_text_filename = os.path.join(TEXT_UPLOAD_FOLDER + text_filename_with_ext)

                                # Check if file already exist
                                if os.path.isfile(full_text_filename):
                                    text_filename = text_filename + '_' + str(os.urandom(8).hex())
                                    text_filename_with_ext = text_filename + '.pdf'
                                    full_text_filename = os.path.join(
                                        TEXT_UPLOAD_FOLDER + text_filename_with_ext)

                                text_file.save(full_text_filename)

                                current_thesis.text_uri = text_filename_with_ext
                                db.session.commit()
                                flash('Текст успешно загружен!', category='success')

        elif 'submit_review_button' in request.form:
            supervisor_review_file = werkzeug.datastructures.FileStorage()
            consultant_review_file = werkzeug.datastructures.FileStorage()
            if 'supervisor_review' in request.files:
                supervisor_review_file = request.files['supervisor_review']
            if 'consultant_review' in request.files:
                consultant_review_file = request.files['consultant_review']

            if supervisor_review_file.filename == '' and consultant_review_file.filename == '':
                flash('Вы не загрузили отзыв.', category='error')
            elif supervisor_review_file and not allowed_file(supervisor_review_file.filename) or \
                    consultant_review_file and not allowed_file(consultant_review_file.filename):
                flash("Текст отзывов должен быть в формате .PDF", category='error')
            else:
                author_en = translit(current_user.get_name(), 'ru', reversed=True)
                author_en = author_en.replace(" ", "_")

                if supervisor_review_file:
                    review_filename = author_en + '_' + get_thesis_type_id_string(current_thesis.worktype_id)

                    review_filename = review_filename + '_' + str(date.today().year) + '_supervisor_review'
                    review_filename_with_ext = review_filename + '.pdf'
                    full_review_filename = os.path.join(REVIEW_UPLOAD_FOLDER + review_filename_with_ext)

                    # Check if file already exist
                    if os.path.isfile(full_review_filename):
                        review_filename = review_filename + '_' + str(os.urandom(8).hex())
                        review_filename_with_ext = review_filename + '.pdf'
                        full_review_filename = os.path.join(REVIEW_UPLOAD_FOLDER + review_filename_with_ext)

                    supervisor_review_file.save(full_review_filename)

                    current_thesis.supervisor_review_uri = review_filename_with_ext
                    db.session.commit()
                    flash('Отзыв научного руководителя успешно загружен!', category='success')

                if consultant_review_file:
                    review_filename = author_en + '_' + get_thesis_type_id_string(current_thesis.worktype_id)

                    review_filename = review_filename + '_' + str(date.today().year) + '_reviewer_review'
                    review_filename_with_ext = review_filename + '.pdf'
                    full_review_filename = os.path.join(REVIEW_UPLOAD_FOLDER + review_filename_with_ext)

                    # Check if file already exist
                    if os.path.isfile(full_review_filename):
                        review_filename = review_filename + '_' + str(os.urandom(8).hex())
                        review_filename_with_ext = review_filename + '.pdf'
                        full_review_filename = os.path.join(REVIEW_UPLOAD_FOLDER + review_filename_with_ext)

                    consultant_review_file.save(full_review_filename)

                    current_thesis.reviewer_review_uri = review_filename_with_ext
                    db.session.commit()
                    flash('Отзыв рецензента успешно загружен!', category='success')

        elif 'submit_presentation_button' in request.form:
            presentation_file = werkzeug.datastructures.FileStorage()
            if 'presentation' in request.files:
                presentation_file = request.files['presentation']

            if not current_thesis.presentation_uri and current_thesis.presentation_link:
                if presentation_file.filename:
                    if presentation_file and not allowed_file(presentation_file.filename):
                        flash("Презентация должна быть в формате .PDF", category='error')
                    else:
                        if presentation_file:
                            author_en = translit(current_user.get_name(), 'ru', reversed=True)
                            author_en = author_en.replace(" ", "_")
                            presentation_filename = author_en + '_' + get_thesis_type_id_string(
                                current_thesis.worktype_id)

                            presentation_filename = presentation_filename + '_' + str(date.today().year) + '_slides'
                            presentation_filename_with_ext = presentation_filename + '.pdf'
                            full_presentation_filename = os.path.join(
                                PRESENTATION_UPLOAD_FOLDER + presentation_filename_with_ext)

                            # Check if file already exist
                            if os.path.isfile(full_presentation_filename):
                                presentation_filename = presentation_filename + '_' + str(os.urandom(8).hex())
                                presentation_filename_with_ext = presentation_filename + '.pdf'
                                full_presentation_filename = os.path.join(
                                    PRESENTATION_UPLOAD_FOLDER + presentation_filename_with_ext)

                            presentation_file.save(full_presentation_filename)

                            current_thesis.presentation_uri = presentation_filename_with_ext
                            db.session.commit()
                            flash('Презентация успешно загружена!', category='success')
                else:
                    flash('Вы не загрузили презентацию.', category='error')

            elif current_thesis.presentation_uri and not current_thesis.presentation_link:
                if request.form['presentation_link']:
                    presentation_link = request.form['presentation_link']
                    current_thesis.presentation_link = presentation_link
                    db.session.commit()
                    flash('Ссылка на презентацию сохранена!', category='success')
                else:
                    flash('Вы не указали ссылку на презентацию;', category='error')

            elif not current_thesis.presentation_uri and not current_thesis.presentation_link:
                if not request.form['presentation_link'] and not presentation_file.filename:
                    flash('Вы не загрузили презентацию и не указали ссылку на неё.', category='error')
                else:
                    if request.form['presentation_link']:
                        presentation_link = request.form['presentation_link']
                        current_thesis.presentation_link = presentation_link
                        db.session.commit()
                        flash('Ссылка на презентацию сохранена!', category='success')

                    if presentation_file.filename:
                        if presentation_file and not allowed_file(presentation_file.filename):
                            flash("Презентация должна быть в формате .PDF", category='error')
                        else:
                            if presentation_file:
                                author_en = translit(current_user.get_name(), 'ru', reversed=True)
                                author_en = author_en.replace(" ", "_")
                                presentation_filename = author_en + '_' + get_thesis_type_id_string(
                                    current_thesis.worktype_id)

                                presentation_filename = presentation_filename + '_' + str(date.today().year) + '_slides'
                                presentation_filename_with_ext = presentation_filename + '.pdf'
                                full_presentation_filename = os.path.join(
                                    PRESENTATION_UPLOAD_FOLDER + presentation_filename_with_ext)

                                # Check if file already exist
                                if os.path.isfile(full_presentation_filename):
                                    presentation_filename = presentation_filename + '_' + str(os.urandom(8).hex())
                                    presentation_filename_with_ext = presentation_filename + '.pdf'
                                    full_presentation_filename = os.path.join(
                                        PRESENTATION_UPLOAD_FOLDER + presentation_filename_with_ext)

                                presentation_file.save(full_presentation_filename)

                                current_thesis.presentation_uri = presentation_filename_with_ext
                                db.session.commit()
                                flash('Презентация успешно загружена!', category='success')

        elif 'delete_text_button' in request.form:
            current_thesis.text_uri = None
            db.session.commit()
        elif 'delete_text_link_button' in request.form:
            current_thesis.text_link = None
            db.session.commit()
        elif 'delete_presentation_button' in request.form:
            current_thesis.presentation_uri = None
            db.session.commit()
        elif 'delete_presentation_link_button' in request.form:
            current_thesis.presentation_link = None
            db.session.commit()
        elif 'delete_reviewer_review_button' in request.form:
            current_thesis.reviewer_review_uri = None
            db.session.commit()
        elif 'delete_supevisor_review_button' in request.form:
            current_thesis.supervisor_review_uri = None
            db.session.commit()

    deadline = Deadline.query.filter_by(worktype_id=current_thesis.worktype_id). \
        filter_by(area_id=current_thesis.area_id).first()

    return render_template('coursework/student/preparation.html', thesises=get_list_of_thesises(),
                           practice=current_thesis, deadline=deadline,
                           remaining_time_submit=get_remaining_time(deadline, "submit_work_for_review"),
                           remaining_time_upload=get_remaining_time(deadline, "upload_reviews"))


@login_required
def coursework_thesis_defense():
    current_thesis_id = request.args.get('id', type=int)
    if not current_thesis_id:
        return redirect(url_for('coursework_index'))

    current_thesis = CurrentThesis.query.filter_by(author_id=current_user.id).filter_by(id=current_thesis_id).first()
    if not current_thesis or current_thesis.deleted:
        return redirect(url_for('coursework_index'))

    return render_template('coursework/student/defense.html', thesises=get_list_of_thesises(), practice=current_thesis)


@login_required
def coursework_data_for_practice():
    current_thesis_id = request.args.get('id', type=int)
    if not current_thesis_id:
        return redirect(url_for('coursework_index'))

    current_thesis = CurrentThesis.query.filter_by(author_id=current_user.id).filter_by(id=current_thesis_id).first()
    if not current_thesis or current_thesis.deleted:
        return redirect(url_for('coursework_index'))

    user = current_user
    form = CurrentWorktypeArea()
    if request.method == "POST":
        if request.form['submit_button'] == 'Сохранить':
            current_area_id = request.form.get('area', type=int)
            current_worktype_id = request.form.get('worktype', type=int)

            if current_area_id == current_thesis.area_id and current_worktype_id == current_thesis.worktype_id:
                flash('Никаких изменений нет.', category='error')
            else:
                if current_area_id != current_thesis.area_id:
                    current_thesis.area_id = current_area_id
                if current_worktype_id != current_thesis.worktype_id:
                    current_thesis.worktype_id = current_worktype_id

                db.session.commit()
                flash('Изменения сохранены', category='success')

        elif request.form['submit_button'] == 'Да, удалить!':
            current_thesis.deleted = True
            db.session.commit()
            return redirect(url_for('coursework_index'))

    form.area.choices.append((current_thesis.area_id, current_thesis.area.area))
    for area in AreasOfStudy.query.filter(AreasOfStudy.id > 1).filter(AreasOfStudy.id != current_thesis.area.id). \
            order_by('id').all():
        form.area.choices.append((area.id, area.area))

    form.worktype.choices.append((current_thesis.worktype_id, current_thesis.worktype.type))
    for worktype in Worktype.query.filter(Worktype.id > 2).all():
        if worktype.id != current_thesis.worktype_id:
            form.worktype.choices.append((worktype.id, worktype))

    return render_template('coursework/student/data_for_practice.html', thesises=get_list_of_thesises(), user=user,
                           form=form,
                           practice=current_thesis)


def get_list_of_thesises():
    """
    Returns list of current thesises, which are not deleted, for current user

    :return: list of objects that are CurrentThesis
    """
    user = current_user
    return [thesis for thesis in user.current_thesises if not thesis.deleted]


def get_remaining_time(deadline, type_deadline):
    """
    Counts the remaining time until the deadline

    :param deadline: Deadline for specified work type and area of study
    :param type_deadline: String that indicates for what deadline to count remaining time
    :return: Tuple (time, word for time, text-color), if deadline is not exist, returns empty tuple
    """
    if not deadline:
        return None

    remaining_time_timedelta = timedelta()
    if type_deadline == "choose_topic":
        if not deadline.choose_topic:
            return None
        remaining_time_timedelta = deadline.choose_topic - datetime.utcnow()
    elif type_deadline == "submit_work_for_review":
        if not deadline.submit_work_for_review:
            return None
        remaining_time_timedelta = deadline.submit_work_for_review - datetime.utcnow()
    elif type_deadline == "upload_reviews":
        if not deadline.upload_reviews:
            return None
        remaining_time_timedelta = deadline.upload_reviews - datetime.utcnow()
    elif type_deadline == "pre_defense":
        if not deadline.pre_defense:
            return None
        remaining_time_timedelta = deadline.pre_defense - datetime.utcnow()
    elif type_deadline == "defense":
        if not deadline.defense:
            return None
        remaining_time_timedelta = deadline.defense - datetime.utcnow()

    if remaining_time_timedelta < timedelta(0):
        remaining_time = (-1, "", "")
    elif remaining_time_timedelta.seconds // 60 < 60 and remaining_time_timedelta.days < 1:
        minutes = remaining_time_timedelta.seconds // 60
        if minutes in {1, 21, 31, 41, 51}:
            remaining_time = (minutes, "минута", "danger")
        elif minutes % 10 in {2, 3, 4} and minutes % 100 // 10 != 1:
            remaining_time = (minutes, "минуты", "danger")
        else:
            remaining_time = (minutes, "минут", "danger")
    elif remaining_time_timedelta.days < 1:
        hours = remaining_time_timedelta.seconds // 3600
        if hours in {1, 21}:
            remaining_time = (hours, "час", "danger")
        elif hours in {2, 3, 4, 22, 23, 24}:
            remaining_time = (hours, "часа", "danger")
        else:
            remaining_time = (hours, "часов", "danger")
    else:
        days = remaining_time_timedelta.days
        if days % 100 // 10 == 1:
            word_for_time = "дней"
        elif days % 10 == 1:
            word_for_time = "день"
        elif days % 10 in {2, 3, 4}:
            word_for_time = "дня"
        else:
            word_for_time = "дней"

        if days < 3:
            remaining_time = (days, word_for_time, "danger")
        elif days < 7:
            remaining_time = (days, word_for_time, "warning")
        else:
            remaining_time = (days, word_for_time, "body")

    return remaining_time

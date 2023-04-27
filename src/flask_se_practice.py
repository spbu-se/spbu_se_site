# -*- coding: utf-8 -*-

import os
from datetime import date, timedelta
from enum import Enum
from functools import wraps
from typing import List, Tuple

from flask import flash, redirect, request, render_template, url_for
from flask_login import current_user
from sqlalchemy import desc, asc
from datetime import datetime
from transliterate import translit

from flask_se_auth import login_required
from flask_se_config import get_thesis_type_id_string
from se_forms import ChooseTopic, UserAddReport, CurrentWorktypeArea, AddGoal, AddTask
from se_models import Users, AreasOfStudy, CurrentThesis, Staff, Worktype, NotificationPractice, Deadline, db, \
    ThesisReport, ThesisTask, add_mail_notification

from templates.practice.student.templates import PracticeStudentTemplates
from templates.notification.templates import NotificationTemplates

# Global variables
TEXT_UPLOAD_FOLDER = 'static/currentThesis/texts/'
REVIEW_UPLOAD_FOLDER = 'static/currentThesis/reviews/'
PRESENTATION_UPLOAD_FOLDER = 'static/currentThesis/slides/'
ALLOWED_EXTENSIONS = {'pdf'}
MIN_LENGTH_OF_TOPIC = 7
MIN_LENGTH_OF_GOAL = 20
MIN_LENGTH_OF_TASK = 15
MIN_LENGTH_OF_FIELD_WAS_DONE = 10
MIN_LENGTH_OF_FIELD_PLANNED_TO_DO = 10


class TypeOfFile(Enum):
    TEXT = "text"
    REVIEWER_REVIEW = "reviewer_review"
    SUPERVISOR_REVIEW = "supervisor_review"
    PRESENTATION = "slides"


def allowed_file(filename) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def current_thesis_exists_or_redirect(func):
    @wraps(func)
    def get_current_thesis_decorator():
        current_thesis_id = request.args.get('id', type=int)
        if not current_thesis_id:
            return redirect(url_for('practice_index'))
        current_thesis = CurrentThesis.query.filter_by(author_id=current_user.id).\
            filter_by(id=current_thesis_id).first()
        if not current_thesis or current_thesis.deleted:
            return redirect(url_for('practice_index'))
        return func(current_thesis)
    return get_current_thesis_decorator


@login_required
def practice_index():
    if request.method == "POST":
        if 'read_notification_button' in request.form:
            notification_id = request.form['read_notification_button']
            notification = NotificationPractice.query.filter_by(id=notification_id).first()
            if notification:
                notification.viewed = True
                db.session.commit()

    user = current_user
    type_notifications = request.args.get('notifications', type=str, default='new')

    notifications = NotificationPractice.query.filter_by(recipient_id=user.id).\
        order_by(desc(NotificationPractice.time)).all()
    notifications_not_viewed = NotificationPractice.query.filter_by(recipient_id=user.id).filter_by(viewed=False).\
        order_by(desc(NotificationPractice.time)).all()

    return render_template(PracticeStudentTemplates.MAIN.value, thesises=get_list_of_thesises(),
                           notifications=notifications, notifications_not_viewed=notifications_not_viewed,
                           type_notifications=type_notifications)


@login_required
def practice_guide():
    return render_template(PracticeStudentTemplates.GUIDE.value, thesises=get_list_of_thesises())


@login_required
def practice_new_thesis():
    if request.method == "POST":
        current_area_id = request.form.get('area', type=int)
        current_worktype_id = request.form.get('worktype', type=int)
        if current_worktype_id == 0:
            flash('Выберите тип работы.', category='error')
        elif current_area_id == 0:
            flash('Выберите направление.', category='error')
        else:
            new_thesis = CurrentThesis(author_id=current_user.id, worktype_id=current_worktype_id,
                                       area_id=current_area_id)
            db.session.add(new_thesis)
            db.session.commit()
            return redirect(url_for('practice_choosing_topic', id=new_thesis.id))

    form = CurrentWorktypeArea()
    form.area.choices.append((0, 'Выберите направление'))
    for area in AreasOfStudy.query.filter(AreasOfStudy.id > 1).order_by('id').all():
        form.area.choices.append((area.id, area.area))
    form.worktype.choices.append((0, 'Выберите тип работы'))
    for worktype in Worktype.query.filter(Worktype.id > 2).all():
        form.worktype.choices.append((worktype.id, worktype.type))

    return render_template(PracticeStudentTemplates.NEW_PRACTICE.value, thesises=get_list_of_thesises(),
                           user=current_user, review_filter=form, form=form)


@login_required
@current_thesis_exists_or_redirect
def practice_choosing_topic(current_thesis):
    if request.method == "POST":
        if 'save_topic_button' in request.form:
            topic = request.form.get('topic', type=str)
            supervisor_id = request.form.get('staff', type=int)
            if not topic:
                flash('Введите название темы.', category='error')
            elif len(topic) <= MIN_LENGTH_OF_TOPIC:
                flash('Слишком короткое название темы.', category='error')
            elif not supervisor_id:
                flash('Выберите научного руководителя.', category='error')
            else:
                current_thesis.title = topic
                current_thesis.supervisor_id = supervisor_id
                db.session.commit()
                add_mail_notification(supervisor_id, "Добавлена новая учебная практика/ВКР",
                                      render_template(NotificationTemplates.NEW_PRACTICE_TO_SUPERVISOR.value,
                                                      user=current_user, practice=current_thesis))

        elif 'delete_topic_button' in request.form:
            current_thesis.title = None
            current_thesis.supervisor_id = None
            db.session.commit()

    deadline = Deadline.query.filter_by(worktype_id=current_thesis.worktype_id).\
        filter_by(area_id=current_thesis.area_id).first()

    form = ChooseTopic()
    form.staff.choices.append((0, 'Выберите научного руководителя'))
    for supervisor in Staff.query.join(Users, Staff.user_id == Users.id).order_by(asc(Users.last_name)).all():
        form.staff.choices.append((supervisor.id, supervisor.user.get_name()))

    return render_template(PracticeStudentTemplates.CHOOSING_TOPIC.value, thesises=get_list_of_thesises(), form=form,
                           practice=current_thesis, deadline=deadline,
                           remaining_time=get_remaining_time(deadline, "choose_topic"))


@login_required
@current_thesis_exists_or_redirect
def practice_edit_theme(current_thesis):
    if request.method == "POST":
        if 'save_topic_button' in request.form:
            topic = request.form.get('topic', type=str)
            supervisor_id = request.form.get('staff', type=int)

            if not topic:
                flash('Введите название темы.', category='error')
            elif len(topic) <= MIN_LENGTH_OF_TOPIC:
                flash('Слишком короткое название темы.', category='error')
            elif not supervisor_id:
                flash('Выберите научного руководителя.', category='error')
            else:
                current_thesis.title = topic
                if current_thesis.supervisor_id != supervisor_id:
                    add_mail_notification(supervisor_id, "Добавлена новая учебная практика/ВКР",
                                          render_template(NotificationTemplates.NEW_PRACTICE_TO_SUPERVISOR.value,
                                                          user=current_user, practice=current_thesis))
                    current_thesis.supervisor_id = supervisor_id
                db.session.commit()
                return redirect(url_for('practice_choosing_topic', id=current_thesis.id))

    form = ChooseTopic()
    form.topic.data = current_thesis.title
    form.staff.choices.append((current_thesis.supervisor_id, current_thesis.supervisor))
    for supervisor in Staff.query.join(Users, Staff.user_id == Users.id).\
            filter(Staff.id != current_thesis.supervisor_id).order_by(asc(Users.last_name)).all():
        form.staff.choices.append((supervisor.id, supervisor.user.get_name()))

    return render_template(PracticeStudentTemplates.EDIT_TOPIC.value, thesises=get_list_of_thesises(), form=form,
                           practice=current_thesis)


@login_required
@current_thesis_exists_or_redirect
def practice_goals_tasks(current_thesis):
    if request.method == "POST":
        if 'submit_goal_button' in request.form or 'edit_goal_button' in request.form:
            goal = request.form.get('goal', type=str)
            if goal is None:
                return redirect(url_for('practice_goals_tasks', id=current_thesis.id))

            if len(goal) <= MIN_LENGTH_OF_GOAL:
                flash("Слишком короткое описание цели, напишите подробнее!", category='error')
                return redirect(url_for('practice_goals_tasks', id=current_thesis.id))

            if current_thesis.goal != goal:
                current_thesis.goal = goal
                db.session.commit()
                flash('Цель добавлена!' if 'submit_goal_button' in request.form else 'Цель изменена!',
                      category='success')

        elif 'submit_task_button' in request.form:
            task = request.form.get('task', type=str)

            if len(task) <= MIN_LENGTH_OF_TASK:
                flash("Опишите задачу подробнее!", category='error')
                return redirect(url_for('practice_goals_tasks', id=current_thesis.id))

            new_task = ThesisTask(task_text=task, current_thesis_id=current_thesis.id)
            db.session.add(new_task)
            db.session.commit()
            flash('Задача добавлена!', category='success')

        elif 'delete_task_id_button' in request.form and request.form['delete_task_id_button'] != "0":
            task_id = request.form['delete_task_id_button']
            task = ThesisTask.query.filter_by(id=task_id).first()
            if task is None:
                return redirect(url_for('practice_goals_tasks', id=current_thesis.id))

            task.deleted = True
            db.session.commit()
            flash('Задача удалена!', category='success')

        elif 'edit_task_id_button' in request.form and request.form['edit_task_id_button'] != "0":
            task_id = request.form['edit_task_id_button']
            task = ThesisTask.query.filter_by(id=task_id).first()
            if task is None:
                return redirect(url_for('practice_goals_tasks', id=current_thesis.id))

            new_task = request.form.get('task', type=str)
            if len(new_task) <= MIN_LENGTH_OF_TASK:
                flash("Опишите задачу подробнее!", category='error')
                return redirect(url_for('practice_goals_tasks', id=current_thesis.id))

            if task.task_text != new_task:
                task.task_text = new_task
                db.session.commit()
                flash('Задача изменена!', category='success')

    return render_template(PracticeStudentTemplates.GOALS_TASKS.value, thesises=get_list_of_thesises(),
                           practice=current_thesis)


@login_required
@current_thesis_exists_or_redirect
def practice_workflow(current_thesis):
    if request.method == "POST":
        if 'delete_button' in request.form:
            report_id = request.form['delete_button']
            report = ThesisReport.query.filter_by(id=report_id).first()
            report.deleted = True
            db.session.commit()
            flash('Отчёт удален!', category='success')

    reports = (ThesisReport.query.filter_by(current_thesis_id=current_thesis.id).filter_by(deleted=False)
               .order_by(desc(ThesisReport.time)).all())
    return render_template(PracticeStudentTemplates.WORKFLOW.value, thesises=get_list_of_thesises(),
                           practice=current_thesis, reports=reports)


@login_required
@current_thesis_exists_or_redirect
def practice_add_new_report(current_thesis):
    if request.method == 'POST':
        was_done = request.form.get('was_done', type=str)
        planned_to_do = request.form.get('planned_to_do', type=str)

        if not was_done:
            flash('Поле "Что было сделано?" является обязательным!', category='error')
        elif not planned_to_do:
            flash('Поле "Что планируется сделать?" является обязательным!', category='error')
        elif len(was_done) <= MIN_LENGTH_OF_FIELD_WAS_DONE:
            flash("Слишком короткое описание проделанной работы, напишите подробнее!", category='error')
        elif len(planned_to_do) <= MIN_LENGTH_OF_FIELD_PLANNED_TO_DO:
            flash("Слишком короткое описание дальнейших планов, напишите подробнее!", category='error')
        else:
            new_report = ThesisReport(was_done=was_done, planned_to_do=planned_to_do,
                                      current_thesis_id=current_thesis.id, author_id=current_user.id)
            db.session.add(new_report)
            db.session.commit()
            add_mail_notification(current_thesis.supervisor_id, "Новый отчёт по учебной практике",
                                  render_template(NotificationTemplates.NEW_REPORT_TO_SUPERVISOR.value,
                                                  user=current_user, practice=current_thesis))
            flash('Отчёт успешно отправлен!', category='success')
            return redirect(url_for('practice_workflow', id=current_thesis.id))

    add_thesis_report_form = UserAddReport()
    return render_template(PracticeStudentTemplates.NEW_REPORT.value, thesises=get_list_of_thesises(),
                           practice=current_thesis, form=add_thesis_report_form, user=current_user)


@login_required
@current_thesis_exists_or_redirect
def practice_preparation(current_thesis):
    if request.method == 'POST':
        if 'submit_text_button' in request.form:
            text_file = request.files['text'] if 'text' in request.files else None

            if text_file is not None and text_file.filename == ''\
                    and 'text_link' in request.form and request.form['text_link'] == '':
                flash('Вы не загрузили текст работы и не указали ссылку на текст.', category='error')
                return redirect(url_for('practice_preparation', id=current_thesis.id))

            if text_file is None and 'text_link' in request.form and request.form['text_link'] == '':
                flash('Вы не указали ссылку на текст.', category='error')
                return redirect(url_for('practice_preparation', id=current_thesis.id))

            if 'text_link' not in request.form and text_file is not None and text_file.filename == '':
                flash('Вы не загрузили текст работы.', category='error')
                return redirect(url_for('practice_preparation', id=current_thesis.id))

            if 'text_link' in request.form and request.form['text_link'] != '':
                current_thesis.text_link = request.form['text_link']
                db.session.commit()
                flash('Ссылка на текст работы сохранена!', category='success')

            if text_file is not None and (text_file.filename != '' and not allowed_file(text_file.filename)):
                flash("Текст работы должен быть в формате .PDF", category='error')
                return redirect(url_for('practice_preparation', id=current_thesis.id))

            if text_file is not None and text_file.filename != '':
                full_filename, filename = __get_filename(current_thesis, TEXT_UPLOAD_FOLDER, TypeOfFile.TEXT.value)
                text_file.save(full_filename)
                current_thesis.text_uri = filename
                db.session.commit()
                flash('Текст успешно загружен!', category='success')

        elif 'submit_review_button' in request.form:
            supervisor_review = request.files['supervisor_review'] if 'supervisor_review' in request.files else None
            reviewer_review = request.files['consultant_review'] if 'consultant_review' in request.files else None

            if supervisor_review is None and reviewer_review is None:
                return redirect(url_for('practice_preparation', id=current_thesis.id))

            # Check at least one review has been uploaded
            if supervisor_review is not None and supervisor_review.filename == ''\
                    and reviewer_review is not None and reviewer_review.filename == ''\
                    or supervisor_review is None and reviewer_review is not None and reviewer_review.filename == ''\
                    or reviewer_review is None and supervisor_review is not None and supervisor_review.filename == '':
                flash('Вы не загрузили отзыв.', category='error')
                return redirect(url_for('practice_preparation', id=current_thesis.id))

            if supervisor_review is not None and (not supervisor_review.filename == ''
                                                  and not allowed_file(supervisor_review.filename)) \
                    or reviewer_review is not None and (not reviewer_review.filename == ''
                                                        and not allowed_file(reviewer_review.filename)):
                flash('Текст отзывов должен быть в формате .PDF', category='error')
                return redirect(url_for('practice_preparation', id=current_thesis.id))

            if supervisor_review:
                full_filename, filename = __get_filename(current_thesis, REVIEW_UPLOAD_FOLDER,
                                                         TypeOfFile.SUPERVISOR_REVIEW.value)
                supervisor_review.save(full_filename)
                current_thesis.supervisor_review_uri = filename
                db.session.commit()
                flash('Отзыв научного руководителя успешно загружен!', category='success')

            if reviewer_review:
                full_filename, filename = __get_filename(current_thesis, REVIEW_UPLOAD_FOLDER,
                                                         TypeOfFile.REVIEWER_REVIEW.value)
                reviewer_review.save(full_filename)
                current_thesis.reviewer_review_uri = filename
                db.session.commit()
                flash('Отзыв рецензента успешно загружен!', category='success')

        elif 'submit_presentation_button' in request.form:
            presentation_file = request.files['presentation'] if 'presentation' in request.files else None

            if presentation_file is not None and presentation_file.filename == ''\
                    and 'presentation_link' in request.form and request.form['presentation_link'] == '':
                flash('Вы не загрузили презентацию и не указали ссылку на неё.', category='error')
                return redirect(url_for('practice_preparation', id=current_thesis.id))

            if presentation_file is None and ('presentation_link' in request.form
                                              and request.form['presentation_link'] == ''):
                flash('Вы не указали ссылку на презентацию.', category='error')
                return redirect(url_for('practice_preparation', id=current_thesis.id))

            if 'presentation_link' not in request.form and (presentation_file is not None
                                                            and presentation_file.filename == ''):
                flash('Вы не загрузили презентацию.', category='error')
                return redirect(url_for('practice_preparation', id=current_thesis.id))

            if 'presentation_link' in request.form and request.form['presentation_link'] != '':
                current_thesis.presentation_link = request.form['presentation_link']
                db.session.commit()
                flash('Ссылка на презентацию сохранена!', category='success')

            if presentation_file is not None and (presentation_file.filename != ''
                                                  and not allowed_file(presentation_file.filename)):
                flash("Презентация должна быть в формате .PDF", category='error')
                return redirect(url_for('practice_preparation', id=current_thesis.id))

            if presentation_file is not None and presentation_file.filename != '':
                full_filename, filename = __get_filename(current_thesis, PRESENTATION_UPLOAD_FOLDER,
                                                         TypeOfFile.PRESENTATION.value)
                presentation_file.save(full_filename)
                current_thesis.presentation_uri = filename
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

    deadline = Deadline.query.filter_by(worktype_id=current_thesis.worktype_id).\
        filter_by(area_id=current_thesis.area_id).first()

    return render_template(PracticeStudentTemplates.PREPARATION.value, thesises=get_list_of_thesises(),
                           practice=current_thesis, deadline=deadline,
                           remaining_time_submit=get_remaining_time(deadline, "submit_work_for_review"),
                           remaining_time_upload=get_remaining_time(deadline, "upload_reviews"))


def __get_filename(current_thesis: CurrentThesis, folder: str, type_of_file: str) -> Tuple[str, str]:
    author_en = translit(current_user.get_name(), 'ru', reversed=True)
    author_en = author_en.replace(" ", "_")

    filename = author_en + '_' + get_thesis_type_id_string(current_thesis.worktype_id)
    filename = filename + '_' + str(date.today().year) + '_' + type_of_file
    filename_with_ext = filename + '.pdf'
    full_filename = os.path.join(folder + filename_with_ext)

    # Check if file already exist
    if os.path.isfile(full_filename):
        filename = filename + '_' + str(os.urandom(8).hex())
        filename_with_ext = filename + '.pdf'
        full_filename = os.path.join(folder + filename_with_ext)

    return full_filename, filename_with_ext


@login_required
@current_thesis_exists_or_redirect
def practice_thesis_defense(current_thesis):
    return render_template(PracticeStudentTemplates.DEFENSE.value, thesises=get_list_of_thesises(),
                           practice=current_thesis)


@login_required
@current_thesis_exists_or_redirect
def practice_data_for_practice(current_thesis):
    if request.method == "POST":
        if 'save_button' in request.form:
            current_area_id = request.form.get('area', type=int)
            current_worktype_id = request.form.get('worktype', type=int)

            if current_area_id == current_thesis.area_id and current_worktype_id == current_thesis.worktype_id:
                flash('Никаких изменений нет.', category='error')
            else:
                current_thesis.area_id = current_area_id
                current_thesis.worktype_id = current_worktype_id
                db.session.commit()
                flash('Изменения сохранены', category='success')

        elif 'delete_thesis_button' in request.form:
            current_thesis.deleted = True
            db.session.commit()
            return redirect(url_for('practice_index'))

    form = CurrentWorktypeArea()
    form.area.choices.append((current_thesis.area_id, current_thesis.area.area))
    for area in AreasOfStudy.query.filter(AreasOfStudy.id > 1).filter(AreasOfStudy.id != current_thesis.area.id). \
            order_by('id').all():
        form.area.choices.append((area.id, area.area))

    form.worktype.choices.append((current_thesis.worktype_id, current_thesis.worktype.type))
    for worktype in Worktype.query.filter(Worktype.id > 2).all():
        if worktype.id != current_thesis.worktype_id:
            form.worktype.choices.append((worktype.id, worktype))

    return render_template(PracticeStudentTemplates.SETTINGS.value, thesises=get_list_of_thesises(), user=current_user,
                           form=form, practice=current_thesis)


def get_list_of_thesises() -> List[CurrentThesis]:
    return [thesis for thesis in current_user.current_thesises if not thesis.deleted]


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

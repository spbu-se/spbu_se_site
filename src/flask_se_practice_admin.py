# -*- coding: utf-8 -*-
import os
import io
from functools import wraps

import pytz
from flask import flash, redirect, request, render_template, url_for, send_file
from datetime import datetime
from flask_login import current_user
from pytz import timezone
from zipfile import ZipFile
from transliterate import translit

from flask_se_auth import login_required
from se_forms import DeadlineTemp, CurrentWorktypeArea
from se_models import (AreasOfStudy, CurrentThesis, Worktype, NotificationPractice, Deadline, db, add_mail_notification,
                       Staff)
from flask_se_practice import TEXT_UPLOAD_FOLDER, PRESENTATION_UPLOAD_FOLDER, REVIEW_UPLOAD_FOLDER
from flask_se_config import get_thesis_type_id_string
from templates.practice.admin.templates import PracticeAdminTemplates

FORMAT_DATE_TIME = "%d.%m.%Y %H:%M"
ARCHIVE_FOLDER = 'static/zip/'


def user_is_staff(func):
    @wraps(func)
    def check_user_is_staff_decorator(*args, **kwargs):
        user_staff = Staff.query.filter_by(user_id=current_user.id).first()
        if not user_staff:
            return redirect(url_for('practice_index'))
        return func(*args, **kwargs)
    return check_user_is_staff_decorator


@login_required
@user_is_staff
def choose_worktype_admin():
    source = request.args.get('source', type=str)
    if request.method == "POST":
        area_id = request.form.get('area', type=int)
        worktype_id = request.form.get('worktype', type=int)
        if worktype_id == 0:
            flash('Выберите тип работы.', category='error')
        elif area_id == 0:
            flash('Выберите направление.', category='error')
        else:
            return redirect(url_for(source if source is not None else 'index_admin',
                                    area_id=area_id, worktype_id=worktype_id))

    form = CurrentWorktypeArea()
    form.area.choices.append((0, 'Выберите направление'))
    for area in AreasOfStudy.query.filter(AreasOfStudy.id > 1).order_by(AreasOfStudy.id).all():
        form.area.choices.append((area.id, area.area))
    form.worktype.choices.append((0, 'Выберите тип работы'))
    for worktype in Worktype.query.filter(Worktype.id > 2).all():
        form.worktype.choices.append((worktype.id, worktype.type))

    return render_template(PracticeAdminTemplates.CHOOSE_WORKTYPE.value, form=form, source=source)


@login_required
@user_is_staff
def index_admin():
    area_id = request.args.get('area_id', type=int)
    worktype_id = request.args.get('worktype_id', type=int)
    if not area_id or not worktype_id:
        return redirect(url_for('choose_worktype_admin', source=index_admin.__name__))
    area = AreasOfStudy.query.filter_by(id=area_id).first()
    worktype = Worktype.query.filter_by(id=worktype_id).first()

    if request.method == 'POST':
        if "download_materials_button" in request.form:
            return download_materials(area, worktype)

    list_of_thesises = (CurrentThesis.query.filter_by(area_id=area_id).filter_by(worktype_id=worktype_id)
                        .filter_by(deleted=False).filter_by(status=1).all())
    return render_template(PracticeAdminTemplates.CURRENT_THESISES.value,
                           area=area, worktype=worktype,
                           list_of_thesises=list_of_thesises)


@login_required
@user_is_staff
def download_materials(area, worktype):
    thesises = (CurrentThesis.query.filter_by(area_id=area.id).filter_by(worktype_id=worktype.id)
                .filter_by(deleted=False).filter_by(status=1).all())

    filename = (get_thesis_type_id_string(worktype.id) + '_'
                + translit(area.area, 'ru', reversed=True).replace(' ', '_') + '.zip')
    full_filename = ARCHIVE_FOLDER + filename

    with ZipFile(full_filename, 'w') as zip_file:
        for thesis in thesises:
            if thesis.text_uri is not None:
                zip_file.write(TEXT_UPLOAD_FOLDER + thesis.text_uri,
                               arcname=thesis.text_uri)
            if thesis.supervisor_review_uri is not None:
                zip_file.write(REVIEW_UPLOAD_FOLDER + thesis.supervisor_review_uri,
                               arcname=thesis.supervisor_review_uri)
            if thesis.reviewer_review_uri is not None:
                zip_file.write(REVIEW_UPLOAD_FOLDER + thesis.reviewer_review_uri,
                               arcname=thesis.reviewer_review_uri)
            if thesis.presentation_uri is not None:
                zip_file.write(PRESENTATION_UPLOAD_FOLDER + thesis.presentation_uri,
                               arcname=thesis.presentation_uri)

    return __send_file_and_remove(full_filename, filename)


def __send_file_and_remove(full_filename, filename):
    return_data = io.BytesIO()
    with open(full_filename, 'rb') as fo:
        return_data.write(fo.read())
    return_data.seek(0)
    os.remove(full_filename)
    return send_file(return_data, mimetype=full_filename, attachment_filename=filename)


@login_required
@user_is_staff
def thesis_admin():
    current_thesis_id = request.args.get('id', type=int)
    if not current_thesis_id:
        return redirect(url_for('index_admin'))
    current_thesis = CurrentThesis.query.filter_by(id=current_thesis_id).first()
    if not current_thesis:
        return redirect(url_for('index_admin'))
    area_id = request.args.get('area_id', type=int)
    worktype_id = request.args.get('worktype_id', type=int)
    if not area_id or not worktype_id:
        return redirect(url_for('choose_worktype_admin', source=index_admin.__name__))
    area = AreasOfStudy.query.filter_by(id=area_id).first()
    worktype = Worktype.query.filter_by(id=worktype_id).first()

    return render_template(PracticeAdminTemplates.THESIS.value, thesis=current_thesis, area=area, worktype=worktype)


@login_required
@user_is_staff
def deadline_admin():
    area_id = request.args.get('area_id', type=int)
    worktype_id = request.args.get('worktype_id', type=int)
    if not area_id or not worktype_id:
        return redirect(url_for('choose_worktype_admin', source=deadline_admin.__name__))
    area = AreasOfStudy.query.filter_by(id=area_id).first()
    worktype = Worktype.query.filter_by(id=worktype_id).first()

    if request.method == "POST":
        worktype_id = request.form.get('worktype', type=int)
        area_id = request.form.get('area', type=int)

        if not area_id:
            flash('Укажите направление.', category='error')
            redirect()
        elif not worktype_id:
            flash('Укажите тип работы!', category='error')
            redirect()
        else:       # Сначала создавать объект, потом брать его из бд и сравнивать с новым
            deadline = Deadline.query.filter_by(worktype_id=worktype_id).filter_by(area_id=area_id).first()
            if not deadline:
                deadline = Deadline()                 # Передавать в конструктор, а не отдельно
                deadline.worktype_id = worktype_id
                deadline.area_id = area_id
                db.session.add(deadline)

            current_thesises = CurrentThesis.query.filter_by(worktype_id=worktype_id).filter_by(area_id=area_id).\
                filter_by(deleted=False).filter_by(status=1).all()

            if request.form.get('choose_topic'):
                new_deadline = datetime.strptime(request.form.get('choose_topic'), "%Y-%m-%dT%H:%M").astimezone(pytz.UTC)
                if not deadline.choose_topic or deadline.choose_topic and deadline.choose_topic.replace(tzinfo=pytz.UTC) != new_deadline:
                    first_word = ""
                    if not deadline.choose_topic:
                        first_word = "Назначен"
                    elif deadline.choose_topic.replace(tzinfo=pytz.UTC) != new_deadline:
                        first_word = "Изменён"

                    deadline.choose_topic = new_deadline
                    for currentThesis in current_thesises:
                        notification = NotificationPractice()
                        notification.recipient_id = currentThesis.author_id
                        notification.content = first_word + " дедлайн на выбор темы для " + \
                                               Worktype.query.filter_by(id=worktype_id).first().type + \
                                               " для направления " + AreasOfStudy.query.filter_by(id=area_id).first().area + \
                                               ": **" + new_deadline.replace(tzinfo=pytz.UTC).astimezone(timezone("Europe/Moscow")).strftime(FORMAT_DATE_TIME) + " МСК**"
                        add_mail_notification(currentThesis.author_id,
                                              "[SE site] " + first_word + " дедлайн на выбор темы",
                                              notification.content.replace('**', ''))

                        db.session.add(notification)

            if request.form.get('submit_work_for_review'):
                new_deadline = datetime.strptime(request.form.get('submit_work_for_review'),
                                                 "%Y-%m-%dT%H:%M").astimezone(pytz.UTC)
                if not deadline.submit_work_for_review or \
                        deadline.submit_work_for_review and deadline.submit_work_for_review.replace(tzinfo=pytz.UTC) != new_deadline:
                    first_word = ""
                    if not deadline.submit_work_for_review:
                        first_word = "Назначен"
                    elif deadline.submit_work_for_review.replace(tzinfo=pytz.UTC) != new_deadline:
                        first_word = "Изменён"

                    deadline.submit_work_for_review = new_deadline
                    for currentThesis in current_thesises:
                        notification = NotificationPractice()
                        notification.recipient_id = currentThesis.author_id
                        notification.content = first_word + " дедлайн на отправку работы для рецензирования для " + \
                                               Worktype.query.filter_by(id=worktype_id).first().type + \
                                               " для направления " + AreasOfStudy.query.filter_by(id=area_id).first().area + \
                                               ": **" + new_deadline.replace(tzinfo=pytz.UTC).astimezone(timezone("Europe/Moscow")).strftime(FORMAT_DATE_TIME) + " МСК**"
                        add_mail_notification(currentThesis.author_id,
                                              "[SE site] " + first_word + " дедлайн на отправку работы на рецензирование",
                                              notification.content.replace('**', ''))

                        db.session.add(notification)

            if request.form.get('upload_reviews'):
                new_deadline = datetime.strptime(request.form.get('upload_reviews'), "%Y-%m-%dT%H:%M").astimezone(pytz.UTC)
                if not deadline.upload_reviews or \
                        deadline.upload_reviews and deadline.upload_reviews.replace(tzinfo=pytz.UTC) != new_deadline:
                    first_word = ""
                    if not deadline.upload_reviews:
                        first_word = "Назначен"
                    elif deadline.upload_reviews.replace(tzinfo=pytz.UTC) != new_deadline:
                        first_word = "Изменён"

                    deadline.upload_reviews = new_deadline
                    for currentThesis in current_thesises:
                        notification = NotificationPractice()
                        notification.recipient_id = currentThesis.author_id
                        notification.content = first_word + " дедлайн на загрузку отзывов для " + \
                                               Worktype.query.filter_by(id=worktype_id).first().type + \
                                               " для направления " + AreasOfStudy.query.filter_by(id=area_id).first().area + \
                                               ": **" + new_deadline.replace(tzinfo=pytz.UTC).astimezone(timezone("Europe/Moscow")).strftime(FORMAT_DATE_TIME) + " МСК**"
                        add_mail_notification(currentThesis.author_id,
                                              "[SE site] " + first_word + " дедлайн на загрузку отзывов",
                                              notification.content.replace('**', ''))

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
                        notification = NotificationPractice()
                        notification.recipient_id = currentThesis.author_id
                        notification.content = first_word + " время предзащиты для " + \
                                               Worktype.query.filter_by(id=worktype_id).first().type + \
                                               " для направления " + AreasOfStudy.query.filter_by(id=area_id).first().area + \
                                               ": **" + new_deadline.replace(tzinfo=pytz.UTC).astimezone(timezone("Europe/Moscow")).strftime(FORMAT_DATE_TIME) + " МСК**"
                        add_mail_notification(currentThesis.author_id,
                                              "[SE site] " + first_word + " время предзащиты",
                                              notification.content.replace('**', ''))
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
                        notification = NotificationPractice()
                        notification.recipient_id = currentThesis.author_id
                        notification.content = first_word + " время защиты для " + \
                                               Worktype.query.filter_by(id=worktype_id).first().type + \
                                               " для направления " + AreasOfStudy.query.filter_by(id=area_id).first().area + \
                                               ": **" + new_deadline.replace(tzinfo=pytz.UTC).astimezone(timezone("Europe/Moscow")).strftime(FORMAT_DATE_TIME) + " МСК**"
                        add_mail_notification(currentThesis.author_id,
                                              "[SE site] " + first_word + " время защиты",
                                              notification.content.replace('**', ''))
                        db.session.add(notification)

            db.session.commit()

    form = DeadlineTemp()

    return render_template(PracticeAdminTemplates.DEADLINE.value, form=form,
                           area=area, worktype=worktype)

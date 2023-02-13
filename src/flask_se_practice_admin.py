# -*- coding: utf-8 -*-

import pytz
from flask import flash, redirect, request, render_template
from datetime import datetime
from pytz import timezone

from flask_se_auth import login_required
from se_forms import DeadlineTemp
from se_models import AreasOfStudy, CurrentThesis, Worktype, NotificationPractice, Deadline, db, add_mail_notification

from templates.practice.admin.templates import PracticeAdminTemplates

FORMAT_DATE_TIME = "%d.%m.%Y %H:%M"


@login_required
def index_admin():
    return render_template(PracticeAdminTemplates.CURRENT_THESISES.value)


@login_required
def deadline_admin():
    form = DeadlineTemp()

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

    form.area.choices.append((0, 'Выберите направление'))
    for area in AreasOfStudy.query.filter(AreasOfStudy.id > 1).order_by('id').all():
        form.area.choices.append((area.id, area.area))

    form.worktype.choices.append((0, 'Выберите тип работы'))
    for worktype in Worktype.query.filter(Worktype.id > 2).order_by('id').all():
        form.worktype.choices.append((worktype.id, worktype.type))

    return render_template(PracticeAdminTemplates.DEADLINE.value, form=form)

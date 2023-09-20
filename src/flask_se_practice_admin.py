"""
   Copyright 2023 Alexander Slugin

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""
# -*- coding: utf-8 -*-

import os
import io
from enum import Enum
from functools import wraps
import pytz
import shutil

from flask import flash, redirect, request, render_template, url_for, send_file, session
from datetime import datetime
from flask_login import current_user
from pytz import timezone
from zipfile import ZipFile
from transliterate import translit

from flask_se_auth import login_required
from se_forms import DeadlineTemp, ChooseCourseAndYear
from se_models import (
    AreasOfStudy,
    CurrentThesis,
    Worktype,
    NotificationPractice,
    Deadline,
    db,
    add_mail_notification,
    Staff,
    Courses,
    Thesis,
)

from flask_se_config import get_thesis_type_id_string
from templates.practice.admin.templates import PracticeAdminTemplates
from templates.notification.templates import NotificationTemplates
from flask_se_practice_yandex_disk import handle_yandex_table
from flask_se_practice_config import (
    TABLE_COLUMNS,
    ARCHIVE_FOLDER,
    TEXT_UPLOAD_FOLDER,
    PRESENTATION_UPLOAD_FOLDER,
    REVIEW_UPLOAD_FOLDER,
    FORMAT_DATE_TIME,
    ARCHIVE_TEXT_FOLDER,
    ARCHIVE_REVIEW_FOLDER,
    ARCHIVE_PRESENTATION_FOLDER,
    get_filename,
    TypeOfFile,
    FOLDER_FOR_TABLE,
)
from flask_se_practice_table import edit_table


class PracticeAdminPage(Enum):
    CURRENT_THESISES = "current_thesises"
    FINISHED_THESISES = "finished_thesises"
    THESIS = "thesis"


def user_is_staff(func):
    @wraps(func)
    def check_user_is_staff_decorator(*args, **kwargs):
        user_staff = Staff.query.filter_by(user_id=current_user.id).first()
        if not user_staff:
            return redirect(url_for("practice_index"))
        return func(*args, **kwargs)

    return check_user_is_staff_decorator


@login_required
@user_is_staff
def choose_area_and_worktype_admin():
    area_id = request.args.get("area_id", type=int)
    worktype_id = request.args.get("worktype_id", type=int)

    previous_page = session.get("previous_page")
    if previous_page == PracticeAdminPage.CURRENT_THESISES.value:
        return redirect(
            url_for("index_admin", area_id=area_id, worktype_id=worktype_id)
        )
    elif previous_page == PracticeAdminPage.FINISHED_THESISES.value:
        return redirect(
            url_for("finished_thesises_admin", area_id=area_id, worktype_id=worktype_id)
        )

    return redirect(url_for("index_admin", area_id=area_id, worktype_id=worktype_id))


@login_required
@user_is_staff
def index_admin():
    area_id = request.args.get("area_id", type=int)
    worktype_id = request.args.get("worktype_id", type=int)
    area = AreasOfStudy.query.filter_by(id=area_id).first()
    worktype = Worktype.query.filter_by(id=worktype_id).first()

    if request.method == "POST":
        if "download_materials_button" in request.form:
            return download_materials(area, worktype)
        if "yandex_button" in request.form or "download_table" in request.form:
            table_name = request.form["table_name"]
            sheet_name = request.form["sheet_name"]
            if table_name is None or table_name == "":
                flash(
                    "Введите название файла для выгрузки на Яндекс Диск"
                    if "yandex_button" in request.form
                    else "Введите название файла для скачивания таблицы с результатами",
                    category="error",
                )
                return redirect(
                    url_for("index_admin", area_id=area.id, worktype_id=worktype.id)
                )

            column_names = {
                "name": request.form.get("user_name_column", ""),
                "how_to_contact": request.form.get("how_to_contact_column", ""),
                "supervisor": request.form.get("supervisor_column", ""),
                "consultant": request.form.get("consultant_column", ""),
                "theme": request.form.get("theme_column", ""),
                "text": request.form.get("text_column", ""),
                "supervisor_review": request.form.get("supervisor_review_column", ""),
                "reviewer_review": request.form.get("reviewer_review_column", ""),
                "code": request.form.get("code_column", ""),
                "committer": request.form.get("committer_column", ""),
                "presentation": request.form.get("presentation_column", ""),
            }
            for value in column_names.values():
                if not value or value == "":
                    flash(
                        "Название столбца таблицы не может быть пустым",
                        category="error",
                    )
                    return redirect(
                        url_for("index_admin", area_id=area.id, worktype_id=worktype.id)
                    )

            if "yandex_button" in request.form:
                return handle_yandex_table(
                    table_name=table_name,
                    sheet_name=sheet_name,
                    area_id=area.id,
                    worktype_id=worktype.id,
                    column_names=column_names,
                )
            else:
                table_filename = table_name.split("/")[-1]
                full_filename = FOLDER_FOR_TABLE + table_filename
                edit_table(
                    path_to_table=full_filename,
                    sheet_name=sheet_name,
                    area_id=area.id,
                    worktype_id=worktype.id,
                    column_names=column_names,
                )
                table = io.BytesIO()
                with open(full_filename, "rb") as fo:
                    table.write(fo.read())
                table.seek(0)
                os.remove(full_filename)
                return send_file(
                    table, mimetype=full_filename, download_name=table_filename
                )

    list_of_thesises = (
        CurrentThesis.query.filter_by(area_id=area_id)
        .filter_by(worktype_id=worktype_id)
        .filter_by(deleted=False)
        .filter_by(status=1)
        .filter(CurrentThesis.title != None)
        .all()
    )

    list_of_areas = (
        AreasOfStudy.query.filter(AreasOfStudy.id > 1).order_by(AreasOfStudy.id).all()
    )
    list_of_work_types = Worktype.query.filter(Worktype.id > 2).all()
    session["previous_page"] = PracticeAdminPage.CURRENT_THESISES.value

    return render_template(
        PracticeAdminTemplates.CURRENT_THESISES.value,
        area=area,
        worktype=worktype,
        list_of_areas=list_of_areas,
        list_of_worktypes=list_of_work_types,
        list_of_thesises=list_of_thesises,
        table_columns=TABLE_COLUMNS,
    )


@login_required
@user_is_staff
def download_materials(area, worktype):
    thesises = (
        CurrentThesis.query.filter_by(area_id=area.id)
        .filter_by(worktype_id=worktype.id)
        .filter_by(deleted=False)
        .filter_by(status=1)
        .all()
    )

    filename = (
        get_thesis_type_id_string(worktype.id)
        + "_"
        + translit(area.area, "ru", reversed=True).replace(" ", "_")
        + ".zip"
    )
    full_filename = ARCHIVE_FOLDER + filename

    with ZipFile(full_filename, "w") as zip_file:
        for thesis in thesises:
            if thesis.text_uri is not None:
                zip_file.write(
                    TEXT_UPLOAD_FOLDER + thesis.text_uri, arcname=thesis.text_uri
                )
            if thesis.supervisor_review_uri is not None:
                zip_file.write(
                    REVIEW_UPLOAD_FOLDER + thesis.supervisor_review_uri,
                    arcname=thesis.supervisor_review_uri,
                )
            if thesis.reviewer_review_uri is not None:
                zip_file.write(
                    REVIEW_UPLOAD_FOLDER + thesis.reviewer_review_uri,
                    arcname=thesis.reviewer_review_uri,
                )
            if thesis.presentation_uri is not None:
                zip_file.write(
                    PRESENTATION_UPLOAD_FOLDER + thesis.presentation_uri,
                    arcname=thesis.presentation_uri,
                )

    return __send_file_and_remove(full_filename, filename)


def __send_file_and_remove(full_filename, filename):
    return_data = io.BytesIO()
    with open(full_filename, "rb") as fo:
        return_data.write(fo.read())
    return_data.seek(0)
    os.remove(full_filename)
    return send_file(return_data, mimetype=full_filename, download_name=filename)


@login_required
@user_is_staff
def thesis_admin():
    current_thesis_id = request.args.get("id", type=int)
    if not current_thesis_id:
        return redirect(url_for("index_admin"))

    current_thesis = CurrentThesis.query.filter_by(id=current_thesis_id).first()
    if not current_thesis:
        return redirect(url_for("index_admin"))

    if request.method == "POST":
        if "submit_notification_button" in request.form:
            if request.form["content"] in {None, ""}:
                flash("Нельзя отправить пустое уведомление!", category="error")
                return redirect(url_for("thesis_staff", id=current_thesis.id))

            mail_notification = render_template(
                NotificationTemplates.NOTIFICATION_FROM_CURATOR.value,
                curator=current_user,
                thesis=current_thesis,
                content=request.form["content"],
            )
            add_mail_notification(
                current_thesis.author_id,
                "[SE site] Уведомление от руководителя практики",
                mail_notification,
            )

            notification_content = (
                f"Руководитель практики {current_user.get_name()} "
                f'отправил Вам уведомление по работе "{current_thesis.title}": '
                f"{request.form['content']}"
            )
            notification = NotificationPractice(
                recipient_id=current_thesis.author_id, content=notification_content
            )
            db.session.add(notification)
            db.session.commit()
            flash("Уведомление отправлено!", category="success")
        elif "submit_edit_title_button" in request.form:
            new_title = request.form["title_input"]
            notification_content = (
                "Руководитель практики изменил название Вашей работы "
                + f'"{current_thesis.title}" на "{new_title}"'
            )
            current_thesis.title = new_title
            add_mail_notification(
                current_thesis.author_id,
                "[SE site] Уведомление от руководителя практики",
                notification_content,
            )
            notification = NotificationPractice(
                recipient_id=current_thesis.author_id, content=notification_content
            )
            db.session.add(notification)
            db.session.commit()
        elif "submit_finish_work_button" in request.form:
            current_thesis.status = 2
            db.session.commit()
        elif "submit_restore_work_button" in request.form:
            current_thesis.status = 1
            db.session.commit()

    list_of_areas = (
        AreasOfStudy.query.filter(AreasOfStudy.id > 1).order_by(AreasOfStudy.id).all()
    )
    list_of_work_types = Worktype.query.filter(Worktype.id > 2).all()
    not_deleted_tasks = [task for task in current_thesis.tasks if not task.deleted]
    session["previous_page"] = PracticeAdminPage.THESIS.value
    return render_template(
        PracticeAdminTemplates.THESIS.value,
        area=current_thesis.area,
        worktype=current_thesis.worktype,
        list_of_areas=list_of_areas,
        list_of_worktypes=list_of_work_types,
        thesis=current_thesis,
        tasks=not_deleted_tasks,
    )


@login_required
@user_is_staff
def archive_thesis():
    current_thesis_id = request.args.get("id", type=int)
    if not current_thesis_id:
        return redirect(url_for("index_admin"))

    current_thesis: CurrentThesis = CurrentThesis.query.filter_by(
        id=current_thesis_id
    ).first()
    if not current_thesis:
        return redirect(url_for("index_admin"))

    if request.method == "POST":
        if "thesis_to_archive_button" in request.form:
            course_id = request.form.get("course", type=int)
            if course_id == 0:
                flash(
                    "Выберите направление обучения (бакалавриат/магистратура)",
                    category="error",
                )
                return redirect(url_for("archive_thesis", id=current_thesis.id))

            text_file = request.files["text"] if "text" in request.files else None
            if not current_thesis.text_uri and not text_file:
                flash(
                    "Загрузите текст работы, чтобы перенести её в архив",
                    category="error",
                )
                return redirect(url_for("archive_thesis", id=current_thesis.id))

            presentation_file = (
                request.files["presentation"]
                if "presentation" in request.files
                else None
            )
            if not current_thesis.presentation_uri and not presentation_file:
                flash(
                    "Загрузите презентацию работы, чтобы перенести её в архив",
                    category="error",
                )
                return redirect(url_for("archive_thesis", id=current_thesis.id))

            supervisor_review_file = (
                request.files["supervisor_review"]
                if "supervisor_review" in request.files
                else None
            )
            if not current_thesis.supervisor_review_uri and not supervisor_review_file:
                flash(
                    "Загрузите отзыв научного руководителя, чтобы перенести работу в архив",
                    category="error",
                )
                return redirect(url_for("archive_thesis", id=current_thesis.id))

            thesis = Thesis()
            thesis.type_id = current_thesis.worktype_id
            thesis.course_id = course_id
            thesis.area_id = current_thesis.area_id
            thesis.name_ru = current_thesis.title
            thesis.author = current_thesis.user.get_name()
            thesis.author_id = current_thesis.author_id
            thesis.supervisor_id = current_thesis.supervisor_id
            thesis.publish_year = request.form.get("publish_year", type=int)

            path_to_archive_text, archive_text_filename = get_filename(
                current_thesis, ARCHIVE_TEXT_FOLDER, TypeOfFile.TEXT.value
            )
            if current_thesis.text_uri:
                shutil.copyfile(
                    TEXT_UPLOAD_FOLDER + current_thesis.text_uri, path_to_archive_text
                )
            else:
                text_file.save(path_to_archive_text)
            thesis.text_uri = archive_text_filename

            path_to_archive_presentation, archive_slides_filename = get_filename(
                current_thesis,
                ARCHIVE_PRESENTATION_FOLDER,
                TypeOfFile.PRESENTATION.value,
            )
            if current_thesis.presentation_uri:
                shutil.copyfile(
                    PRESENTATION_UPLOAD_FOLDER + current_thesis.presentation_uri,
                    path_to_archive_presentation,
                )
            else:
                presentation_file.save(path_to_archive_presentation)
            thesis.presentation_uri = archive_slides_filename

            path_to_archive_super_review, archive_super_review_filename = get_filename(
                current_thesis,
                ARCHIVE_REVIEW_FOLDER,
                TypeOfFile.SUPERVISOR_REVIEW.value,
            )
            if current_thesis.supervisor_review_uri:
                shutil.copyfile(
                    REVIEW_UPLOAD_FOLDER + current_thesis.supervisor_review_uri,
                    path_to_archive_super_review,
                )
            else:
                supervisor_review_file.save(path_to_archive_super_review)
            thesis.supervisor_review_uri = archive_super_review_filename

            path_to_archive_rev_review, archive_rev_review_filename = get_filename(
                current_thesis, ARCHIVE_REVIEW_FOLDER, TypeOfFile.REVIEWER_REVIEW.value
            )
            if current_thesis.reviewer_review_uri:
                shutil.copyfile(
                    REVIEW_UPLOAD_FOLDER + current_thesis.reviewer_review_uri,
                    path_to_archive_rev_review,
                )
            else:
                reviewer_review_file = (
                    request.files["consultant_review"]
                    if "consultant_review" in request.files
                    else None
                )
                if reviewer_review_file not in {None, ""}:
                    reviewer_review_file.save(path_to_archive_rev_review)
                    thesis.reviewer_review_uri = archive_rev_review_filename

            if current_thesis.code_link and current_thesis.code_link.find("http") != -1:
                thesis.source_uri = current_thesis.code_link
            else:
                code_link = request.form.get("code_link", type=str)
                if code_link not in {None, ""} and code_link.find("http") != -1:
                    thesis.source_uri = code_link

            db.session.add(thesis)
            current_thesis.archived = True
            current_thesis.status = 2

            add_mail_notification(
                current_thesis.author_id,
                "[SE site] Ваша работы перенесена в архив практик и ВКР",
                render_template(
                    NotificationTemplates.THESIS_WAS_ARCHIVED_BY_ADMIN.value,
                    curator=current_user,
                    thesis=current_thesis,
                ),
            )
            notification_content = (
                f"Руководитель практики { current_user.get_name() }"
                f' перенёс Вашу работу "{ current_thesis.title }"'
                f" в архив практик и ВКР."
            )
            notification = NotificationPractice(
                recipient_id=current_thesis.author_id, content=notification_content
            )
            db.session.add(notification)
            db.session.commit()
            flash("Работа перенесена в архив!", category="success")
            return redirect(url_for("thesis_admin", id=current_thesis.id))

    list_of_areas = (
        AreasOfStudy.query.filter(AreasOfStudy.id > 1).order_by(AreasOfStudy.id).all()
    )
    list_of_work_types = Worktype.query.filter(Worktype.id > 2).all()
    course_and_year_form = ChooseCourseAndYear()
    course_and_year_form.course.choices.append((0, "Выберите направление"))
    for course in Courses.query.all():
        course_and_year_form.course.choices.append((course.id, course.name))

    return render_template(
        PracticeAdminTemplates.ARCHIVE_THESIS.value,
        thesis=current_thesis,
        area=current_thesis.area,
        worktype=current_thesis.worktype,
        list_of_areas=list_of_areas,
        list_of_worktypes=list_of_work_types,
        form=course_and_year_form,
    )


@login_required
@user_is_staff
def finished_thesises_admin():
    area_id = request.args.get("area_id", type=int)
    worktype_id = request.args.get("worktype_id", type=int)
    area = AreasOfStudy.query.filter_by(id=area_id).first()
    worktype = Worktype.query.filter_by(id=worktype_id).first()

    current_thesises = (
        CurrentThesis.query.filter_by(area_id=area_id)
        .filter_by(worktype_id=worktype_id)
        .filter_by(status=2)
        .filter_by(deleted=False)
        .filter(CurrentThesis.title != None)
        .all()
    )

    list_of_areas = (
        AreasOfStudy.query.filter(AreasOfStudy.id > 1).order_by(AreasOfStudy.id).all()
    )
    list_of_work_types = Worktype.query.filter(Worktype.id > 2).all()
    session["previous_page"] = PracticeAdminPage.FINISHED_THESISES.value
    return render_template(
        PracticeAdminTemplates.FINISHED_THESISES.value,
        area=area,
        worktype=worktype,
        list_of_areas=list_of_areas,
        list_of_worktypes=list_of_work_types,
        thesises=current_thesises,
    )


@login_required
@user_is_staff
def deadline_admin():
    area_id = request.args.get("area_id", type=int)
    worktype_id = request.args.get("worktype_id", type=int)
    area = AreasOfStudy.query.filter_by(id=area_id).first()
    worktype = Worktype.query.filter_by(id=worktype_id).first()

    if request.method == "POST":
        worktype_id = request.form.get("worktype", type=int)
        area_id = request.form.get("area", type=int)

        if not area_id:
            flash("Укажите направление.", category="error")
            # redirect()
        elif not worktype_id:
            flash("Укажите тип работы!", category="error")
            # redirect()
        else:  # Сначала создавать объект, потом брать его из бд и сравнивать с новым
            deadline = (
                Deadline.query.filter_by(worktype_id=worktype_id)
                .filter_by(area_id=area_id)
                .first()
            )
            if not deadline:
                deadline = Deadline()  # Передавать в конструктор, а не отдельно
                deadline.worktype_id = worktype_id
                deadline.area_id = area_id
                db.session.add(deadline)

            current_thesises = (
                CurrentThesis.query.filter_by(worktype_id=worktype_id)
                .filter_by(area_id=area_id)
                .filter_by(deleted=False)
                .filter_by(status=1)
                .all()
            )

            if request.form.get("choose_topic"):
                new_deadline = datetime.strptime(
                    request.form.get("choose_topic"), "%Y-%m-%dT%H:%M"
                ).astimezone(pytz.UTC)
                if (
                    not deadline.choose_topic
                    or deadline.choose_topic
                    and deadline.choose_topic.replace(tzinfo=pytz.UTC) != new_deadline
                ):
                    first_word = ""
                    if not deadline.choose_topic:
                        first_word = "Назначен"
                    elif deadline.choose_topic.replace(tzinfo=pytz.UTC) != new_deadline:
                        first_word = "Изменён"

                    deadline.choose_topic = new_deadline
                    for currentThesis in current_thesises:
                        notification = NotificationPractice()
                        notification.recipient_id = currentThesis.author_id
                        notification.content = (
                            first_word
                            + " дедлайн на выбор темы для "
                            + Worktype.query.filter_by(id=worktype_id).first().type
                            + " для направления "
                            + AreasOfStudy.query.filter_by(id=area_id).first().area
                            + ": **"
                            + new_deadline.replace(tzinfo=pytz.UTC)
                            .astimezone(timezone("Europe/Moscow"))
                            .strftime(FORMAT_DATE_TIME)
                            + " МСК**"
                        )
                        add_mail_notification(
                            currentThesis.author_id,
                            "[SE site] " + first_word + " дедлайн на выбор темы",
                            notification.content.replace("**", ""),
                        )

                        db.session.add(notification)

            if request.form.get("submit_work_for_review"):
                new_deadline = datetime.strptime(
                    request.form.get("submit_work_for_review"), "%Y-%m-%dT%H:%M"
                ).astimezone(pytz.UTC)
                if (
                    not deadline.submit_work_for_review
                    or deadline.submit_work_for_review
                    and deadline.submit_work_for_review.replace(tzinfo=pytz.UTC)
                    != new_deadline
                ):
                    first_word = ""
                    if not deadline.submit_work_for_review:
                        first_word = "Назначен"
                    elif (
                        deadline.submit_work_for_review.replace(tzinfo=pytz.UTC)
                        != new_deadline
                    ):
                        first_word = "Изменён"

                    deadline.submit_work_for_review = new_deadline
                    for currentThesis in current_thesises:
                        notification = NotificationPractice()
                        notification.recipient_id = currentThesis.author_id
                        notification.content = (
                            first_word
                            + " дедлайн на отправку работы для рецензирования для "
                            + Worktype.query.filter_by(id=worktype_id).first().type
                            + " для направления "
                            + AreasOfStudy.query.filter_by(id=area_id).first().area
                            + ": **"
                            + new_deadline.replace(tzinfo=pytz.UTC)
                            .astimezone(timezone("Europe/Moscow"))
                            .strftime(FORMAT_DATE_TIME)
                            + " МСК**"
                        )
                        add_mail_notification(
                            currentThesis.author_id,
                            "[SE site] "
                            + first_word
                            + " дедлайн на отправку работы на рецензирование",
                            notification.content.replace("**", ""),
                        )

                        db.session.add(notification)

            if request.form.get("upload_reviews"):
                new_deadline = datetime.strptime(
                    request.form.get("upload_reviews"), "%Y-%m-%dT%H:%M"
                ).astimezone(pytz.UTC)
                if (
                    not deadline.upload_reviews
                    or deadline.upload_reviews
                    and deadline.upload_reviews.replace(tzinfo=pytz.UTC) != new_deadline
                ):
                    first_word = ""
                    if not deadline.upload_reviews:
                        first_word = "Назначен"
                    elif (
                        deadline.upload_reviews.replace(tzinfo=pytz.UTC) != new_deadline
                    ):
                        first_word = "Изменён"

                    deadline.upload_reviews = new_deadline
                    for currentThesis in current_thesises:
                        notification = NotificationPractice()
                        notification.recipient_id = currentThesis.author_id
                        notification.content = (
                            first_word
                            + " дедлайн на загрузку отзывов для "
                            + Worktype.query.filter_by(id=worktype_id).first().type
                            + " для направления "
                            + AreasOfStudy.query.filter_by(id=area_id).first().area
                            + ": **"
                            + new_deadline.replace(tzinfo=pytz.UTC)
                            .astimezone(timezone("Europe/Moscow"))
                            .strftime(FORMAT_DATE_TIME)
                            + " МСК**"
                        )
                        add_mail_notification(
                            currentThesis.author_id,
                            "[SE site] " + first_word + " дедлайн на загрузку отзывов",
                            notification.content.replace("**", ""),
                        )

                        db.session.add(notification)

            if request.form.get("pre_defense"):
                new_deadline = datetime.strptime(
                    request.form.get("pre_defense"), "%Y-%m-%dT%H:%M"
                ).astimezone(pytz.UTC)
                if (
                    not deadline.pre_defense
                    or deadline.pre_defense
                    and deadline.pre_defense.replace(tzinfo=pytz.UTC) != new_deadline
                ):
                    first_word = ""
                    if not deadline.pre_defense:
                        first_word = "Назначено"
                    elif deadline.pre_defense.replace(tzinfo=pytz.UTC) != new_deadline:
                        first_word = "Изменено"

                    deadline.pre_defense = new_deadline
                    for currentThesis in current_thesises:
                        notification = NotificationPractice()
                        notification.recipient_id = currentThesis.author_id
                        notification.content = (
                            first_word
                            + " время предзащиты для "
                            + Worktype.query.filter_by(id=worktype_id).first().type
                            + " для направления "
                            + AreasOfStudy.query.filter_by(id=area_id).first().area
                            + ": **"
                            + new_deadline.replace(tzinfo=pytz.UTC)
                            .astimezone(timezone("Europe/Moscow"))
                            .strftime(FORMAT_DATE_TIME)
                            + " МСК**"
                        )
                        add_mail_notification(
                            currentThesis.author_id,
                            "[SE site] " + first_word + " время предзащиты",
                            notification.content.replace("**", ""),
                        )
                        db.session.add(notification)

            if request.form.get("defense"):
                new_deadline = datetime.strptime(
                    request.form.get("defense"), "%Y-%m-%dT%H:%M"
                ).astimezone(pytz.UTC)
                if (
                    not deadline.defense
                    or deadline.defense
                    and deadline.defense.replace(tzinfo=pytz.UTC) != new_deadline
                ):
                    first_word = ""
                    if not deadline.defense:
                        first_word = "Назначено"
                    elif deadline.defense.replace(tzinfo=pytz.UTC) != new_deadline:
                        first_word = "Изменено"

                    deadline.defense = new_deadline
                    for currentThesis in current_thesises:
                        notification = NotificationPractice()
                        notification.recipient_id = currentThesis.author_id
                        notification.content = (
                            first_word
                            + " время защиты для "
                            + Worktype.query.filter_by(id=worktype_id).first().type
                            + " для направления "
                            + AreasOfStudy.query.filter_by(id=area_id).first().area
                            + ": **"
                            + new_deadline.replace(tzinfo=pytz.UTC)
                            .astimezone(timezone("Europe/Moscow"))
                            .strftime(FORMAT_DATE_TIME)
                            + " МСК**"
                        )
                        add_mail_notification(
                            currentThesis.author_id,
                            "[SE site] " + first_word + " время защиты",
                            notification.content.replace("**", ""),
                        )
                        db.session.add(notification)

            db.session.commit()

    form = DeadlineTemp()

    return render_template(
        PracticeAdminTemplates.DEADLINE.value, form=form, area=area, worktype=worktype
    )

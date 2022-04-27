# -*- coding: utf-8 -*-

import os
from datetime import date

from flask import flash, redirect, request, render_template, url_for
from flask_login import current_user
from transliterate import translit

from flask_se_config import secure_filename, get_thesis_type_id_string
from flask_se_auth import login_required
from se_forms import AddThesisOnReview, ThesisReviewFilter, EditThesisOnReview
from se_review_forms import ReviewForm
from se_models import db, Thesis, Worktype, AreasOfStudy, Staff, ThesisReview


# Global variables
UPLOAD_FOLDER = 'static/thesis/onreview/'
ALLOWED_EXTENSIONS = {'pdf'}
REVIEW_ROLE_LEVEL = 3


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def thesis_review_index():

    user = current_user
    form = ThesisReviewFilter()

    form.status.choices = [(4, 'Все статусы'), (1, 'Требуется рецензия'), (2, 'На рецензии'),
                               (3, 'Требуется доработка'), (0, 'Работа зачтена')]
    form.worktype.choices.append((0, 'Все типы'))

    for type in Worktype.query.filter(Worktype.id > 1).distinct().all():
        form.worktype.choices.append((type.id, type.type))

    form.worktype.choices.sort(key=lambda tup: tup[0])

    for area in AreasOfStudy.query.distinct().all():
        form.areasofstudy.choices.append((area.id, area.area))

    form.areasofstudy.choices.sort(key=lambda tup: tup[0])

    thesis = Thesis.query.filter(Thesis.temporary == True).filter(Thesis.review_status >= 0).all()
    return render_template('thesis_review/index.html', review_filter=form, thesis=thesis, user=user)


@login_required
def submit_thesis_on_review():

    user = current_user
    form = AddThesisOnReview()

    if request.method == "POST":
        title = request.form.get('title').strip()
        author = request.form.get('author').strip()
        worktype = request.form.get('worktype', type=int)
        course = request.form.get('course', type=int)

        if not title:
            flash ("Укажите название вашей работы", 'error')
            return redirect(request.url)

        if not author:
            flash ("Укажите ФИО автора работы", 'error')
            return redirect(request.url)

        if worktype <= 0 or worktype > Worktype.query.distinct().count():
            flash ("Укажите тип работы", 'error')
            return redirect(request.url)

        if course <= 0 or course > AreasOfStudy.query.distinct().count():
            flash ("Укажите направление вашего обучения", 'error')
            return redirect(request.url)

        # check if the post request has the file part
        if 'thesis' not in request.files:
            flash('Вы не загрузили файл с работой', 'error')
            return redirect(request.url)

        file = request.files['thesis']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('Укажите файл с вашей работой для загрузки', 'error')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            author_en = translit(author, 'ru', reversed=True)
            author_en = author_en.replace(" ", "_")
            thesis_filename = author_en
            thesis_filename = thesis_filename + '_' + get_thesis_type_id_string(worktype)

            todays_date = date.today()
            thesis_filename = thesis_filename + '_' + str(todays_date.year) + '_text'
            thesis_filename_with_ext = thesis_filename + '.pdf'

            full_thesis_filename = os.path.join(UPLOAD_FOLDER + "/" + thesis_filename_with_ext)

            # Check if file already exist
            if os.path.isfile(full_thesis_filename):
                thesis_filename = thesis_filename + '_' + str(os.urandom(8).hex())
                thesis_filename_with_ext = thesis_filename + '.pdf'
                full_thesis_filename = os.path.join(UPLOAD_FOLDER + "/" + thesis_filename_with_ext)

            file.save(full_thesis_filename)

            # Add to DB
            thesis = Thesis(name_ru=title, text_uri=thesis_filename_with_ext, author=author, author_id=user.id,
                            publish_year=str(todays_date.year),
                            type_id=worktype, course_id=course, temporary=True, review_status=1)
            db.session.add(thesis)
            db.session.commit()

            return redirect(url_for('thesis_review_index'))
        else:
            flash("Текст работы должен быть в формате .PDF", 'error')
            return redirect(request.url)

    form.worktype.choices.append((0, "Выберите тип вашей работы"))
    form.course.choices.append((0, "Выберите направление, по которому вы обучаетесь"))

    for type in Worktype.query.filter(Worktype.id>1).distinct().all():
        form.worktype.choices.append((type.id, type.type))

    form.worktype.choices.sort(key=lambda tup: tup[0])

    for area in AreasOfStudy.query.filter(AreasOfStudy.id>1).distinct().all():
        form.course.choices.append((area.id, area.area))

    form.course.choices.sort(key=lambda tup: tup[0])

    return render_template('thesis_review/submit.html', filter=form, user=user)


@login_required
def edit_thesis_on_review():

    user = current_user
    thesis_review_id = request.args.get('thesis_review_id', type=int)

    if not thesis_review_id:
        return redirect(url_for('thesis_review_index'))

    thesis_review = Thesis.query.filter_by(id=thesis_review_id).first_or_404()

    if thesis_review.author_id != user.id:
        return redirect(url_for('thesis_review_index'))

    if request.method == "POST":
        title = request.form.get('name_ru', type=str)
        author = request.form.get('author', type=str)
        worktype = request.form.get('type', type=int)
        course = request.form.get('course', type=int)

        if not title:
            flash("Укажите название вашей работы", 'error')
            return redirect(request.url)

        if not author:
            flash("Укажите ФИО автора работы", 'error')
            return redirect(request.url)

        title = title.strip()
        author = author.strip()

        if worktype <= 0 or worktype > Worktype.query.distinct().count():
            flash("Укажите тип работы", 'error')
            return redirect(request.url)

        if course <= 0 or course > AreasOfStudy.query.distinct().count():
            flash("Укажите направление вашего обучения", 'error')
            return redirect(request.url)

        thesis_review.name_ru = title
        thesis_review.author = author
        thesis_review.type_id = worktype
        thesis_review.course_id = course

        # check if the post request has the file part
        if 'thesis' in request.files:

            full_thesis_filename = ""

            file = request.files['thesis']
            # If the user does not select a file, the browser submits an
            # empty file without a filename.
            #
            if file.filename != '':

                if file and allowed_file(file.filename):
                    author_en = translit(author, 'ru', reversed=True)
                    author_en = author_en.replace(" ", "_")
                    thesis_filename = author_en
                    thesis_filename = thesis_filename + '_' + get_thesis_type_id_string(worktype)

                    todays_date = date.today()
                    thesis_filename = thesis_filename + '_' + str(todays_date.year) + '_text'
                    thesis_filename_with_ext = thesis_filename + '.pdf'

                    full_thesis_filename = os.path.join(UPLOAD_FOLDER + "/" + thesis_filename_with_ext)

                    # Check if file already exist
                    if os.path.isfile(full_thesis_filename):
                        thesis_filename = thesis_filename + '_' + str(os.urandom(8).hex())
                        thesis_filename_with_ext = thesis_filename + '.pdf'
                        full_thesis_filename = os.path.join(UPLOAD_FOLDER + "/" + thesis_filename_with_ext)

                    file.save(full_thesis_filename)
                    thesis_review.text_uri = thesis_filename_with_ext
                else:
                    flash("Текст работы должен быть в формате .PDF", 'error')
                    return redirect(request.url)

        db.session.commit()
        return redirect(url_for('thesis_review_index'))

    edit_thesis_onreview = EditThesisOnReview()
    edit_thesis_onreview.type.choices = [(g.id, g.type) for g in
                                             Worktype.query.filter(Worktype.id > 1).order_by('id')]
    edit_thesis_onreview.course.choices = [(g.id, g.area) for g in
                                             AreasOfStudy.query.filter(AreasOfStudy.id > 1).order_by('id')]

    edit_thesis_onreview.type.default = int(thesis_review.type_id)
    edit_thesis_onreview.course.default = int(thesis_review.course_id)
    edit_thesis_onreview.process(name_ru=thesis_review.name_ru, author=thesis_review.author)

    return render_template('thesis_review/edit.html', form=edit_thesis_onreview, user=user, thesis=thesis_review)

@login_required
def delete_thesis_on_review():

    user = current_user
    thesis_id = request.args.get('thesis_review_id', type=int)

    if not thesis_id:
        return redirect(url_for('thesis_review_index'))

    thesis = Thesis.query.filter_by(id=thesis_id).first_or_404()

    if thesis.author_id != current_user.id:
        return redirect(url_for('thesis_review_index'))

    db.session.delete(thesis)
    db.session.commit()

    return redirect(url_for('thesis_review_index'))


@login_required
def review_thesis_on_review():

    user = current_user
    user_staff = Staff.query.filter_by(user_id=user.id).first_or_404()
    thesis_id = request.args.get('thesis_review_id', type=int)
    set_to_review = request.args.get('set_to_review', type=int, default=0)

    if not user_staff:
        return redirect(url_for('thesis_review_index'))

    if not thesis_id:
        return redirect(url_for('thesis_review_index'))

    thesis = Thesis.query.filter_by(id=thesis_id).first_or_404()

    # Check if this users thesis.
    # User can't review it's own thesis.
    if thesis.author_id == user.id:
        return redirect(url_for('thesis_review_index'))

    # Check if user has a persmission
    if user.role < REVIEW_ROLE_LEVEL:
        return redirect(url_for('thesis_review_index'))

    # Ok, we have thesis and user permission.
    # First, ask users about review and set it
    if (thesis.review_status == 1) and (set_to_review == 0):
        return render_template('thesis_review/first_time_review.html', thesis=thesis)

    # Set review_status to 2 (On review)
    # Set reviewer_id to user.id
    if (thesis.review_status == 1) and (set_to_review != 0):
        thesis.review_status = 2
        thesis.reviewer_id = user_staff.id
        db.session.commit()

    review_form = ReviewForm()
    return render_template('thesis_review/review.html', thesis=thesis, user=user, review_form=review_form)


@login_required
def review_submit_review():

    user = current_user
    user_staff = Staff.query.filter_by(user_id=user.id).first_or_404()
    thesis_id = request.args.get('thesis_review_id', type=int)

    if request.method != "POST":
        flash("Неверный метод, разрешается только метод POST", 'error')
        return redirect(url_for('thesis_review_index'))

    if not user_staff:
        flash("Вы не состоите в группе преподавателей", 'error')
        return redirect(url_for('thesis_review_index'))

    if not thesis_id:
        flash("Не указан идентификатор работы", 'error')
        return redirect(url_for('thesis_review_index'))

    thesis = Thesis.query.filter_by(id=thesis_id).first_or_404()

    # Check if this users thesis.
    # User can't review it's own thesis.
    if thesis.author_id == user.id:
        flash("Вы не можете рецензировать свою собственную работу", 'error')
        return redirect(url_for('thesis_review_index'))

    # Check if user has a permission
    if user.role < REVIEW_ROLE_LEVEL:
        flash("У вас недостаточно прав для рецензирования", 'error')
        return redirect(url_for('thesis_review_index'))

    # Only status == 2 allow us to review this thesis.
    if thesis.review_status != 2:
        flash("Работа не находиться на рецензировании", 'error')
        return redirect (url_for('thesis_review_index'))

    # Ok, we can read the review form
    try:
        o1 = request.form['review_o1_radio_switcher']
        o1_comment = request.form['review_o1_comment']
        o2 = request.form['review_o2_radio_switcher']
        o2_comment = request.form['review_o2_comment']
        t1 = request.form['review_t1_radio_switcher']
        t1_comment = request.form['review_t1_comment']
        t2 = request.form['review_t2_radio_switcher']
        t2_comment = request.form['review_t2_comment']
        p1 = request.form['review_p1_radio_switcher']
        p1_comment = request.form['review_t2_comment']
        p2 = request.form['review_p2_radio_switcher']
        p2_comment = request.form['review_t2_comment']

        review_overall_comment = request.form['review_overall_comment']
        verdict = request.form['review_verdict_radio_switcher']

    except KeyError:
        flash("В рецензии есть пропущенные вопросы. Нужно ответить на все вопросы, поля с комментариями являются опциональными.", 'error')
        return redirect(url_for('review_thesis_on_review', thesis_review_id=thesis_id ))

    review = ThesisReview(thesis_id=thesis.id, o1=o1, o1_comment=o1_comment,
                          o2=o2, o2_comment=o2_comment, t1=t1, t1_comment=t1_comment,
                          t2=t2, t2_comment=t2_comment, p1=p1, p1_comment=p1_comment,
                          p2=p2, p2_comment=p2_comment, verdict=verdict,
                          overall_comment=review_overall_comment)

    # Review status = 0 (success)
    # Review status = 3 (Need to be fixed)
    if verdict:
        thesis.review_status = 0
    else:
        thesis.review_status = 3

    db.session.add(review)
    db.session.commit()

    return redirect(url_for('thesis_review_index'))


@login_required
def review_result_thesis_on_review():

    user = current_user
    thesis_id = request.args.get('thesis_review_id', type=int)

    if not thesis_id:
        flash("Не указан идентификатор работы", 'error')
        return redirect(url_for('thesis_review_index'))

    thesis = Thesis.query.filter_by(id=thesis_id).first_or_404()
    review = ThesisReview.query.filter_by(thesis_id=thesis_id).first_or_404()

    #if thesis.author_id != user.id:
    #    flash("Вы не можете просматривать рецензию на чужую работу", 'error')
    #    return redirect(url_for('thesis_review_index'))

    if (thesis.review_status == 1) or (thesis.review_status == 2):
        flash("Рецензия по данной работе не завершена", 'error')
        return redirect (url_for('thesis_review_index'))

    review_form = ReviewForm(review_o1_radio_switcher=review.o1,
                             review_o1_comment=review.o1_comment,
                             review_o2_radio_switcher=review.o2,
                             review_o2_comment=review.o2_comment,
                             review_t1_radio_switcher=review.t1,
                             review_t1_comment=review.t1_comment,
                             review_t2_radio_switcher=review.t2,
                             review_t2_comment=review.t2_comment,
                             review_p1_radio_switcher=review.p1,
                             review_p1_comment=review.p1_comment,
                             review_p2_radio_switcher=review.p2,
                             review_p2_comment=review.p2_comment,
                             review_overall_comment=review.overall_comment,
                             review_verdict_radio_switcher=review.verdict)

    return render_template('thesis_review/result_review.html', thesis=thesis, user=user, review_form=review_form)

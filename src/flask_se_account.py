# -*- coding: utf-8 -*-


from flask import flash, redirect, request, render_template, url_for
from flask_login import current_user

from flask_se_auth import login_required
from se_forms import CurrentCourseArea
from se_models import AreasOfStudy, Users, CurrentThesis
from se_internship_forms import AddInternship, InternshipsFilter
from se_models import db, Internships, InternshipFormat, InternshipCompany


@login_required
def account_profile():
    user = current_user
    return render_template('account/profile.html', user=user)


@login_required
def submit_course_area():
    user = current_user
    form = CurrentCourseArea()
    course = form.course

    if request.method == "POST":
        currentarea = request.form.get('area', type=str)
        course = request.form.get('course', type=int)
        new_thesis = CurrentThesis()
        new_thesis.area = currentarea
        new_thesis.course = course
        new_thesis.title = "None"
        new_thesis.user_id = user.id

        db.session.add(new_thesis)
        db.session.commit()

    for area in AreasOfStudy.query.filter(AreasOfStudy.id > 1).distinct().all():
        form.area.choices.append(area.area)

    form.area.choices.sort(key=lambda tup: tup[0])

    for course in range(2, 7):
        form.course.choices.append(course)

    form.fname = Users.query.filter(Users.id == user.id).distinct().first().first_name
    form.mname = Users.query.filter(Users.id == user.id).distinct().first().middle_name
    form.lname = Users.query.filter(Users.id == user.id).distinct().first().last_name

    return render_template('account/profile.html', review_filter=form, user=user, form=form)
'''
@login_required
def connect_db_course_area():
    user = current_user
    thesis_review_id = request.args.get('thesis_review_id', type=int)

    if not thesis_review_id:
        return redirect(url_for('thesis_review_index'))

    thesis_review = ThesisOnReview.query.filter_by(id=thesis_review_id).first_or_404()

    if thesis_review.author_id != user.id:
        return redirect(url_for('thesis_review_index'))

    if request.method == "POST":
        title = request.form.get('name_ru', type=str)
        worktype = request.form.get('type', type=int)
        area = request.form.get('area', type=int)

        if not title:
            flash("Укажите название вашей работы", 'error')
            return redirect(request.url)

        title = title.strip()
        author = thesis_review.author.get_name()

        if worktype <= 0 or worktype > ThesisOnReviewWorktype.query.distinct().count():
            flash("Укажите тип работы", 'error')
            return redirect(request.url)

        if area <= 0 or area > AreasOfStudy.query.distinct().count():
            flash("Укажите направление вашего обучения", 'error')
            return redirect(request.url)

        thesis_review.name_ru = title
        thesis_review.author_id = user.id
        thesis_review.thesis_on_review_type_id = int(worktype)
        thesis_review.area_id = int(area)

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

        thesis_review.review_status = 1
        db.session.commit()
        return redirect(url_for('thesis_review_index'))

    edit_thesis_onreview = EditThesisOnReview()
    edit_thesis_onreview.type.choices = [(g.id, g.type) for g in
                                             ThesisOnReviewWorktype.query.filter(ThesisOnReviewWorktype.id > 1).order_by('id')]
    edit_thesis_onreview.area.choices = [(g.id, g.area) for g in
                                             AreasOfStudy.query.filter(AreasOfStudy.id > 1).order_by('id')]

    edit_thesis_onreview.type.default = int(thesis_review.thesis_on_review_type_id)
    edit_thesis_onreview.area.default = int(thesis_review.area_id)
    edit_thesis_onreview.process(name_ru=thesis_review.name_ru,
                                 area=int(thesis_review.area_id),
                                 type=thesis_review.thesis_on_review_type_id,
                                 author=thesis_review.author.get_name())

    return render_template('thesis_review/edit.html', form=edit_thesis_onreview, user=user, thesis=thesis_review)
'''
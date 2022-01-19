# -*- coding: utf-8 -*-

import json
import logging
import os
from os.path import splitext
from urllib.parse import urlparse

from flask import render_template, request, jsonify, redirect, url_for
from transliterate import translit

from flask_se_config import SECRET_KEY_THESIS
from se_forms import ThesisFilter
from se_models import db, Staff, Users, Thesis, Worktype, Courses

log = logging.getLogger('flask_se.sub')


def theses_search():

    filter = ThesisFilter()

    for sid in Thesis.query.with_entities(Thesis.type_id).distinct().all():
        type = Worktype.query.filter_by(id=sid[0]).first()

        filter.worktype.choices.append((sid[0], type.type))
        filter.worktype.choices.sort(key=lambda tup: tup[1])

    for sid in Thesis.query.with_entities(Thesis.course_id).distinct().all():
        course = Courses.query.filter_by(id=sid[0]).first()

        filter.course.choices.append((sid[0], course.name))
        filter.course.choices.sort(key=lambda tup: tup[1])

    dates = [theses.publish_year for theses in Thesis.query.filter(Thesis.temporary == False).with_entities(Thesis.publish_year).distinct()]
    dates.sort(reverse=True)
    filter.startdate.choices = dates
    filter.enddate.choices = dates

    for sid in Thesis.query.with_entities(Thesis.supervisor_id).distinct().all():
        staff = Staff.query.filter_by(id=sid[0]).first()
        last_name = ""
        initials = ""

        if staff.user.last_name:
            last_name = staff.user.last_name

        if staff.user.first_name:
            initials = initials + staff.user.first_name[0] + "."

        if staff.user.middle_name:
            initials = initials + staff.user.middle_name[0] + "."

        filter.supervisor.choices.append((sid[0], last_name + " " + initials))
        filter.supervisor.choices.sort(key=lambda tup: tup[1])

    filter.supervisor.choices.insert(0, (0, "Все"))
    filter.course.choices.insert(0, (0, "Все"))
    filter.worktype.choices.insert(0, (0, "Все"))

    return render_template('theses.html', filter=filter)


def fetch_theses():

    worktype = request.args.get('worktype', default = 1, type = int)
    page = request.args.get('page', default=1, type=int)
    supervisor = request.args.get('supervisor', default=0, type=int)
    course = request.args.get('course', default=0, type=int)

    dates = [theses.publish_year for theses in Thesis.query.filter(Thesis.temporary == False).with_entities(Thesis.publish_year).distinct()]
    dates.sort(reverse=True)

    if dates:
        startdate = request.args.get('startdate', default=dates[-1], type=int)
        enddate = request.args.get('enddate', default=dates[0], type=int)
    else:
        startdate = 2021
        enddate = 2021

    # Check if end date less than start date
    if enddate < startdate:
        enddate = startdate

    records = Thesis.query.filter(Thesis.temporary == False).filter(Thesis.publish_year >= startdate).filter(Thesis.publish_year <= enddate).order_by(Thesis.publish_year.desc())

    if course:
        # Check if course exists
        records = records.filter(Thesis.course_id == course)

    if supervisor:

        # Check if supervisor exists
        print(supervisor)
        ids = Thesis.query.with_entities(Thesis.supervisor_id).distinct().all()
        print(ids)
        if [item for item in ids if item[0] == supervisor]:
            print (456)
            records = records.filter(Thesis.supervisor_id == supervisor)
        else:
            supervisor = 0

    if worktype > 1:
        records = records.filter_by(type_id=worktype).paginate(per_page=10, page=page, error_out=False)
    else:
        records = records.paginate(per_page=10, page=page, error_out=False)

    if len(records.items):
        return render_template('fetch_theses.html', theses=records, worktype=worktype, course=course,
                               startdate=startdate, enddate=enddate, supervisor=supervisor)
    else:
        return render_template('fetch_theses_blank.html')


def post_theses():

    error_status = 500
    success_status = 0
    thesis_text = None
    presentation = None
    supervisor_review = None
    reviewer_review = None
    thesis_info = None
    source_uri = None

    presentation_filename = None
    supervisor_review_filename = None
    reviewer_review_filename = None

    type_id_string = ['', 'Bachelor_Report', 'Bachelor_Thesis', 'Master_Thesis']

    if 'thesis_text' in request.files:
        thesis_text = request.files['thesis_text']

    if 'presentation' in request.files:
        presentation = request.files['presentation']

    if 'supervisor_review' in request.files:
        supervisor_review = request.files['supervisor_review']

    if 'reviewer_review' in request.files:
        reviewer_review = request.files['reviewer_review']

    if 'thesis_info' in request.files:
        thesis_info = json.load(request.files['thesis_info'])

    if not thesis_text:
        return jsonify(
            status=error_status,
            string='No thesis text found.'
        )

    if not thesis_info:
        return jsonify(
            status=error_status,
            string='No thesis_info found.'
        )

    try:
        name_ru = thesis_info['name_ru']
        secret_key = thesis_info['secret_key']
        type_id = thesis_info['type_id']
        course_id = thesis_info['course_id']
        author = thesis_info['author']
        supervisor = thesis_info['supervisor']
        publish_year = thesis_info['publish_year']
    except KeyError as e:
        return jsonify(
            status=error_status,
            string='Key ' + str(e) + ' not found'
        )

    if secret_key != SECRET_KEY_THESIS:
        return jsonify(
            status=error_status,
            string='Invalid secret key: ' + str(secret_key)
        )

    if 'source_uri' in thesis_info:
        source_uri = thesis_info['source_uri']

    if type_id < 2 or type_id > len(type_id_string):
        return jsonify(
            status=error_status,
            string='Wrong type_id: ' + str(type_id)
        )

    if course_id < 1 or course_id > 7:
        return jsonify(
            status=error_status,
            string='Wrong course_id: ' + str(course_id)
        )

    # Try to get SuperVisor Id
    q = Users.query.filter_by(last_name=supervisor).first()
    if q:
        r = Staff.query.filter_by(user_id=q.id).first()
        supervisor_id = r.id
    else:
        return jsonify(
            status=error_status,
            string='Can\'t find supervisor: ' + str(supervisor)
        )

    author_en = translit(author, 'ru', reversed=True)
    author_en = author_en.replace(" ", "_")
    thesis_filename = author_en
    thesis_filename = thesis_filename + '_' + type_id_string[type_id-1]
    thesis_filename = thesis_filename + '_' + str(publish_year) + '_text'

    path = urlparse(thesis_text.filename).path
    extension = splitext(path)[1]
    thesis_filename = thesis_filename + extension

    # Before we going on, check if this thesis already exists?
    records = Thesis.query.filter_by(text_uri=thesis_filename)
    if records.count():
        return jsonify(
            status=error_status,
            string='Work already exists: ' + str(thesis_filename)
        )

    # Save file to TMP
    thesis_text.save(os.path.join('./static/tmp/texts/', thesis_filename))

    if presentation:
        presentation_filename = author_en
        presentation_filename = presentation_filename + '_' + type_id_string[type_id-1]
        presentation_filename = presentation_filename + '_' + str(publish_year) + '_slides'

        path = urlparse(presentation.filename).path
        extension = splitext(path)[1]
        presentation_filename = presentation_filename + extension

        presentation.save(os.path.join('./static/tmp/slides/', presentation_filename))

    if supervisor_review:
        supervisor_review_filename = author_en
        supervisor_review_filename = supervisor_review_filename + '_' + type_id_string[type_id-1]
        supervisor_review_filename = supervisor_review_filename + '_' + str(publish_year) + '_supervisor_review'

        path = urlparse(supervisor_review.filename).path
        extension = splitext(path)[1]
        supervisor_review_filename = supervisor_review_filename + extension

        supervisor_review.save(os.path.join('./static/tmp/reviews/', supervisor_review_filename))

    if reviewer_review:
        reviewer_review_filename = author_en
        reviewer_review_filename = reviewer_review_filename + '_' + type_id_string[type_id-1]
        reviewer_review_filename = reviewer_review_filename + '_' + str(publish_year) + '_reviewer_review'

        path = urlparse(reviewer_review.filename).path
        extension = splitext(path)[1]
        reviewer_review_filename = reviewer_review_filename + extension

        reviewer_review.save(os.path.join('./static/tmp/reviews/', reviewer_review_filename))

    if source_uri:
        t = Thesis(name_ru=name_ru, text_uri=thesis_filename,
                   presentation_uri=presentation_filename,
                   supervisor_review_uri=supervisor_review_filename, reviewer_review_uri=reviewer_review_filename,
                   author=author, supervisor_id=supervisor_id, reviewer_id=2,
                   publish_year=publish_year, type_id=type_id, course_id=course_id, source_uri=source_uri,
                   temporary=True)
    else:
        t = Thesis(name_ru=name_ru, text_uri=thesis_filename,
                   presentation_uri=presentation_filename,
                   supervisor_review_uri=supervisor_review_filename, reviewer_review_uri=reviewer_review_filename,
                   author=author, supervisor_id=supervisor_id, reviewer_id=2,
                   publish_year=publish_year, type_id=type_id, course_id=course_id,
                   temporary=True)

    db.session.add(t)

    try:
        db.session.commit()
    except AssertionError as err:
        db.session.rollback()
        log.error(err)
    except Exception as err:
        db.session.rollback()
        log.error(err)

    return jsonify(
        status=success_status,
        string='Success'
    )


def theses_tmp():

    records = Thesis.query.filter_by(temporary=True)
    return render_template('theses_tmp.html', theses=records)


def theses_delete_tmp():

    thesis_id = request.args.get('thesis_id', default=1, type=int)
    thesis = Thesis.query.filter_by(id=thesis_id).filter_by(temporary=True).first()

    if thesis:
        db.session.delete(thesis)
        db.session.commit()

    return redirect(url_for('theses_tmp'))


def theses_add_tmp():

    thesis_id = request.args.get('thesis_id', default=1, type=int)
    thesis = Thesis.query.filter_by(id=thesis_id).filter_by(temporary=True).first()

    if thesis:
        thesis.temporary=False
        db.session.commit()

        if thesis.text_uri:
            os.rename('./static/tmp/texts/' + thesis.text_uri, './static/thesis/texts/' + thesis.text_uri)

        if thesis.presentation_uri:
            os.rename('./static/tmp/slides/' + thesis.presentation_uri, './static/thesis/slides/' + thesis.presentation_uri)

        if thesis.supervisor_review_uri:
            os.rename('./static/tmp/reviews/' + thesis.supervisor_review_uri, './static/thesis/reviews/' + thesis.supervisor_review_uri)

        if thesis.reviewer_review_uri:
            os.rename('./static/tmp/reviews/' + thesis.reviewer_review_uri, './static/thesis/reviews/' + thesis.reviewer_review_uri)

    return redirect(url_for('theses_tmp'))
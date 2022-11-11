# -*- coding:utf-8 -*-

import json
import logging
import os
import random
import re
import fitz
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
    hints = ['"Максим" можно искать как Максим, максим, Макс* или *акс*.',
             'Полнотекстовый поиск по названиям работ и авторам',
             '"Дом" можно искать как дом, д?м или д*м']

    hint = random.choice(hints)

    for sid in Thesis.query.with_entities(Thesis.type_id).distinct().all():
        type = Worktype.query.filter_by(id=sid[0]).first()

        filter.worktype.choices.append((sid[0], type.type))
        filter.worktype.choices.sort(key=lambda tup: tup[1])

    for sid in Thesis.query.with_entities(Thesis.course_id).distinct().all():
        course = Courses.query.filter_by(id=sid[0]).first()

        filter.course.choices.append((sid[0], course.name))
        filter.course.choices.sort(key=lambda tup: tup[1])

    dates = [theses.publish_year for theses in
             Thesis.query.filter(Thesis.temporary == False).with_entities(Thesis.publish_year).distinct()]
    dates.sort(reverse=True)
    filter.startdate.choices = dates
    filter.enddate.choices = dates

    for sid in Thesis.query.with_entities(Thesis.supervisor_id).distinct().all():
        staff = Staff.query.filter_by(id=sid[0]).first()
        last_name = ""
        initials = ""

        if not staff:
            staff = Staff.query.filter_by(id=1).first()

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

    return render_template('theses.html', filter=filter, hint=hint)


def fetch_theses():

    worktype = request.args.get('worktype', default = 1, type = int)
    page = request.args.get('page', default=1, type=int)
    supervisor = request.args.get('supervisor', default=0, type=int)
    course = request.args.get('course', default=0, type=int)
    search = request.args.get('search', default='', type=str)
    context = {}

    dates = [theses.publish_year for theses in
             Thesis.query.filter(Thesis.temporary == False).with_entities(Thesis.publish_year).distinct()]
    dates.sort(reverse=True)

    if dates:
        startdate = request.args.get('startdate', default=dates[-1], type=int)
        enddate = request.args.get('enddate', default=dates[0], type=int)
    else:
        startdate = 2007
        enddate = 2022

    # Check if end date less than start date
    if enddate < startdate:
        enddate = startdate

    if search:
        records = Thesis.query.msearch(search).filter(Thesis.temporary == False).filter(
            Thesis.publish_year >= startdate).filter(Thesis.publish_year <= enddate).order_by(
            Thesis.publish_year.desc())
    else:
        records = Thesis.query.filter(Thesis.temporary == False).filter(Thesis.publish_year >= startdate).filter(Thesis.publish_year <= enddate).order_by(Thesis.publish_year.desc())

    if course:
        # Check if course exists
        records = records.filter(Thesis.course_id == course)

    if supervisor:

        # Check if supervisor exists
        ids = Thesis.query.with_entities(Thesis.supervisor_id).distinct().all()
        if [item for item in ids if item[0] == supervisor]:
            records = records.filter(Thesis.supervisor_id == supervisor)
        else:
            supervisor = 0

    if worktype > 1:
        records = records.filter_by(type_id=worktype).paginate(per_page=10, page=page, error_out=False)
    else:
        records = records.paginate(per_page=10, page=page, error_out=False)

    if len(records.items):
        first_priority = []
        second_priority = []
        third_priority = []

        for item in records.items:
            text_index = item.text.find(search.lower())
            search_in_name = str(item.name_ru).lower().find(search.lower()) != -1 or str(item.description).lower().find(search.lower()) != -1 or str(item.author).lower().find(search.lower()) != -1

            if search_in_name and text_index != -1:
                first_priority.append(item)
            elif search_in_name:
                second_priority.append(item)
            else:
                third_priority.append(item)

            if text_index != -1:
                left_space_index = item.text.find(' ', text_index - 60)
                right_space_index = item.text.find(' ', text_index + 60)
                context[item] = item.text[left_space_index:right_space_index].split()

        records.items = first_priority + second_priority + third_priority

        return render_template('fetch_theses.html', theses=records, worktype=worktype, course=course,
                               startdate=startdate, enddate=enddate, supervisor=supervisor, search=search
                               , context=context)
    else:
        return render_template('fetch_theses_blank.html')


def get_text(filename):
    doc = fitz.open(filename)
    text = ''

    for current_page in range(3, len(doc)):
        page = doc.load_page(current_page)
        text += page.get_text('text').lower() + '\n'
        text = text.replace('-\n', '')
        text = re.sub(r'[^a-z а-я \n : / . () # - ]', '', text)

    return text

# Download thesis link
def download_thesis():

    thesis_id = request.args.get('thesis_id', default=0, type=int)

    if not thesis_id:
        return redirect('theses_search')

    thesis = Thesis.query.filter_by(id=thesis_id).first()

    if not thesis:
        return redirect('theses_search')

    if not thesis.text_uri:
        return redirect('theses_search')

    # Increment counter
    thesis.download_thesis = thesis.download_thesis + 1
    db.session.commit()

    return redirect(url_for('static', filename='/thesis/texts/' + thesis.text_uri))


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

    type_id_string = ['', 'Bachelor_Report', 'Bachelor_Thesis', 'Master_Thesis',
                      'Autumn_practice_2nd_year', 'Spring_practice_2nd_year', 'Autumn_practice_3rd_year',
                      'Spring_practice_3rd_year']

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

    if course_id < 1 or course_id > 8:
        return jsonify(
            status=error_status,
            string='Wrong course_id: ' + str(course_id)
        )

    # Try to get SuperVisor Id
    qq = Users.query.filter_by(last_name=supervisor).all()
    supervisor_id = ''

    if qq:
        for q in qq:
            r = Staff.query.filter_by(user_id=q.id).first()

            if r:
                supervisor_id = r.id
                continue

        if not supervisor_id:
            return jsonify(
                status=error_status,
                string='Can\'t find supervisor in staff: ' + str(supervisor)
            )
    else:
        return jsonify(
            status=error_status,
            string='Can\'t find supervisor in users: ' + str(supervisor)
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

    text = get_text(os.path.join('./static/tmp/texts/', thesis_filename))

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
                   temporary=True, text=text)
    else:
        t = Thesis(name_ru=name_ru, text_uri=thesis_filename,
                   presentation_uri=presentation_filename,
                   supervisor_review_uri=supervisor_review_filename, reviewer_review_uri=reviewer_review_filename,
                   author=author, supervisor_id=supervisor_id, reviewer_id=2,
                   publish_year=publish_year, type_id=type_id, course_id=course_id,
                   temporary=True, text=text)

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

    records = Thesis.query.filter_by(temporary=True).filter_by(review_status=10)
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
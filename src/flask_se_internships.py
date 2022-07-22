# -*- coding: utf-8 -*-

import markdown

from flask import flash, redirect, request, render_template, url_for
from flask_login import current_user

from flask_se_auth import login_required
from se_internship_forms import AddInternship, InternshipsFilter
from se_models import db, Internships, InternshipFormat, InternshipCompany


def internships_index():
    internship_filter = InternshipsFilter()

    user = current_user
    for x in Internships.query.with_entities(Internships.company_id).distinct().all():
        company = InternshipCompany.query.filter_by(id=x[0]).first()
        internship_filter.company.choices.append((x[0], company.name))
        internship_filter.company.choices.sort(key=lambda tup: tup[1])

    for sid in InternshipFormat.query.all():
        internship_filter.format.choices.append((sid.id, sid.format))

    internship_filter.format.choices.insert(0, (0, "Все"))
    internship_filter.company.choices.insert(0, (0, "Все"))

    return render_template('internships/internships_index.html',
                           internship_filter=internship_filter, user=user)


@login_required
def add_internship():

    user = current_user
    add_internship = AddInternship()
    add_internship.format.choices = [(g.id, g.format) for g in InternshipFormat.query.order_by('id').all()]

    if request.method == 'POST':
        name_vacancy = request.form.get('name_vacancy', type=str)
        description = request.form.get('description', type=str)
        requirements = request.form.get('requirements', type=str)
        company = request.form.get('company', type=str)
        location = request.form.get('location', type=str)
        salary = request.form.get('salary', type=str)
        more_inf = request.form.get('more_inf', type=str)
        format = request.form.getlist('format', type=int)

        format_list = []

        int_format = InternshipFormat.query.all()

        for f in int_format:
            if f.id in format:
                format_list.append(f)

        if not name_vacancy:
            flash("Пожалуйста, укажите название вакансии.")
            return render_template('internships/add_internship.html', form=add_internship, user=user)

        if not format:
            flash("Пожалуйста, выберите формат стажировки.")
            return render_template('internships/add_internship.html', form=add_internship, user=user)

        if not company:
            flash("Пожалуйста, укажите название компании")
            return render_template('internships/add_internship.html', form=add_internship, user=user)

        if not db.session.query(InternshipCompany.id).filter_by(name=company).scalar():
            company_entity = InternshipCompany(name=company)
            db.session.add(company_entity)
            db.session.commit()

        company_id = InternshipCompany.query.with_entities(InternshipCompany.id).filter_by(name=company).distinct().first()

        internship = Internships(name_vacancy=name_vacancy, salary=salary, description=description, location=location,
                                 company_id=company_id[0], requirements=requirements, more_inf=more_inf, author_id=user.id)

        internship.format = format_list

        try:
            db.session.add(internship)
            db.session.commit()
            return redirect(url_for('internships_index'))
        except:
            return "Что-то пошло не так"

    return render_template('internships/add_internship.html', form=add_internship, user=user)


def page_internship(id):

    user = current_user

    internship = Internships.query.filter_by(id=id).first()

    return render_template("internships/page_internship.html", internship=internship, user=user)


# @login_required
def delete_internship(id):

    internship = Internships.query.get_or_404(id)

    try:
        db.session.delete(internship)
        db.session.commit()
        return redirect(url_for('internships_index'))
    except:
           "При удалении стажировки произошла ошибка"


@login_required
def update_internship(id):

    upd_internship = AddInternship()
    upd_internship.format.choices = [(g.id, g.format) for g in InternshipFormat.query.order_by('id').all()]
    internship = Internships.query.get(id)

    if request.method == 'POST':
        internship.name_vacancy = request.form.get('name_vacancy', type=str)
        internship.description = request.form.get('description', type=str)
        internship.requirements = request.form.get('requirements', type=str)
        internship.company = request.form.get('company', type=str)
        internship.location = request.form.get('location', type=str)
        internship.salary = request.form.get('salary', type=str)
        internship.more_inf = request.form.get('more_inf', type=str)

        try:
            db.session.commit()
            return redirect(url_for('internships_index'))
        except:
            return "Что-то пошло не так"
    else:
        return render_template('internships/update_internship.html', form=upd_internship, internship=internship)


def fetch_internships():

    format = request.args.get('format', default=0, type=int)
    page = request.args.get('page', default=1, type=int)
    company = request.args.get('company', default=0, type=int)

    if company:
        records = Internships.query.filter(Internships.company_id == company).order_by(Internships.id.desc())
    else:
        records = Internships.query.order_by(Internships.id.desc())

    if format:
        records = records.filter(Internships.format.any(id=format)).paginate(per_page=10, page=page, error_out=False)
    else:
        records = records.paginate(per_page=10, page=page, error_out=False)

    if len(records.items):
        return render_template('internships/fetch_internships.html', internships=records, format=format, company=company)
    else:
        return render_template('internships/fetch_internships_blank.html')
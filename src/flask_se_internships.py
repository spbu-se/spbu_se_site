# -*- coding: utf-8 -*-

import markdown
import os.path

from flask import flash, redirect, request, render_template, url_for
from flask_login import current_user

from flask_se_auth import login_required
from se_forms import AddInternship, InternshipsFilter
from se_models import db, Internships, InternshipFormat, InternshipCompany, InternshipTag


def internships_index():
    internship_filter = InternshipsFilter()

    user = current_user
    for x in Internships.query.with_entities(Internships.company_id).distinct().all():
        company = InternshipCompany.query.filter_by(id=x[0]).first()
        internship_filter.company.choices.append((x[0], company.name))
        internship_filter.company.choices.sort(key=lambda tup: tup[1])

    for sid in InternshipFormat.query.all():
        internship_filter.format.choices.append((sid.id, sid.format))

    internship_filter.tag.choices = sorted(list({(y.id, y.tag) for x in Internships.query.all() for y in x.tag}), key=lambda x: x[1])
    internship_filter.tag.choices.insert(0, (0, "Все"))
    internship_filter.format.choices.insert(0, (0, "Все"))
    internship_filter.company.choices.insert(0, (0, "Все"))

    internships = Internships.query.all()
    return render_template('internships/internships_index.html', internships=internships,
                           internship_filter=internship_filter, user=user)


def old_internships_index():
    return redirect(url_for('internships_index'))

@login_required
def add_internship():

    user = current_user
    add_intern = AddInternship()
    add_intern.format.choices = [(g.id, g.format) for g in InternshipFormat.query.order_by('id').all()]
    add_intern.tag.choices = [(t.id, t.tag) for t in InternshipTag.query.order_by('tag').all()]
    add_intern.company.choices = [g.name for g in InternshipCompany.query.order_by('id')]


    if request.method == 'POST':
        name_vacancy = request.form.get('name_vacancy', type=str)
        description = request.form.get('description', type=str)
        requirements = request.form.get('requirements', type=str)
        company = request.form.get('company', type=str)
        location = request.form.get('location', type=str)
        salary = request.form.get('salary', type=str)
        more_inf = request.form.get('more_inf', type=str)
        format = request.form.getlist('format', type=int)
        tags = request.form.get('tag', type=str)

        if not tags:
            flash("Пожалуйста, укажите технологии.")
            return render_template('internships/add_internship.html', form=add_intern, user=user)

        if not name_vacancy:
            flash("Пожалуйста, укажите название вакансии.")
            return render_template('internships/add_internship.html', form=add_intern, user=user)

        if not format:
            flash("Пожалуйста, выберите формат стажировки.")
            return render_template('internships/add_internship.html', form=add_intern, user=user)

        if not company:
            flash("Пожалуйста, укажите название компании")
            return render_template('internships/add_internship.html', form=add_intern, user=user)

        tag_list = []
        list_of_tags = list(map(lambda x: x.strip(), tags.rstrip(',').split(',')))
        for t in list_of_tags:
            is_finded = False
            for posb_tag in InternshipTag.query.all():
                if posb_tag.tag.upper() == t.upper():
                    is_finded = True
                    tag_list.append(posb_tag)
                    break
            if not is_finded:
                flash("Тег " + t + " не рапознан. Пожалуйста, свяжитесь с администрацией сайта, чтобы его добавить.")
                return  render_template('internships/add_internship.html', form=add_intern, user=user)

        format_list = []

        int_format = InternshipFormat.query.all()

        for f in int_format:
            if f.id in format:
                format_list.append(f)


        if not db.session.query(InternshipCompany.id).filter_by(name=company).scalar():
            company_entity = InternshipCompany(name=company)
            db.session.add(company_entity)
            db.session.commit()

        company_id = InternshipCompany.query.with_entities(InternshipCompany.id).filter_by(name=company).distinct().first()

        internship = Internships(name_vacancy=name_vacancy, salary=salary, description=description, location=location,
                                 company_id=company_id[0], requirements=requirements, more_inf=more_inf, author_id=user.id)

        internship.format = format_list
        internship.tag = tag_list

        try:
            db.session.add(internship)
            db.session.commit()
            return redirect(url_for('internships_index'))
        except:
            return "Что-то пошло не так"

    return render_template('internships/add_internship.html', form=add_intern, user=user)


def page_internship(id):
    user = current_user
    internships = Internships.query.filter_by(id=id)

    if internships.count() < 1:
        return render_template('404.html')

    return render_template("internships/page_internship.html", internship=internships.first(), user=user)


# @login_required
def delete_internship(id):
    internship = Internships.query.get_or_404(id)
    user = current_user
    try:
        db.session.delete(internship)
        db.session.commit()
        return redirect(url_for('internships_index'))
    except:
        flash("При удалении стажировки произошла ошибка.")
        return render_template("internships/page_internship.html", internship=internship, user=user)



@login_required
def update_internship(id):

    user = current_user
    internship = Internships.query.get(id)
    if not internship:
        return redirect(url_for('internships_index'))
    upd_internship = AddInternship(obj=internship)

    upd_internship.format.choices = [(g.id, g.format) for g in InternshipFormat.query.order_by('id').all()]
    upd_internship.tag.choices = [(t.id, t.tag) for t in InternshipTag.query.order_by('id').all()]
    upd_internship.tag.data = ''.join([t.tag + ', ' for t in internship.tag]).strip(", ")
    upd_internship.format.data = [c.id for c in internship.format]
    upd_internship.company.choices = [g.name for g in InternshipCompany.query.order_by('id')]


    if request.method == 'POST':

        name_vacancy = request.form.get('name_vacancy', type=str)
        internship.description = request.form.get('description', type=str)
        internship.requirements = request.form.get('requirements', type=str)
        internship.location = request.form.get('location', type=str)
        internship.salary = request.form.get('salary', type=str)
        internship.more_inf = request.form.get('more_inf', type=str)
        company = request.form.get('company', type=str)
        format = request.form.getlist('format', type=int)
        tags = request.form.get('tag', type=str)

        if not tags:
            flash("Пожалуйста, укажите технологии.")
            return render_template('internships/update_internship.html', internship=internship, form=upd_internship, user=user)

        if not name_vacancy:
            flash("Пожалуйста, укажите название вакансии.")
            return render_template('internships/update_internship.html', internship=internship, form=upd_internship, user=user)

        if not format:
            flash("Пожалуйста, выберите формат стажировки.")
            return render_template('internships/update_internship.html', internship=internship, form=upd_internship, user=user)

        if not company:
            flash("Пожалуйста, укажите название компании")
            return render_template('internships/update_internship.html', internship=internship, form=upd_internship, user=user)

        tag_list = []
        list_of_tags = list(map(lambda x: x.strip(), tags.rstrip(',').split(',')))
        for t in list_of_tags:
            is_finded = False
            for posb_tag in InternshipTag.query.all():
                if posb_tag.tag.upper() == t.upper():
                    is_finded = True
                    tag_list.append(posb_tag)
                    break
            if not is_finded:
                flash("Тег " + t + " не рапознан. Пожалуйста, свяжитесь с администрацией сайта, чтобы его добавить.")
                return  render_template('internships/update_internship.html', internship=internship, form=upd_internship, user=user)

        format_list = []

        int_format = InternshipFormat.query.all()

        for f in int_format:
            if f.id in format:
                format_list.append(f)

        if not db.session.query(InternshipCompany.id).filter_by(name=company).scalar():
            company_entity = InternshipCompany(name=company)
            db.session.add(company_entity)
            db.session.commit()

        company_id = InternshipCompany.query.with_entities(InternshipCompany.id).filter_by(name=company).distinct().first()
        internship.format = format_list
        internship.tag = tag_list
        internship.name_vacancy = name_vacancy

        internship.company_id = company_id[0]
        try:
            db.session.commit()
            return redirect(url_for('page_internship', id=internship.id))
        except:
            return "Что-то пошло не так"
    else:
        return render_template('internships/update_internship.html', form=upd_internship, internship=internship)


def fetch_internships():

    user = current_user
    
    format = request.args.get('format', default=0, type=int)
    page = request.args.get('page', default=1, type=int)
    company = request.args.get('company', default=0, type=int)
    tag = request.args.get('tag', default=0, type=int)

    if company:
        records = Internships.query.filter(Internships.company_id == company).order_by(Internships.id.desc())
    else:
        records = Internships.query.order_by(Internships.id.desc())

    if format:
        records = records.filter(Internships.format.any(id=format))

    if tag:
        records = records.filter(Internships.tag.any(id=tag))

    records = records.paginate(per_page=10, page=page, error_out=False)

    if len(records.items):
        return render_template('internships/fetch_internships.html', internships=records, format=format, company=company, tag=tag, user=user)
    else:
        return render_template('internships/fetch_internships_blank.html')


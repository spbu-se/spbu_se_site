# -*- coding: utf-8 -*-

import markdown

from flask import flash, redirect, request, render_template, url_for
from flask_login import current_user

from flask_se_auth import login_required
from se_forms import UserAddTheme, UserEditTheme, DiplomaThemesFilter
from se_models import db, DiplomaThemes, ThemesLevel, Company, Staff, Users


def diplomas_index():

    diploma_filter = DiplomaThemesFilter()

    #themes = DiplomaThemes.query.filter_by(status=2).all()
    user_themes_count = 0

    for sid in DiplomaThemes.query.with_entities(DiplomaThemes.company_id).filter_by(status=2).distinct().all():
        company = Company.query.filter_by(id=sid[0]).first()
        diploma_filter.company.choices.append((sid[0], company.name))
        diploma_filter.company.choices.sort(key=lambda tup: tup[1])

    for sid in DiplomaThemes.query.with_entities(DiplomaThemes.supervisor_id).filter_by(status=2).distinct().all():

        if sid[0] is None:
            continue

        user = Users.query.filter_by(id=sid[0]).first()
        last_name = ""
        initials = ""

        if not user:
            user = Users.query.filter_by(id=1).first()

        if user.last_name:
            last_name = user.last_name

        if user.first_name:
            initials = initials + user.first_name[0] + "."

        if user.middle_name:
            initials = initials + user.middle_name[0] + "."

        diploma_filter.supervisor.choices.append((sid[0], last_name + " " + initials))
        diploma_filter.supervisor.choices.sort(key=lambda tup: tup[1])

    for sid in ThemesLevel.query.all():
        diploma_filter.level.choices.append((sid.id, sid.level))
        diploma_filter.level.choices.sort(key=lambda tup: tup[1])

    diploma_filter.supervisor.choices.insert(0, (0, "Все"))
    diploma_filter.level.choices.insert(0, (0, "Все"))
    diploma_filter.company.choices.insert(0, (0, "Все"))

    if current_user.is_authenticated:
        user = current_user
        user_themes_count = DiplomaThemes.query.filter_by(author_id=user.id).count()

    return render_template('diplomas/themes.html', user_themes_count=user_themes_count,
                           diploma_filter=diploma_filter)


def fetch_themes():

    level = request.args.get('level', default=0, type=int)
    page = request.args.get('page', default=1, type=int)
    supervisor = request.args.get('supervisor', default=0, type=int)
    company = request.args.get('company', default=0, type=int)

    if company:
        # Check if company exists
        records = DiplomaThemes.query.filter(DiplomaThemes.status == 2).filter(DiplomaThemes.company_id == company).order_by(DiplomaThemes.id.desc())
    else:
        records = DiplomaThemes.query.filter(DiplomaThemes.status == 2).order_by(DiplomaThemes.id.desc())

    if supervisor:

        # Check if supervisor exists
        ids = DiplomaThemes.query.with_entities(DiplomaThemes.supervisor_id).distinct().all()
        if [item for item in ids if item[0] == supervisor]:
            records = records.filter(DiplomaThemes.supervisor_id == supervisor)
        else:
            supervisor = 0

    if level:
        records = records.filter(DiplomaThemes.levels.any(id=level)).paginate(per_page=10, page=page, error_out=False)
    else:
        records = records.paginate(per_page=10, page=page, error_out=False)

    if len(records.items):
        return render_template('diplomas/fetch_themes.html', themes=records, level=level, company=company,
                               supervisor=supervisor)
    else:
        return render_template('diplomas/fetch_themes_blank.html')


@login_required
def user_diplomas_index():

    user = current_user
    themes = DiplomaThemes.query.filter_by(author_id=user.id).order_by(DiplomaThemes.id.desc()).all()
    user_themes_count = DiplomaThemes.query.filter_by(author_id=user.id).count()

    if not user_themes_count:
        return redirect(url_for('diplomas_index'))

    return render_template('diplomas/user_themes.html', themes=themes)


def get_theme():

    theme_id = request.args.get('id', type=int)

    if not theme_id:
        return redirect(url_for('diplomas_index'))

    theme = DiplomaThemes.query.filter_by(id=theme_id).first_or_404()

    return render_template('diplomas/theme.html', theme=theme)


@login_required
def add_user_theme():

    user = current_user
    add_theme = UserAddTheme()
    add_theme.levels.choices = [(g.id, g.level) for g in ThemesLevel.query.order_by('id').all()]
    add_theme.company.choices = [(g.id, g.name) for g in Company.query.filter_by(status=0).order_by('id')]

    if request.method == 'POST':
        title = request.form.get('title', type=str)
        description = request.form.get('description', type=str)
        requirements = request.form.get('requirements', type=str)
        levels = request.form.getlist('levels', type=int)
        company = request.form.get('company', type=int)

        level_accepted = []

        if not title:
            flash("Заголовок у темы является обязательным полем.")
            return render_template('diplomas/add_theme.html', form=add_theme, user=user)

        if not description:
            flash("Описание у темы является обязательным полем.")
            return render_template('diplomas/add_theme.html', form=add_theme, user=user)

        if not levels:
            flash("Необходимо указать уровень темы.")
            return render_template('diplomas/add_theme.html', form=add_theme, user=user)

        if not company:
            flash("Необходимо указать, от кого предлагается тема.")
            return render_template('diplomas/add_theme.html', form=add_theme, user=user)

        themes_level = ThemesLevel.query.all()
        company_count = Company.query.count()

        for tl in themes_level:
            if tl.id in levels:
                level_accepted.append(tl)

        if not level_accepted:
            flash("Уровень темы указан неверно")
            return render_template('diplomas/add_theme.html', form=add_theme, user=user)

        if company < 1 or company > company_count:
            flash("Уровень темы указан неверно")
            return render_template('diplomas/add_theme.html', form=add_theme, user=user)

        c = DiplomaThemes(title=title, description=description, requirements=requirements,
                          consultant_id=user.id, company_id=company, author_id=user.id)

        c.levels = level_accepted
        db.session.add(c)
        db.session.commit()

        return redirect(url_for('user_diplomas_index'))

    return render_template('diplomas/add_theme.html', form=add_theme, user=user)


@login_required
def delete_theme():

    theme_id = request.args.get('theme_id', type=int)

    if not theme_id:
        return redirect(url_for('diplomas_index'))

    theme = DiplomaThemes.query.filter_by(id=theme_id).first_or_404()

    if theme.author.id != current_user.id:
        return redirect(url_for('diplomas_index'))

    db.session.delete(theme)
    db.session.commit()

    return redirect(url_for('user_diplomas_index'))


@login_required
def edit_user_theme():

    user = current_user
    theme_id = request.args.get('theme_id', type=int)

    if not theme_id:
        return redirect(url_for('diplomas_index'))

    theme = DiplomaThemes.query.filter_by(id=theme_id).first_or_404()

    if theme.author.id != current_user.id:
        return redirect(url_for('diplomas_index'))

    edit_theme = UserEditTheme()
    edit_theme.levels.choices = [(g.id, g.level) for g in ThemesLevel.query.order_by('id')]
    edit_theme.company.choices = [(g.id, g.name) for g in Company.query.order_by('id')]
    edit_theme.levels.data = [c.id for c in theme.levels]
    edit_theme.company.data = str(theme.company_id)
    edit_theme.comment.data = theme.comment
    edit_theme.title.data = theme.title
    edit_theme.description.data = theme.description
    edit_theme.requirements.data = theme.requirements
    edit_theme.consultant.data = theme.consultant
    edit_theme.supervisor.data = theme.supervisor
    edit_theme.theme_id = theme.id
    edit_theme.status.data = theme.status

    if request.method == 'POST':

        title = request.form.get('title', type=str)
        description = request.form.get('description', type=str)
        requirements = request.form.get('requirements', type=str)
        levels = request.form.getlist('levels', type=int)
        company = request.form.get('company', type=int)
        level_accepted = []

        if not title:
            flash("Заголовок у темы является обязательным полем.")
            return render_template('diplomas/edit_theme.html', form=edit_theme, user=user)

        if not description:
            flash("Описание у темы является обязательным полем.")
            return render_template('diplomas/edit_theme.html', form=edit_theme, user=user)

        if not levels:
            flash("Необходимо указать уровень темы.")
            return render_template('diplomas/edit_theme.html', form=edit_theme, user=user)

        if not company:
            flash("Необходимо указать, от кого предлагается тема.")
            return render_template('diplomas/edit_theme.html', form=edit_theme, user=user)

        themes_level = ThemesLevel.query.all()
        company_count = Company.query.count()

        for tl in themes_level:
            if tl.id in levels:
                level_accepted.append(tl)

        if not level_accepted:
            flash("Уровень темы указан неверно")
            return render_template('diplomas/add_theme.html', form=edit_theme, user=user)

        if company < 1 or company > company_count:
            flash("Уровень темы указан неверно")
            return render_template('diplomas/edit_theme.html', form=edit_theme, user=user)

        theme.title = title
        theme.description = description
        theme.requirements = requirements
        theme.levels = level_accepted
        theme.company_id = company
        theme.status = 0
        db.session.commit()

        return redirect(url_for('user_diplomas_index'))

    return render_template('diplomas/edit_theme.html', form=edit_theme, user=user)


@login_required
def archive_theme():

    theme_id = request.args.get('theme_id', type=int)

    if not theme_id:
        return redirect(url_for('diplomas_index'))

    theme = DiplomaThemes.query.filter_by(id=theme_id).first_or_404()

    if theme.author.id != current_user.id:
        return redirect(url_for('diplomas_index'))

    theme.status = 3
    db.session.commit()

    return redirect(url_for('get_theme', id=theme.id))


@login_required
def unarchive_theme():

    theme_id = request.args.get('theme_id', type=int)

    if not theme_id:
        return redirect(url_for('diplomas_index'))

    theme = DiplomaThemes.query.filter_by(id=theme_id).first_or_404()

    if theme.author.id != current_user.id:
        return redirect(url_for('diplomas_index'))

    theme.status = 0
    db.session.commit()

    return redirect(url_for('get_theme', id=theme.id))
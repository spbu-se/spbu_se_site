# -*- coding: utf-8 -*-

import markdown

from flask import flash, redirect, request, render_template, url_for
from flask_login import current_user

from flask_se_auth import login_required
from se_forms import UserAddTheme, UserEditTheme
from se_models import db, DiplomaThemes, ThemesLevel, Company


def diplomas_index():

    themes = DiplomaThemes.query.filter_by(status=2).all()
    user_themes_count = 0

    if current_user.is_authenticated:
        user = current_user
        user_themes_count = DiplomaThemes.query.filter_by(author_id=user.id).count()

    return render_template('diplomas/themes.html', themes=themes, user_themes_count=user_themes_count)


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
    add_theme.level.choices = [(g.id, g.level) for g in ThemesLevel.query.order_by('id')]
    add_theme.company.choices = [(g.id, g.name) for g in Company.query.order_by('id')]

    if request.method == 'POST':
        title = request.form.get('title', type=str)
        description = request.form.get('description', type=str)
        requirements = request.form.get('requirements', type=str)
        level = request.form.get('level', type=int)
        company = request.form.get('company', type=int)

        if not title:
            flash("Заголовок у темы является обязательным полем.")
            return render_template('diplomas/add_theme.html', form=add_theme, user=user)

        if not description:
            flash("Описание у темы является обязательным полем.")
            return render_template('diplomas/add_theme.html', form=add_theme, user=user)

        if not level:
            flash("Необходимо указать, для кого подходит тема.")
            return render_template('diplomas/add_theme.html', form=add_theme, user=user)

        if not company:
            flash("Необходимо указать, от кого предлагается тема.")
            return render_template('diplomas/add_theme.html', form=add_theme, user=user)

        level_count = ThemesLevel.query.count()
        company_count = Company.query.count()

        if level < 1 or level > level_count:
            flash("Уровень темы указан неверно")
            return render_template('diplomas/add_theme.html', form=add_theme, user=user)

        if company < 1 or company > company_count:
            flash("Уровень темы указан неверно")
            return render_template('diplomas/add_theme.html', form=add_theme, user=user)

        c = DiplomaThemes(title=title, description=description, requirements=requirements, level_id=level,
                          consultant_id=user.id, company_id=company, author_id=user.id)
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
    edit_theme.level.choices = [(g.id, g.level) for g in ThemesLevel.query.order_by('id')]
    edit_theme.company.choices = [(g.id, g.name) for g in Company.query.order_by('id')]
    edit_theme.level.data = str(theme.level_id)
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
        level = request.form.get('level', type=int)
        company = request.form.get('company', type=int)

        if not title:
            flash("Заголовок у темы является обязательным полем.")
            return render_template('diplomas/edit_theme.html', form=edit_theme, user=user)

        if not description:
            flash("Описание у темы является обязательным полем.")
            return render_template('diplomas/edit_theme.html', form=edit_theme, user=user)

        if not level:
            flash("Необходимо указать, для кого подходит тема.")
            return render_template('diplomas/edit_theme.html', form=edit_theme, user=user)

        if not company:
            flash("Необходимо указать, от кого предлагается тема.")
            return render_template('diplomas/edit_theme.html', form=edit_theme, user=user)

        level_count = ThemesLevel.query.count()
        company_count = Company.query.count()

        if level < 1 or level > level_count:
            flash("Уровень темы указан неверно")
            return render_template('diplomas/edit_theme.html', form=edit_theme, user=user)

        if company < 1 or company > company_count:
            flash("Уровень темы указан неверно")
            return render_template('diplomas/edit_theme.html', form=edit_theme, user=user)

        theme.title = title
        theme.description = description
        theme.requirements = requirements
        theme.level_id = level
        theme.company_id = company
        theme.status = 0
        db.session.commit()

        return redirect(url_for('user_diplomas_index'))

    return render_template('diplomas/edit_theme.html', form=edit_theme, user=user)
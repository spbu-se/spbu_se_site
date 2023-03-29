# -*- coding: utf-8 -*-

from os import urandom
import shutil

from datetime import datetime, timedelta
from pathlib import Path

import pytz
from dateutil import tz
from sqlalchemy import MetaData
from flask import render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from flask_msearch import Search
from werkzeug.security import generate_password_hash
from datetime import datetime


from flask_se_config import post_ranking_score, get_hours_since, SQLITE_DATABASE_NAME, SQLITE_DATABASE_BACKUP_NAME

convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)
db = SQLAlchemy(metadata=metadata)
search = Search()



tag = db.Table('tag',
               db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'), primary_key=True),
               db.Column('thesis_id', db.Integer, db.ForeignKey('thesis.id'), primary_key=True)
               )

diploma_themes_tag = db.Table('diploma_themes_tag',
                              db.Column('diploma_themes_tag_id', db.Integer, db.ForeignKey('diploma_themes_tags.id'),
                                        primary_key=True),
                              db.Column('diploma_themes_id', db.Integer, db.ForeignKey('diploma_themes.id'),
                                        primary_key=True)
                              )

diploma_themes_level = db.Table('diploma_themes_level',
              db.Column('themes_level_id', db.Integer, db.ForeignKey('themes_level.id'), primary_key=True),
              db.Column('diploma_themes_id', db.Integer, db.ForeignKey('diploma_themes.id'), primary_key=True)
              )

internships_format = db.Table('internships_format',
             db.Column('internships_format_id', db.Integer, db.ForeignKey('internship_format.id'), primary_key=True),
             db.Column('internships_id', db.Integer, db.ForeignKey('internships.id'), primary_key=True)
             )

internships_tag = db.Table('internships_tag',
             db.Column('internships_tag_id', db.Integer, db.ForeignKey('internship_tag.id'), primary_key=True),
             db.Column('internships_id', db.Integer, db.ForeignKey('internships.id'), primary_key=True)
             )


class Staff(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    official_email = db.Column(db.String(255), unique=True, nullable=False)
    position = db.Column(db.String(255), nullable=False)
    science_degree = db.Column(db.String(255), nullable=True)
    still_working = db.Column(db.Boolean, default=False, nullable=False)

    supervisor = db.relationship("Thesis", backref=db.backref("supervisor"), foreign_keys='Thesis.supervisor_id')
    adviser = db.relationship("Thesis", backref=db.backref("reviewer"), foreign_keys='Thesis.reviewer_id')
    current_thesises = db.relationship("CurrentThesis", backref=db.backref("supervisor"))

    def __repr__(self):
        return '<%r>' % self.official_email

    def __str__(self):
        return self.user.get_name()


class Users(db.Model, UserMixin):
    __searchable__ = ['first_name', 'middle_name', 'last_name']

    id = db.Column(db.Integer, primary_key=True)

    email = db.Column(db.String(255), unique=True, nullable=True)
    password_hash = db.Column(db.String(255), unique=False, nullable=True)

    first_name = db.Column(db.String(255), nullable=False)
    middle_name = db.Column(db.String(255), nullable=True)
    last_name = db.Column(db.String(255), nullable=True)

    avatar_uri = db.Column(db.String(512), default='empty.jpg', nullable=False)

    role = db.Column(db.Integer, default=0, nullable=False)
    how_to_contact = db.Column(db.String(512), default='', nullable=True)

    vk_id = db.Column(db.String(255), nullable=True)
    fb_id = db.Column(db.String(255), nullable=True)
    google_id = db.Column(db.String(255), nullable=True)

    staff = db.relationship("Staff", backref=db.backref("user", uselist=False))
    news = db.relationship("Posts", backref=db.backref("author", uselist=False))
    diploma_themes_supervisor = db.relationship("DiplomaThemes", backref=db.backref("supervisor", uselist=False),
                                                foreign_keys='DiplomaThemes.supervisor_id')
    diploma_themes_thesis_supervisor = db.relationship("DiplomaThemes",
                                                       backref=db.backref("supervisor_thesis", uselist=False),
                                                       foreign_keys='DiplomaThemes.supervisor_thesis_id')
    diploma_themes_consultant = db.relationship("DiplomaThemes", backref=db.backref("consultant", uselist=False),
                                                foreign_keys='DiplomaThemes.consultant_id')
    diploma_themes_author = db.relationship("DiplomaThemes", backref=db.backref("author", uselist=False),
                                            foreign_keys='DiplomaThemes.author_id')

    current_thesises = db.relationship('CurrentThesis', backref=db.backref("user", uselist=False))
    thesises = db.relationship("Thesis", backref=db.backref("owner", uselist=False))
    thesis_on_review_author = db.relationship("ThesisOnReview", backref=db.backref("author", uselist=False))

    reviewer = db.relationship('Reviewer', back_populates='user')

    all_user_votes = db.relationship('PostVote', back_populates='user')
    internship_author = db.relationship("Internships", backref=db.backref("user", uselist=False),
                                        foreign_keys='Internships.author_id')

    def get_name(self):
        full_name = ''
        if self.last_name:
            full_name = str(self.last_name)

        if self.first_name:
            full_name = full_name + " " + self.first_name

        if self.middle_name:
            full_name = full_name + " " + self.middle_name

        return full_name

    def is_staff(self):
        return Staff.query.filter_by(user_id=self.id).first() is not None

    def __str__(self):
        full_name = ''
        if self.last_name:
            full_name = str(self.last_name)

        if self.first_name:
            full_name = full_name + " " + self.first_name

        if self.middle_name:
            full_name = full_name + " " + self.middle_name

        if self.email:
            return full_name + ' (' + self.email + ')'
        else:
            return full_name

    def __repr__(self):
        full_name = ''
        if self.last_name:
            full_name = full_name + self.last_name

        if self.first_name:
            full_name = full_name + " " + self.first_name

        if self.middle_name:
            full_name = full_name + " " + self.middle_name

        return full_name


class InternshipFormat(db.Model):
    __tablename__ = 'internship_format'

    id = db.Column(db.Integer, primary_key=True)
    format = db.Column(db.String(100), nullable=False)

    def __str__(self):
        return "{self.format}"


class InternshipTag(db.Model):
    __tablename__ = 'internship_tag'

    id = db.Column(db.Integer, primary_key=True)
    tag = db.Column(db.String(100), nullable=False)

    def __str__(self):
        return self.tag


class CurrentThesis(db.Model):
    __tablename__ = 'current_thesis'

    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    area_id = db.Column(db.Integer, db.ForeignKey('areas_of_study.id'), nullable=True)

    title = db.Column(db.String(512), nullable=True)
    supervisor_id = db.Column(db.Integer, db.ForeignKey('staff.id'), nullable=True)
    worktype_id = db.Column(db.Integer, db.ForeignKey('worktype.id'), nullable=False)

    goal = db.Column(db.String(2048), nullable=True)

    text_uri = db.Column(db.String(512), nullable=True)
    supervisor_review_uri = db.Column(db.String(512), nullable=True)
    reviewer_review_uri = db.Column(db.String(512), nullable=True)
    presentation_uri = db.Column(db.String(512), nullable=True)

    text_link = db.Column(db.String(2048), nullable=True)
    presentation_link = db.Column(db.String(2048), nullable=True)

    reports = db.relationship('ThesisReport', backref=db.backref('practice'))
    tasks = db.relationship('ThesisTask', backref=db.backref('practice'))

    deleted = db.Column(db.Boolean, default=False)
    status = db.Column(db.Integer, default=1)
    # 1 - active practice
    # 2 - past practice

    def __init__(self, author_id, worktype_id, area_id):
        self.author_id = author_id
        self.worktype_id = worktype_id
        self.area_id = area_id

    def __repr__(self):
        return self.title


class NotificationPractice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    recipient_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.String(512), nullable=False)
    time = db.Column(db.DateTime, default=datetime.utcnow)
    viewed = db.Column(db.Boolean, default=False, nullable=False)

    def __init__(self, recipient_id, content):
        self.recipient_id = recipient_id
        self.content = content

    def __repr__(self):
        return self.content


class Deadline(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    worktype_id = db.Column(db.Integer, db.ForeignKey('worktype.id'), nullable=False)
    area_id = db.Column(db.Integer, db.ForeignKey('areas_of_study.id'), nullable=False)

    choose_topic = db.Column(db.DateTime, nullable=True)
    submit_work_for_review = db.Column(db.DateTime, nullable=True)
    upload_reviews = db.Column(db.DateTime, nullable=True)

    pre_defense = db.Column(db.DateTime, nullable=True)
    defense = db.Column(db.DateTime, nullable=True)


class ThesisTask(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task_text = db.Column(db.String(2048), nullable=False)
    deleted = db.Column(db.Boolean, default=False)
    current_thesis_id = db.Column(db.Integer, db.ForeignKey('current_thesis.id'))

    def __init__(self, task_text, current_thesis_id):
        self.task_text = task_text
        self.current_thesis_id = current_thesis_id

    def __repr__(self):
        return self.task_text


class ThesisReport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    current_thesis_id = db.Column(db.Integer, db.ForeignKey('current_thesis.id'))

    was_done = db.Column(db.String(2048), nullable=True)
    planned_to_do = db.Column(db.String(2048), nullable=True)
    time = db.Column(db.DateTime, default=datetime.utcnow)

    deleted = db.Column(db.Boolean, default=False)

    comment = db.Column(db.String(2048), nullable=True)
    comment_time = db.Column(db.DateTime, nullable=True)

    def __init__(self, was_done, planned_to_do, current_thesis_id, author_id):
        self.was_done = was_done
        self.planned_to_do = planned_to_do
        self.current_thesis_id = current_thesis_id
        self.author_id = author_id


class InternshipCompany(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(512), nullable=False)
    logo_uri = db.Column(db.String(512), nullable=True)
    internship = db.relationship('Internships', back_populates='company')

    def __str__(self):
        return (self.name)


class Internships(db.Model):

    __tablename__ = 'internships'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    name_vacancy = db.Column(db.String(70), nullable=False)
    salary = db.Column(db.String(30), nullable=False)
    company = db.relationship('InternshipCompany', back_populates='internship')
    company_id = db.Column(db.Integer, db.ForeignKey('internship_company.id'))
    requirements = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    more_inf = db.Column(db.String, nullable=True) # ссылка на сайт
    description = db.Column(db.String, nullable=True) # короткое описание того, чем нужно будет заниматься
    location = db.Column(db.String(50), nullable=True)
    format = db.relationship('InternshipFormat', secondary=internships_format, lazy='subquery',
                           backref=db.backref('internship', lazy=True), order_by=internships_format.c.internships_format_id)
    tag = db.relationship('InternshipTag', secondary=internships_tag, lazy='subquery',
                             backref=db.backref('internship', lazy=True),
                             order_by=internships_tag.c.internships_tag_id)

    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def __repr__(self):
        return self.name_vacancy

    def __self__(self):
        return self.name_vacancy


# Practice, diploma
class Worktype(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(255), nullable=False)

    thesis = db.relationship("Thesis", backref=db.backref("type", uselist=False))
    thesis_on_review = db.relationship("ThesisOnReview", backref=db.backref('worktype', uselist=False))
    current_thesis = db.relationship("CurrentThesis", backref=db.backref("worktype"))
    deadline = db.relationship("Deadline", backref=db.backref('worktype', uselist=False))

    def __repr__(self):
        return self.type


# Thesis on review worktypes
class ThesisOnReviewWorktype(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(255), nullable=False)

    thesis_on_review = db.relationship("ThesisOnReview", backref=db.backref('thesis_on_review_worktype', uselist=False))

    def __repr__(self):
        return self.type


# Courses
class Courses(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    code = db.Column(db.String(15), nullable=False)

    thesis = db.relationship("Thesis", backref=db.backref('course', uselist=False))
    curriculum = db.relationship("Curriculum", backref=db.backref('course', uselist=False))

    def __repr__(self):
        return '<%r>' % (self.name)


class Thesis(db.Model):
    __searchable__ = ['name_ru', 'description', 'author', 'text']

    id = db.Column(db.Integer, primary_key=True)

    type_id = db.Column(db.Integer, db.ForeignKey('worktype.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)

    area_id = db.Column(db.Integer, db.ForeignKey('areas_of_study.id'), nullable=True)

    name_ru = db.Column(db.String(512), nullable=False)
    name_en = db.Column(db.String(512), nullable=True)
    description = db.Column(db.String(4096), nullable=True)

    text_uri = db.Column(db.String(512), nullable=True)
    old_text_uri = db.Column(db.String(512), nullable=True)
    presentation_uri = db.Column(db.String(512), nullable=True)
    supervisor_review_uri = db.Column(db.String(512), nullable=True)
    reviewer_review_uri = db.Column(db.String(512), nullable=True)
    source_uri = db.Column(db.String(512), nullable=True)

    author = db.Column(db.String(512), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    supervisor_id = db.Column(db.Integer, db.ForeignKey('staff.id'), nullable=True)
    reviewer_id = db.Column(db.Integer, db.ForeignKey('staff.id'), nullable=True)

    publish_year = db.Column(db.Integer, nullable=False)
    recomended = db.Column(db.Boolean, default=False, nullable=False)
    temporary = db.Column(db.Boolean, default=False, nullable=False)
    text = db.Column(db.Text, nullable=True)

    # 0 - success review (or not needed)
    # 1 - need to review
    # 2 - on review (in progress)
    # 3 - failed to review
    review_status = db.Column(db.Integer, nullable=True, default=10)

    review = db.relationship('ThesisReview', back_populates='thesis')

    download_thesis = db.Column(db.Integer, default=0, nullable=True)
    download_presentation = db.Column(db.Integer, default=0, nullable=True)


class AreasOfStudy(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    area = db.Column(db.String(512), nullable=False)

    current_thesis = db.relationship("CurrentThesis", backref=db.backref('area', uselist=False))
    thesis = db.relationship("Thesis", backref=db.backref('area', uselist=False))
    thesis_on_review = db.relationship("ThesisOnReview", backref=db.backref('area', uselist=False))

    def __repr__(self):
        return self.area


class Tags(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    tags = db.relationship('Thesis', secondary=tag, lazy='subquery', backref=db.backref('tags', lazy=True))


class Curriculum(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer, nullable=False)
    discipline = db.Column(db.String(256), nullable=False)
    study_year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(1024), nullable=True)
    type = db.Column(db.Integer, nullable=False, default=1)

    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)


class SummerSchool(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer, default=2021, nullable=False)
    project_name = db.Column(db.String(1024), nullable=False)
    description = db.Column(db.String(2048), nullable=False)
    tech = db.Column(db.String(1024), nullable=False)
    repo = db.Column(db.String(1024), nullable=True)
    demos = db.Column(db.String(1024), nullable=True)
    advisors = db.Column(db.String(1024), nullable=False)
    requirements = db.Column(db.String(1024), nullable=False)


class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(2048), nullable=False)
    uri = db.Column(db.String(1024), nullable=True)
    domain = db.Column(db.String(512), nullable=True)
    text = db.Column(db.String(4096), nullable=True)
    votes = db.Column(db.Integer, nullable=False, default=1)
    views = db.Column(db.Integer, nullable=False, default=1)

    created_on = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    updated_on = db.Column(db.DateTime(timezone=True), server_default=db.func.now(), server_onupdate=db.func.now())

    rank = db.Column(db.Float, nullable=False, default=post_ranking_score)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    all_news_votes = db.relationship('PostVote', back_populates='post')

    type_id = db.Column(db.Integer, db.ForeignKey('post_type.id'))
    type = db.relationship('PostType', back_populates='post')


class PostVote(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)
    user = db.relationship('Users', back_populates='all_user_votes')

    post_id = db.Column(db.Integer, db.ForeignKey("posts.id"))
    post = db.relationship('Posts', back_populates='all_news_votes')

    upvote = db.Column(db.Boolean, nullable=False)
    timestamp = db.Column(db.DateTime, server_default=db.func.now())

    def __repr__(self):
        if self.upvote:
            vote = 'Up'
        else:
            vote = 'Down'
        return '<Vote - {}, from {} for {}>'.format(vote, self.user.get_name(), self.post.title)


class PostType(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    type = db.Column(db.Integer, nullable=False, default=1)
    name = db.Column(db.String(512), nullable=False)

    post = db.relationship('Posts', back_populates='type')

    def __str__(self):
        return self.name


class ThemesLevel(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    level = db.Column(db.String(512), nullable=False)

    #    theme = db.relationship('DiplomaThemes', back_populates='level')
    #    themes_id = db.Column(db.Integer, db.ForeignKey('diploma_themes.id'))

    def __str__(self):
        return f"{self.level}"


class DiplomaThemes(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(512), nullable=False)
    description = db.Column(db.String(2048), nullable=True)
    requirements = db.Column(db.String(2048), nullable=True)
    status = db.Column(db.Integer, default=0, nullable=False) # 0 - new, 1 - need update, 2 - approved, 3 - archive
    
    comment = db.Column(db.String(2048), nullable=True)

    levels = db.relationship('ThemesLevel', secondary=diploma_themes_level, lazy='subquery',
                             backref=db.backref('diploma_themes', lazy=True),
                             order_by=diploma_themes_level.c.themes_level_id)

    company_id = db.Column(db.Integer, db.ForeignKey('company.id'))
    company = db.relationship('Company', back_populates='theme')

    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    supervisor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    supervisor_thesis_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    consultant_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def __repr__(self):
        return f"{self.title}"

    def __str__(self):
        return f"{self.title}"


class DiplomaThemesTags(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    tags = db.relationship('DiplomaThemes', secondary=diploma_themes_tag, lazy='subquery',
                           backref=db.backref('diploma_themes_tags', lazy=True))


class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(512), nullable=False)
    logo_uri = db.Column(db.String(512), nullable=True)
    status = db.Column(db.Integer, default=0, nullable=True)

    theme = db.relationship('DiplomaThemes', back_populates='company')
    reviewer = db.relationship('Reviewer', back_populates='company')

    def __str__(self):
        return f"{self.name}"


class ThesisReview(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    thesis_id = db.Column(db.Integer, db.ForeignKey('thesis.id'))
    thesis = db.relationship('Thesis', back_populates='review')

    thesis_on_review_id = db.Column(db.Integer, db.ForeignKey('thesis_on_review.id'))
    thesis_on_review = db.relationship('ThesisOnReview', back_populates='review')

    o1 = db.Column(db.Integer, nullable=True)
    o1_comment = db.Column(db.String(1024), nullable=True)
    o2 = db.Column(db.Integer, nullable=True)
    o2_comment = db.Column(db.String(1024), nullable=True)
    t1 = db.Column(db.Integer, nullable=True)
    t1_comment = db.Column(db.String(1024), nullable=True)
    t2 = db.Column(db.Integer, nullable=True)
    t2_comment = db.Column(db.String(1024), nullable=True)
    p1 = db.Column(db.Integer, nullable=True)
    p1_comment = db.Column(db.String(1024), nullable=True)
    p2 = db.Column(db.Integer, nullable=True)
    p2_comment = db.Column(db.String(1024), nullable=True)

    verdict = db.Column(db.Integer, nullable=False, default=0)
    overall_comment = db.Column(db.String(1024), nullable=True)

    review_file_uri = db.Column(db.String(512), nullable=True)


class Reviewer(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('Users', back_populates='reviewer')

    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=True)
    company = db.relationship('Company', back_populates='reviewer')

    reviewer = db.relationship('ThesisOnReview', back_populates='reviewer')

    def __str__(self):
        return self.user.get_name()


class ThesisOnReview(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    type_id = db.Column(db.Integer, db.ForeignKey('worktype.id'), nullable=False)
    area_id = db.Column(db.Integer, db.ForeignKey('areas_of_study.id'), nullable=True)

    thesis_on_review_type_id = db.Column(db.Integer, db.ForeignKey('thesis_on_review_worktype.id'), nullable=True)

    name_ru = db.Column(db.String(512), nullable=False)

    text_uri = db.Column(db.String(512), nullable=True)
    presentation_uri = db.Column(db.String(512), nullable=True)
    source_uri = db.Column(db.String(512), nullable=True)

    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    reviewer_id = db.Column(db.Integer, db.ForeignKey('reviewer.id'), nullable=True)
    reviewer = db.relationship('Reviewer', back_populates='reviewer')

    supervisor_id = db.Column(db.Integer, db.ForeignKey('staff.id'), nullable=True)

    # 0 - success review (or not needed)
    # 1 - need to review
    # 2 - on review (in progress)
    # 3 - failed to review
    review_status = db.Column(db.Integer, nullable=True, default=10)
    review = db.relationship('ThesisReview', back_populates='thesis_on_review')

    # 0 - is active
    # 1 - not active
    deleted = db.Column(db.Integer, nullable=True, default=0)


class PromoCode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(512), nullable=False)


class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    # 0 - Mail
    type = db.Column(db.Integer, default=0, nullable=False)

    recipient = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(512), nullable=True)
    content = db.Column(db.String(8192), nullable=True)


def recalculate_post_rank():
    posts = Posts.query.order_by(Posts.id.desc()).limit(100).all()

    for post in posts:
        age = get_hours_since(post.created_on)
        post.rank = post_ranking_score(post.votes, age, post.views)

    db.session.commit()


def add_mail_notification(user_id, title, content):
    if not Users.query.filter_by(id=user_id).first():
        return

    n = Notification(recipient=user_id, title=title, content=content)
    db.session.add(n)
    db.session.commit()


def init_db():
    # Data
    users = [
        {'email': 'a.terekhov@spbu.ru', 'first_name': 'Андрей', 'last_name': 'Терехов', 'middle_name': 'Николаевич',
         'avatar_uri': 'terekhov.jpg'},
        {'email': 'o.granichin@spbu.ru', 'first_name': 'Олег', 'last_name': 'Граничин', 'middle_name': 'Николаевич',
         'avatar_uri': 'granichin.jpg'},
        {'email': 'd.koznov@spbu.ru', 'first_name': 'Дмитрий', 'last_name': 'Кознов', 'middle_name': 'Владимирович',
         'avatar_uri': 'koznov.jpg'},
        {'email': 't.bryksin@spbu.ru', 'first_name': 'Тимофей', 'last_name': 'Брыксин', 'middle_name': 'Александрович',
         'avatar_uri': 'bryksin.jpg'},
        {'email': 'd.bylychev@spbu.ru', 'first_name': 'Дмитрий', 'last_name': 'Булычев', 'middle_name': 'Юрьевич',
         'avatar_uri': 'boulytchev.jpg'},
        {'email': 'y.litvinov@spbu.ru', 'first_name': 'Юрий', 'last_name': 'Литвинов', 'middle_name': 'Викторович',
         'avatar_uri': 'litvinov.jpg'},
        {'email': 'd.lutsiv@spbu.ru', 'first_name': 'Дмитрий', 'last_name': 'Луцив', 'middle_name': 'Вадимович',
         'avatar_uri': 'luciv.jpg'},
        {'email': 'k.romanovsky@spbu.ru', 'first_name': 'Константин', 'last_name': 'Романовский',
         'middle_name': 'Юрьевич',
         'avatar_uri': 'empty.jpg'},
        {'email': 'm.serov@spbu.ru', 'first_name': 'Михаил', 'last_name': 'Серов',
         'middle_name': 'Александрович', 'avatar_uri': 'empty.jpg'},
        {'email': 's.s.sysoev@spbu.ru', 'first_name': 'Сергей', 'last_name': 'Сысоев',
         'middle_name': 'Сергеевич', 'avatar_uri': 'empty.jpg'},
        {'email': 'm.baklanovsky@spbu.ru', 'first_name': 'Максим', 'last_name': 'Баклановский',
         'middle_name': 'Викторович', 'avatar_uri': 'baklanovsky.jpg'},
        {'email': 'm.m.zhuravlev@spbu.ru', 'first_name': 'Максим', 'last_name': 'Журавлев',
         'middle_name': 'Михайлович', 'avatar_uri': 'zhuravlev.jpg'},
        {'email': 'i.zelenchuk@spbu.ru', 'first_name': 'Илья', 'last_name': 'Зеленчук',
         'middle_name': 'Валерьевич', 'avatar_uri': 'zelenchuk.jpg'},
        {'email': 'y.kirilenko@spbu.ru', 'first_name': 'Яков', 'last_name': 'Кириленко',
         'middle_name': 'Александрович', 'avatar_uri': 'kirilenko.jpg'},
        {'email': 'st035425@student.spbu.ru', 'first_name': 'Антон', 'last_name': 'Козлов',
         'middle_name': 'Павлович', 'avatar_uri': 'empty.jpg'},
        {'email': 'egor.k.kulikov@gmail.com', 'first_name': 'Егор', 'last_name': 'Куликов',
         'middle_name': 'Константинович', 'avatar_uri': 'kulikov.jpg'},
        {'email': 'd.mordvinov@spbu.ru', 'first_name': 'Дмитрий', 'last_name': 'Мордвинов',
         'middle_name': 'Александрович', 'avatar_uri': 'mordvinov.jpg'},
        {'email': 'm.nemeshev@spbu.ru', 'first_name': 'Марат', 'last_name': 'Немешев',
         'middle_name': 'Халимович', 'avatar_uri': 'nemeshev.jpg'},
        {'email': 'stanislav.sartasov@spbu.ru', 'first_name': 'Станислав', 'last_name': 'Сартасов',
         'middle_name': 'Юрьевич', 'avatar_uri': 'empty.jpg'},
        {'email': 'm.n.smirnov@spbu.ru', 'first_name': 'Михаил', 'last_name': 'Смирнов',
         'middle_name': 'Николаевич', 'avatar_uri': 'smirnov.jpg'},
        {'email': 'st036451@student.spbu.ru', 'first_name': 'Артур', 'last_name': 'Ханов',
         'middle_name': 'Рафаэльевич', 'avatar_uri': 'khanov.jpg'},
        {'email': 's.shilov@spbu.ru', 'first_name': 'Сергей', 'last_name': 'Шилов',
         'middle_name': 'Юрьевич', 'avatar_uri': 'empty.jpg'},
        {'email': 'st013464@student.spbu.ru', 'first_name': 'Петр', 'last_name': 'Лозов',
         'middle_name': 'Алексеевич', 'avatar_uri': 'empty.jpg'},
        {'email': 'st013039@student.spbu.ru', 'first_name': 'Евгений', 'last_name': 'Моисеенко',
         'middle_name': 'Александрович', 'avatar_uri': 'empty.jpg'},
        {'email': 's.v.grigoriev@spbu.ru', 'first_name': 'Семен', 'last_name': 'Григорьев',
         'middle_name': 'Вячеславович', 'avatar_uri': 'empty.jpg'},
        {'email': 'pimenov_aa_stub@spbu.ru', 'first_name': 'Александр', 'last_name': 'Пименов',
         'middle_name': 'Александрович', 'avatar_uri': 'empty.jpg'},
        {'email': 's.salischev@spbu.ru', 'first_name': 'Сергей', 'last_name': 'Салищев',
         'middle_name': 'Игоревич', 'avatar_uri': 'empty.jpg'},
        {'email': 'd.sagunov@spbu.ru', 'first_name': 'Данил', 'last_name': 'Сагунов',
         'middle_name': 'Георгиевич', 'avatar_uri': 'empty.jpg'},
        {'email': 'g.chernyshev@spbu.ru', 'first_name': 'Георгий', 'last_name': 'Чернышев',
         'middle_name': 'Алексеевич', 'avatar_uri': 'empty.jpg'},
    ]
    staff = [
        {'position': 'Заведующий кафедрой, профессор', 'science_degree': 'д.ф.-м.н.',
         'official_email': 'a.terekhov@spbu.ru', 'still_working': True},
        {'position': 'Профессор', 'science_degree': 'д.ф.-м.н.',
         'official_email': 'o.granichin@spbu.ru', 'still_working': True},
        {'position': 'Профессор', 'science_degree': 'д.т.н.',
         'official_email': 'd.koznov@spbu.ru', 'still_working': True},
        {'position': 'Доцент', 'science_degree': 'к.т.н.',
         'official_email': 't.bryksin@spbu.ru', 'still_working': True},
        {'position': 'Доцент', 'science_degree': 'к.ф.-м.н.',
         'official_email': 'd.bylychev@spbu.ru', 'still_working': True},
        {'position': 'Доцент', 'science_degree': 'к.т.н.',
         'official_email': 'y.litvinov@spbu.ru', 'still_working': True},
        {'position': 'Доцент', 'science_degree': 'к.ф.-м.н.',
         'official_email': 'd.lutsiv@spbu.ru', 'still_working': True},
        {'position': 'Доцент', 'science_degree': 'к.ф.-м.н.',
         'official_email': 'k.romanovsky@spbu.ru', 'still_working': True},
        {'position': 'Доцент', 'official_email': 'm.serov@spbu.ru', 'still_working': True},
        {'position': 'Преподаватель-практик', 'science_degree': 'к.ф.-м.н.',
         'official_email': 's.s.sysoev@spbu.ru', 'still_working': True},
        {'position': 'Старший преподаватель', 'official_email': 'm.baklanovsky@spbu.ru', 'still_working': True},
        {'position': 'Старший преподаватель', 'official_email': 'm.m.zhuravlev@spbu.ru', 'still_working': True},
        {'position': 'Старший преподаватель', 'official_email': 'i.zelenchuk@spbu.ru', 'still_working': True},
        {'position': 'Старший преподаватель', 'official_email': 'y.kirilenko@spbu.ru', 'still_working': True},
        {'position': 'Старший преподаватель', 'official_email': 'st035425@student.spbu.ru', 'still_working': True},
        {'position': 'Старший преподаватель', 'official_email': 'egor.k.kulikov@gmail.com', 'still_working': True},
        {'position': 'Старший преподаватель', 'official_email': 'd.mordvinov@spbu.ru', 'still_working': True},
        {'position': 'Старший преподаватель', 'official_email': 'm.nemeshev@spbu.ru', 'still_working': True},
        {'position': 'Старший преподаватель', 'official_email': 'stanislav.sartasov@spbu.ru', 'still_working': True},
        {'position': 'Старший преподаватель', 'science_degree': 'к.т.н.', 'official_email': 'm.n.smirnov@spbu.ru',
         'still_working': True},
        {'position': 'Старший преподаватель', 'official_email': 'st036451@student.spbu.ru', 'still_working': True},
        {'position': 'Старший преподаватель', 'official_email': 's.shilov@spbu.ru', 'still_working': True},
        {'position': 'Инженер-исследователь', 'official_email': 'st013464@student.spbu.ru', 'still_working': True},
        {'position': 'Инженер-исследователь', 'official_email': 'st013039@student.spbu.ru', 'still_working': True},
        {'position': 'Доцент', 'official_email': 's.v.grigoriev@spbu.ru', 'science_degree': 'к.ф.-м.н.',
         'still_working': False},
        {'position': 'Старший преподаватель', 'official_email': 'pimenov_aa_stub@spbu.ru', 'still_working': False},
        {'position': 'Старший преподаватель', 'official_email': 's.salischev@spbu.ru', 'still_working': False},
        {'position': 'Ассистент', 'official_email': 'd.sagunov@spbu.ru', 'still_working': False},
        {'position': 'Ассистент', 'official_email': 'g.chernyshev@spbu.ru', 'still_working': False},
    ]
    wtypes = [
        {'type': 'Все работы'},
        {'type': 'Курсовая'},
        {'type': 'Бакалаврская ВКР'},
        {'type': 'Магистерская ВКР'},
        {'type': 'Практика осенняя, 2 курс'},
        {'type': 'Практика весенняя, 2 курс'},
        {'type': 'Практика осенняя, 3 курс'},
        {'type': 'Практика весенняя, 3 курс'},
        {'type': 'Производственная практика'},
        {'type': 'Преддипломная практика'},
    ]

    internship_formats = [
        {'format': 'Очно'},
        {'format': 'Дистанционно'}
    ]
    internship_tags = [
        {'tag': 'C'},
        {'tag': 'C++'},
        {'tag': 'C#'}
    ]
    courses = [
        {'name': 'Математическое обеспечение и администрирование информационных систем (бакалавриат)',
         'code': '02.03.03'},
        {'name': 'Программная инженерия (бакалавриат)', 'code': '09.03.04'},
        {'name': 'Математическое обеспечение и администрирование информационных систем (магистратура)',
         'code': '02.04.03'},
        {'name': '371 группа (бакалавриат)', 'code': '371'},
        {'name': '343 группа (бакалавриат)', 'code': '343'},
        {'name': '344 группа (бакалавриат)', 'code': '344'},
        {'name': 'Программная инженерия (магистратура)', 'code': '09.04.04'},
    ]
    tags = [
        {
            'name': 'Компилятор'
        },
        {
            'name': 'Android'
        },
        {
            'name': 'F#'
        },
        {
            'name': 'РуСи'
        }
    ]
    curriculum = [
        {'year': 2019, 'discipline': 'Практикум на ЭВМ', 'study_year': 1, 'type': 1, 'course_id': 2},
        {'year': 2019, 'discipline': 'Дискретная математика', 'study_year': 1, 'type': 2, 'course_id': 2},
        {'year': 2019, 'discipline': 'Математический анализ', 'study_year': 1, 'type': 2, 'course_id': 2},
        {'year': 2019, 'discipline': 'Безопасность жизнедеятельности', 'study_year': 1, 'type': 3, 'course_id': 2},
        {'year': 2019, 'discipline': 'Основы программирования', 'study_year': 1, 'type': 1, 'course_id': 2},
        {'year': 2019, 'discipline': 'Групповая динамика и коммуникации', 'study_year': 1, 'type': 3, 'course_id': 2},
        {'year': 2019, 'discipline': 'Физическая культура и спорт', 'study_year': 1, 'type': 3, 'course_id': 2},
        {'year': 2019, 'discipline': 'Алгебра', 'study_year': 1, 'type': 2, 'course_id': 2},
        {'year': 2019, 'discipline': 'Иностранный язык', 'study_year': 1, 'type': 3, 'course_id': 2},
        {'year': 2019, 'discipline': 'Цифровая культура', 'study_year': 1, 'type': 3, 'course_id': 2},
        {'year': 2019, 'discipline': 'Алгоритмы и структуры данных', 'study_year': 1, 'type': 1, 'course_id': 2},
        {'year': 2019, 'discipline': 'Архитектура вычислительных систем', 'study_year': 1, 'type': 1, 'course_id': 2},
        {'year': 2019, 'discipline': 'Геометрия', 'study_year': 1, 'type': 2, 'course_id': 2},
        {'year': 2019, 'discipline': 'Введение в программную инженерию', 'study_year': 2, 'type': 1, 'course_id': 2},
        {'year': 2019, 'discipline': 'Практикум на ЭВМ', 'study_year': 2, 'type': 1, 'course_id': 2},
        {'year': 2019, 'discipline': 'История России', 'study_year': 2, 'type': 3, 'course_id': 2},
        {'year': 2019, 'discipline': 'Математический анализ', 'study_year': 2, 'type': 2, 'course_id': 2},
        {'year': 2019, 'discipline': 'Операционные системы', 'study_year': 2, 'type': 1, 'course_id': 2},
        {'year': 2019, 'discipline': 'Алгоритмы и анализ сложности', 'study_year': 2, 'type': 1, 'course_id': 2},
        {'year': 2019, 'discipline': 'Физическая культура и спорт', 'study_year': 2, 'type': 3, 'course_id': 2},
        {'year': 2019, 'discipline': 'Язык эффективной коммуникации', 'study_year': 2, 'type': 3, 'course_id': 2},
        {'year': 2019, 'discipline': 'Функциональное программирование', 'study_year': 2, 'type': 1, 'course_id': 2},
        {'year': 2019, 'discipline': 'Инженерная экономика', 'study_year': 2, 'type': 3, 'course_id': 2},
        {'year': 2019, 'discipline': 'Учебная практика (научно-исследовательская работа)', 'study_year': 2, 'type': 1,
         'course_id': 2},
        {'year': 2019, 'discipline': 'Иностранный язык', 'study_year': 2, 'type': 3, 'course_id': 2},
        {'year': 2019, 'discipline': 'Разработка программного обеспечения', 'study_year': 2, 'type': 1, 'course_id': 2},
        {'year': 2019, 'discipline': 'Дифференциальные и разностные уравнения', 'study_year': 2, 'type': 2,
         'course_id': 2},
        {'year': 2019, 'discipline': 'Основы бизнеса', 'study_year': 2, 'type': 3, 'course_id': 2},
        {'year': 2019, 'discipline': 'Человеко-машинное взаимодействие', 'study_year': 2, 'type': 1, 'course_id': 2},
        {'year': 2019, 'discipline': 'Теория вероятностей и математическая статистика', 'study_year': 2, 'type': 2,
         'course_id': 2},
        {'year': 2019, 'discipline': 'Вычислительная математика', 'study_year': 2, 'type': 1, 'course_id': 2},
        {'year': 2019, 'discipline': 'Математическая логика', 'study_year': 2, 'type': 1, 'course_id': 2},
        {'year': 2019, 'discipline': 'Компьютерные сети', 'study_year': 3, 'type': 1, 'course_id': 2},
        {'year': 2019, 'discipline': 'Основы противодействия коррупции и экстремизму (онлайн-курс)', 'study_year': 3,
         'type': 3, 'course_id': 2},
        {'year': 2019, 'discipline': 'Компьютерная графика', 'study_year': 3, 'type': 1, 'course_id': 2},
        {'year': 2019, 'discipline': 'Обеспечение качества и тестирование программного обеспечения ', 'study_year': 3,
         'type': 1, 'course_id': 2},
        {'year': 2019, 'discipline': 'Теория автоматов и формальных языков ', 'study_year': 3, 'type': 1,
         'course_id': 2},
        {'year': 2019, 'discipline': 'Базы данных', 'study_year': 3, 'type': 1, 'course_id': 2},
        {'year': 2019, 'discipline': 'Производственная практика', 'study_year': 3, 'type': 1, 'course_id': 2},
        {'year': 2019, 'discipline': 'Трансляция языков программирования', 'study_year': 3, 'type': 1, 'course_id': 2},
        {'year': 2019, 'discipline': 'Иностранный язык', 'study_year': 3, 'type': 3, 'course_id': 2},
        {'year': 2019, 'discipline': 'Методы оптимизации и исследование операций', 'study_year': 3, 'type': 2,
         'course_id': 2},
        {'year': 2019, 'discipline': 'Моделирование информационных процессов ', 'study_year': 3, 'type': 1,
         'course_id': 2},
        {'year': 2019, 'discipline': 'Основы педагогической деятельности (онлайн-курс)', 'study_year': 3, 'type': 3,
         'course_id': 2},
        {'year': 2019, 'discipline': 'Теория графов', 'study_year': 3, 'type': 1, 'course_id': 2},
        {'year': 2019, 'discipline': 'Социально-правовые вопросы программной инженерии', 'study_year': 3, 'type': 3,
         'course_id': 2},
        {'year': 2019, 'discipline': 'Проектирование и архитектура программного обеспечения', 'study_year': 3,
         'type': 1, 'course_id': 2},
        {'year': 2019, 'discipline': 'Алгоритмы анализа графов (по выбору)', 'study_year': 3, 'type': 1,
         'course_id': 2},
        {'year': 2019, 'discipline': 'Операционные системы и реализация языков программирования (по выбору)',
         'study_year': 3, 'type': 1, 'course_id': 2},
        {'year': 2019, 'discipline': 'Реинжиниринг систем программирования (по выбору)', 'study_year': 3, 'type': 1,
         'course_id': 2},
        {'year': 2019, 'discipline': 'Телекоммуникации (по выбору)', 'study_year': 3, 'type': 1, 'course_id': 2},
        {'year': 2019, 'discipline': 'Введение в специальность (по выбору)', 'study_year': 3, 'type': 1,
         'course_id': 2},
        {'year': 2019, 'discipline': 'Системное программирование (по выбору)', 'study_year': 3, 'type': 1,
         'course_id': 2},
        {'year': 2019, 'discipline': 'Преддипломная практика', 'study_year': 4, 'type': 1, 'course_id': 2},
        {'year': 2019, 'discipline': 'Интеллектуальные системы', 'study_year': 4, 'type': 1, 'course_id': 2},
        {'year': 2019, 'discipline': 'Прикладные задачи теории вероятностей', 'study_year': 4, 'type': 2,
         'course_id': 2},
        {'year': 2019, 'discipline': 'Защита информации', 'study_year': 4, 'type': 1, 'course_id': 2},
        {'year': 2019, 'discipline': 'Анализ требований к программному обеспечению', 'study_year': 4, 'type': 1,
         'course_id': 2},
        {'year': 2019, 'discipline': 'Управление программными проектами', 'study_year': 4, 'type': 1, 'course_id': 2},
        {'year': 2019, 'discipline': 'Иностранный язык', 'study_year': 4, 'type': 3, 'course_id': 2},
        {'year': 2019, 'discipline': 'Разработка приложений в СУБД (по выбору)', 'study_year': 4, 'type': 1,
         'course_id': 2},
        {'year': 2019, 'discipline': 'Стохастическое программирование (по выбору)', 'study_year': 4, 'type': 1,
         'course_id': 2},
        {'year': 2019, 'discipline': 'Введение в MS.NET (по выбору)', 'study_year': 4, 'type': 1, 'course_id': 2},
        {'year': 2019, 'discipline': 'Современные технологии разработки бизнес-приложений (по выбору)', 'study_year': 4,
         'type': 1, 'course_id': 2},
        {'year': 2019, 'discipline': 'Программная инженерия (по выбору)', 'study_year': 4, 'type': 1, 'course_id': 2},
        {'year': 2019, 'discipline': 'Системное программирование для современных платформ (по выбору)', 'study_year': 4,
         'type': 1, 'course_id': 2},
        {'year': 2019, 'discipline': 'Основы менеджмента', 'study_year': 4, 'type': 3, 'course_id': 2},
        {'year': 2019, 'discipline': 'Философия (онлайн-курс)', 'study_year': 4, 'type': 3, 'course_id': 2},
        {'year': 2019, 'discipline': 'Практика разработки документации (на английском языке) (по выбору)',
         'study_year': 4, 'type': 1, 'course_id': 2},
        {'year': 2019, 'discipline': 'Стохастическая оптимизация в информатике (на английском языке) (по выбору)',
         'study_year': 4, 'type': 1, 'course_id': 2},
        {'year': 2019, 'discipline': 'Алгоритмические основы робототехники (по выбору)', 'study_year': 4, 'type': 1,
         'course_id': 2},
        {'year': 2019, 'discipline': 'Статический анализ программ (по выбору)', 'study_year': 4, 'type': 1,
         'course_id': 2},
        {'year': 2019, 'discipline': 'Программирование', 'study_year': 1, 'type': 1, 'course_id': 1},
        {'year': 2019, 'discipline': 'Информатика', 'study_year': 1, 'type': 1, 'course_id': 1},
        {'year': 2019, 'discipline': 'Физическая культура и спорт', 'study_year': 1, 'type': 3, 'course_id': 1},
        {'year': 2019, 'discipline': 'Дискретная математика', 'study_year': 1, 'type': 2, 'course_id': 1},
        {'year': 2019, 'discipline': 'Математический анализ', 'study_year': 1, 'type': 2, 'course_id': 1},
        {'year': 2019, 'discipline': 'Алгебра и теория чисел', 'study_year': 1, 'type': 2, 'course_id': 1},
        {'year': 2019, 'discipline': 'Геометрия и топология', 'study_year': 1, 'type': 2, 'course_id': 1},
        {'year': 2019, 'discipline': 'Иностранный язык', 'study_year': 1, 'type': 3, 'course_id': 1},
        {'year': 2019, 'discipline': 'Цифровая культура (ЭО)', 'study_year': 1, 'type': 3, 'course_id': 1},
        {'year': 2019, 'discipline': 'История России (онлайн-курс)', 'study_year': 1, 'type': 3, 'course_id': 1},
        {'year': 2019, 'discipline': 'Программирование', 'study_year': 2, 'type': 1, 'course_id': 1},
        {'year': 2019, 'discipline': 'Учебная практика 1', 'study_year': 2, 'type': 1, 'course_id': 1},
        {'year': 2019, 'discipline': 'Информатика', 'study_year': 2, 'type': 1, 'course_id': 1},
        {'year': 2019, 'discipline': 'Физическая культура и спорт', 'study_year': 2, 'type': 3, 'course_id': 1},
        {'year': 2019, 'discipline': 'Математический анализ', 'study_year': 2, 'type': 2, 'course_id': 1},
        {'year': 2019, 'discipline': 'Алгебра и теория чисел', 'study_year': 2, 'type': 2, 'course_id': 1},
        {'year': 2019, 'discipline': 'Геометрия и топология', 'study_year': 2, 'type': 2, 'course_id': 1},
        {'year': 2019, 'discipline': 'Язык эффективной коммуникации (онлайнкурс)', 'study_year': 2, 'type': 3,
         'course_id': 1},
        {'year': 2019, 'discipline': 'Дифференциальные уравнения', 'study_year': 2, 'type': 2, 'course_id': 1},
        {'year': 2019, 'discipline': 'Иностранный язык', 'study_year': 2, 'type': 3, 'course_id': 1},
        {'year': 2019, 'discipline': 'Операционные системы и оболочки', 'study_year': 2, 'type': 1, 'course_id': 1},
        {'year': 2019, 'discipline': 'Базы данных и СУБД', 'study_year': 2, 'type': 1, 'course_id': 1},
        {'year': 2019, 'discipline': 'Основы противодействия коррупции и экстремизму (онлайн-курс)', 'study_year': 2,
         'type': 3, 'course_id': 1},
        {'year': 2019, 'discipline': 'Параллельное программирование', 'study_year': 2, 'type': 1, 'course_id': 1},
        {'year': 2019, 'discipline': 'Архитектура ЭВМ', 'study_year': 2, 'type': 1, 'course_id': 1},
        {'year': 2019, 'discipline': 'Математическая логика', 'study_year': 2, 'type': 2, 'course_id': 1},
        {'year': 2019, 'discipline': 'Структуры и алгоритмы компьютерной обработки данных', 'study_year': 2, 'type': 1,
         'course_id': 1},
        {'year': 2019, 'discipline': 'Методы вычислений и вычислительный практикум', 'study_year': 3, 'type': 1,
         'course_id': 1},
        {'year': 2019, 'discipline': 'Функциональный анализ', 'study_year': 3, 'type': 2, 'course_id': 1},
        {'year': 2019, 'discipline': 'Теория вероятностей и математическая статистика', 'study_year': 3, 'type': 2,
         'course_id': 1},
        {'year': 2019, 'discipline': 'Основы бизнеса (онлайн-курс)', 'study_year': 3, 'type': 3, 'course_id': 1},
        {'year': 2019, 'discipline': 'Теория формальных языков и трансляций', 'study_year': 3, 'type': 1,
         'course_id': 1},
        {'year': 2019, 'discipline': 'Учебная практика 2', 'study_year': 3, 'type': 1, 'course_id': 1},
        {'year': 2019, 'discipline': 'Математическая логика', 'study_year': 3, 'type': 2, 'course_id': 1},
        {'year': 2019, 'discipline': 'Математическая логика', 'study_year': 3, 'type': 2, 'course_id': 1},
        {'year': 2019, 'discipline': 'Иностранный язык', 'study_year': 3, 'type': 3, 'course_id': 1},
        {'year': 2019, 'discipline': 'Java-технологии. Часть 1 (по выбору)', 'study_year': 3, 'type': 1,
         'course_id': 1},
        {'year': 2019, 'discipline': 'Алгоритмические языки параллельного программирования (по выбору)',
         'study_year': 3, 'type': 1, 'course_id': 1},
        {'year': 2019, 'discipline': 'Архитектура процессора (по выбору)', 'study_year': 3, 'type': 1, 'course_id': 1},
        {'year': 2019, 'discipline': 'Введение в компьютерную математику (по выбору)', 'study_year': 3, 'type': 1,
         'course_id': 1},
        {'year': 2019, 'discipline': 'Введение в теорию параллельных вычислений (по выбору)', 'study_year': 3,
         'type': 1, 'course_id': 1},
        {'year': 2019, 'discipline': 'Задачи и методы динамических систем (по выбору)', 'study_year': 3, 'type': 1,
         'course_id': 1},
        {'year': 2019, 'discipline': 'Модели и методы хранения и поиска информации (по выбору)', 'study_year': 3,
         'type': 1, 'course_id': 1},
        {'year': 2019, 'discipline': 'Мультиагентные системы (по выбору)', 'study_year': 3, 'type': 1, 'course_id': 1},
        {'year': 2019, 'discipline': 'Основы компьютерной графики и обработки изображений (по выбору)', 'study_year': 3,
         'type': 1, 'course_id': 1},
        {'year': 2019, 'discipline': 'Распараллеливание в OpenMP и интервальные вычисления (по выбору)',
         'study_year': 3, 'type': 1, 'course_id': 1},
        {'year': 2019, 'discipline': 'Теория логического вывода (по выбору)',
         'study_year': 3, 'type': 1, 'course_id': 1},
        {'year': 2019, 'discipline': 'Хранение и управление данными (по выбору)',
         'study_year': 3, 'type': 1, 'course_id': 1},
        {'year': 2019, 'discipline': 'Автоматическое доказательство теорем (по выбору)',
         'study_year': 3, 'type': 2, 'course_id': 1},
        {'year': 2019, 'discipline': 'Введение в специальность (по выбору)',
         'study_year': 3, 'type': 3, 'course_id': 1},
        {'year': 2019, 'discipline': 'Логическое программирование (по выбору)',
         'study_year': 3, 'type': 1, 'course_id': 1},
        {'year': 2019, 'discipline': 'Методы хранения и индексирования (по выбору)',
         'study_year': 3, 'type': 1, 'course_id': 1},
        {'year': 2019, 'discipline': 'Поиск информации в неструктурированных данных (по выбору)',
         'study_year': 3, 'type': 1, 'course_id': 1},
        {'year': 2019, 'discipline': 'Системное программирование (по выбору)',
         'study_year': 3, 'type': 1, 'course_id': 1},
        {'year': 2019, 'discipline': 'Теория и практика распараллеливания в OpenMP (по выбору)',
         'study_year': 3, 'type': 1, 'course_id': 1},
        {'year': 2019, 'discipline': 'Теория распараллеливания над общей памятью (по выбору)',
         'study_year': 3, 'type': 1, 'course_id': 1},
        {'year': 2019, 'discipline': 'Технология преобразования последовательных программ в параллельные (по выбору)',
         'study_year': 3, 'type': 1, 'course_id': 1},
        {'year': 2019, 'discipline': 'Технология разработки программного обеспечения', 'study_year': 3, 'type': 1,
         'course_id': 1},
        {'year': 2019, 'discipline': 'Основы педагогической деятельности (онлайнкурс)', 'study_year': 3, 'type': 3,
         'course_id': 1},
        {'year': 2019, 'discipline': 'Вычислительный практикум', 'study_year': 3, 'type': 1, 'course_id': 1},
        {'year': 2019, 'discipline': 'Уравнения математической физики', 'study_year': 3, 'type': 2, 'course_id': 1},
        {'year': 2019, 'discipline': 'Информационный поиск в Internet (по выбору)', 'study_year': 3, 'type': 1,
         'course_id': 1},
        {'year': 2019, 'discipline': 'Параллельные алгоритмы численного моделирования (по выбору)', 'study_year': 3,
         'type': 1,
         'course_id': 1},
        {'year': 2019, 'discipline': 'Распределенные параллельные системы (по выбору)', 'study_year': 3, 'type': 1,
         'course_id': 1},
        {'year': 2019, 'discipline': 'Реинжиниринг информационных систем (по выбору)', 'study_year': 3, 'type': 1,
         'course_id': 1},
        {'year': 2019, 'discipline': 'Сетевые технологии (по выбору)', 'study_year': 3, 'type': 1,
         'course_id': 1},
        {'year': 2019, 'discipline': 'Статистический анализ данных (по выбору)', 'study_year': 3, 'type': 1,
         'course_id': 1},
        {'year': 2019, 'discipline': 'Телекоммуникации (по выбору)', 'study_year': 3, 'type': 1,
         'course_id': 1},
        {'year': 2019, 'discipline': 'Язык программирования С++ (по выбору)', 'study_year': 3, 'type': 1,
         'course_id': 1},
        {'year': 2019, 'discipline': 'Java-технологии. Часть 2 (по выбору)', 'study_year': 3, 'type': 1,
         'course_id': 1},
        {'year': 2019, 'discipline': 'Алгоритмы анализа графов (по выбору)', 'study_year': 3, 'type': 1,
         'course_id': 1},
        {'year': 2019, 'discipline': 'Архитектура параллельных систем (по выбору)', 'study_year': 3, 'type': 1,
         'course_id': 1},
        {'year': 2019, 'discipline': 'Введение в архитектуру программ (по выбору)', 'study_year': 3, 'type': 1,
         'course_id': 1},
        {'year': 2019, 'discipline': 'Локальные сети и вычислительные системы (по выбору)', 'study_year': 3, 'type': 1,
         'course_id': 1},
        {'year': 2019, 'discipline': 'Организация и дизайн современных компьютеров (по выбору)', 'study_year': 3,
         'type': 1,
         'course_id': 1},
        {'year': 2019, 'discipline': 'Параллельные вычисления с использованием графических процессоров (по выбору)',
         'study_year': 3, 'type': 1,
         'course_id': 1},
        {'year': 2019, 'discipline': 'Программная инженерия (по выбору)', 'study_year': 3, 'type': 1,
         'course_id': 1},
        {'year': 2019, 'discipline': 'Реализация языков программирования (по выбору)', 'study_year': 3, 'type': 1,
         'course_id': 1},
        {'year': 2019, 'discipline': 'Системы управления контентом (по выбору)', 'study_year': 3, 'type': 1,
         'course_id': 1},
        {'year': 2019, 'discipline': 'Методы вычислений (по выбору)', 'study_year': 3, 'type': 1,
         'course_id': 1},
        {'year': 2019, 'discipline': 'Экстремальные задачи (по выбору)', 'study_year': 3, 'type': 1,
         'course_id': 1},

        {'year': 2019, 'discipline': 'Введение в компьютерное моделирование динамических систем', 'study_year': 4,
         'type': 1,
         'course_id': 1},
        {'year': 2019, 'discipline': 'Теория вычислительных процессов и структур', 'study_year': 4,
         'type': 1,
         'course_id': 1},
        {'year': 2019, 'discipline': 'Архитектура вычислительных систем и компьютерных сетей', 'study_year': 4,
         'type': 1,
         'course_id': 1},
        {'year': 2019, 'discipline': 'Производственная практика', 'study_year': 4,
         'type': 1,
         'course_id': 1},
        {'year': 2019, 'discipline': 'Иностранный язык', 'study_year': 4, 'type': 3, 'course_id': 1},
        {'year': 2019, 'discipline': 'Всплесковая обработка числовых потоков и распараллеливание (по выбору)',
         'study_year': 4,
         'type': 1,
         'course_id': 1},
        {'year': 2019, 'discipline': 'Конечно-автоматные модели. Анализ, синтез и оптимизация (по выбору)',
         'study_year': 4, 'type': 1, 'course_id': 1},
        {'year': 2019, 'discipline': 'Основы компьютерной безопасности (по выбору)',
         'study_year': 4, 'type': 1, 'course_id': 1},
        {'year': 2019, 'discipline': 'Программирование на платформе Microsoft.NET (по выбору)',
         'study_year': 4, 'type': 1, 'course_id': 1},
        {'year': 2019, 'discipline': 'Разработка Интернет-приложений (по выбору)',
         'study_year': 4, 'type': 1, 'course_id': 1},
        {'year': 2019, 'discipline': 'Распараллеливание алгоритмов в многопоточных системах (по выбору)',
         'study_year': 4, 'type': 1, 'course_id': 1},
        {'year': 2019, 'discipline': 'Распределенная обработка информации и NoSQL базы данных (по выбору)',
         'study_year': 4, 'type': 1, 'course_id': 1},
        {'year': 2019, 'discipline': 'Рекурсивно-логическое программирование (по выбору)',
         'study_year': 4, 'type': 1, 'course_id': 1},
        {'year': 2019, 'discipline': 'Функциональное программирование (по выбору)',
         'study_year': 4, 'type': 1, 'course_id': 1},
        {'year': 2019, 'discipline': 'Мультиагентные технологии (по выбору)',
         'study_year': 4, 'type': 1, 'course_id': 1},
        {'year': 2019, 'discipline': 'Параллельные алгоритмы обработки изображений (по выбору)',
         'study_year': 4, 'type': 1, 'course_id': 1},
        {'year': 2019, 'discipline': 'Системное программирование для современных платформ (по выбору)',
         'study_year': 4, 'type': 1, 'course_id': 1},
        {'year': 2019, 'discipline': 'Технология разработки программного обеспечения (по выбору)',
         'study_year': 4, 'type': 1, 'course_id': 1},
        {'year': 2019, 'discipline': 'Технология синхронного распараллеливания в многопоточных системах (по выбору)',
         'study_year': 4, 'type': 1, 'course_id': 1},
        {'year': 2019, 'discipline': 'Язык XML и его использование (по выбору)',
         'study_year': 4, 'type': 1, 'course_id': 1},
        {'year': 2019, 'discipline': 'Анализ алгоритмов (по выбору)',
         'study_year': 4, 'type': 1, 'course_id': 1},
        {'year': 2019, 'discipline': 'Конкретная математика (по выбору)',
         'study_year': 4, 'type': 2, 'course_id': 1},
        {'year': 2019, 'discipline': 'Алгоритмы СУБД (по выбору)',
         'study_year': 4, 'type': 1, 'course_id': 1},
        {'year': 2019, 'discipline': 'Сети Петри и представление процессов (по выбору)',
         'study_year': 4, 'type': 1, 'course_id': 1},
        {'year': 2019, 'discipline': 'Проектирование программного обеспечения (по выбору)',
         'study_year': 4, 'type': 1, 'course_id': 1},
        {'year': 2019, 'discipline': 'Философия (онлайн-курс)', 'study_year': 4, 'type': 3, 'course_id': 1},
        {'year': 2019, 'discipline': 'Безопасность жизнедеятельности (онлайнкурс)', 'study_year': 4, 'type': 3,
         'course_id': 1},
        {'year': 2019, 'discipline': 'Преддипломная практика', 'study_year': 4, 'type': 1, 'course_id': 1},
        {'year': 2019, 'discipline': 'Администрирование информационных систем (на английском языке)', 'study_year': 4,
         'type': 1, 'course_id': 1},
        {'year': 2019, 'discipline': 'Интеллектуальные системы (по выбору)', 'study_year': 4, 'type': 1,
         'course_id': 1},
        {'year': 2019, 'discipline': 'Квантовые компьютеры (по выбору)', 'study_year': 4, 'type': 1, 'course_id': 1},
        {'year': 2019,
         'discipline': 'Параллельное программирование с использованием стандартных интерфейсов (по выбору)',
         'study_year': 4, 'type': 1, 'course_id': 1},
        {'year': 2019, 'discipline': 'Практика разработки документации (по выбору)', 'study_year': 4, 'type': 1,
         'course_id': 1},
        {'year': 2019, 'discipline': 'Распараллеливание алгоритмов в распределенных системах (по выбору)',
         'study_year': 4, 'type': 1, 'course_id': 1},
        {'year': 2019, 'discipline': 'Стандарты параллельного программирования (по выбору)', 'study_year': 4, 'type': 1,
         'course_id': 1},
        {'year': 2019, 'discipline': 'Компьютерное моделирование динамических систем (по выбору)', 'study_year': 4,
         'type': 1, 'course_id': 1},
        {'year': 2019, 'discipline': 'Теория и практика параллельного программирования (по выбору)', 'study_year': 4,
         'type': 1, 'course_id': 1},
        {'year': 2019, 'discipline': 'Математические основы искусственного интеллекта (по выбору)', 'study_year': 4,
         'type': 1, 'course_id': 1},
        {'year': 2019, 'discipline': 'Системы искусственного интеллекта (по выбору)', 'study_year': 4, 'type': 1,
         'course_id': 1},
        {'year': 2019, 'discipline': 'Алгоритмы компьютерного зрения (по выбору)', 'study_year': 4, 'type': 1,
         'course_id': 1},
        {'year': 2019, 'discipline': 'Коммуникационные среды для параллельных систем (по выбору)', 'study_year': 4,
         'type': 1, 'course_id': 1},
        {'year': 2019, 'discipline': 'Модели и архитектуры программ и знаний (по выбору)', 'study_year': 4,
         'type': 1, 'course_id': 1},
        {'year': 2019, 'discipline': 'Распараллеливание в ОС UNIX (по выбору)', 'study_year': 4,
         'type': 1, 'course_id': 1},
        {'year': 2019, 'discipline': 'Современные подходы к хранению, управлению и защите данных (по выбору)',
         'study_year': 4,
         'type': 1, 'course_id': 1},
        {'year': 2019, 'discipline': 'Технология синхронного распараллеливания в распределенных системах (по выбору)',
         'study_year': 4,
         'type': 1, 'course_id': 1},
        {'year': 2019, 'discipline': 'Управление проектами (по выбору)', 'study_year': 4,
         'type': 1, 'course_id': 1},
    ]
    curriculum2 = [
        {'year': 2019, 'discipline': 'Практикум на ЭВМ', 'semestr': 1, 'type': 1, 'course_id': 2, 'hard': 5},
        {'year': 2019, 'discipline': 'Дискретная математика', 'semestr': 1, 'type': 2, 'course_id': 2, 'hard': 5},
        {'year': 2019, 'discipline': 'Математический анализ', 'semestr': 1, 'type': 2, 'course_id': 2, 'hard': 7},
        {'year': 2019, 'discipline': 'Безопасность жизнедеятельности (онлайн-курс)', 'semestr': 1, 'type': 3,
         'course_id': 2, 'hard': 0},
        {'year': 2019, 'discipline': 'Основы программирования', 'semestr': 1, 'type': 1, 'course_id': 2, 'hard': 3},
        {'year': 2019, 'discipline': 'Групповая динамика и коммуникации', 'semestr': 1, 'type': 3, 'course_id': 2,
         'hard': 2},
        {'year': 2019, 'discipline': 'Физическая культура и спорт', 'semestr': 1, 'type': 3, 'course_id': 2, 'hard': 0},
        {'year': 2019, 'discipline': 'Алгебра', 'semestr': 1, 'type': 2, 'course_id': 2, 'hard': 5},
        {'year': 2019, 'discipline': 'Иностранный язык', 'semestr': 1, 'type': 3, 'course_id': 2, 'hard': 3},
        {'year': 2019, 'discipline': 'Практикум на ЭВМ', 'semestr': 2, 'type': 1, 'course_id': 2, 'hard': 3},
        {'year': 2019, 'discipline': 'Цифровая культура', 'semestr': 2, 'type': 3, 'course_id': 2, 'hard': 1},
        {'year': 2019, 'discipline': 'Дискретная математика', 'semestr': 2, 'type': 2, 'course_id': 2, 'hard': 4},
        {'year': 2019, 'discipline': 'Математический анализ', 'semestr': 2, 'type': 2, 'course_id': 2, 'hard': 5},
        {'year': 2019, 'discipline': 'Алгоритмы и структуры данных', 'semestr': 2, 'type': 1, 'course_id': 2,
         'hard': 2},
        {'year': 2019, 'discipline': 'Основы программирования', 'semestr': 2, 'type': 1, 'course_id': 2, 'hard': 3},
        {'year': 2019, 'discipline': 'Физическая культура и спорт', 'semestr': 2, 'type': 3, 'course_id': 2, 'hard': 0},
        {'year': 2019, 'discipline': 'Алгебра', 'semestr': 2, 'type': 2, 'course_id': 2, 'hard': 2},
        {'year': 2019, 'discipline': 'Архитектура вычислительных систем', 'semestr': 2, 'type': 1, 'course_id': 2,
         'hard': 3},
        {'year': 2019, 'discipline': 'Геометрия', 'semestr': 2, 'type': 2, 'course_id': 2, 'hard': 4},
        {'year': 2019, 'discipline': 'Иностранный язык', 'semestr': 2, 'type': 3, 'course_id': 2, 'hard': 3},
        {'year': 2019, 'discipline': 'Введение в программную инженерию', 'semestr': 3, 'type': 3, 'course_id': 2,
         'hard': 3},
        {'year': 2019, 'discipline': 'Практикум на ЭВМ', 'semestr': 3, 'type': 1, 'course_id': 2,
         'hard': 3},
        {'year': 2019, 'discipline': 'История России (онлайн-курс)', 'semestr': 3, 'type': 3, 'course_id': 2,
         'hard': 3},
        {'year': 2019, 'discipline': 'Математический анализ', 'semestr': 3, 'type': 2, 'course_id': 2,
         'hard': 4},
        {'year': 2019, 'discipline': 'Операционные системы', 'semestr': 3, 'type': 1, 'course_id': 2,
         'hard': 3},
        {'year': 2019, 'discipline': 'Алгоритмы и анализ сложности', 'semestr': 3, 'type': 2, 'course_id': 2,
         'hard': 4},
        {'year': 2019, 'discipline': 'Физическая культура и спорт', 'semestr': 3, 'type': 3, 'course_id': 2,
         'hard': 0},
        {'year': 2019, 'discipline': 'Язык эффективной коммуникации (онлайн-курс)', 'semestr': 3, 'type': 3,
         'course_id': 2,
         'hard': 1},
        {'year': 2019, 'discipline': 'Функциональное программирование', 'semestr': 3, 'type': 1, 'course_id': 2,
         'hard': 2},
        {'year': 2019, 'discipline': 'Инженерная экономика', 'semestr': 3, 'type': 3, 'course_id': 2,
         'hard': 2},
        {'year': 2019, 'discipline': 'Учебная практика (научноисследовательская работа)', 'semestr': 3, 'type': 1,
         'course_id': 2,
         'hard': 2},
        {'year': 2019, 'discipline': 'Иностранный язык', 'semestr': 3, 'type': 3, 'course_id': 2,
         'hard': 2},
        {'year': 2019, 'discipline': 'Разработка программного обеспечения', 'semestr': 4, 'type': 1, 'course_id': 2,
         'hard': 3},
        {'year': 2019, 'discipline': 'Дифференциальные и разностные уравнения', 'semestr': 4, 'type': 2, 'course_id': 2,
         'hard': 5},
        {'year': 2019, 'discipline': 'Практикум на ЭВМ', 'semestr': 4, 'type': 1, 'course_id': 2,
         'hard': 4},
        {'year': 2019, 'discipline': 'Основы бизнеса (онлайн-курс)', 'semestr': 4, 'type': 3, 'course_id': 2,
         'hard': 1},
        {'year': 2019, 'discipline': 'Человеко-машинное взаимодействие', 'semestr': 4, 'type': 1, 'course_id': 2,
         'hard': 1},
        {'year': 2019, 'discipline': ' Теория вероятностей и математическая статистика', 'semestr': 4, 'type': 2,
         'course_id': 2,
         'hard': 4},
        {'year': 2019, 'discipline': 'Физическая культура и спорт', 'semestr': 3, 'type': 3, 'course_id': 2,
         'hard': 0},
        {'year': 2019, 'discipline': 'Вычислительная математика', 'semestr': 4, 'type': 2, 'course_id': 2,
         'hard': 3},
        {'year': 2019, 'discipline': ' Математическая логика', 'semestr': 4, 'type': 1, 'course_id': 2,
         'hard': 3},
        {'year': 2019, 'discipline': 'Учебная практика (научно-исследовательская работа)', 'semestr': 4, 'type': 1,
         'course_id': 2,
         'hard': 3},
        {'year': 2019, 'discipline': 'Иностранный язык', 'semestr': 3, 'type': 3, 'course_id': 2,
         'hard': 2},
    ]

    thesis = []
    posts = [
        {'title': 'Это пробная новость с URI', 'uri': 'https://se.math.spbu.ru/', 'author_id': 1},
        {'title': 'Это пробная новость с текстом', 'text': 'Это моя первая новость, посмотрим, как она выглядит?',
         'author_id': 2}
    ]

    company = [
        {'name': 'Raidix', 'logo_uri': 'raidix.png'},
        {'name': 'Digital Design', 'logo_uri': 'digital_design.png'}
    ]

    themes_level = [
        {'level': '2 курс'},
        {'level': '3 курс'},
        {'level': 'Бакалаврская ВКР'},
        {'level': 'Магистерская ВКР'}
    ]

    areas = [
        {'area': 'Направление обучения'},
        {'area': 'Технологии программирования'},
        {'area': 'Программная инженерия'},
        {'area': 'Математика и компьютерные науки'},
        {'area': 'Механика и математическое моделирование'},
        {'area': 'Прикладная математика, программирование и искусственный интеллект'},
        {'area': 'Программная инженерия'},
        {'area': 'Астрономия (специалитет)'},
        {'area': 'Фундаментальная механика (специалитет)'}
    ]

    d_themes = [
        {'title': 'Изучение журналирования для all flash RAID массива',
         'description': 'Журналирование позволяет решить проблему write-hole и порчу данных в случае сложных отказов системы. В рамках задачи предлагается изучить технологию журналирования в Linux dm-log. Исследование включает в себя функциональные возможности, параметры настройки, производительность при различных паттернах. Интегрирование с нашим RAID engine. Возможна исследование и реализация и различных подходов к журналирования внутри RAID engine а не сторонними средствами, для того чтобы получить более производительное решение.',
         'levels': [1, 2],
         'company_id': 1,
         'supervisor_id': 5,
         'consultant_id': 4,
         'author_id': 4,
         'status': 2
         },
        {'title': 'Оптимизация алгоритма адаптивного объединения запросов в RAID',
         'description': 'При последовательной записи объединение запросов позволят решить проблему read-modify-write на RAID с контрольными суммами. Имеющийся алгоритм зависит от нескольких параметров и есть ряд наработок, которые позволяют автоматически подстраивать параметры в зависимости от нагрузки (размер ио, интенсивность, многопоточность), однако не справляется с некоторыми паттернами. В рамках работы необходимо изучить алгоритм адаптивного объединения, улучшить его или предложить альтернативный. Также предполагает изучения объединения запросов не только на искусственных паттернах.',
         'levels': [1, 2, 3],
         'company_id': 1,
         'supervisor_id': 5,
         'consultant_id': 4,
         'author_id': 3,
         'status': 2
         },
        {'title': 'Изучение RAM кэша для RAID массива',
         'description': 'В рамках работы планируется изучить технологии Open Cache Acceleration Software для реализации RAM cache или кэш на быстрых накопителях для нашего RAID engine. Изучение включает в себя функциональные возможности, параметры и настройку, производительность в различных конфигурациях и паттернах нагрузки. Внедрение технологии, ее улучшение и адаптация под наш RAID. Возможно изучение и сравнение с имеющимися технологиями кеширования в Linux такими как dm-cache, bcache. Возможно также углубление в изучение алгоритмов Read-Ahead.',
         'levels': [3, 4],
         'company_id': 2,
         'supervisor_id': 5,
         'consultant_id': 4,
         'author_id': 4,
         'status': 2
         },
    ]


    # Check if db file already exists. If so, backup it
    db_file = Path(SQLITE_DATABASE_NAME)
    if db_file.is_file():
        shutil.copyfile(SQLITE_DATABASE_NAME, SQLITE_DATABASE_BACKUP_NAME)

    # Init DB
    db.session.commit()  # https://stackoverflow.com/questions/24289808/drop-all-freezes-in-flask-with-sqlalchemy
    db.drop_all()
    db.create_all()

    # Create areas
    print("Create areas")
    for area in areas:
        a = AreasOfStudy(area=area['area'])

        db.session.add(a)
        db.session.commit()

    # Create users
    print("Create users")
    for user in users:
        u = Users(email=user['email'], password_hash=generate_password_hash(urandom(16).hex()),
                  first_name=user['first_name'], last_name=user['last_name'],
                  middle_name=user['middle_name'], avatar_uri=user['avatar_uri'])

        db.session.add(u)
        db.session.commit()

    # Create staff
    print("Create staff")
    for user in staff:
        u = Users.query.filter_by(email=user['official_email']).first()

        if 'science_degree' in user:
            s = Staff(position=user['position'], science_degree=user['science_degree'],
                      official_email=user['official_email'], still_working=user['still_working'],
                      user_id=u.id)
        else:
            s = Staff(position=user['position'], official_email=user['official_email'],
                      still_working=user['still_working'], user_id=u.id)

        db.session.add(s)
        db.session.commit()

    # Create WorkTypes
    print("Create worktypes")
    for w in wtypes:
        wt = Worktype(type=w['type'])
        db.session.add(wt)
        db.session.commit()

    # Create Courses
    print("Create courses")
    for course in courses:
        c = Courses(name=course['name'], code=course['code'])
        db.session.add(c)
        db.session.commit()

    # Create Curriculum
    print("Create curriculum")
    for cur in curriculum:
        if 'type' in cur:
            c = Curriculum(year=cur['year'], discipline=cur['discipline'], study_year=cur['study_year'],
                           type=cur['type'], course_id=cur['course_id'])
        else:
            c = Curriculum(year=cur['year'], discipline=cur['discipline'], study_year=cur['study_year'],
                           course_id=cur['course_id'])

        db.session.add(c)
        db.session.commit()

    # Create News
    print("Create news")
    for cur in posts:
        if 'uri' in cur:
            c = Posts(title=cur['title'], uri=cur['uri'], domain='se.math.spbu.ru', author_id=cur['author_id'])
        else:
            c = Posts(title=cur['title'], text=cur['text'], author_id=cur['author_id'])

        db.session.add(c)
        db.session.commit()

    for tag in tags:
        t = Tags(name=tag['name'])
        db.session.add(t)
        db.session.commit()

    # Create Thesis
    print("Create thesis")
    for work in thesis:
        if 'source_uri' in work:
            t = Thesis(name_ru=work['name_ru'], name_en=work['name_en'], description=work['description'],
                       text_uri=work['text_uri'], presentation_uri=work['presentation_uri'],
                       supervisor_review_uri=work['supervisor_review_uri'],
                       reviewer_review_uri=work['reviewer_review_uri'],
                       author=work['author'], supervisor_id=work['supervisor_id'], reviewer_id=work['reviewer_id'],
                       publish_year=work['publish_year'], type_id=work['type_id'], course_id=1,
                       source_uri=work['source_uri'])
        else:
            t = Thesis(name_ru=work['name_ru'], name_en=work['name_en'], description=work['description'],
                       text_uri=work['text_uri'], presentation_uri=work['presentation_uri'],
                       supervisor_review_uri=work['supervisor_review_uri'],
                       reviewer_review_uri=work['reviewer_review_uri'],
                       author=work['author'], supervisor_id=work['supervisor_id'], reviewer_id=work['reviewer_id'],
                       publish_year=work['publish_year'], type_id=work['type_id'], course_id=1)

        db.session.add(t)
        db.session.commit()

        # Adds tags
        records = Tags.query.all()
        for tag in records:
            t.tags.append(tag)
            db.session.commit()

    # Create Companies
    print("Create companies")
    for cur in company:
        c = Company(name=cur['name'], logo_uri=cur['logo_uri'])

        db.session.add(c)
        db.session.commit()

    # Create ThemesLevels
    print("Create diploma theme levels")
    for cur in themes_level:
        c = ThemesLevel(level=cur['level'])

        db.session.add(c)
        db.session.commit()

    # Create DiplomaThems
    print("Create diploma themes")
    for cur in d_themes:

        c = DiplomaThemes(title=cur['title'], description=cur['description'],
                          company_id=cur['company_id'], supervisor_id=cur['supervisor_id'],
                          consultant_id=cur['consultant_id'], author_id=cur['author_id'],
                          status=cur['status'])

        for tl_id in cur['levels']:
            c.levels.append(ThemesLevel.query.filter_by(id=tl_id).first())

        db.session.add(c)
        db.session.commit()

    # Create InternshipsFormat
    print("Create internship formats")
    print("Create addinternship formats")
    for cur in internship_formats:
        c = InternshipFormat(format=cur['format'])

        db.session.add(c)
        db.session.commit()

    print("Create internship tags")
    for cur in internship_tags:
        t = InternshipTag(tag=cur['tag'])

        db.session.add(t)
        db.session.commit()

# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0

import shutil
from datetime import datetime
from os import urandom
from pathlib import Path

from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from flask_whooshee import Whooshee
from sqlalchemy import MetaData
from werkzeug.security import generate_password_hash

from flask_se_config import (
    SQLITE_DATABASE_BACKUP_NAME,
    SQLITE_DATABASE_NAME,
    SQLITE_DATABASE_PATH,
    get_hours_since,
    post_ranking_score,
)

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

metadata = MetaData(naming_convention=convention)
db = SQLAlchemy(metadata=metadata)
whooshee = Whooshee()

tag = db.Table(
    "tag",
    db.Column("tag_id", db.Integer, db.ForeignKey("tags.id"), primary_key=True),
    db.Column("thesis_id", db.Integer, db.ForeignKey("thesis.id"), primary_key=True),
)

diploma_themes_tag = db.Table(
    "diploma_themes_tag",
    db.Column(
        "diploma_themes_tag_id",
        db.Integer,
        db.ForeignKey("diploma_themes_tags.id"),
        primary_key=True,
    ),
    db.Column(
        "diploma_themes_id",
        db.Integer,
        db.ForeignKey("diploma_themes.id"),
        primary_key=True,
    ),
)

diploma_themes_level = db.Table(
    "diploma_themes_level",
    db.Column(
        "themes_level_id",
        db.Integer,
        db.ForeignKey("themes_level.id"),
        primary_key=True,
    ),
    db.Column(
        "diploma_themes_id",
        db.Integer,
        db.ForeignKey("diploma_themes.id"),
        primary_key=True,
    ),
)

internships_format = db.Table(
    "internships_format",
    db.Column(
        "internships_format_id",
        db.Integer,
        db.ForeignKey("internship_format.id"),
        primary_key=True,
    ),
    db.Column("internships_id", db.Integer, db.ForeignKey("internships.id"), primary_key=True),
)

internships_tag = db.Table(
    "internships_tag",
    db.Column(
        "internships_tag_id",
        db.Integer,
        db.ForeignKey("internship_tag.id"),
        primary_key=True,
    ),
    db.Column("internships_id", db.Integer, db.ForeignKey("internships.id"), primary_key=True),
)


class Staff(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    official_email = db.Column(db.String(255), unique=True, nullable=False)
    position = db.Column(db.String(255), nullable=False)
    science_degree = db.Column(db.String(255), nullable=True)
    still_working = db.Column(db.Boolean, default=False, nullable=False)

    supervisor = db.relationship(
        "Thesis", backref=db.backref("supervisor"), foreign_keys="Thesis.supervisor_id"
    )
    adviser = db.relationship(
        "Thesis", backref=db.backref("reviewer"), foreign_keys="Thesis.reviewer_id"
    )
    current_thesises = db.relationship("CurrentThesis", backref=db.backref("supervisor"))

    def __repr__(self):
        return f"<{self.official_email!r}>"

    def __str__(self):
        return self.user.get_name()


@whooshee.register_model("first_name", "middle_name", "last_name")
class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)

    email = db.Column(db.String(255), unique=True, nullable=True)
    password_hash = db.Column(db.String(255), unique=False, nullable=True)

    first_name = db.Column(db.String(255), nullable=False)
    middle_name = db.Column(db.String(255), nullable=True)
    last_name = db.Column(db.String(255), nullable=True)

    avatar_uri = db.Column(db.String(512), default="empty.jpg", nullable=False)

    role = db.Column(db.Integer, default=0, nullable=False)
    how_to_contact = db.Column(db.String(512), default="", nullable=True)

    vk_id = db.Column(db.String(255), nullable=True)
    fb_id = db.Column(db.String(255), nullable=True)
    google_id = db.Column(db.String(255), nullable=True)

    staff = db.relationship("Staff", backref=db.backref("user", uselist=False))
    news = db.relationship("Posts", backref=db.backref("author", uselist=False))
    diploma_themes_supervisor = db.relationship(
        "DiplomaThemes",
        backref=db.backref("supervisor", uselist=False),
        foreign_keys="DiplomaThemes.supervisor_id",
    )
    diploma_themes_thesis_supervisor = db.relationship(
        "DiplomaThemes",
        backref=db.backref("supervisor_thesis", uselist=False),
        foreign_keys="DiplomaThemes.supervisor_thesis_id",
    )
    diploma_themes_consultant = db.relationship(
        "DiplomaThemes",
        backref=db.backref("consultant", uselist=False),
        foreign_keys="DiplomaThemes.consultant_id",
    )
    diploma_themes_author = db.relationship(
        "DiplomaThemes",
        backref=db.backref("author", uselist=False),
        foreign_keys="DiplomaThemes.author_id",
    )

    current_thesises = db.relationship("CurrentThesis", backref=db.backref("user", uselist=False))
    thesises = db.relationship("Thesis", backref=db.backref("owner", uselist=False))
    thesis_on_review_author = db.relationship(
        "ThesisOnReview", backref=db.backref("author", uselist=False)
    )

    reviewer = db.relationship("Reviewer", back_populates="user")

    all_user_votes = db.relationship("PostVote", back_populates="user")
    internship_author = db.relationship(
        "Internships",
        backref=db.backref("user", uselist=False),
        foreign_keys="Internships.author_id",
    )

    def get_name(self):
        full_name = ""
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
        full_name = ""
        if self.last_name:
            full_name = str(self.last_name)

        if self.first_name:
            full_name = full_name + " " + self.first_name

        if self.middle_name:
            full_name = full_name + " " + self.middle_name

        if self.email:
            return full_name + " (" + self.email + ")"
        else:
            return full_name

    def __repr__(self):
        full_name = ""
        if self.last_name:
            full_name = full_name + self.last_name

        if self.first_name:
            full_name = full_name + " " + self.first_name

        if self.middle_name:
            full_name = full_name + " " + self.middle_name

        return full_name


class InternshipFormat(db.Model):
    __tablename__ = "internship_format"

    id = db.Column(db.Integer, primary_key=True)
    format = db.Column(db.String(100), nullable=False)

    def __str__(self):
        return "{self.format}"


class InternshipTag(db.Model):
    __tablename__ = "internship_tag"

    id = db.Column(db.Integer, primary_key=True)
    tag = db.Column(db.String(100), nullable=False)

    def __str__(self):
        return self.tag


class CurrentThesis(db.Model):
    __tablename__ = "current_thesis"

    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    area_id = db.Column(db.Integer, db.ForeignKey("areas_of_study.id"), nullable=True)

    title = db.Column(db.String(512), nullable=True)

    supervisor_id = db.Column(db.Integer, db.ForeignKey("staff.id"), nullable=True)
    worktype_id = db.Column(db.Integer, db.ForeignKey("worktype.id"), nullable=False)
    consultant = db.Column(db.String(2048), nullable=True)

    goal = db.Column(db.String(2048), nullable=True)

    text_uri = db.Column(db.String(512), nullable=True)
    supervisor_review_uri = db.Column(db.String(512), nullable=True)
    reviewer_review_uri = db.Column(db.String(512), nullable=True)
    presentation_uri = db.Column(db.String(512), nullable=True)

    text_link = db.Column(db.String(2048), nullable=True)
    presentation_link = db.Column(db.String(2048), nullable=True)
    code_link = db.Column(db.String(2048), nullable=True)
    account_name = db.Column(db.String(512), nullable=True)

    reports = db.relationship("ThesisReport", backref=db.backref("practice"))
    tasks = db.relationship("ThesisTask", backref=db.backref("practice"))

    archived = db.Column(db.Boolean, default=False)
    deleted = db.Column(db.Boolean, default=False)
    status = db.Column(db.Integer, default=1)
    # 1 - active practice
    # 2 - past practice

    def __init__(self, author_id, worktype_id, area_id, **kwargs):
        self.author_id = author_id
        self.worktype_id = worktype_id
        self.area_id = area_id
        super().__init__(**kwargs)

    def __repr__(self):
        return self.title


class NotificationPractice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    recipient_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
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
    worktype_id = db.Column(db.Integer, db.ForeignKey("worktype.id"), nullable=False)
    area_id = db.Column(db.Integer, db.ForeignKey("areas_of_study.id"), nullable=False)

    choose_topic = db.Column(db.DateTime, nullable=True)
    submit_work_for_review = db.Column(db.DateTime, nullable=True)
    upload_reviews = db.Column(db.DateTime, nullable=True)

    pre_defense = db.Column(db.DateTime, nullable=True)
    defense = db.Column(db.DateTime, nullable=True)


class ThesisTask(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task_text = db.Column(db.String(2048), nullable=False)
    deleted = db.Column(db.Boolean, default=False)
    current_thesis_id = db.Column(db.Integer, db.ForeignKey("current_thesis.id"))

    def __init__(self, task_text, current_thesis_id, **kwargs):
        self.task_text = task_text
        self.current_thesis_id = current_thesis_id
        super().__init__(**kwargs)

    def __repr__(self):
        return self.task_text


class ThesisReport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    current_thesis_id = db.Column(db.Integer, db.ForeignKey("current_thesis.id"))

    was_done = db.Column(db.String(2048), nullable=True)
    planned_to_do = db.Column(db.String(2048), nullable=True)
    time = db.Column(db.DateTime, default=datetime.utcnow)

    deleted = db.Column(db.Boolean, default=False)

    comment = db.Column(db.String(2048), nullable=True)
    comment_time = db.Column(db.DateTime, nullable=True)

    def __init__(self, was_done, planned_to_do, current_thesis_id, author_id, **kwargs):
        self.was_done = was_done
        self.planned_to_do = planned_to_do
        self.current_thesis_id = current_thesis_id
        self.author_id = author_id
        super().__init__(**kwargs)


class InternshipCompany(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(512), nullable=False)
    logo_uri = db.Column(db.String(512), nullable=True)
    internship = db.relationship("Internships", back_populates="company")

    def __str__(self):
        return self.name


class Internships(db.Model):
    __tablename__ = "internships"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    name_vacancy = db.Column(db.String(70), nullable=False)
    salary = db.Column(db.String(30), nullable=False)
    company = db.relationship("InternshipCompany", back_populates="internship")
    company_id = db.Column(db.Integer, db.ForeignKey("internship_company.id"))
    requirements = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    more_inf = db.Column(db.String, nullable=True)  # СЃСЃС‹Р»РєР° РЅР° СЃР°Р№С‚
    description = db.Column(
        db.String, nullable=True
    )  # РєРѕСЂРѕС‚РєРѕРµ РѕРїРёСЃР°РЅРёРµ С‚РѕРіРѕ, С‡РµРј РЅСѓР¶РЅРѕ Р±СѓРґРµС‚ Р·Р°РЅРёРјР°С‚СЊСЃСЏ
    location = db.Column(db.String(50), nullable=True)
    format = db.relationship(
        "InternshipFormat",
        secondary=internships_format,
        lazy="subquery",
        backref=db.backref("internship", lazy=True),
        order_by=internships_format.c.internships_format_id,
    )
    tag = db.relationship(
        "InternshipTag",
        secondary=internships_tag,
        lazy="subquery",
        backref=db.backref("internship", lazy=True),
        order_by=internships_tag.c.internships_tag_id,
    )

    author_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    def __repr__(self):
        return self.name_vacancy

    def __self__(self):
        return self.name_vacancy


# Practice, diploma
class Worktype(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(255), nullable=False)

    thesis = db.relationship("Thesis", backref=db.backref("type", uselist=False))
    thesis_on_review = db.relationship(
        "ThesisOnReview", backref=db.backref("worktype", uselist=False)
    )
    current_thesis = db.relationship("CurrentThesis", backref=db.backref("worktype"))
    deadline = db.relationship("Deadline", backref=db.backref("worktype", uselist=False))

    def __repr__(self):
        return self.type


# Thesis on review worktypes
class ThesisOnReviewWorktype(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(255), nullable=False)

    thesis_on_review = db.relationship(
        "ThesisOnReview", backref=db.backref("thesis_on_review_worktype", uselist=False)
    )

    def __repr__(self):
        return self.type


# Courses
class Courses(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    code = db.Column(db.String(15), nullable=False)

    thesis = db.relationship("Thesis", backref=db.backref("course", uselist=False))
    curriculum = db.relationship("Curriculum", backref=db.backref("course", uselist=False))

    def __repr__(self):
        return f"<{self.name!r}>"


@whooshee.register_model("name_ru", "description", "author", "text")
class Thesis(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    type_id = db.Column(db.Integer, db.ForeignKey("worktype.id"), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey("courses.id"), nullable=False)

    area_id = db.Column(db.Integer, db.ForeignKey("areas_of_study.id"), nullable=True)

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
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    supervisor_id = db.Column(db.Integer, db.ForeignKey("staff.id"), nullable=True)
    reviewer_id = db.Column(db.Integer, db.ForeignKey("staff.id"), nullable=True)

    publish_year = db.Column(db.Integer, nullable=False)
    recomended = db.Column(db.Boolean, default=False, nullable=False)
    temporary = db.Column(db.Boolean, default=False, nullable=False)
    text = db.Column(db.Text, nullable=True)

    # 0 - success review (or not needed)
    # 1 - need to review
    # 2 - on review (in progress)
    # 3 - failed to review
    review_status = db.Column(db.Integer, nullable=True, default=10)

    review = db.relationship("ThesisReview", back_populates="thesis")

    download_thesis = db.Column(db.Integer, default=0, nullable=True)
    download_presentation = db.Column(db.Integer, default=0, nullable=True)


class AreasOfStudy(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    area = db.Column(db.String(512), nullable=False)

    current_thesis = db.relationship("CurrentThesis", backref=db.backref("area", uselist=False))
    thesis = db.relationship("Thesis", backref=db.backref("area", uselist=False))
    thesis_on_review = db.relationship("ThesisOnReview", backref=db.backref("area", uselist=False))

    def __repr__(self):
        return self.area


class Tags(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    tags = db.relationship(
        "Thesis", secondary=tag, lazy="subquery", backref=db.backref("tags", lazy=True)
    )


class Curriculum(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer, nullable=False)
    discipline = db.Column(db.String(256), nullable=False)
    study_year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(1024), nullable=True)
    type = db.Column(db.Integer, nullable=False, default=1)

    course_id = db.Column(db.Integer, db.ForeignKey("courses.id"), nullable=False)


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
    updated_on = db.Column(
        db.DateTime(timezone=True),
        server_default=db.func.now(),
        server_onupdate=db.func.now(),
    )

    rank = db.Column(db.Float, nullable=False, default=post_ranking_score)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    all_news_votes = db.relationship("PostVote", back_populates="post")

    type_id = db.Column(db.Integer, db.ForeignKey("post_type.id"))
    type = db.relationship("PostType", back_populates="post")


class PostVote(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)
    user = db.relationship("Users", back_populates="all_user_votes")

    post_id = db.Column(db.Integer, db.ForeignKey("posts.id"))
    post = db.relationship("Posts", back_populates="all_news_votes")

    upvote = db.Column(db.Boolean, nullable=False)
    timestamp = db.Column(db.DateTime, server_default=db.func.now())

    def __repr__(self):
        vote = "Up" if self.upvote else "Down"
        return f"<Vote - {vote}, from {self.user.get_name()} for {self.post.title}>"


class PostType(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    type = db.Column(db.Integer, nullable=False, default=1)
    name = db.Column(db.String(512), nullable=False)

    post = db.relationship("Posts", back_populates="type")

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
    status = db.Column(
        db.Integer, default=0, nullable=False
    )  # 0 - new, 1 - need update, 2 - approved, 3 - archive, 4 - rejected

    comment = db.Column(db.String(2048), nullable=True)

    levels = db.relationship(
        "ThemesLevel",
        secondary=diploma_themes_level,
        lazy="subquery",
        backref=db.backref("diploma_themes", lazy=True),
        order_by=diploma_themes_level.c.themes_level_id,
    )

    company_id = db.Column(db.Integer, db.ForeignKey("company.id"))
    company = db.relationship("Company", back_populates="theme")

    author_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    supervisor_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    supervisor_thesis_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    consultant_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    def __repr__(self):
        return f"{self.title}"

    def __str__(self):
        return f"{self.title}"


class DiplomaThemesTags(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    tags = db.relationship(
        "DiplomaThemes",
        secondary=diploma_themes_tag,
        lazy="subquery",
        backref=db.backref("diploma_themes_tags", lazy=True),
    )


class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(512), nullable=False)
    logo_uri = db.Column(db.String(512), nullable=True)
    status = db.Column(db.Integer, default=0, nullable=True)

    theme = db.relationship("DiplomaThemes", back_populates="company")
    reviewer = db.relationship("Reviewer", back_populates="company")

    def __str__(self):
        return f"{self.name}"


class ThesisReview(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    thesis_id = db.Column(db.Integer, db.ForeignKey("thesis.id"))
    thesis = db.relationship("Thesis", back_populates="review")

    thesis_on_review_id = db.Column(db.Integer, db.ForeignKey("thesis_on_review.id"))
    thesis_on_review = db.relationship("ThesisOnReview", back_populates="review")

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

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    user = db.relationship("Users", back_populates="reviewer")

    company_id = db.Column(db.Integer, db.ForeignKey("company.id"), nullable=True)
    company = db.relationship("Company", back_populates="reviewer")

    reviewer = db.relationship("ThesisOnReview", back_populates="reviewer")

    def __str__(self):
        return self.user.get_name()


class ThesisOnReview(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    type_id = db.Column(db.Integer, db.ForeignKey("worktype.id"), nullable=False)
    area_id = db.Column(db.Integer, db.ForeignKey("areas_of_study.id"), nullable=True)

    thesis_on_review_type_id = db.Column(
        db.Integer, db.ForeignKey("thesis_on_review_worktype.id"), nullable=True
    )

    name_ru = db.Column(db.String(512), nullable=False)

    text_uri = db.Column(db.String(512), nullable=True)
    presentation_uri = db.Column(db.String(512), nullable=True)
    source_uri = db.Column(db.String(512), nullable=True)

    author_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    reviewer_id = db.Column(db.Integer, db.ForeignKey("reviewer.id"), nullable=True)
    reviewer = db.relationship("Reviewer", back_populates="reviewer")

    supervisor_id = db.Column(db.Integer, db.ForeignKey("staff.id"), nullable=True)

    # 0 - success review (or not needed)
    # 1 - need to review
    # 2 - on review (in progress)
    # 3 - failed to review
    review_status = db.Column(db.Integer, nullable=True, default=10)
    review = db.relationship("ThesisReview", back_populates="thesis_on_review")

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

    recipient = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
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
        {
            "email": "a.terekhov@spbu.ru",
            "first_name": "РђРЅРґСЂРµР№",
            "last_name": "РўРµСЂРµС…РѕРІ",
            "middle_name": "РќРёРєРѕР»Р°РµРІРёС‡",
            "avatar_uri": "terekhov.jpg",
        },
        {
            "email": "o.granichin@spbu.ru",
            "first_name": "РћР»РµРі",
            "last_name": "Р“СЂР°РЅРёС‡РёРЅ",
            "middle_name": "РќРёРєРѕР»Р°РµРІРёС‡",
            "avatar_uri": "granichin.jpg",
        },
        {
            "email": "d.koznov@spbu.ru",
            "first_name": "Р”РјРёС‚СЂРёР№",
            "last_name": "РљРѕР·РЅРѕРІ",
            "middle_name": "Р’Р»Р°РґРёРјРёСЂРѕРІРёС‡",
            "avatar_uri": "koznov.jpg",
        },
        {
            "email": "t.bryksin@spbu.ru",
            "first_name": "РўРёРјРѕС„РµР№",
            "last_name": "Р‘СЂС‹РєСЃРёРЅ",
            "middle_name": "РђР»РµРєСЃР°РЅРґСЂРѕРІРёС‡",
            "avatar_uri": "bryksin.jpg",
        },
        {
            "email": "d.bylychev@spbu.ru",
            "first_name": "Р”РјРёС‚СЂРёР№",
            "last_name": "Р‘СѓР»С‹С‡РµРІ",
            "middle_name": "Р®СЂСЊРµРІРёС‡",
            "avatar_uri": "boulytchev.jpg",
        },
        {
            "email": "y.litvinov@spbu.ru",
            "first_name": "Р®СЂРёР№",
            "last_name": "Р›РёС‚РІРёРЅРѕРІ",
            "middle_name": "Р’РёРєС‚РѕСЂРѕРІРёС‡",
            "avatar_uri": "litvinov.jpg",
        },
        {
            "email": "d.lutsiv@spbu.ru",
            "first_name": "Р”РјРёС‚СЂРёР№",
            "last_name": "Р›СѓС†РёРІ",
            "middle_name": "Р’Р°РґРёРјРѕРІРёС‡",
            "avatar_uri": "luciv.jpg",
        },
        {
            "email": "k.romanovsky@spbu.ru",
            "first_name": "РљРѕРЅСЃС‚Р°РЅС‚РёРЅ",
            "last_name": "Р РѕРјР°РЅРѕРІСЃРєРёР№",
            "middle_name": "Р®СЂСЊРµРІРёС‡",
            "avatar_uri": "empty.jpg",
        },
        {
            "email": "m.serov@spbu.ru",
            "first_name": "РњРёС…Р°РёР»",
            "last_name": "РЎРµСЂРѕРІ",
            "middle_name": "РђР»РµРєСЃР°РЅРґСЂРѕРІРёС‡",
            "avatar_uri": "empty.jpg",
        },
        {
            "email": "s.s.sysoev@spbu.ru",
            "first_name": "РЎРµСЂРіРµР№",
            "last_name": "РЎС‹СЃРѕРµРІ",
            "middle_name": "РЎРµСЂРіРµРµРІРёС‡",
            "avatar_uri": "empty.jpg",
        },
        {
            "email": "m.baklanovsky@spbu.ru",
            "first_name": "РњР°РєСЃРёРј",
            "last_name": "Р‘Р°РєР»Р°РЅРѕРІСЃРєРёР№",
            "middle_name": "Р’РёРєС‚РѕСЂРѕРІРёС‡",
            "avatar_uri": "baklanovsky.jpg",
        },
        {
            "email": "m.m.zhuravlev@spbu.ru",
            "first_name": "РњР°РєСЃРёРј",
            "last_name": "Р–СѓСЂР°РІР»РµРІ",
            "middle_name": "РњРёС…Р°Р№Р»РѕРІРёС‡",
            "avatar_uri": "zhuravlev.jpg",
        },
        {
            "email": "i.zelenchuk@spbu.ru",
            "first_name": "РР»СЊСЏ",
            "last_name": "Р—РµР»РµРЅС‡СѓРє",
            "middle_name": "Р’Р°Р»РµСЂСЊРµРІРёС‡",
            "avatar_uri": "zelenchuk.jpg",
        },
        {
            "email": "y.kirilenko@spbu.ru",
            "first_name": "РЇРєРѕРІ",
            "last_name": "РљРёСЂРёР»РµРЅРєРѕ",
            "middle_name": "РђР»РµРєСЃР°РЅРґСЂРѕРІРёС‡",
            "avatar_uri": "kirilenko.jpg",
        },
        {
            "email": "st035425@student.spbu.ru",
            "first_name": "РђРЅС‚РѕРЅ",
            "last_name": "РљРѕР·Р»РѕРІ",
            "middle_name": "РџР°РІР»РѕРІРёС‡",
            "avatar_uri": "empty.jpg",
        },
        {
            "email": "egor.k.kulikov@gmail.com",
            "first_name": "Р•РіРѕСЂ",
            "last_name": "РљСѓР»РёРєРѕРІ",
            "middle_name": "РљРѕРЅСЃС‚Р°РЅС‚РёРЅРѕРІРёС‡",
            "avatar_uri": "kulikov.jpg",
        },
        {
            "email": "d.mordvinov@spbu.ru",
            "first_name": "Р”РјРёС‚СЂРёР№",
            "last_name": "РњРѕСЂРґРІРёРЅРѕРІ",
            "middle_name": "РђР»РµРєСЃР°РЅРґСЂРѕРІРёС‡",
            "avatar_uri": "mordvinov.jpg",
        },
        {
            "email": "m.nemeshev@spbu.ru",
            "first_name": "РњР°СЂР°С‚",
            "last_name": "РќРµРјРµС€РµРІ",
            "middle_name": "РҐР°Р»РёРјРѕРІРёС‡",
            "avatar_uri": "nemeshev.jpg",
        },
        {
            "email": "stanislav.sartasov@spbu.ru",
            "first_name": "РЎС‚Р°РЅРёСЃР»Р°РІ",
            "last_name": "РЎР°СЂС‚Р°СЃРѕРІ",
            "middle_name": "Р®СЂСЊРµРІРёС‡",
            "avatar_uri": "empty.jpg",
        },
        {
            "email": "m.n.smirnov@spbu.ru",
            "first_name": "РњРёС…Р°РёР»",
            "last_name": "РЎРјРёСЂРЅРѕРІ",
            "middle_name": "РќРёРєРѕР»Р°РµРІРёС‡",
            "avatar_uri": "smirnov.jpg",
        },
        {
            "email": "st036451@student.spbu.ru",
            "first_name": "РђСЂС‚СѓСЂ",
            "last_name": "РҐР°РЅРѕРІ",
            "middle_name": "Р Р°С„Р°СЌР»СЊРµРІРёС‡",
            "avatar_uri": "khanov.jpg",
        },
        {
            "email": "s.shilov@spbu.ru",
            "first_name": "РЎРµСЂРіРµР№",
            "last_name": "РЁРёР»РѕРІ",
            "middle_name": "Р®СЂСЊРµРІРёС‡",
            "avatar_uri": "empty.jpg",
        },
        {
            "email": "st013464@student.spbu.ru",
            "first_name": "РџРµС‚СЂ",
            "last_name": "Р›РѕР·РѕРІ",
            "middle_name": "РђР»РµРєСЃРµРµРІРёС‡",
            "avatar_uri": "empty.jpg",
        },
        {
            "email": "st013039@student.spbu.ru",
            "first_name": "Р•РІРіРµРЅРёР№",
            "last_name": "РњРѕРёСЃРµРµРЅРєРѕ",
            "middle_name": "РђР»РµРєСЃР°РЅРґСЂРѕРІРёС‡",
            "avatar_uri": "empty.jpg",
        },
        {
            "email": "s.v.grigoriev@spbu.ru",
            "first_name": "РЎРµРјРµРЅ",
            "last_name": "Р“СЂРёРіРѕСЂСЊРµРІ",
            "middle_name": "Р’СЏС‡РµСЃР»Р°РІРѕРІРёС‡",
            "avatar_uri": "empty.jpg",
        },
        {
            "email": "pimenov_aa_stub@spbu.ru",
            "first_name": "РђР»РµРєСЃР°РЅРґСЂ",
            "last_name": "РџРёРјРµРЅРѕРІ",
            "middle_name": "РђР»РµРєСЃР°РЅРґСЂРѕРІРёС‡",
            "avatar_uri": "empty.jpg",
        },
        {
            "email": "s.salischev@spbu.ru",
            "first_name": "РЎРµСЂРіРµР№",
            "last_name": "РЎР°Р»РёС‰РµРІ",
            "middle_name": "РРіРѕСЂРµРІРёС‡",
            "avatar_uri": "empty.jpg",
        },
        {
            "email": "d.sagunov@spbu.ru",
            "first_name": "Р”Р°РЅРёР»",
            "last_name": "РЎР°РіСѓРЅРѕРІ",
            "middle_name": "Р“РµРѕСЂРіРёРµРІРёС‡",
            "avatar_uri": "empty.jpg",
        },
        {
            "email": "g.chernyshev@spbu.ru",
            "first_name": "Р“РµРѕСЂРіРёР№",
            "last_name": "Р§РµСЂРЅС‹С€РµРІ",
            "middle_name": "РђР»РµРєСЃРµРµРІРёС‡",
            "avatar_uri": "empty.jpg",
        },
    ]
    staff = [
        {
            "position": "Р—Р°РІРµРґСѓСЋС‰РёР№ РєР°С„РµРґСЂРѕР№, РїСЂРѕС„РµСЃСЃРѕСЂ",
            "science_degree": "Рґ.С„.-Рј.РЅ.",
            "official_email": "a.terekhov@spbu.ru",
            "still_working": True,
        },
        {
            "position": "РџСЂРѕС„РµСЃСЃРѕСЂ",
            "science_degree": "Рґ.С„.-Рј.РЅ.",
            "official_email": "o.granichin@spbu.ru",
            "still_working": True,
        },
        {
            "position": "РџСЂРѕС„РµСЃСЃРѕСЂ",
            "science_degree": "Рґ.С‚.РЅ.",
            "official_email": "d.koznov@spbu.ru",
            "still_working": True,
        },
        {
            "position": "Р”РѕС†РµРЅС‚",
            "science_degree": "Рє.С‚.РЅ.",
            "official_email": "t.bryksin@spbu.ru",
            "still_working": True,
        },
        {
            "position": "Р”РѕС†РµРЅС‚",
            "science_degree": "Рє.С„.-Рј.РЅ.",
            "official_email": "d.bylychev@spbu.ru",
            "still_working": True,
        },
        {
            "position": "Р”РѕС†РµРЅС‚",
            "science_degree": "Рє.С‚.РЅ.",
            "official_email": "y.litvinov@spbu.ru",
            "still_working": True,
        },
        {
            "position": "Р”РѕС†РµРЅС‚",
            "science_degree": "Рє.С„.-Рј.РЅ.",
            "official_email": "d.lutsiv@spbu.ru",
            "still_working": True,
        },
        {
            "position": "Р”РѕС†РµРЅС‚",
            "science_degree": "Рє.С„.-Рј.РЅ.",
            "official_email": "k.romanovsky@spbu.ru",
            "still_working": True,
        },
        {
            "position": "Р”РѕС†РµРЅС‚",
            "official_email": "m.serov@spbu.ru",
            "still_working": True,
        },
        {
            "position": "РџСЂРµРїРѕРґР°РІР°С‚РµР»СЊ-РїСЂР°РєС‚РёРє",
            "science_degree": "Рє.С„.-Рј.РЅ.",
            "official_email": "s.s.sysoev@spbu.ru",
            "still_working": True,
        },
        {
            "position": "РЎС‚Р°СЂС€РёР№ РїСЂРµРїРѕРґР°РІР°С‚РµР»СЊ",
            "official_email": "m.baklanovsky@spbu.ru",
            "still_working": True,
        },
        {
            "position": "РЎС‚Р°СЂС€РёР№ РїСЂРµРїРѕРґР°РІР°С‚РµР»СЊ",
            "official_email": "m.m.zhuravlev@spbu.ru",
            "still_working": True,
        },
        {
            "position": "РЎС‚Р°СЂС€РёР№ РїСЂРµРїРѕРґР°РІР°С‚РµР»СЊ",
            "official_email": "i.zelenchuk@spbu.ru",
            "still_working": True,
        },
        {
            "position": "РЎС‚Р°СЂС€РёР№ РїСЂРµРїРѕРґР°РІР°С‚РµР»СЊ",
            "official_email": "y.kirilenko@spbu.ru",
            "still_working": True,
        },
        {
            "position": "РЎС‚Р°СЂС€РёР№ РїСЂРµРїРѕРґР°РІР°С‚РµР»СЊ",
            "official_email": "st035425@student.spbu.ru",
            "still_working": True,
        },
        {
            "position": "РЎС‚Р°СЂС€РёР№ РїСЂРµРїРѕРґР°РІР°С‚РµР»СЊ",
            "official_email": "egor.k.kulikov@gmail.com",
            "still_working": True,
        },
        {
            "position": "РЎС‚Р°СЂС€РёР№ РїСЂРµРїРѕРґР°РІР°С‚РµР»СЊ",
            "official_email": "d.mordvinov@spbu.ru",
            "still_working": True,
        },
        {
            "position": "РЎС‚Р°СЂС€РёР№ РїСЂРµРїРѕРґР°РІР°С‚РµР»СЊ",
            "official_email": "m.nemeshev@spbu.ru",
            "still_working": True,
        },
        {
            "position": "РЎС‚Р°СЂС€РёР№ РїСЂРµРїРѕРґР°РІР°С‚РµР»СЊ",
            "official_email": "stanislav.sartasov@spbu.ru",
            "still_working": True,
        },
        {
            "position": "РЎС‚Р°СЂС€РёР№ РїСЂРµРїРѕРґР°РІР°С‚РµР»СЊ",
            "science_degree": "Рє.С‚.РЅ.",
            "official_email": "m.n.smirnov@spbu.ru",
            "still_working": True,
        },
        {
            "position": "РЎС‚Р°СЂС€РёР№ РїСЂРµРїРѕРґР°РІР°С‚РµР»СЊ",
            "official_email": "st036451@student.spbu.ru",
            "still_working": True,
        },
        {
            "position": "РЎС‚Р°СЂС€РёР№ РїСЂРµРїРѕРґР°РІР°С‚РµР»СЊ",
            "official_email": "s.shilov@spbu.ru",
            "still_working": True,
        },
        {
            "position": "РРЅР¶РµРЅРµСЂ-РёСЃСЃР»РµРґРѕРІР°С‚РµР»СЊ",
            "official_email": "st013464@student.spbu.ru",
            "still_working": True,
        },
        {
            "position": "РРЅР¶РµРЅРµСЂ-РёСЃСЃР»РµРґРѕРІР°С‚РµР»СЊ",
            "official_email": "st013039@student.spbu.ru",
            "still_working": True,
        },
        {
            "position": "Р”РѕС†РµРЅС‚",
            "official_email": "s.v.grigoriev@spbu.ru",
            "science_degree": "Рє.С„.-Рј.РЅ.",
            "still_working": False,
        },
        {
            "position": "РЎС‚Р°СЂС€РёР№ РїСЂРµРїРѕРґР°РІР°С‚РµР»СЊ",
            "official_email": "pimenov_aa_stub@spbu.ru",
            "still_working": False,
        },
        {
            "position": "РЎС‚Р°СЂС€РёР№ РїСЂРµРїРѕРґР°РІР°С‚РµР»СЊ",
            "official_email": "s.salischev@spbu.ru",
            "still_working": False,
        },
        {
            "position": "РђСЃСЃРёСЃС‚РµРЅС‚",
            "official_email": "d.sagunov@spbu.ru",
            "still_working": False,
        },
        {
            "position": "РђСЃСЃРёСЃС‚РµРЅС‚",
            "official_email": "g.chernyshev@spbu.ru",
            "still_working": False,
        },
    ]
    wtypes = [
        {"type": "Р’СЃРµ СЂР°Р±РѕС‚С‹"},
        {"type": "РљСѓСЂСЃРѕРІР°СЏ"},
        {"type": "Р‘Р°РєР°Р»Р°РІСЂСЃРєР°СЏ Р’РљР "},
        {"type": "РњР°РіРёСЃС‚РµСЂСЃРєР°СЏ Р’РљР "},
        {"type": "РџСЂР°РєС‚РёРєР° РѕСЃРµРЅРЅСЏСЏ, 2 РєСѓСЂСЃ"},
        {"type": "РџСЂР°РєС‚РёРєР° РІРµСЃРµРЅРЅСЏСЏ, 2 РєСѓСЂСЃ"},
        {"type": "РџСЂР°РєС‚РёРєР° РѕСЃРµРЅРЅСЏСЏ, 3 РєСѓСЂСЃ"},
        {"type": "РџСЂР°РєС‚РёРєР° РІРµСЃРµРЅРЅСЏСЏ, 3 РєСѓСЂСЃ"},
        {"type": "РџСЂРѕРёР·РІРѕРґСЃС‚РІРµРЅРЅР°СЏ РїСЂР°РєС‚РёРєР°"},
        {"type": "РџСЂРµРґРґРёРїР»РѕРјРЅР°СЏ РїСЂР°РєС‚РёРєР°"},
    ]

    internship_formats = [{"format": "РћС‡РЅРѕ"}, {"format": "Р”РёСЃС‚Р°РЅС†РёРѕРЅРЅРѕ"}]
    internship_tags = [{"tag": "C"}, {"tag": "C++"}, {"tag": "C#"}]
    courses = [
        {
            "name": "РњР°С‚РµРјР°С‚РёС‡РµСЃРєРѕРµ РѕР±РµСЃРїРµС‡РµРЅРёРµ Рё Р°РґРјРёРЅРёСЃС‚СЂРёСЂРѕРІР°РЅРёРµ РёРЅС„РѕСЂРјР°С†РёРѕРЅРЅС‹С… СЃРёСЃС‚РµРј (Р±Р°РєР°Р»Р°РІСЂРёР°С‚)",
            "code": "02.03.03",
        },
        {
            "name": "РџСЂРѕРіСЂР°РјРјРЅР°СЏ РёРЅР¶РµРЅРµСЂРёСЏ (Р±Р°РєР°Р»Р°РІСЂРёР°С‚)",
            "code": "09.03.04",
        },
        {
            "name": "РњР°С‚РµРјР°С‚РёС‡РµСЃРєРѕРµ РѕР±РµСЃРїРµС‡РµРЅРёРµ Рё Р°РґРјРёРЅРёСЃС‚СЂРёСЂРѕРІР°РЅРёРµ РёРЅС„РѕСЂРјР°С†РёРѕРЅРЅС‹С… СЃРёСЃС‚РµРј (РјР°РіРёСЃС‚СЂР°С‚СѓСЂР°)",
            "code": "02.04.03",
        },
        {"name": "371 РіСЂСѓРїРїР° (Р±Р°РєР°Р»Р°РІСЂРёР°С‚)", "code": "371"},
        {"name": "343 РіСЂСѓРїРїР° (Р±Р°РєР°Р»Р°РІСЂРёР°С‚)", "code": "343"},
        {"name": "344 РіСЂСѓРїРїР° (Р±Р°РєР°Р»Р°РІСЂРёР°С‚)", "code": "344"},
        {
            "name": "РџСЂРѕРіСЂР°РјРјРЅР°СЏ РёРЅР¶РµРЅРµСЂРёСЏ (РјР°РіРёСЃС‚СЂР°С‚СѓСЂР°)",
            "code": "09.04.04",
        },
    ]
    tags = [
        {"name": "РљРѕРјРїРёР»СЏС‚РѕСЂ"},
        {"name": "Android"},
        {"name": "F#"},
        {"name": "Р СѓРЎРё"},
    ]
    curriculum = [
        {
            "year": 2019,
            "discipline": "РџСЂР°РєС‚РёРєСѓРј РЅР° Р­Р’Рњ",
            "study_year": 1,
            "type": 1,
            "course_id": 2,
        },
        {
            "year": 2019,
            "discipline": "Р”РёСЃРєСЂРµС‚РЅР°СЏ РјР°С‚РµРјР°С‚РёРєР°",
            "study_year": 1,
            "type": 2,
            "course_id": 2,
        },
        {
            "year": 2019,
            "discipline": "РњР°С‚РµРјР°С‚РёС‡РµСЃРєРёР№ Р°РЅР°Р»РёР·",
            "study_year": 1,
            "type": 2,
            "course_id": 2,
        },
        {
            "year": 2019,
            "discipline": "Р‘РµР·РѕРїР°СЃРЅРѕСЃС‚СЊ Р¶РёР·РЅРµРґРµСЏС‚РµР»СЊРЅРѕСЃС‚Рё",
            "study_year": 1,
            "type": 3,
            "course_id": 2,
        },
        {
            "year": 2019,
            "discipline": "РћСЃРЅРѕРІС‹ РїСЂРѕРіСЂР°РјРјРёСЂРѕРІР°РЅРёСЏ",
            "study_year": 1,
            "type": 1,
            "course_id": 2,
        },
        {
            "year": 2019,
            "discipline": "Р“СЂСѓРїРїРѕРІР°СЏ РґРёРЅР°РјРёРєР° Рё РєРѕРјРјСѓРЅРёРєР°С†РёРё",
            "study_year": 1,
            "type": 3,
            "course_id": 2,
        },
        {
            "year": 2019,
            "discipline": "Р¤РёР·РёС‡РµСЃРєР°СЏ РєСѓР»СЊС‚СѓСЂР° Рё СЃРїРѕСЂС‚",
            "study_year": 1,
            "type": 3,
            "course_id": 2,
        },
        {
            "year": 2019,
            "discipline": "РђР»РіРµР±СЂР°",
            "study_year": 1,
            "type": 2,
            "course_id": 2,
        },
        {
            "year": 2019,
            "discipline": "РРЅРѕСЃС‚СЂР°РЅРЅС‹Р№ СЏР·С‹Рє",
            "study_year": 1,
            "type": 3,
            "course_id": 2,
        },
        {
            "year": 2019,
            "discipline": "Р¦РёС„СЂРѕРІР°СЏ РєСѓР»СЊС‚СѓСЂР°",
            "study_year": 1,
            "type": 3,
            "course_id": 2,
        },
        {
            "year": 2019,
            "discipline": "РђР»РіРѕСЂРёС‚РјС‹ Рё СЃС‚СЂСѓРєС‚СѓСЂС‹ РґР°РЅРЅС‹С…",
            "study_year": 1,
            "type": 1,
            "course_id": 2,
        },
        {
            "year": 2019,
            "discipline": "РђСЂС…РёС‚РµРєС‚СѓСЂР° РІС‹С‡РёСЃР»РёС‚РµР»СЊРЅС‹С… СЃРёСЃС‚РµРј",
            "study_year": 1,
            "type": 1,
            "course_id": 2,
        },
        {
            "year": 2019,
            "discipline": "Р“РµРѕРјРµС‚СЂРёСЏ",
            "study_year": 1,
            "type": 2,
            "course_id": 2,
        },
        {
            "year": 2019,
            "discipline": "Р’РІРµРґРµРЅРёРµ РІ РїСЂРѕРіСЂР°РјРјРЅСѓСЋ РёРЅР¶РµРЅРµСЂРёСЋ",
            "study_year": 2,
            "type": 1,
            "course_id": 2,
        },
        {
            "year": 2019,
            "discipline": "РџСЂР°РєС‚РёРєСѓРј РЅР° Р­Р’Рњ",
            "study_year": 2,
            "type": 1,
            "course_id": 2,
        },
        {
            "year": 2019,
            "discipline": "РСЃС‚РѕСЂРёСЏ Р РѕСЃСЃРёРё",
            "study_year": 2,
            "type": 3,
            "course_id": 2,
        },
        {
            "year": 2019,
            "discipline": "РњР°С‚РµРјР°С‚РёС‡РµСЃРєРёР№ Р°РЅР°Р»РёР·",
            "study_year": 2,
            "type": 2,
            "course_id": 2,
        },
        {
            "year": 2019,
            "discipline": "РћРїРµСЂР°С†РёРѕРЅРЅС‹Рµ СЃРёСЃС‚РµРјС‹",
            "study_year": 2,
            "type": 1,
            "course_id": 2,
        },
        {
            "year": 2019,
            "discipline": "РђР»РіРѕСЂРёС‚РјС‹ Рё Р°РЅР°Р»РёР· СЃР»РѕР¶РЅРѕСЃС‚Рё",
            "study_year": 2,
            "type": 1,
            "course_id": 2,
        },
        {
            "year": 2019,
            "discipline": "Р¤РёР·РёС‡РµСЃРєР°СЏ РєСѓР»СЊС‚СѓСЂР° Рё СЃРїРѕСЂС‚",
            "study_year": 2,
            "type": 3,
            "course_id": 2,
        },
        {
            "year": 2019,
            "discipline": "РЇР·С‹Рє СЌС„С„РµРєС‚РёРІРЅРѕР№ РєРѕРјРјСѓРЅРёРєР°С†РёРё",
            "study_year": 2,
            "type": 3,
            "course_id": 2,
        },
        {
            "year": 2019,
            "discipline": "Р¤СѓРЅРєС†РёРѕРЅР°Р»СЊРЅРѕРµ РїСЂРѕРіСЂР°РјРјРёСЂРѕРІР°РЅРёРµ",
            "study_year": 2,
            "type": 1,
            "course_id": 2,
        },
        {
            "year": 2019,
            "discipline": "РРЅР¶РµРЅРµСЂРЅР°СЏ СЌРєРѕРЅРѕРјРёРєР°",
            "study_year": 2,
            "type": 3,
            "course_id": 2,
        },
        {
            "year": 2019,
            "discipline": "РЈС‡РµР±РЅР°СЏ РїСЂР°РєС‚РёРєР° (РЅР°СѓС‡РЅРѕ-РёСЃСЃР»РµРґРѕРІР°С‚РµР»СЊСЃРєР°СЏ СЂР°Р±РѕС‚Р°)",
            "study_year": 2,
            "type": 1,
            "course_id": 2,
        },
        {
            "year": 2019,
            "discipline": "РРЅРѕСЃС‚СЂР°РЅРЅС‹Р№ СЏР·С‹Рє",
            "study_year": 2,
            "type": 3,
            "course_id": 2,
        },
        {
            "year": 2019,
            "discipline": "Р Р°Р·СЂР°Р±РѕС‚РєР° РїСЂРѕРіСЂР°РјРјРЅРѕРіРѕ РѕР±РµСЃРїРµС‡РµРЅРёСЏ",
            "study_year": 2,
            "type": 1,
            "course_id": 2,
        },
        {
            "year": 2019,
            "discipline": "Р”РёС„С„РµСЂРµРЅС†РёР°Р»СЊРЅС‹Рµ Рё СЂР°Р·РЅРѕСЃС‚РЅС‹Рµ СѓСЂР°РІРЅРµРЅРёСЏ",
            "study_year": 2,
            "type": 2,
            "course_id": 2,
        },
        {
            "year": 2019,
            "discipline": "РћСЃРЅРѕРІС‹ Р±РёР·РЅРµСЃР°",
            "study_year": 2,
            "type": 3,
            "course_id": 2,
        },
        {
            "year": 2019,
            "discipline": "Р§РµР»РѕРІРµРєРѕ-РјР°С€РёРЅРЅРѕРµ РІР·Р°РёРјРѕРґРµР№СЃС‚РІРёРµ",
            "study_year": 2,
            "type": 1,
            "course_id": 2,
        },
        {
            "year": 2019,
            "discipline": "РўРµРѕСЂРёСЏ РІРµСЂРѕСЏС‚РЅРѕСЃС‚РµР№ Рё РјР°С‚РµРјР°С‚РёС‡РµСЃРєР°СЏ СЃС‚Р°С‚РёСЃС‚РёРєР°",
            "study_year": 2,
            "type": 2,
            "course_id": 2,
        },
        {
            "year": 2019,
            "discipline": "Р’С‹С‡РёСЃР»РёС‚РµР»СЊРЅР°СЏ РјР°С‚РµРјР°С‚РёРєР°",
            "study_year": 2,
            "type": 1,
            "course_id": 2,
        },
        {
            "year": 2019,
            "discipline": "РњР°С‚РµРјР°С‚РёС‡РµСЃРєР°СЏ Р»РѕРіРёРєР°",
            "study_year": 2,
            "type": 1,
            "course_id": 2,
        },
        {
            "year": 2019,
            "discipline": "РљРѕРјРїСЊСЋС‚РµСЂРЅС‹Рµ СЃРµС‚Рё",
            "study_year": 3,
            "type": 1,
            "course_id": 2,
        },
        {
            "year": 2019,
            "discipline": "РћСЃРЅРѕРІС‹ РїСЂРѕС‚РёРІРѕРґРµР№СЃС‚РІРёСЏ РєРѕСЂСЂСѓРїС†РёРё Рё СЌРєСЃС‚СЂРµРјРёР·РјСѓ (РѕРЅР»Р°Р№РЅ-РєСѓСЂСЃ)",
            "study_year": 3,
            "type": 3,
            "course_id": 2,
        },
        {
            "year": 2019,
            "discipline": "РљРѕРјРїСЊСЋС‚РµСЂРЅР°СЏ РіСЂР°С„РёРєР°",
            "study_year": 3,
            "type": 1,
            "course_id": 2,
        },
        {
            "year": 2019,
            "discipline": "РћР±РµСЃРїРµС‡РµРЅРёРµ РєР°С‡РµСЃС‚РІР° Рё С‚РµСЃС‚РёСЂРѕРІР°РЅРёРµ РїСЂРѕРіСЂР°РјРјРЅРѕРіРѕ РѕР±РµСЃРїРµС‡РµРЅРёСЏ ",
            "study_year": 3,
            "type": 1,
            "course_id": 2,
        },
        {
            "year": 2019,
            "discipline": "РўРµРѕСЂРёСЏ Р°РІС‚РѕРјР°С‚РѕРІ Рё С„РѕСЂРјР°Р»СЊРЅС‹С… СЏР·С‹РєРѕРІ ",
            "study_year": 3,
            "type": 1,
            "course_id": 2,
        },
        {
            "year": 2019,
            "discipline": "Р‘Р°Р·С‹ РґР°РЅРЅС‹С…",
            "study_year": 3,
            "type": 1,
            "course_id": 2,
        },
        {
            "year": 2019,
            "discipline": "РџСЂРѕРёР·РІРѕРґСЃС‚РІРµРЅРЅР°СЏ РїСЂР°РєС‚РёРєР°",
            "study_year": 3,
            "type": 1,
            "course_id": 2,
        },
        {
            "year": 2019,
            "discipline": "РўСЂР°РЅСЃР»СЏС†РёСЏ СЏР·С‹РєРѕРІ РїСЂРѕРіСЂР°РјРјРёСЂРѕРІР°РЅРёСЏ",
            "study_year": 3,
            "type": 1,
            "course_id": 2,
        },
        {
            "year": 2019,
            "discipline": "РРЅРѕСЃС‚СЂР°РЅРЅС‹Р№ СЏР·С‹Рє",
            "study_year": 3,
            "type": 3,
            "course_id": 2,
        },
        {
            "year": 2019,
            "discipline": "РњРµС‚РѕРґС‹ РѕРїС‚РёРјРёР·Р°С†РёРё Рё РёСЃСЃР»РµРґРѕРІР°РЅРёРµ РѕРїРµСЂР°С†РёР№",
            "study_year": 3,
            "type": 2,
            "course_id": 2,
        },
        {
            "year": 2019,
            "discipline": "РњРѕРґРµР»РёСЂРѕРІР°РЅРёРµ РёРЅС„РѕСЂРјР°С†РёРѕРЅРЅС‹С… РїСЂРѕС†РµСЃСЃРѕРІ ",
            "study_year": 3,
            "type": 1,
            "course_id": 2,
        },
        {
            "year": 2019,
            "discipline": "РћСЃРЅРѕРІС‹ РїРµРґР°РіРѕРіРёС‡РµСЃРєРѕР№ РґРµСЏС‚РµР»СЊРЅРѕСЃС‚Рё (РѕРЅР»Р°Р№РЅ-РєСѓСЂСЃ)",
            "study_year": 3,
            "type": 3,
            "course_id": 2,
        },
        {
            "year": 2019,
            "discipline": "РўРµРѕСЂРёСЏ РіСЂР°С„РѕРІ",
            "study_year": 3,
            "type": 1,
            "course_id": 2,
        },
        {
            "year": 2019,
            "discipline": "РЎРѕС†РёР°Р»СЊРЅРѕ-РїСЂР°РІРѕРІС‹Рµ РІРѕРїСЂРѕСЃС‹ РїСЂРѕРіСЂР°РјРјРЅРѕР№ РёРЅР¶РµРЅРµСЂРёРё",
            "study_year": 3,
            "type": 3,
            "course_id": 2,
        },
        {
            "year": 2019,
            "discipline": "РџСЂРѕРµРєС‚РёСЂРѕРІР°РЅРёРµ Рё Р°СЂС…РёС‚РµРєС‚СѓСЂР° РїСЂРѕРіСЂР°РјРјРЅРѕРіРѕ РѕР±РµСЃРїРµС‡РµРЅРёСЏ",
            "study_year": 3,
            "type": 1,
            "course_id": 2,
        },
        {
            "year": 2019,
            "discipline": "РђР»РіРѕСЂРёС‚РјС‹ Р°РЅР°Р»РёР·Р° РіСЂР°С„РѕРІ (РїРѕ РІС‹Р±РѕСЂСѓ)",
            "study_year": 3,
            "type": 1,
            "course_id": 2,
        },
        {
            "year": 2019,
            "discipline": "РћРїРµСЂР°С†РёРѕРЅРЅС‹Рµ СЃРёСЃС‚РµРјС‹ Рё СЂРµР°Р»РёР·Р°С†РёСЏ СЏР·С‹РєРѕРІ РїСЂРѕРіСЂР°РјРјРёСЂРѕРІР°РЅРёСЏ (РїРѕ РІС‹Р±РѕСЂСѓ)",
            "study_year": 3,
            "type": 1,
            "course_id": 2,
        },
        {
            "year": 2019,
            "discipline": "Р РµРёРЅР¶РёРЅРёСЂРёРЅРі СЃРёСЃС‚РµРј РїСЂРѕРіСЂР°РјРјРёСЂРѕРІР°РЅРёСЏ (РїРѕ РІС‹Р±РѕСЂСѓ)",
            "study_year": 3,
            "type": 1,
            "course_id": 2,
        },
        {
            "year": 2019,
            "discipline": "РўРµР»РµРєРѕРјРјСѓРЅРёРєР°С†РёРё (РїРѕ РІС‹Р±РѕСЂСѓ)",
            "study_year": 3,
            "type": 1,
            "course_id": 2,
        },
        {
            "year": 2019,
            "discipline": "Р’РІРµРґРµРЅРёРµ РІ СЃРїРµС†РёР°Р»СЊРЅРѕСЃС‚СЊ (РїРѕ РІС‹Р±РѕСЂСѓ)",
            "study_year": 3,
            "type": 1,
            "course_id": 2,
        },
        {
            "year": 2019,
            "discipline": "РЎРёСЃС‚РµРјРЅРѕРµ РїСЂРѕРіСЂР°РјРјРёСЂРѕРІР°РЅРёРµ (РїРѕ РІС‹Р±РѕСЂСѓ)",
            "study_year": 3,
            "type": 1,
            "course_id": 2,
        },
        {
            "year": 2019,
            "discipline": "РџСЂРµРґРґРёРїР»РѕРјРЅР°СЏ РїСЂР°РєС‚РёРєР°",
            "study_year": 4,
            "type": 1,
            "course_id": 2,
        },
        {
            "year": 2019,
            "discipline": "РРЅС‚РµР»Р»РµРєС‚СѓР°Р»СЊРЅС‹Рµ СЃРёСЃС‚РµРјС‹",
            "study_year": 4,
            "type": 1,
            "course_id": 2,
        },
        {
            "year": 2019,
            "discipline": "РџСЂРёРєР»Р°РґРЅС‹Рµ Р·Р°РґР°С‡Рё С‚РµРѕСЂРёРё РІРµСЂРѕСЏС‚РЅРѕСЃС‚РµР№",
            "study_year": 4,
            "type": 2,
            "course_id": 2,
        },
        {
            "year": 2019,
            "discipline": "Р—Р°С‰РёС‚Р° РёРЅС„РѕСЂРјР°С†РёРё",
            "study_year": 4,
            "type": 1,
            "course_id": 2,
        },
        {
            "year": 2019,
            "discipline": "РђРЅР°Р»РёР· С‚СЂРµР±РѕРІР°РЅРёР№ Рє РїСЂРѕРіСЂР°РјРјРЅРѕРјСѓ РѕР±РµСЃРїРµС‡РµРЅРёСЋ",
            "study_year": 4,
            "type": 1,
            "course_id": 2,
        },
        {
            "year": 2019,
            "discipline": "РЈРїСЂР°РІР»РµРЅРёРµ РїСЂРѕРіСЂР°РјРјРЅС‹РјРё РїСЂРѕРµРєС‚Р°РјРё",
            "study_year": 4,
            "type": 1,
            "course_id": 2,
        },
        {
            "year": 2019,
            "discipline": "РРЅРѕСЃС‚СЂР°РЅРЅС‹Р№ СЏР·С‹Рє",
            "study_year": 4,
            "type": 3,
            "course_id": 2,
        },
        {
            "year": 2019,
            "discipline": "Р Р°Р·СЂР°Р±РѕС‚РєР° РїСЂРёР»РѕР¶РµРЅРёР№ РІ РЎРЈР‘Р” (РїРѕ РІС‹Р±РѕСЂСѓ)",
            "study_year": 4,
            "type": 1,
            "course_id": 2,
        },
        {
            "year": 2019,
            "discipline": "РЎС‚РѕС…Р°СЃС‚РёС‡РµСЃРєРѕРµ РїСЂРѕРіСЂР°РјРјРёСЂРѕРІР°РЅРёРµ (РїРѕ РІС‹Р±РѕСЂСѓ)",
            "study_year": 4,
            "type": 1,
            "course_id": 2,
        },
        {
            "year": 2019,
            "discipline": "Р’РІРµРґРµРЅРёРµ РІ MS.NET (РїРѕ РІС‹Р±РѕСЂСѓ)",
            "study_year": 4,
            "type": 1,
            "course_id": 2,
        },
        {
            "year": 2019,
            "discipline": "РЎРѕРІСЂРµРјРµРЅРЅС‹Рµ С‚РµС…РЅРѕР»РѕРіРёРё СЂР°Р·СЂР°Р±РѕС‚РєРё Р±РёР·РЅРµСЃ-РїСЂРёР»РѕР¶РµРЅРёР№ (РїРѕ РІС‹Р±РѕСЂСѓ)",
            "study_year": 4,
            "type": 1,
            "course_id": 2,
        },
        {
            "year": 2019,
            "discipline": "РџСЂРѕРіСЂР°РјРјРЅР°СЏ РёРЅР¶РµРЅРµСЂРёСЏ (РїРѕ РІС‹Р±РѕСЂСѓ)",
            "study_year": 4,
            "type": 1,
            "course_id": 2,
        },
        {
            "year": 2019,
            "discipline": "РЎРёСЃС‚РµРјРЅРѕРµ РїСЂРѕРіСЂР°РјРјРёСЂРѕРІР°РЅРёРµ РґР»СЏ СЃРѕРІСЂРµРјРµРЅРЅС‹С… РїР»Р°С‚С„РѕСЂРј (РїРѕ РІС‹Р±РѕСЂСѓ)",
            "study_year": 4,
            "type": 1,
            "course_id": 2,
        },
        {
            "year": 2019,
            "discipline": "РћСЃРЅРѕРІС‹ РјРµРЅРµРґР¶РјРµРЅС‚Р°",
            "study_year": 4,
            "type": 3,
            "course_id": 2,
        },
        {
            "year": 2019,
            "discipline": "Р¤РёР»РѕСЃРѕС„РёСЏ (РѕРЅР»Р°Р№РЅ-РєСѓСЂСЃ)",
            "study_year": 4,
            "type": 3,
            "course_id": 2,
        },
        {
            "year": 2019,
            "discipline": "РџСЂР°РєС‚РёРєР° СЂР°Р·СЂР°Р±РѕС‚РєРё РґРѕРєСѓРјРµРЅС‚Р°С†РёРё (РЅР° Р°РЅРіР»РёР№СЃРєРѕРј СЏР·С‹РєРµ) (РїРѕ РІС‹Р±РѕСЂСѓ)",
            "study_year": 4,
            "type": 1,
            "course_id": 2,
        },
        {
            "year": 2019,
            "discipline": "РЎС‚РѕС…Р°СЃС‚РёС‡РµСЃРєР°СЏ РѕРїС‚РёРјРёР·Р°С†РёСЏ РІ РёРЅС„РѕСЂРјР°С‚РёРєРµ (РЅР° Р°РЅРіР»РёР№СЃРєРѕРј СЏР·С‹РєРµ) (РїРѕ РІС‹Р±РѕСЂСѓ)",
            "study_year": 4,
            "type": 1,
            "course_id": 2,
        },
        {
            "year": 2019,
            "discipline": "РђР»РіРѕСЂРёС‚РјРёС‡РµСЃРєРёРµ РѕСЃРЅРѕРІС‹ СЂРѕР±РѕС‚РѕС‚РµС…РЅРёРєРё (РїРѕ РІС‹Р±РѕСЂСѓ)",
            "study_year": 4,
            "type": 1,
            "course_id": 2,
        },
        {
            "year": 2019,
            "discipline": "РЎС‚Р°С‚РёС‡РµСЃРєРёР№ Р°РЅР°Р»РёР· РїСЂРѕРіСЂР°РјРј (РїРѕ РІС‹Р±РѕСЂСѓ)",
            "study_year": 4,
            "type": 1,
            "course_id": 2,
        },
        {
            "year": 2019,
            "discipline": "РџСЂРѕРіСЂР°РјРјРёСЂРѕРІР°РЅРёРµ",
            "study_year": 1,
            "type": 1,
            "course_id": 1,
        },
        {
            "year": 2019,
            "discipline": "РРЅС„РѕСЂРјР°С‚РёРєР°",
            "study_year": 1,
            "type": 1,
            "course_id": 1,
        },
        {
            "year": 2019,
            "discipline": "Р¤РёР·РёС‡РµСЃРєР°СЏ РєСѓР»СЊС‚СѓСЂР° Рё СЃРїРѕСЂС‚",
            "study_year": 1,
            "type": 3,
            "course_id": 1,
        },
        {
            "year": 2019,
            "discipline": "Р”РёСЃРєСЂРµС‚РЅР°СЏ РјР°С‚РµРјР°С‚РёРєР°",
            "study_year": 1,
            "type": 2,
            "course_id": 1,
        },
        {
            "year": 2019,
            "discipline": "РњР°С‚РµРјР°С‚РёС‡РµСЃРєРёР№ Р°РЅР°Р»РёР·",
            "study_year": 1,
            "type": 2,
            "course_id": 1,
        },
        {
            "year": 2019,
            "discipline": "РђР»РіРµР±СЂР° Рё С‚РµРѕСЂРёСЏ С‡РёСЃРµР»",
            "study_year": 1,
            "type": 2,
            "course_id": 1,
        },
        {
            "year": 2019,
            "discipline": "Р“РµРѕРјРµС‚СЂРёСЏ Рё С‚РѕРїРѕР»РѕРіРёСЏ",
            "study_year": 1,
            "type": 2,
            "course_id": 1,
        },
        {
            "year": 2019,
            "discipline": "РРЅРѕСЃС‚СЂР°РЅРЅС‹Р№ СЏР·С‹Рє",
            "study_year": 1,
            "type": 3,
            "course_id": 1,
        },
        {
            "year": 2019,
            "discipline": "Р¦РёС„СЂРѕРІР°СЏ РєСѓР»СЊС‚СѓСЂР° (Р­Рћ)",
            "study_year": 1,
            "type": 3,
            "course_id": 1,
        },
        {
            "year": 2019,
            "discipline": "РСЃС‚РѕСЂРёСЏ Р РѕСЃСЃРёРё (РѕРЅР»Р°Р№РЅ-РєСѓСЂСЃ)",
            "study_year": 1,
            "type": 3,
            "course_id": 1,
        },
        {
            "year": 2019,
            "discipline": "РџСЂРѕРіСЂР°РјРјРёСЂРѕРІР°РЅРёРµ",
            "study_year": 2,
            "type": 1,
            "course_id": 1,
        },
        {
            "year": 2019,
            "discipline": "РЈС‡РµР±РЅР°СЏ РїСЂР°РєС‚РёРєР° 1",
            "study_year": 2,
            "type": 1,
            "course_id": 1,
        },
        {
            "year": 2019,
            "discipline": "РРЅС„РѕСЂРјР°С‚РёРєР°",
            "study_year": 2,
            "type": 1,
            "course_id": 1,
        },
        {
            "year": 2019,
            "discipline": "Р¤РёР·РёС‡РµСЃРєР°СЏ РєСѓР»СЊС‚СѓСЂР° Рё СЃРїРѕСЂС‚",
            "study_year": 2,
            "type": 3,
            "course_id": 1,
        },
        {
            "year": 2019,
            "discipline": "РњР°С‚РµРјР°С‚РёС‡РµСЃРєРёР№ Р°РЅР°Р»РёР·",
            "study_year": 2,
            "type": 2,
            "course_id": 1,
        },
        {
            "year": 2019,
            "discipline": "РђР»РіРµР±СЂР° Рё С‚РµРѕСЂРёСЏ С‡РёСЃРµР»",
            "study_year": 2,
            "type": 2,
            "course_id": 1,
        },
        {
            "year": 2019,
            "discipline": "Р“РµРѕРјРµС‚СЂРёСЏ Рё С‚РѕРїРѕР»РѕРіРёСЏ",
            "study_year": 2,
            "type": 2,
            "course_id": 1,
        },
        {
            "year": 2019,
            "discipline": "РЇР·С‹Рє СЌС„С„РµРєС‚РёРІРЅРѕР№ РєРѕРјРјСѓРЅРёРєР°С†РёРё (РѕРЅР»Р°Р№РЅРєСѓСЂСЃ)",
            "study_year": 2,
            "type": 3,
            "course_id": 1,
        },
        {
            "year": 2019,
            "discipline": "Р”РёС„С„РµСЂРµРЅС†РёР°Р»СЊРЅС‹Рµ СѓСЂР°РІРЅРµРЅРёСЏ",
            "study_year": 2,
            "type": 2,
            "course_id": 1,
        },
        {
            "year": 2019,
            "discipline": "РРЅРѕСЃС‚СЂР°РЅРЅС‹Р№ СЏР·С‹Рє",
            "study_year": 2,
            "type": 3,
            "course_id": 1,
        },
        {
            "year": 2019,
            "discipline": "РћРїРµСЂР°С†РёРѕРЅРЅС‹Рµ СЃРёСЃС‚РµРјС‹ Рё РѕР±РѕР»РѕС‡РєРё",
            "study_year": 2,
            "type": 1,
            "course_id": 1,
        },
        {
            "year": 2019,
            "discipline": "Р‘Р°Р·С‹ РґР°РЅРЅС‹С… Рё РЎРЈР‘Р”",
            "study_year": 2,
            "type": 1,
            "course_id": 1,
        },
        {
            "year": 2019,
            "discipline": "РћСЃРЅРѕРІС‹ РїСЂРѕС‚РёРІРѕРґРµР№СЃС‚РІРёСЏ РєРѕСЂСЂСѓРїС†РёРё Рё СЌРєСЃС‚СЂРµРјРёР·РјСѓ (РѕРЅР»Р°Р№РЅ-РєСѓСЂСЃ)",
            "study_year": 2,
            "type": 3,
            "course_id": 1,
        },
        {
            "year": 2019,
            "discipline": "РџР°СЂР°Р»Р»РµР»СЊРЅРѕРµ РїСЂРѕРіСЂР°РјРјРёСЂРѕРІР°РЅРёРµ",
            "study_year": 2,
            "type": 1,
            "course_id": 1,
        },
        {
            "year": 2019,
            "discipline": "РђСЂС…РёС‚РµРєС‚СѓСЂР° Р­Р’Рњ",
            "study_year": 2,
            "type": 1,
            "course_id": 1,
        },
        {
            "year": 2019,
            "discipline": "РњР°С‚РµРјР°С‚РёС‡РµСЃРєР°СЏ Р»РѕРіРёРєР°",
            "study_year": 2,
            "type": 2,
            "course_id": 1,
        },
        {
            "year": 2019,
            "discipline": "РЎС‚СЂСѓРєС‚СѓСЂС‹ Рё Р°Р»РіРѕСЂРёС‚РјС‹ РєРѕРјРїСЊСЋС‚РµСЂРЅРѕР№ РѕР±СЂР°Р±РѕС‚РєРё РґР°РЅРЅС‹С…",
            "study_year": 2,
            "type": 1,
            "course_id": 1,
        },
        {
            "year": 2019,
            "discipline": "РњРµС‚РѕРґС‹ РІС‹С‡РёСЃР»РµРЅРёР№ Рё РІС‹С‡РёСЃР»РёС‚РµР»СЊРЅС‹Р№ РїСЂР°РєС‚РёРєСѓРј",
            "study_year": 3,
            "type": 1,
            "course_id": 1,
        },
        {
            "year": 2019,
            "discipline": "Р¤СѓРЅРєС†РёРѕРЅР°Р»СЊРЅС‹Р№ Р°РЅР°Р»РёР·",
            "study_year": 3,
            "type": 2,
            "course_id": 1,
        },
        {
            "year": 2019,
            "discipline": "РўРµРѕСЂРёСЏ РІРµСЂРѕСЏС‚РЅРѕСЃС‚РµР№ Рё РјР°С‚РµРјР°С‚РёС‡РµСЃРєР°СЏ СЃС‚Р°С‚РёСЃС‚РёРєР°",
            "study_year": 3,
            "type": 2,
            "course_id": 1,
        },
        {
            "year": 2019,
            "discipline": "РћСЃРЅРѕРІС‹ Р±РёР·РЅРµСЃР° (РѕРЅР»Р°Р№РЅ-РєСѓСЂСЃ)",
            "study_year": 3,
            "type": 3,
            "course_id": 1,
        },
        {
            "year": 2019,
            "discipline": "РўРµРѕСЂРёСЏ С„РѕСЂРјР°Р»СЊРЅС‹С… СЏР·С‹РєРѕРІ Рё С‚СЂР°РЅСЃР»СЏС†РёР№",
            "study_year": 3,
            "type": 1,
            "course_id": 1,
        },
        {
            "year": 2019,
            "discipline": "РЈС‡РµР±РЅР°СЏ РїСЂР°РєС‚РёРєР° 2",
            "study_year": 3,
            "type": 1,
            "course_id": 1,
        },
        {
            "year": 2019,
            "discipline": "РњР°С‚РµРјР°С‚РёС‡РµСЃРєР°СЏ Р»РѕРіРёРєР°",
            "study_year": 3,
            "type": 2,
            "course_id": 1,
        },
        {
            "year": 2019,
            "discipline": "РњР°С‚РµРјР°С‚РёС‡РµСЃРєР°СЏ Р»РѕРіРёРєР°",
            "study_year": 3,
            "type": 2,
            "course_id": 1,
        },
        {
            "year": 2019,
            "discipline": "РРЅРѕСЃС‚СЂР°РЅРЅС‹Р№ СЏР·С‹Рє",
            "study_year": 3,
            "type": 3,
            "course_id": 1,
        },
        {
            "year": 2019,
            "discipline": "Java-С‚РµС…РЅРѕР»РѕРіРёРё. Р§Р°СЃС‚СЊ 1 (РїРѕ РІС‹Р±РѕСЂСѓ)",
            "study_year": 3,
            "type": 1,
            "course_id": 1,
        },
        {
            "year": 2019,
            "discipline": "РђР»РіРѕСЂРёС‚РјРёС‡РµСЃРєРёРµ СЏР·С‹РєРё РїР°СЂР°Р»Р»РµР»СЊРЅРѕРіРѕ РїСЂРѕРіСЂР°РјРјРёСЂРѕРІР°РЅРёСЏ (РїРѕ РІС‹Р±РѕСЂСѓ)",
            "study_year": 3,
            "type": 1,
            "course_id": 1,
        },
        {
            "year": 2019,
            "discipline": "РђСЂС…РёС‚РµРєС‚СѓСЂР° РїСЂРѕС†РµСЃСЃРѕСЂР° (РїРѕ РІС‹Р±РѕСЂСѓ)",
            "study_year": 3,
            "type": 1,
            "course_id": 1,
        },
        {
            "year": 2019,
            "discipline": "Р’РІРµРґРµРЅРёРµ РІ РєРѕРјРїСЊСЋС‚РµСЂРЅСѓСЋ РјР°С‚РµРјР°С‚РёРєСѓ (РїРѕ РІС‹Р±РѕСЂСѓ)",
            "study_year": 3,
            "type": 1,
            "course_id": 1,
        },
        {
            "year": 2019,
            "discipline": "Р’РІРµРґРµРЅРёРµ РІ С‚РµРѕСЂРёСЋ РїР°СЂР°Р»Р»РµР»СЊРЅС‹С… РІС‹С‡РёСЃР»РµРЅРёР№ (РїРѕ РІС‹Р±РѕСЂСѓ)",
            "study_year": 3,
            "type": 1,
            "course_id": 1,
        },
        {
            "year": 2019,
            "discipline": "Р—Р°РґР°С‡Рё Рё РјРµС‚РѕРґС‹ РґРёРЅР°РјРёС‡РµСЃРєРёС… СЃРёСЃС‚РµРј (РїРѕ РІС‹Р±РѕСЂСѓ)",
            "study_year": 3,
            "type": 1,
            "course_id": 1,
        },
        {
            "year": 2019,
            "discipline": "РњРѕРґРµР»Рё Рё РјРµС‚РѕРґС‹ С…СЂР°РЅРµРЅРёСЏ Рё РїРѕРёСЃРєР° РёРЅС„РѕСЂРјР°С†РёРё (РїРѕ РІС‹Р±РѕСЂСѓ)",
            "study_year": 3,
            "type": 1,
            "course_id": 1,
        },
        {
            "year": 2019,
            "discipline": "РњСѓР»СЊС‚РёР°РіРµРЅС‚РЅС‹Рµ СЃРёСЃС‚РµРјС‹ (РїРѕ РІС‹Р±РѕСЂСѓ)",
            "study_year": 3,
            "type": 1,
            "course_id": 1,
        },
        {
            "year": 2019,
            "discipline": "РћСЃРЅРѕРІС‹ РєРѕРјРїСЊСЋС‚РµСЂРЅРѕР№ РіСЂР°С„РёРєРё Рё РѕР±СЂР°Р±РѕС‚РєРё РёР·РѕР±СЂР°Р¶РµРЅРёР№ (РїРѕ РІС‹Р±РѕСЂСѓ)",
            "study_year": 3,
            "type": 1,
            "course_id": 1,
        },
        {
            "year": 2019,
            "discipline": "Р Р°СЃРїР°СЂР°Р»Р»РµР»РёРІР°РЅРёРµ РІ OpenMP Рё РёРЅС‚РµСЂРІР°Р»СЊРЅС‹Рµ РІС‹С‡РёСЃР»РµРЅРёСЏ (РїРѕ РІС‹Р±РѕСЂСѓ)",
            "study_year": 3,
            "type": 1,
            "course_id": 1,
        },
        {
            "year": 2019,
            "discipline": "РўРµРѕСЂРёСЏ Р»РѕРіРёС‡РµСЃРєРѕРіРѕ РІС‹РІРѕРґР° (РїРѕ РІС‹Р±РѕСЂСѓ)",
            "study_year": 3,
            "type": 1,
            "course_id": 1,
        },
        {
            "year": 2019,
            "discipline": "РҐСЂР°РЅРµРЅРёРµ Рё СѓРїСЂР°РІР»РµРЅРёРµ РґР°РЅРЅС‹РјРё (РїРѕ РІС‹Р±РѕСЂСѓ)",
            "study_year": 3,
            "type": 1,
            "course_id": 1,
        },
        {
            "year": 2019,
            "discipline": "РђРІС‚РѕРјР°С‚РёС‡РµСЃРєРѕРµ РґРѕРєР°Р·Р°С‚РµР»СЊСЃС‚РІРѕ С‚РµРѕСЂРµРј (РїРѕ РІС‹Р±РѕСЂСѓ)",
            "study_year": 3,
            "type": 2,
            "course_id": 1,
        },
        {
            "year": 2019,
            "discipline": "Р’РІРµРґРµРЅРёРµ РІ СЃРїРµС†РёР°Р»СЊРЅРѕСЃС‚СЊ (РїРѕ РІС‹Р±РѕСЂСѓ)",
            "study_year": 3,
            "type": 3,
            "course_id": 1,
        },
        {
            "year": 2019,
            "discipline": "Р›РѕРіРёС‡РµСЃРєРѕРµ РїСЂРѕРіСЂР°РјРјРёСЂРѕРІР°РЅРёРµ (РїРѕ РІС‹Р±РѕСЂСѓ)",
            "study_year": 3,
            "type": 1,
            "course_id": 1,
        },
        {
            "year": 2019,
            "discipline": "РњРµС‚РѕРґС‹ С…СЂР°РЅРµРЅРёСЏ Рё РёРЅРґРµРєСЃРёСЂРѕРІР°РЅРёСЏ (РїРѕ РІС‹Р±РѕСЂСѓ)",
            "study_year": 3,
            "type": 1,
            "course_id": 1,
        },
        {
            "year": 2019,
            "discipline": "РџРѕРёСЃРє РёРЅС„РѕСЂРјР°С†РёРё РІ РЅРµСЃС‚СЂСѓРєС‚СѓСЂРёСЂРѕРІР°РЅРЅС‹С… РґР°РЅРЅС‹С… (РїРѕ РІС‹Р±РѕСЂСѓ)",
            "study_year": 3,
            "type": 1,
            "course_id": 1,
        },
        {
            "year": 2019,
            "discipline": "РЎРёСЃС‚РµРјРЅРѕРµ РїСЂРѕРіСЂР°РјРјРёСЂРѕРІР°РЅРёРµ (РїРѕ РІС‹Р±РѕСЂСѓ)",
            "study_year": 3,
            "type": 1,
            "course_id": 1,
        },
        {
            "year": 2019,
            "discipline": "РўРµРѕСЂРёСЏ Рё РїСЂР°РєС‚РёРєР° СЂР°СЃРїР°СЂР°Р»Р»РµР»РёРІР°РЅРёСЏ РІ OpenMP (РїРѕ РІС‹Р±РѕСЂСѓ)",
            "study_year": 3,
            "type": 1,
            "course_id": 1,
        },
        {
            "year": 2019,
            "discipline": "РўРµРѕСЂРёСЏ СЂР°СЃРїР°СЂР°Р»Р»РµР»РёРІР°РЅРёСЏ РЅР°Рґ РѕР±С‰РµР№ РїР°РјСЏС‚СЊСЋ (РїРѕ РІС‹Р±РѕСЂСѓ)",
            "study_year": 3,
            "type": 1,
            "course_id": 1,
        },
        {
            "year": 2019,
            "discipline": "РўРµС…РЅРѕР»РѕРіРёСЏ РїСЂРµРѕР±СЂР°Р·РѕРІР°РЅРёСЏ РїРѕСЃР»РµРґРѕРІР°С‚РµР»СЊРЅС‹С… РїСЂРѕРіСЂР°РјРј РІ РїР°СЂР°Р»Р»РµР»СЊРЅС‹Рµ (РїРѕ РІС‹Р±РѕСЂСѓ)",
            "study_year": 3,
            "type": 1,
            "course_id": 1,
        },
        {
            "year": 2019,
            "discipline": "РўРµС…РЅРѕР»РѕРіРёСЏ СЂР°Р·СЂР°Р±РѕС‚РєРё РїСЂРѕРіСЂР°РјРјРЅРѕРіРѕ РѕР±РµСЃРїРµС‡РµРЅРёСЏ",
            "study_year": 3,
            "type": 1,
            "course_id": 1,
        },
        {
            "year": 2019,
            "discipline": "РћСЃРЅРѕРІС‹ РїРµРґР°РіРѕРіРёС‡РµСЃРєРѕР№ РґРµСЏС‚РµР»СЊРЅРѕСЃС‚Рё (РѕРЅР»Р°Р№РЅРєСѓСЂСЃ)",
            "study_year": 3,
            "type": 3,
            "course_id": 1,
        },
        {
            "year": 2019,
            "discipline": "Р’С‹С‡РёСЃР»РёС‚РµР»СЊРЅС‹Р№ РїСЂР°РєС‚РёРєСѓРј",
            "study_year": 3,
            "type": 1,
            "course_id": 1,
        },
        {
            "year": 2019,
            "discipline": "РЈСЂР°РІРЅРµРЅРёСЏ РјР°С‚РµРјР°С‚РёС‡РµСЃРєРѕР№ С„РёР·РёРєРё",
            "study_year": 3,
            "type": 2,
            "course_id": 1,
        },
        {
            "year": 2019,
            "discipline": "РРЅС„РѕСЂРјР°С†РёРѕРЅРЅС‹Р№ РїРѕРёСЃРє РІ Internet (РїРѕ РІС‹Р±РѕСЂСѓ)",
            "study_year": 3,
            "type": 1,
            "course_id": 1,
        },
        {
            "year": 2019,
            "discipline": "РџР°СЂР°Р»Р»РµР»СЊРЅС‹Рµ Р°Р»РіРѕСЂРёС‚РјС‹ С‡РёСЃР»РµРЅРЅРѕРіРѕ РјРѕРґРµР»РёСЂРѕРІР°РЅРёСЏ (РїРѕ РІС‹Р±РѕСЂСѓ)",
            "study_year": 3,
            "type": 1,
            "course_id": 1,
        },
        {
            "year": 2019,
            "discipline": "Р Р°СЃРїСЂРµРґРµР»РµРЅРЅС‹Рµ РїР°СЂР°Р»Р»РµР»СЊРЅС‹Рµ СЃРёСЃС‚РµРјС‹ (РїРѕ РІС‹Р±РѕСЂСѓ)",
            "study_year": 3,
            "type": 1,
            "course_id": 1,
        },
        {
            "year": 2019,
            "discipline": "Р РµРёРЅР¶РёРЅРёСЂРёРЅРі РёРЅС„РѕСЂРјР°С†РёРѕРЅРЅС‹С… СЃРёСЃС‚РµРј (РїРѕ РІС‹Р±РѕСЂСѓ)",
            "study_year": 3,
            "type": 1,
            "course_id": 1,
        },
        {
            "year": 2019,
            "discipline": "РЎРµС‚РµРІС‹Рµ С‚РµС…РЅРѕР»РѕРіРёРё (РїРѕ РІС‹Р±РѕСЂСѓ)",
            "study_year": 3,
            "type": 1,
            "course_id": 1,
        },
        {
            "year": 2019,
            "discipline": "РЎС‚Р°С‚РёСЃС‚РёС‡РµСЃРєРёР№ Р°РЅР°Р»РёР· РґР°РЅРЅС‹С… (РїРѕ РІС‹Р±РѕСЂСѓ)",
            "study_year": 3,
            "type": 1,
            "course_id": 1,
        },
        {
            "year": 2019,
            "discipline": "РўРµР»РµРєРѕРјРјСѓРЅРёРєР°С†РёРё (РїРѕ РІС‹Р±РѕСЂСѓ)",
            "study_year": 3,
            "type": 1,
            "course_id": 1,
        },
        {
            "year": 2019,
            "discipline": "РЇР·С‹Рє РїСЂРѕРіСЂР°РјРјРёСЂРѕРІР°РЅРёСЏ РЎ++ (РїРѕ РІС‹Р±РѕСЂСѓ)",
            "study_year": 3,
            "type": 1,
            "course_id": 1,
        },
        {
            "year": 2019,
            "discipline": "Java-С‚РµС…РЅРѕР»РѕРіРёРё. Р§Р°СЃС‚СЊ 2 (РїРѕ РІС‹Р±РѕСЂСѓ)",
            "study_year": 3,
            "type": 1,
            "course_id": 1,
        },
        {
            "year": 2019,
            "discipline": "РђР»РіРѕСЂРёС‚РјС‹ Р°РЅР°Р»РёР·Р° РіСЂР°С„РѕРІ (РїРѕ РІС‹Р±РѕСЂСѓ)",
            "study_year": 3,
            "type": 1,
            "course_id": 1,
        },
        {
            "year": 2019,
            "discipline": "РђСЂС…РёС‚РµРєС‚СѓСЂР° РїР°СЂР°Р»Р»РµР»СЊРЅС‹С… СЃРёСЃС‚РµРј (РїРѕ РІС‹Р±РѕСЂСѓ)",
            "study_year": 3,
            "type": 1,
            "course_id": 1,
        },
        {
            "year": 2019,
            "discipline": "Р’РІРµРґРµРЅРёРµ РІ Р°СЂС…РёС‚РµРєС‚СѓСЂСѓ РїСЂРѕРіСЂР°РјРј (РїРѕ РІС‹Р±РѕСЂСѓ)",
            "study_year": 3,
            "type": 1,
            "course_id": 1,
        },
        {
            "year": 2019,
            "discipline": "Р›РѕРєР°Р»СЊРЅС‹Рµ СЃРµС‚Рё Рё РІС‹С‡РёСЃР»РёС‚РµР»СЊРЅС‹Рµ СЃРёСЃС‚РµРјС‹ (РїРѕ РІС‹Р±РѕСЂСѓ)",
            "study_year": 3,
            "type": 1,
            "course_id": 1,
        },
        {
            "year": 2019,
            "discipline": "РћСЂРіР°РЅРёР·Р°С†РёСЏ Рё РґРёР·Р°Р№РЅ СЃРѕРІСЂРµРјРµРЅРЅС‹С… РєРѕРјРїСЊСЋС‚РµСЂРѕРІ (РїРѕ РІС‹Р±РѕСЂСѓ)",
            "study_year": 3,
            "type": 1,
            "course_id": 1,
        },
        {
            "year": 2019,
            "discipline": "РџР°СЂР°Р»Р»РµР»СЊРЅС‹Рµ РІС‹С‡РёСЃР»РµРЅРёСЏ СЃ РёСЃРїРѕР»СЊР·РѕРІР°РЅРёРµРј РіСЂР°С„РёС‡РµСЃРєРёС… РїСЂРѕС†РµСЃСЃРѕСЂРѕРІ (РїРѕ РІС‹Р±РѕСЂСѓ)",
            "study_year": 3,
            "type": 1,
            "course_id": 1,
        },
        {
            "year": 2019,
            "discipline": "РџСЂРѕРіСЂР°РјРјРЅР°СЏ РёРЅР¶РµРЅРµСЂРёСЏ (РїРѕ РІС‹Р±РѕСЂСѓ)",
            "study_year": 3,
            "type": 1,
            "course_id": 1,
        },
        {
            "year": 2019,
            "discipline": "Р РµР°Р»РёР·Р°С†РёСЏ СЏР·С‹РєРѕРІ РїСЂРѕРіСЂР°РјРјРёСЂРѕРІР°РЅРёСЏ (РїРѕ РІС‹Р±РѕСЂСѓ)",
            "study_year": 3,
            "type": 1,
            "course_id": 1,
        },
        {
            "year": 2019,
            "discipline": "РЎРёСЃС‚РµРјС‹ СѓРїСЂР°РІР»РµРЅРёСЏ РєРѕРЅС‚РµРЅС‚РѕРј (РїРѕ РІС‹Р±РѕСЂСѓ)",
            "study_year": 3,
            "type": 1,
            "course_id": 1,
        },
        {
            "year": 2019,
            "discipline": "РњРµС‚РѕРґС‹ РІС‹С‡РёСЃР»РµРЅРёР№ (РїРѕ РІС‹Р±РѕСЂСѓ)",
            "study_year": 3,
            "type": 1,
            "course_id": 1,
        },
        {
            "year": 2019,
            "discipline": "Р­РєСЃС‚СЂРµРјР°Р»СЊРЅС‹Рµ Р·Р°РґР°С‡Рё (РїРѕ РІС‹Р±РѕСЂСѓ)",
            "study_year": 3,
            "type": 1,
            "course_id": 1,
        },
        {
            "year": 2019,
            "discipline": "Р’РІРµРґРµРЅРёРµ РІ РєРѕРјРїСЊСЋС‚РµСЂРЅРѕРµ РјРѕРґРµР»РёСЂРѕРІР°РЅРёРµ РґРёРЅР°РјРёС‡РµСЃРєРёС… СЃРёСЃС‚РµРј",
            "study_year": 4,
            "type": 1,
            "course_id": 1,
        },
        {
            "year": 2019,
            "discipline": "РўРµРѕСЂРёСЏ РІС‹С‡РёСЃР»РёС‚РµР»СЊРЅС‹С… РїСЂРѕС†РµСЃСЃРѕРІ Рё СЃС‚СЂСѓРєС‚СѓСЂ",
            "study_year": 4,
            "type": 1,
            "course_id": 1,
        },
        {
            "year": 2019,
            "discipline": "РђСЂС…РёС‚РµРєС‚СѓСЂР° РІС‹С‡РёСЃР»РёС‚РµР»СЊРЅС‹С… СЃРёСЃС‚РµРј Рё РєРѕРјРїСЊСЋС‚РµСЂРЅС‹С… СЃРµС‚РµР№",
            "study_year": 4,
            "type": 1,
            "course_id": 1,
        },
        {
            "year": 2019,
            "discipline": "РџСЂРѕРёР·РІРѕРґСЃС‚РІРµРЅРЅР°СЏ РїСЂР°РєС‚РёРєР°",
            "study_year": 4,
            "type": 1,
            "course_id": 1,
        },
        {
            "year": 2019,
            "discipline": "РРЅРѕСЃС‚СЂР°РЅРЅС‹Р№ СЏР·С‹Рє",
            "study_year": 4,
            "type": 3,
            "course_id": 1,
        },
        {
            "year": 2019,
            "discipline": "Р’СЃРїР»РµСЃРєРѕРІР°СЏ РѕР±СЂР°Р±РѕС‚РєР° С‡РёСЃР»РѕРІС‹С… РїРѕС‚РѕРєРѕРІ Рё СЂР°СЃРїР°СЂР°Р»Р»РµР»РёРІР°РЅРёРµ (РїРѕ РІС‹Р±РѕСЂСѓ)",
            "study_year": 4,
            "type": 1,
            "course_id": 1,
        },
        {
            "year": 2019,
            "discipline": "РљРѕРЅРµС‡РЅРѕ-Р°РІС‚РѕРјР°С‚РЅС‹Рµ РјРѕРґРµР»Рё. РђРЅР°Р»РёР·, СЃРёРЅС‚РµР· Рё РѕРїС‚РёРјРёР·Р°С†РёСЏ (РїРѕ РІС‹Р±РѕСЂСѓ)",
            "study_year": 4,
            "type": 1,
            "course_id": 1,
        },
        {
            "year": 2019,
            "discipline": "РћСЃРЅРѕРІС‹ РєРѕРјРїСЊСЋС‚РµСЂРЅРѕР№ Р±РµР·РѕРїР°СЃРЅРѕСЃС‚Рё (РїРѕ РІС‹Р±РѕСЂСѓ)",
            "study_year": 4,
            "type": 1,
            "course_id": 1,
        },
        {
            "year": 2019,
            "discipline": "РџСЂРѕРіСЂР°РјРјРёСЂРѕРІР°РЅРёРµ РЅР° РїР»Р°С‚С„РѕСЂРјРµ Microsoft.NET (РїРѕ РІС‹Р±РѕСЂСѓ)",
            "study_year": 4,
            "type": 1,
            "course_id": 1,
        },
        {
            "year": 2019,
            "discipline": "Р Р°Р·СЂР°Р±РѕС‚РєР° РРЅС‚РµСЂРЅРµС‚-РїСЂРёР»РѕР¶РµРЅРёР№ (РїРѕ РІС‹Р±РѕСЂСѓ)",
            "study_year": 4,
            "type": 1,
            "course_id": 1,
        },
        {
            "year": 2019,
            "discipline": "Р Р°СЃРїР°СЂР°Р»Р»РµР»РёРІР°РЅРёРµ Р°Р»РіРѕСЂРёС‚РјРѕРІ РІ РјРЅРѕРіРѕРїРѕС‚РѕС‡РЅС‹С… СЃРёСЃС‚РµРјР°С… (РїРѕ РІС‹Р±РѕСЂСѓ)",
            "study_year": 4,
            "type": 1,
            "course_id": 1,
        },
        {
            "year": 2019,
            "discipline": "Р Р°СЃРїСЂРµРґРµР»РµРЅРЅР°СЏ РѕР±СЂР°Р±РѕС‚РєР° РёРЅС„РѕСЂРјР°С†РёРё Рё NoSQL Р±Р°Р·С‹ РґР°РЅРЅС‹С… (РїРѕ РІС‹Р±РѕСЂСѓ)",
            "study_year": 4,
            "type": 1,
            "course_id": 1,
        },
        {
            "year": 2019,
            "discipline": "Р РµРєСѓСЂСЃРёРІРЅРѕ-Р»РѕРіРёС‡РµСЃРєРѕРµ РїСЂРѕРіСЂР°РјРјРёСЂРѕРІР°РЅРёРµ (РїРѕ РІС‹Р±РѕСЂСѓ)",
            "study_year": 4,
            "type": 1,
            "course_id": 1,
        },
        {
            "year": 2019,
            "discipline": "Р¤СѓРЅРєС†РёРѕРЅР°Р»СЊРЅРѕРµ РїСЂРѕРіСЂР°РјРјРёСЂРѕРІР°РЅРёРµ (РїРѕ РІС‹Р±РѕСЂСѓ)",
            "study_year": 4,
            "type": 1,
            "course_id": 1,
        },
        {
            "year": 2019,
            "discipline": "РњСѓР»СЊС‚РёР°РіРµРЅС‚РЅС‹Рµ С‚РµС…РЅРѕР»РѕРіРёРё (РїРѕ РІС‹Р±РѕСЂСѓ)",
            "study_year": 4,
            "type": 1,
            "course_id": 1,
        },
        {
            "year": 2019,
            "discipline": "РџР°СЂР°Р»Р»РµР»СЊРЅС‹Рµ Р°Р»РіРѕСЂРёС‚РјС‹ РѕР±СЂР°Р±РѕС‚РєРё РёР·РѕР±СЂР°Р¶РµРЅРёР№ (РїРѕ РІС‹Р±РѕСЂСѓ)",
            "study_year": 4,
            "type": 1,
            "course_id": 1,
        },
        {
            "year": 2019,
            "discipline": "РЎРёСЃС‚РµРјРЅРѕРµ РїСЂРѕРіСЂР°РјРјРёСЂРѕРІР°РЅРёРµ РґР»СЏ СЃРѕРІСЂРµРјРµРЅРЅС‹С… РїР»Р°С‚С„РѕСЂРј (РїРѕ РІС‹Р±РѕСЂСѓ)",
            "study_year": 4,
            "type": 1,
            "course_id": 1,
        },
        {
            "year": 2019,
            "discipline": "РўРµС…РЅРѕР»РѕРіРёСЏ СЂР°Р·СЂР°Р±РѕС‚РєРё РїСЂРѕРіСЂР°РјРјРЅРѕРіРѕ РѕР±РµСЃРїРµС‡РµРЅРёСЏ (РїРѕ РІС‹Р±РѕСЂСѓ)",
            "study_year": 4,
            "type": 1,
            "course_id": 1,
        },
        {
            "year": 2019,
            "discipline": "РўРµС…РЅРѕР»РѕРіРёСЏ СЃРёРЅС…СЂРѕРЅРЅРѕРіРѕ СЂР°СЃРїР°СЂР°Р»Р»РµР»РёРІР°РЅРёСЏ РІ РјРЅРѕРіРѕРїРѕС‚РѕС‡РЅС‹С… СЃРёСЃС‚РµРјР°С… (РїРѕ РІС‹Р±РѕСЂСѓ)",
            "study_year": 4,
            "type": 1,
            "course_id": 1,
        },
        {
            "year": 2019,
            "discipline": "РЇР·С‹Рє XML Рё РµРіРѕ РёСЃРїРѕР»СЊР·РѕРІР°РЅРёРµ (РїРѕ РІС‹Р±РѕСЂСѓ)",
            "study_year": 4,
            "type": 1,
            "course_id": 1,
        },
        {
            "year": 2019,
            "discipline": "РђРЅР°Р»РёР· Р°Р»РіРѕСЂРёС‚РјРѕРІ (РїРѕ РІС‹Р±РѕСЂСѓ)",
            "study_year": 4,
            "type": 1,
            "course_id": 1,
        },
        {
            "year": 2019,
            "discipline": "РљРѕРЅРєСЂРµС‚РЅР°СЏ РјР°С‚РµРјР°С‚РёРєР° (РїРѕ РІС‹Р±РѕСЂСѓ)",
            "study_year": 4,
            "type": 2,
            "course_id": 1,
        },
        {
            "year": 2019,
            "discipline": "РђР»РіРѕСЂРёС‚РјС‹ РЎРЈР‘Р” (РїРѕ РІС‹Р±РѕСЂСѓ)",
            "study_year": 4,
            "type": 1,
            "course_id": 1,
        },
        {
            "year": 2019,
            "discipline": "РЎРµС‚Рё РџРµС‚СЂРё Рё РїСЂРµРґСЃС‚Р°РІР»РµРЅРёРµ РїСЂРѕС†РµСЃСЃРѕРІ (РїРѕ РІС‹Р±РѕСЂСѓ)",
            "study_year": 4,
            "type": 1,
            "course_id": 1,
        },
        {
            "year": 2019,
            "discipline": "РџСЂРѕРµРєС‚РёСЂРѕРІР°РЅРёРµ РїСЂРѕРіСЂР°РјРјРЅРѕРіРѕ РѕР±РµСЃРїРµС‡РµРЅРёСЏ (РїРѕ РІС‹Р±РѕСЂСѓ)",
            "study_year": 4,
            "type": 1,
            "course_id": 1,
        },
        {
            "year": 2019,
            "discipline": "Р¤РёР»РѕСЃРѕС„РёСЏ (РѕРЅР»Р°Р№РЅ-РєСѓСЂСЃ)",
            "study_year": 4,
            "type": 3,
            "course_id": 1,
        },
        {
            "year": 2019,
            "discipline": "Р‘РµР·РѕРїР°СЃРЅРѕСЃС‚СЊ Р¶РёР·РЅРµРґРµСЏС‚РµР»СЊРЅРѕСЃС‚Рё (РѕРЅР»Р°Р№РЅРєСѓСЂСЃ)",
            "study_year": 4,
            "type": 3,
            "course_id": 1,
        },
        {
            "year": 2019,
            "discipline": "РџСЂРµРґРґРёРїР»РѕРјРЅР°СЏ РїСЂР°РєС‚РёРєР°",
            "study_year": 4,
            "type": 1,
            "course_id": 1,
        },
        {
            "year": 2019,
            "discipline": "РђРґРјРёРЅРёСЃС‚СЂРёСЂРѕРІР°РЅРёРµ РёРЅС„РѕСЂРјР°С†РёРѕРЅРЅС‹С… СЃРёСЃС‚РµРј (РЅР° Р°РЅРіР»РёР№СЃРєРѕРј СЏР·С‹РєРµ)",
            "study_year": 4,
            "type": 1,
            "course_id": 1,
        },
        {
            "year": 2019,
            "discipline": "РРЅС‚РµР»Р»РµРєС‚СѓР°Р»СЊРЅС‹Рµ СЃРёСЃС‚РµРјС‹ (РїРѕ РІС‹Р±РѕСЂСѓ)",
            "study_year": 4,
            "type": 1,
            "course_id": 1,
        },
        {
            "year": 2019,
            "discipline": "РљРІР°РЅС‚РѕРІС‹Рµ РєРѕРјРїСЊСЋС‚РµСЂС‹ (РїРѕ РІС‹Р±РѕСЂСѓ)",
            "study_year": 4,
            "type": 1,
            "course_id": 1,
        },
        {
            "year": 2019,
            "discipline": "РџР°СЂР°Р»Р»РµР»СЊРЅРѕРµ РїСЂРѕРіСЂР°РјРјРёСЂРѕРІР°РЅРёРµ СЃ РёСЃРїРѕР»СЊР·РѕРІР°РЅРёРµРј СЃС‚Р°РЅРґР°СЂС‚РЅС‹С… РёРЅС‚РµСЂС„РµР№СЃРѕРІ (РїРѕ РІС‹Р±РѕСЂСѓ)",
            "study_year": 4,
            "type": 1,
            "course_id": 1,
        },
        {
            "year": 2019,
            "discipline": "РџСЂР°РєС‚РёРєР° СЂР°Р·СЂР°Р±РѕС‚РєРё РґРѕРєСѓРјРµРЅС‚Р°С†РёРё (РїРѕ РІС‹Р±РѕСЂСѓ)",
            "study_year": 4,
            "type": 1,
            "course_id": 1,
        },
        {
            "year": 2019,
            "discipline": "Р Р°СЃРїР°СЂР°Р»Р»РµР»РёРІР°РЅРёРµ Р°Р»РіРѕСЂРёС‚РјРѕРІ РІ СЂР°СЃРїСЂРµРґРµР»РµРЅРЅС‹С… СЃРёСЃС‚РµРјР°С… (РїРѕ РІС‹Р±РѕСЂСѓ)",
            "study_year": 4,
            "type": 1,
            "course_id": 1,
        },
        {
            "year": 2019,
            "discipline": "РЎС‚Р°РЅРґР°СЂС‚С‹ РїР°СЂР°Р»Р»РµР»СЊРЅРѕРіРѕ РїСЂРѕРіСЂР°РјРјРёСЂРѕРІР°РЅРёСЏ (РїРѕ РІС‹Р±РѕСЂСѓ)",
            "study_year": 4,
            "type": 1,
            "course_id": 1,
        },
        {
            "year": 2019,
            "discipline": "РљРѕРјРїСЊСЋС‚РµСЂРЅРѕРµ РјРѕРґРµР»РёСЂРѕРІР°РЅРёРµ РґРёРЅР°РјРёС‡РµСЃРєРёС… СЃРёСЃС‚РµРј (РїРѕ РІС‹Р±РѕСЂСѓ)",
            "study_year": 4,
            "type": 1,
            "course_id": 1,
        },
        {
            "year": 2019,
            "discipline": "РўРµРѕСЂРёСЏ Рё РїСЂР°РєС‚РёРєР° РїР°СЂР°Р»Р»РµР»СЊРЅРѕРіРѕ РїСЂРѕРіСЂР°РјРјРёСЂРѕРІР°РЅРёСЏ (РїРѕ РІС‹Р±РѕСЂСѓ)",
            "study_year": 4,
            "type": 1,
            "course_id": 1,
        },
        {
            "year": 2019,
            "discipline": "РњР°С‚РµРјР°С‚РёС‡РµСЃРєРёРµ РѕСЃРЅРѕРІС‹ РёСЃРєСѓСЃСЃС‚РІРµРЅРЅРѕРіРѕ РёРЅС‚РµР»Р»РµРєС‚Р° (РїРѕ РІС‹Р±РѕСЂСѓ)",
            "study_year": 4,
            "type": 1,
            "course_id": 1,
        },
        {
            "year": 2019,
            "discipline": "РЎРёСЃС‚РµРјС‹ РёСЃРєСѓСЃСЃС‚РІРµРЅРЅРѕРіРѕ РёРЅС‚РµР»Р»РµРєС‚Р° (РїРѕ РІС‹Р±РѕСЂСѓ)",
            "study_year": 4,
            "type": 1,
            "course_id": 1,
        },
        {
            "year": 2019,
            "discipline": "РђР»РіРѕСЂРёС‚РјС‹ РєРѕРјРїСЊСЋС‚РµСЂРЅРѕРіРѕ Р·СЂРµРЅРёСЏ (РїРѕ РІС‹Р±РѕСЂСѓ)",
            "study_year": 4,
            "type": 1,
            "course_id": 1,
        },
        {
            "year": 2019,
            "discipline": "РљРѕРјРјСѓРЅРёРєР°С†РёРѕРЅРЅС‹Рµ СЃСЂРµРґС‹ РґР»СЏ РїР°СЂР°Р»Р»РµР»СЊРЅС‹С… СЃРёСЃС‚РµРј (РїРѕ РІС‹Р±РѕСЂСѓ)",
            "study_year": 4,
            "type": 1,
            "course_id": 1,
        },
        {
            "year": 2019,
            "discipline": "РњРѕРґРµР»Рё Рё Р°СЂС…РёС‚РµРєС‚СѓСЂС‹ РїСЂРѕРіСЂР°РјРј Рё Р·РЅР°РЅРёР№ (РїРѕ РІС‹Р±РѕСЂСѓ)",
            "study_year": 4,
            "type": 1,
            "course_id": 1,
        },
        {
            "year": 2019,
            "discipline": "Р Р°СЃРїР°СЂР°Р»Р»РµР»РёРІР°РЅРёРµ РІ РћРЎ UNIX (РїРѕ РІС‹Р±РѕСЂСѓ)",
            "study_year": 4,
            "type": 1,
            "course_id": 1,
        },
        {
            "year": 2019,
            "discipline": "РЎРѕРІСЂРµРјРµРЅРЅС‹Рµ РїРѕРґС…РѕРґС‹ Рє С…СЂР°РЅРµРЅРёСЋ, СѓРїСЂР°РІР»РµРЅРёСЋ Рё Р·Р°С‰РёС‚Рµ РґР°РЅРЅС‹С… (РїРѕ РІС‹Р±РѕСЂСѓ)",
            "study_year": 4,
            "type": 1,
            "course_id": 1,
        },
        {
            "year": 2019,
            "discipline": "РўРµС…РЅРѕР»РѕРіРёСЏ СЃРёРЅС…СЂРѕРЅРЅРѕРіРѕ СЂР°СЃРїР°СЂР°Р»Р»РµР»РёРІР°РЅРёСЏ РІ СЂР°СЃРїСЂРµРґРµР»РµРЅРЅС‹С… СЃРёСЃС‚РµРјР°С… (РїРѕ РІС‹Р±РѕСЂСѓ)",
            "study_year": 4,
            "type": 1,
            "course_id": 1,
        },
        {
            "year": 2019,
            "discipline": "РЈРїСЂР°РІР»РµРЅРёРµ РїСЂРѕРµРєС‚Р°РјРё (РїРѕ РІС‹Р±РѕСЂСѓ)",
            "study_year": 4,
            "type": 1,
            "course_id": 1,
        },
    ]

    thesis = []
    posts = [
        {
            "title": "Р­С‚Рѕ РїСЂРѕР±РЅР°СЏ РЅРѕРІРѕСЃС‚СЊ СЃ URI",
            "uri": "https://se.math.spbu.ru/",
            "author_id": 1,
        },
        {
            "title": "Р­С‚Рѕ РїСЂРѕР±РЅР°СЏ РЅРѕРІРѕСЃС‚СЊ СЃ С‚РµРєСЃС‚РѕРј",
            "text": "Р­С‚Рѕ РјРѕСЏ РїРµСЂРІР°СЏ РЅРѕРІРѕСЃС‚СЊ, РїРѕСЃРјРѕС‚СЂРёРј, РєР°Рє РѕРЅР° РІС‹РіР»СЏРґРёС‚?",
            "author_id": 2,
        },
    ]

    company = [
        {"name": "Raidix", "logo_uri": "raidix.png"},
        {"name": "Digital Design", "logo_uri": "digital_design.png"},
    ]

    themes_level = [
        {"level": "2 РєСѓСЂСЃ"},
        {"level": "3 РєСѓСЂСЃ"},
        {"level": "Р‘Р°РєР°Р»Р°РІСЂСЃРєР°СЏ Р’РљР "},
        {"level": "РњР°РіРёСЃС‚РµСЂСЃРєР°СЏ Р’РљР "},
    ]

    areas = [
        {"area": "РќР°РїСЂР°РІР»РµРЅРёРµ РѕР±СѓС‡РµРЅРёСЏ"},
        {"area": "РўРµС…РЅРѕР»РѕРіРёРё РїСЂРѕРіСЂР°РјРјРёСЂРѕРІР°РЅРёСЏ"},
        {"area": "РџСЂРѕРіСЂР°РјРјРЅР°СЏ РёРЅР¶РµРЅРµСЂРёСЏ"},
        {"area": "РњР°С‚РµРјР°С‚РёРєР° Рё РєРѕРјРїСЊСЋС‚РµСЂРЅС‹Рµ РЅР°СѓРєРё"},
        {"area": "РњРµС…Р°РЅРёРєР° Рё РјР°С‚РµРјР°С‚РёС‡РµСЃРєРѕРµ РјРѕРґРµР»РёСЂРѕРІР°РЅРёРµ"},
        {
            "area": "РџСЂРёРєР»Р°РґРЅР°СЏ РјР°С‚РµРјР°С‚РёРєР°, РїСЂРѕРіСЂР°РјРјРёСЂРѕРІР°РЅРёРµ Рё РёСЃРєСѓСЃСЃС‚РІРµРЅРЅС‹Р№ РёРЅС‚РµР»Р»РµРєС‚"
        },
        {"area": "РџСЂРѕРіСЂР°РјРјРЅР°СЏ РёРЅР¶РµРЅРµСЂРёСЏ"},
        {"area": "РђСЃС‚СЂРѕРЅРѕРјРёСЏ (СЃРїРµС†РёР°Р»РёС‚РµС‚)"},
        {"area": "Р¤СѓРЅРґР°РјРµРЅС‚Р°Р»СЊРЅР°СЏ РјРµС…Р°РЅРёРєР° (СЃРїРµС†РёР°Р»РёС‚РµС‚)"},
    ]

    d_themes = [
        {
            "title": "РР·СѓС‡РµРЅРёРµ Р¶СѓСЂРЅР°Р»РёСЂРѕРІР°РЅРёСЏ РґР»СЏ all flash RAID РјР°СЃСЃРёРІР°",
            "description": "Р–СѓСЂРЅР°Р»РёСЂРѕРІР°РЅРёРµ РїРѕР·РІРѕР»СЏРµС‚ СЂРµС€РёС‚СЊ РїСЂРѕР±Р»РµРјСѓ write-hole Рё РїРѕСЂС‡Сѓ РґР°РЅРЅС‹С… РІ СЃР»СѓС‡Р°Рµ СЃР»РѕР¶РЅС‹С… РѕС‚РєР°Р·РѕРІ СЃРёСЃС‚РµРјС‹. Р’ СЂР°РјРєР°С… Р·Р°РґР°С‡Рё РїСЂРµРґР»Р°РіР°РµС‚СЃСЏ РёР·СѓС‡РёС‚СЊ С‚РµС…РЅРѕР»РѕРіРёСЋ Р¶СѓСЂРЅР°Р»РёСЂРѕРІР°РЅРёСЏ РІ Linux dm-log. РСЃСЃР»РµРґРѕРІР°РЅРёРµ РІРєР»СЋС‡Р°РµС‚ РІ СЃРµР±СЏ С„СѓРЅРєС†РёРѕРЅР°Р»СЊРЅС‹Рµ РІРѕР·РјРѕР¶РЅРѕСЃС‚Рё, РїР°СЂР°РјРµС‚СЂС‹ РЅР°СЃС‚СЂРѕР№РєРё, РїСЂРѕРёР·РІРѕРґРёС‚РµР»СЊРЅРѕСЃС‚СЊ РїСЂРё СЂР°Р·Р»РёС‡РЅС‹С… РїР°С‚С‚РµСЂРЅР°С…. РРЅС‚РµРіСЂРёСЂРѕРІР°РЅРёРµ СЃ РЅР°С€РёРј RAID engine. Р’РѕР·РјРѕР¶РЅР° РёСЃСЃР»РµРґРѕРІР°РЅРёРµ Рё СЂРµР°Р»РёР·Р°С†РёСЏ Рё СЂР°Р·Р»РёС‡РЅС‹С… РїРѕРґС…РѕРґРѕРІ Рє Р¶СѓСЂРЅР°Р»РёСЂРѕРІР°РЅРёСЏ РІРЅСѓС‚СЂРё RAID engine Р° РЅРµ СЃС‚РѕСЂРѕРЅРЅРёРјРё СЃСЂРµРґСЃС‚РІР°РјРё, РґР»СЏ С‚РѕРіРѕ С‡С‚РѕР±С‹ РїРѕР»СѓС‡РёС‚СЊ Р±РѕР»РµРµ РїСЂРѕРёР·РІРѕРґРёС‚РµР»СЊРЅРѕРµ СЂРµС€РµРЅРёРµ.",
            "levels": [1, 2],
            "company_id": 1,
            "supervisor_id": 5,
            "consultant_id": 4,
            "author_id": 4,
            "status": 2,
        },
        {
            "title": "РћРїС‚РёРјРёР·Р°С†РёСЏ Р°Р»РіРѕСЂРёС‚РјР° Р°РґР°РїС‚РёРІРЅРѕРіРѕ РѕР±СЉРµРґРёРЅРµРЅРёСЏ Р·Р°РїСЂРѕСЃРѕРІ РІ RAID",
            "description": "РџСЂРё РїРѕСЃР»РµРґРѕРІР°С‚РµР»СЊРЅРѕР№ Р·Р°РїРёСЃРё РѕР±СЉРµРґРёРЅРµРЅРёРµ Р·Р°РїСЂРѕСЃРѕРІ РїРѕР·РІРѕР»СЏС‚ СЂРµС€РёС‚СЊ РїСЂРѕР±Р»РµРјСѓ read-modify-write РЅР° RAID СЃ РєРѕРЅС‚СЂРѕР»СЊРЅС‹РјРё СЃСѓРјРјР°РјРё. РРјРµСЋС‰РёР№СЃСЏ Р°Р»РіРѕСЂРёС‚Рј Р·Р°РІРёСЃРёС‚ РѕС‚ РЅРµСЃРєРѕР»СЊРєРёС… РїР°СЂР°РјРµС‚СЂРѕРІ Рё РµСЃС‚СЊ СЂСЏРґ РЅР°СЂР°Р±РѕС‚РѕРє, РєРѕС‚РѕСЂС‹Рµ РїРѕР·РІРѕР»СЏСЋС‚ Р°РІС‚РѕРјР°С‚РёС‡РµСЃРєРё РїРѕРґСЃС‚СЂР°РёРІР°С‚СЊ РїР°СЂР°РјРµС‚СЂС‹ РІ Р·Р°РІРёСЃРёРјРѕСЃС‚Рё РѕС‚ РЅР°РіСЂСѓР·РєРё (СЂР°Р·РјРµСЂ РёРѕ, РёРЅС‚РµРЅСЃРёРІРЅРѕСЃС‚СЊ, РјРЅРѕРіРѕРїРѕС‚РѕС‡РЅРѕСЃС‚СЊ), РѕРґРЅР°РєРѕ РЅРµ СЃРїСЂР°РІР»СЏРµС‚СЃСЏ СЃ РЅРµРєРѕС‚РѕСЂС‹РјРё РїР°С‚С‚РµСЂРЅР°РјРё. Р’ СЂР°РјРєР°С… СЂР°Р±РѕС‚С‹ РЅРµРѕР±С…РѕРґРёРјРѕ РёР·СѓС‡РёС‚СЊ Р°Р»РіРѕСЂРёС‚Рј Р°РґР°РїС‚РёРІРЅРѕРіРѕ РѕР±СЉРµРґРёРЅРµРЅРёСЏ, СѓР»СѓС‡С€РёС‚СЊ РµРіРѕ РёР»Рё РїСЂРµРґР»РѕР¶РёС‚СЊ Р°Р»СЊС‚РµСЂРЅР°С‚РёРІРЅС‹Р№. РўР°РєР¶Рµ РїСЂРµРґРїРѕР»Р°РіР°РµС‚ РёР·СѓС‡РµРЅРёСЏ РѕР±СЉРµРґРёРЅРµРЅРёСЏ Р·Р°РїСЂРѕСЃРѕРІ РЅРµ С‚РѕР»СЊРєРѕ РЅР° РёСЃРєСѓСЃСЃС‚РІРµРЅРЅС‹С… РїР°С‚С‚РµСЂРЅР°С….",
            "levels": [1, 2, 3],
            "company_id": 1,
            "supervisor_id": 5,
            "consultant_id": 4,
            "author_id": 3,
            "status": 2,
        },
        {
            "title": "РР·СѓС‡РµРЅРёРµ RAM РєСЌС€Р° РґР»СЏ RAID РјР°СЃСЃРёРІР°",
            "description": "Р’ СЂР°РјРєР°С… СЂР°Р±РѕС‚С‹ РїР»Р°РЅРёСЂСѓРµС‚СЃСЏ РёР·СѓС‡РёС‚СЊ С‚РµС…РЅРѕР»РѕРіРёРё Open Cache Acceleration Software РґР»СЏ СЂРµР°Р»РёР·Р°С†РёРё RAM cache РёР»Рё РєСЌС€ РЅР° Р±С‹СЃС‚СЂС‹С… РЅР°РєРѕРїРёС‚РµР»СЏС… РґР»СЏ РЅР°С€РµРіРѕ RAID engine. РР·СѓС‡РµРЅРёРµ РІРєР»СЋС‡Р°РµС‚ РІ СЃРµР±СЏ С„СѓРЅРєС†РёРѕРЅР°Р»СЊРЅС‹Рµ РІРѕР·РјРѕР¶РЅРѕСЃС‚Рё, РїР°СЂР°РјРµС‚СЂС‹ Рё РЅР°СЃС‚СЂРѕР№РєСѓ, РїСЂРѕРёР·РІРѕРґРёС‚РµР»СЊРЅРѕСЃС‚СЊ РІ СЂР°Р·Р»РёС‡РЅС‹С… РєРѕРЅС„РёРіСѓСЂР°С†РёСЏС… Рё РїР°С‚С‚РµСЂРЅР°С… РЅР°РіСЂСѓР·РєРё. Р’РЅРµРґСЂРµРЅРёРµ С‚РµС…РЅРѕР»РѕРіРёРё, РµРµ СѓР»СѓС‡С€РµРЅРёРµ Рё Р°РґР°РїС‚Р°С†РёСЏ РїРѕРґ РЅР°С€ RAID. Р’РѕР·РјРѕР¶РЅРѕ РёР·СѓС‡РµРЅРёРµ Рё СЃСЂР°РІРЅРµРЅРёРµ СЃ РёРјРµСЋС‰РёРјРёСЃСЏ С‚РµС…РЅРѕР»РѕРіРёСЏРјРё РєРµС€РёСЂРѕРІР°РЅРёСЏ РІ Linux С‚Р°РєРёРјРё РєР°Рє dm-cache, bcache. Р’РѕР·РјРѕР¶РЅРѕ С‚Р°РєР¶Рµ СѓРіР»СѓР±Р»РµРЅРёРµ РІ РёР·СѓС‡РµРЅРёРµ Р°Р»РіРѕСЂРёС‚РјРѕРІ Read-Ahead.",
            "levels": [3, 4],
            "company_id": 2,
            "supervisor_id": 5,
            "consultant_id": 4,
            "author_id": 4,
            "status": 2,
        },
    ]

    # Check if databases directory exists. If not, create it
    db_dir = Path(SQLITE_DATABASE_PATH)
    if not db_dir.exists():
        db_dir.mkdir()

    # Check if db file already exists. If so, backup it
    db_file = Path(SQLITE_DATABASE_PATH + SQLITE_DATABASE_NAME)
    if db_file.is_file():
        shutil.copyfile(
            SQLITE_DATABASE_PATH + SQLITE_DATABASE_NAME,
            SQLITE_DATABASE_PATH + SQLITE_DATABASE_BACKUP_NAME,
        )

    # Init DB
    db.session.commit()  # https://stackoverflow.com/questions/24289808/drop-all-freezes-in-flask-with-sqlalchemy
    db.drop_all()
    db.create_all()

    # Create areas
    print("Create areas")
    for area in areas:
        a = AreasOfStudy(area=area["area"])

        db.session.add(a)
        db.session.commit()

    # Create users
    print("Create users")
    for user in users:
        u = Users(
            email=user["email"],
            password_hash=generate_password_hash(urandom(16).hex()),
            first_name=user["first_name"],
            last_name=user["last_name"],
            middle_name=user["middle_name"],
            avatar_uri=user["avatar_uri"],
        )

        db.session.add(u)
        db.session.commit()

    # Create staff
    print("Create staff")
    for user in staff:
        u = Users.query.filter_by(email=user["official_email"]).first()

        if "science_degree" in user:
            s = Staff(
                position=user["position"],
                science_degree=user["science_degree"],
                official_email=user["official_email"],
                still_working=user["still_working"],
                user_id=u.id,
            )
        else:
            s = Staff(
                position=user["position"],
                official_email=user["official_email"],
                still_working=user["still_working"],
                user_id=u.id,
            )

        db.session.add(s)
        db.session.commit()

    # Create WorkTypes
    print("Create worktypes")
    for w in wtypes:
        wt = Worktype(type=w["type"])
        db.session.add(wt)
        db.session.commit()

    # Create Courses
    print("Create courses")
    for course in courses:
        c = Courses(name=course["name"], code=course["code"])
        db.session.add(c)
        db.session.commit()

    # Create Curriculum
    print("Create curriculum")
    for cur in curriculum:
        if "type" in cur:
            c = Curriculum(
                year=cur["year"],
                discipline=cur["discipline"],
                study_year=cur["study_year"],
                type=cur["type"],
                course_id=cur["course_id"],
            )
        else:
            c = Curriculum(
                year=cur["year"],
                discipline=cur["discipline"],
                study_year=cur["study_year"],
                course_id=cur["course_id"],
            )

        db.session.add(c)
        db.session.commit()

    # Create News
    print("Create news")
    for cur in posts:
        if "uri" in cur:
            c = Posts(
                title=cur["title"],
                uri=cur["uri"],
                domain="se.math.spbu.ru",
                author_id=cur["author_id"],
            )
        else:
            c = Posts(title=cur["title"], text=cur["text"], author_id=cur["author_id"])

        db.session.add(c)
        db.session.commit()

    for tag in tags:
        t = Tags(name=tag["name"])
        db.session.add(t)
        db.session.commit()

    # Create Thesis
    print("Create thesis")
    for work in thesis:
        if "source_uri" in work:
            t = Thesis(
                name_ru=work["name_ru"],
                name_en=work["name_en"],
                description=work["description"],
                text_uri=work["text_uri"],
                presentation_uri=work["presentation_uri"],
                supervisor_review_uri=work["supervisor_review_uri"],
                reviewer_review_uri=work["reviewer_review_uri"],
                author=work["author"],
                supervisor_id=work["supervisor_id"],
                reviewer_id=work["reviewer_id"],
                publish_year=work["publish_year"],
                type_id=work["type_id"],
                course_id=1,
                source_uri=work["source_uri"],
            )
        else:
            t = Thesis(
                name_ru=work["name_ru"],
                name_en=work["name_en"],
                description=work["description"],
                text_uri=work["text_uri"],
                presentation_uri=work["presentation_uri"],
                supervisor_review_uri=work["supervisor_review_uri"],
                reviewer_review_uri=work["reviewer_review_uri"],
                author=work["author"],
                supervisor_id=work["supervisor_id"],
                reviewer_id=work["reviewer_id"],
                publish_year=work["publish_year"],
                type_id=work["type_id"],
                course_id=1,
            )

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
        c = Company(name=cur["name"], logo_uri=cur["logo_uri"])

        db.session.add(c)
        db.session.commit()

    # Create ThemesLevels
    print("Create diploma theme levels")
    for cur in themes_level:
        c = ThemesLevel(level=cur["level"])

        db.session.add(c)
        db.session.commit()

    # Create DiplomaThems
    print("Create diploma themes")
    for cur in d_themes:
        c = DiplomaThemes(
            title=cur["title"],
            description=cur["description"],
            company_id=cur["company_id"],
            supervisor_id=cur["supervisor_id"],
            consultant_id=cur["consultant_id"],
            author_id=cur["author_id"],
            status=cur["status"],
        )

        for tl_id in cur["levels"]:
            c.levels.append(ThemesLevel.query.filter_by(id=tl_id).first())

        db.session.add(c)
        db.session.commit()

    # Create InternshipsFormat
    print("Create internship formats")
    print("Create addinternship formats")
    for cur in internship_formats:
        c = InternshipFormat(format=cur["format"])

        db.session.add(c)
        db.session.commit()

    print("Create internship tags")
    for cur in internship_tags:
        t = InternshipTag(tag=cur["tag"])

        db.session.add(t)
        db.session.commit()

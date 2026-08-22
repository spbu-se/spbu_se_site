# -*- coding: utf-8 -*-
from datetime import datetime

import pytest

from se_models import DiplomaThemesTags, Tags


def test_staff_repr(app_ctx):
    from se_models import Staff, Users, db

    u = Users(email="staff@test.ru", first_name="Staff", last_name="User")
    db.session.add(u)
    db.session.flush()
    s = Staff(position="Professor", official_email="staff@test.ru", user_id=u.id)
    db.session.add(s)
    db.session.commit()
    assert repr(s) == "<'staff@test.ru'>"


def test_users_str_without_email(app_ctx):
    from se_models import Users, db

    u = Users(first_name="NoEmail", last_name="User")
    db.session.add(u)
    db.session.commit()
    assert str(u) == "User NoEmail"


def test_users_str_with_email(app_ctx):
    from se_models import Users, db

    u = Users(first_name="With", last_name="Email", email="with@test.ru")
    db.session.add(u)
    db.session.commit()
    assert str(u) == "Email With (with@test.ru)"


def test_users_str_only_first_name(app_ctx):
    from se_models import Users, db

    u = Users(first_name="OnlyFirst")
    db.session.add(u)
    db.session.commit()
    assert str(u) == " OnlyFirst"


def test_users_str_middle_name(app_ctx):
    from se_models import Users, db

    u = Users(first_name="Ivan", middle_name="Petrovich", last_name="Sidorov", email="ivan@test.ru")
    db.session.add(u)
    db.session.commit()
    assert str(u) == "Sidorov Ivan Petrovich (ivan@test.ru)"


@pytest.mark.parametrize(
    "model_name,kwargs,exp_repr,exp_str",
    [
        ("InternshipFormat", {"format": "Online"}, None, "Online"),
        ("InternshipTag", {"tag": "Python"}, None, "Python"),
        ("ThesisOnReviewWorktype", {"type": "Bachelor"}, "Bachelor", None),
        ("Courses", {"name": "Algorithms", "code": "CS101"}, "<'Algorithms'>", None),
        ("PostType", {"name": "Announcement", "type": 2}, None, "Announcement"),
        ("InternshipFormat", {"format": "Remote"}, "Remote", None),
        ("InternshipTag", {"tag": "Go"}, "Go", None),
        (
            "ThesisReport",
            {
                "was_done": "Completed X",
                "planned_to_do": "Do Y",
                "current_thesis_id": 1,
                "author_id": 1,
            },
            "Completed X",
            "Completed X",
        ),
        ("InternshipCompany", {"name": "Acme Corp"}, "Acme Corp", None),
        ("Worktype", {"type": "bachelor"}, "bachelor", "bachelor"),
        ("ThesisOnReviewWorktype", {"type": "Master"}, None, "Master"),
        ("Courses", {"name": "Data Structures", "code": "DS101"}, None, "Data Structures"),
        ("AreasOfStudy", {"area": "Applied Math"}, None, "Applied Math"),
        ("Tags", {"name": "python"}, "python", "python"),
        ("PostType", {"name": "Event", "type": 3}, "Event", None),
        ("ThemesLevel", {"level": "Hard"}, "Hard", None),
        ("DiplomaThemesTags", {"name": "AI"}, "AI", "AI"),
        ("Company", {"name": "TechCorp"}, "TechCorp", None),
        ("PromoCode", {"code": "DISCOUNT2024"}, "DISCOUNT2024", "DISCOUNT2024"),
        (
            "Notification",
            {"recipient": 1, "title": "Welcome", "content": "Hello!"},
            "Welcome",
            "Welcome",
        ),
        ("Notification", {"recipient": 1, "content": "No title"}, "", ""),
    ],
)
def test_model_repr_str(app_ctx, model_name, kwargs, exp_repr, exp_str):
    import importlib

    from se_models import db

    model = getattr(importlib.import_module("se_models"), model_name)
    obj = model(**kwargs)
    db.session.add(obj)
    db.session.commit()
    if exp_repr is not None:
        assert repr(obj) == exp_repr
    if exp_str is not None:
        assert str(obj) == exp_str


def test_current_thesis_repr_str(app_ctx):
    from se_models import AreasOfStudy, CurrentThesis, Worktype, db

    wt = Worktype(type="practice")
    db.session.add(wt)
    db.session.flush()
    a = AreasOfStudy(area="CS")
    db.session.add(a)
    db.session.flush()
    ct = CurrentThesis(author_id=1, worktype_id=wt.id, area_id=a.id)
    ct.title = "My Thesis"
    db.session.add(ct)
    db.session.commit()
    assert repr(ct) == "My Thesis"
    assert str(ct) == "My Thesis"


def test_notification_practice_repr_str(app_ctx):
    from se_models import NotificationPractice, db

    n = NotificationPractice(recipient_id=1, content="Test notification")
    db.session.add(n)
    db.session.commit()
    assert repr(n) == "Test notification"
    assert str(n) == "Test notification"


def test_thesis_task_repr_str(app_ctx):
    from se_models import ThesisTask, db

    t = ThesisTask(task_text="Implement feature X", current_thesis_id=1)
    db.session.add(t)
    db.session.commit()
    assert repr(t) == "Implement feature X"
    assert str(t) == "Implement feature X"


def test_internships_repr_str(app_ctx):
    from se_models import Internships, Users, db

    u = Users(first_name="Author", last_name="User", email="author@test.ru")
    db.session.add(u)
    db.session.flush()
    i = Internships(
        name_vacancy="Junior Dev",
        salary="50000",
        requirements="Python",
        author_id=u.id,
    )
    db.session.add(i)
    db.session.commit()
    assert repr(i) == "Junior Dev"
    assert str(i) == "Junior Dev"


def test_diploma_themes_repr_str(app_ctx):
    from se_models import DiplomaThemes, Users, db

    u = Users(first_name="D", last_name="User", email="d@test.ru")
    db.session.add(u)
    db.session.flush()
    dt = DiplomaThemes(
        title="AI Research",
        author_id=u.id,
        consultant_id=u.id,
    )
    db.session.add(dt)
    db.session.commit()
    assert repr(dt) == "AI Research"
    assert str(dt) == "AI Research"


def test_reviewer_repr_str(app_ctx):
    from se_models import Reviewer, Users, db

    u = Users(first_name="Review", last_name="User", email="review@test.ru")
    db.session.add(u)
    db.session.flush()
    r = Reviewer(user_id=u.id)
    db.session.add(r)
    db.session.commit()
    assert str(r) == "User Review"
    assert repr(r) == "User Review"


@pytest.mark.parametrize(
    "upvote,name,title,expected_substrings",
    [
        (True, "news", "Test Post", ["Up", "User Voter", "Test Post"]),
        (False, "news2", "Another Post", ["Down"]),
    ],
)
def test_post_vote_repr(app_ctx, upvote, name, title, expected_substrings):
    from se_models import Posts, PostType, PostVote, Users, db

    pt = PostType(name=name, type=1)
    db.session.add(pt)
    db.session.flush()
    author = Users(first_name="Author", last_name="Voter", email="voter@test.ru")
    db.session.add(author)
    db.session.flush()
    post = Posts(title=title, text="Content", author_id=author.id, type_id=pt.id)
    db.session.add(post)
    db.session.flush()
    voter = Users(first_name="Voter", last_name="User", email="voter2@test.ru")
    db.session.add(voter)
    db.session.flush()
    pv = PostVote(user_id=voter.id, post_id=post.id, upvote=upvote)
    db.session.add(pv)
    db.session.commit()
    result = repr(pv)
    for sub in expected_substrings:
        assert sub in result


def test_recalculate_post_rank(app_ctx):
    from flask_se_config import get_hours_since, post_ranking_score
    from se_models import Posts, PostType, Users, db, recalculate_post_rank

    pt = PostType(name="rank_test", type=1)
    db.session.add(pt)
    db.session.flush()
    u = Users(first_name="Rank", last_name="Test", email="rank@test.ru")
    db.session.add(u)
    db.session.flush()
    post = Posts(
        title="Rank Post",
        text="Content",
        author_id=u.id,
        votes=10,
        views=100,
        type_id=pt.id,
        created_on=datetime(2024, 1, 1),
    )
    db.session.add(post)
    db.session.commit()
    recalculate_post_rank()
    expected = post_ranking_score(10, get_hours_since(post.created_on), 100)
    assert post.rank == expected


def test_add_mail_notification_nonexistent_user(app_ctx):
    from se_models import Notification, add_mail_notification

    add_mail_notification(99999, "Title", "Content")
    assert Notification.query.count() == 0


def test_add_mail_notification_existing_user(app_ctx):
    from se_models import Notification, Users, add_mail_notification, db

    u = Users(first_name="Notify", last_name="User", email="notify@test.ru")
    db.session.add(u)
    db.session.commit()

    add_mail_notification(u.id, "Hello", "World")
    n = Notification.query.first()
    assert n is not None
    assert n.title == "Hello"
    assert n.content == "World"
    assert n.recipient == u.id


def test_deadline_repr_str(app_ctx):
    from se_models import AreasOfStudy, Deadline, Worktype, db

    wt = Worktype(type="diploma")
    db.session.add(wt)
    db.session.flush()
    a = AreasOfStudy(area="CS")
    db.session.add(a)
    db.session.flush()
    d = Deadline(worktype_id=wt.id, area_id=a.id)
    db.session.add(d)
    db.session.commit()
    assert "Deadline" in repr(d)
    assert "Deadline" in str(d)


def test_thesis_repr_str(app_ctx):
    from se_models import Courses, Thesis, Worktype, db

    wt = Worktype(type="master")
    db.session.add(wt)
    db.session.flush()
    c = Courses(name="CS", code="CS101")
    db.session.add(c)
    db.session.flush()
    t = Thesis(
        name_ru="ML Research", author="John", type_id=wt.id, course_id=c.id, publish_year=2024
    )
    db.session.add(t)
    db.session.commit()
    assert repr(t) == "ML Research"
    assert str(t) == "ML Research"


def test_curriculum_repr_str(app_ctx):
    from se_models import Courses, Curriculum, db

    c = Courses(name="CS", code="CS101")
    db.session.add(c)
    db.session.flush()
    cur = Curriculum(year=2024, discipline="Algorithms", study_year=2, course_id=c.id)
    db.session.add(cur)
    db.session.commit()
    assert repr(cur) == "Algorithms (2024)"
    assert str(cur) == "Algorithms (2024)"


def test_posts_repr_str(app_ctx):
    from se_models import Posts, PostType, Users, db

    pt = PostType(name="news", type=1)
    db.session.add(pt)
    db.session.flush()
    u = Users(first_name="Author", last_name="User", email="author@test.ru")
    db.session.add(u)
    db.session.flush()
    p = Posts(title="Hello World", text="Content", author_id=u.id, type_id=pt.id)
    db.session.add(p)
    db.session.commit()
    assert repr(p) == "Hello World"
    assert str(p) == "Hello World"


def test_thesis_review_repr_str(app_ctx):
    from se_models import ThesisReview, db

    tr = ThesisReview(verdict=1)
    db.session.add(tr)
    db.session.commit()
    assert "Review" in repr(tr)
    assert "Review" in str(tr)


def test_thesis_on_review_repr_str(app_ctx):
    from se_models import AreasOfStudy, ThesisOnReview, Worktype, db

    wt = Worktype(type="diploma")
    db.session.add(wt)
    db.session.flush()
    a = AreasOfStudy(area="CS")
    db.session.add(a)
    db.session.flush()
    tor = ThesisOnReview(name_ru="Quantum Computing", type_id=wt.id, area_id=a.id)
    db.session.add(tor)
    db.session.commit()
    assert repr(tor) == "Quantum Computing"
    assert str(tor) == "Quantum Computing"


def _make_school(
    project_name="AI Assistant",
    description="Build an AI",
    tech="Python",
    advisors="Prof. X",
    requirements="Laptop",
    year=None,
):
    from se_models import SummerSchool

    fields = {
        "project_name": project_name,
        "description": description,
        "tech": tech,
        "advisors": advisors,
        "requirements": requirements,
    }
    if year is not None:
        fields["year"] = year
    return SummerSchool(**fields)


def test_summer_school_repr_str(app_ctx):
    from se_models import db

    s = _make_school()
    db.session.add(s)
    db.session.commit()
    assert repr(s) == "AI Assistant"
    assert str(s) == "AI Assistant"


def test_summer_school_default_year(app_ctx):
    from se_models import db

    s = _make_school(
        project_name="No Year",
        description="Test",
        tech="Python",
        advisors="Prof. Y",
        requirements="None",
    )
    db.session.add(s)
    db.session.commit()
    assert s.year == 2021


def test_summer_school_query_by_year(app_ctx):
    from se_models import SummerSchool, db

    for y in [2024, 2024, 2025]:
        db.session.add(
            _make_school(
                project_name=f"Project {y}",
                description="Desc",
                tech="Tech",
                advisors="Advisor",
                requirements="Req",
                year=y,
            )
        )
    db.session.commit()
    assert len(SummerSchool.query.filter_by(year=2024).all()) == 2
    assert len(SummerSchool.query.filter_by(year=2025).all()) == 1
    assert len(SummerSchool.query.filter_by(year=2026).all()) == 0


def test_summer_school_update(app_ctx):
    from se_models import db

    s = _make_school(
        project_name="Old Name",
        description="Old desc",
        tech="Java",
        advisors="Dr. A",
        requirements="RAM",
    )
    db.session.add(s)
    db.session.commit()

    s.project_name = "New Name"
    s.year = 2025
    db.session.commit()
    db.session.refresh(s)
    assert s.project_name == "New Name"
    assert s.year == 2025


def test_summer_school_delete(app_ctx):
    from se_models import SummerSchool, db

    s = _make_school(
        project_name="To Delete",
        description="Del",
        tech="C++",
        advisors="Dr. B",
        requirements="Disk",
    )
    db.session.add(s)
    db.session.commit()
    sid = s.id
    db.session.delete(s)
    db.session.commit()
    assert db.session.get(SummerSchool, sid) is None


def test_summer_school_nullable_fields(app_ctx):
    from se_models import db

    s = _make_school(
        project_name="Nullable Test",
        description="Test",
        tech="Rust",
        advisors="Dr. C",
        requirements="CPU",
    )
    db.session.add(s)
    db.session.commit()
    assert s.repo is None
    assert s.demos is None


def test_summer_school_filter_by_year_empty(app_ctx):
    from se_models import SummerSchool

    assert SummerSchool.query.filter_by(year=2099).all() == []


def test_summer_school_multiple_years_order(app_ctx):
    from se_models import SummerSchool, db

    for y in [2021, 2022, 2023]:
        db.session.add(
            _make_school(
                project_name=f"P{y}",
                description="D",
                tech="T",
                advisors="A",
                requirements="R",
                year=y,
            )
        )
    db.session.commit()
    years = [s.year for s in SummerSchool.query.order_by(SummerSchool.year).all()]
    assert years == [2021, 2022, 2023]


@pytest.mark.parametrize("model_cls", [Tags, DiplomaThemesTags])
def test_tags_create_and_query(app_ctx, model_cls):
    from se_models import db

    obj = model_cls(name="machine-learning")
    db.session.add(obj)
    db.session.commit()
    assert model_cls.query.filter_by(name="machine-learning").first() is not None


@pytest.mark.parametrize("model_cls", [Tags, DiplomaThemesTags])
def test_tags_delete(app_ctx, model_cls):
    from se_models import db

    obj = model_cls(name="temporary-tag")
    db.session.add(obj)
    db.session.commit()
    oid = obj.id
    db.session.delete(obj)
    db.session.commit()
    assert db.session.get(model_cls, oid) is None


def test_init_db_creates_all_26_tables_in_one_call(app_ctx):
    from conftest import _assert_seeded_tables

    from se_models import (
        Curriculum,
        init_db,
    )

    init_db()
    _assert_seeded_tables()
    assert Curriculum.query.count() > 0

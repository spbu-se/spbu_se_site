# -*- coding: utf-8 -*-
from datetime import datetime


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


def test_internship_format_str(app_ctx):
    from se_models import InternshipFormat, db

    f = InternshipFormat(format="Online")
    db.session.add(f)
    db.session.commit()
    assert str(f) == "Online"


def test_internship_tag_str(app_ctx):
    from se_models import InternshipTag, db

    t = InternshipTag(tag="Python")
    db.session.add(t)
    db.session.commit()
    assert str(t) == "Python"


def test_current_thesis_repr(app_ctx):
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


def test_notification_practice_repr(app_ctx):
    from se_models import NotificationPractice, db

    n = NotificationPractice(recipient_id=1, content="Test notification")
    db.session.add(n)
    db.session.commit()
    assert repr(n) == "Test notification"


def test_thesis_task_repr(app_ctx):
    from se_models import ThesisTask, db

    t = ThesisTask(task_text="Implement feature X", current_thesis_id=1)
    db.session.add(t)
    db.session.commit()
    assert repr(t) == "Implement feature X"


def test_internships_repr(app_ctx):
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


def test_internships_str(app_ctx):
    from se_models import Internships, Users, db

    u = Users(first_name="A2", last_name="U2", email="a2@test.ru")
    db.session.add(u)
    db.session.flush()
    i = Internships(
        name_vacancy="Senior Dev",
        salary="100000",
        requirements="Go",
        author_id=u.id,
    )
    db.session.add(i)
    db.session.commit()
    assert str(i) == "Senior Dev"


def test_thesis_on_review_worktype_repr(app_ctx):
    from se_models import ThesisOnReviewWorktype, db

    t = ThesisOnReviewWorktype(type="Bachelor")
    db.session.add(t)
    db.session.commit()
    assert repr(t) == "Bachelor"


def test_courses_repr(app_ctx):
    from se_models import Courses, db

    c = Courses(name="Algorithms", code="CS101")
    db.session.add(c)
    db.session.commit()
    assert repr(c) == "<'Algorithms'>"


def test_post_vote_repr_upvote(app_ctx):
    from se_models import Posts, PostType, PostVote, Users, db

    pt = PostType(name="news", type=1)
    db.session.add(pt)
    db.session.flush()
    author = Users(first_name="Author", last_name="Voter", email="voter@test.ru")
    db.session.add(author)
    db.session.flush()
    post = Posts(title="Test Post", text="Content", author_id=author.id, type_id=pt.id)
    db.session.add(post)
    db.session.flush()
    voter = Users(first_name="Voter", last_name="User", email="voter2@test.ru")
    db.session.add(voter)
    db.session.flush()
    pv = PostVote(user_id=voter.id, post_id=post.id, upvote=True)
    db.session.add(pv)
    db.session.commit()
    result = repr(pv)
    assert "Up" in result
    assert voter.get_name() in result
    assert "Test Post" in result


def test_post_vote_repr_downvote(app_ctx):
    from se_models import Posts, PostType, PostVote, Users, db

    pt = PostType(name="news2", type=1)
    db.session.add(pt)
    db.session.flush()
    author = Users(first_name="Auth2", last_name="Usr2", email="au2@test.ru")
    db.session.add(author)
    db.session.flush()
    post = Posts(title="Another Post", text="Stuff", author_id=author.id, type_id=pt.id)
    db.session.add(post)
    db.session.flush()
    voter = Users(first_name="Down", last_name="Voter", email="down@test.ru")
    db.session.add(voter)
    db.session.flush()
    pv = PostVote(user_id=voter.id, post_id=post.id, upvote=False)
    db.session.add(pv)
    db.session.commit()
    result = repr(pv)
    assert "Down" in result


def test_post_type_str(app_ctx):
    from se_models import PostType, db

    pt = PostType(name="Announcement", type=2)
    db.session.add(pt)
    db.session.commit()
    assert str(pt) == "Announcement"


def test_diploma_themes_repr(app_ctx):
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


def test_diploma_themes_str(app_ctx):
    from se_models import DiplomaThemes, Users, db

    u = Users(first_name="S", last_name="User", email="s@test.ru")
    db.session.add(u)
    db.session.flush()
    dt = DiplomaThemes(
        title="ML Study",
        author_id=u.id,
        consultant_id=u.id,
    )
    db.session.add(dt)
    db.session.commit()
    assert str(dt) == "ML Study"


def test_reviewer_str(app_ctx):
    from se_models import Reviewer, Users, db

    u = Users(first_name="Review", last_name="User", email="review@test.ru")
    db.session.add(u)
    db.session.flush()
    r = Reviewer(user_id=u.id)
    db.session.add(r)
    db.session.commit()
    assert str(r) == "User Review"


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


def test_internship_format_repr(app_ctx):
    from se_models import InternshipFormat, db

    f = InternshipFormat(format="Remote")
    db.session.add(f)
    db.session.commit()
    assert repr(f) == "Remote"


def test_internship_tag_repr(app_ctx):
    from se_models import InternshipTag, db

    t = InternshipTag(tag="Go")
    db.session.add(t)
    db.session.commit()
    assert repr(t) == "Go"


def test_current_thesis_str(app_ctx):
    from se_models import AreasOfStudy, CurrentThesis, Worktype, db

    wt = Worktype(type="practice")
    db.session.add(wt)
    db.session.flush()
    a = AreasOfStudy(area="CS")
    db.session.add(a)
    db.session.flush()
    ct = CurrentThesis(author_id=1, worktype_id=wt.id, area_id=a.id)
    ct.title = "Active Work"
    db.session.add(ct)
    db.session.commit()
    assert str(ct) == "Active Work"


def test_notification_practice_str(app_ctx):
    from se_models import NotificationPractice, db

    n = NotificationPractice(recipient_id=1, content="Practice note")
    db.session.add(n)
    db.session.commit()
    assert str(n) == "Practice note"


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


def test_thesis_task_str(app_ctx):
    from se_models import ThesisTask, db

    t = ThesisTask(task_text="Write tests", current_thesis_id=1)
    db.session.add(t)
    db.session.commit()
    assert str(t) == "Write tests"


def test_thesis_report_repr_str(app_ctx):
    from se_models import ThesisReport, db

    r = ThesisReport(was_done="Completed X", planned_to_do="Do Y", current_thesis_id=1, author_id=1)
    db.session.add(r)
    db.session.commit()
    assert repr(r) == "Completed X"
    assert str(r) == "Completed X"


def test_internship_company_repr(app_ctx):
    from se_models import InternshipCompany, db

    c = InternshipCompany(name="Acme Corp")
    db.session.add(c)
    db.session.commit()
    assert repr(c) == "Acme Corp"


def test_worktype_repr_str(app_ctx):
    from se_models import Worktype, db

    wt = Worktype(type="bachelor")
    db.session.add(wt)
    db.session.commit()
    assert repr(wt) == "bachelor"
    assert str(wt) == "bachelor"


def test_thesis_on_review_worktype_str(app_ctx):
    from se_models import ThesisOnReviewWorktype, db

    t = ThesisOnReviewWorktype(type="Master")
    db.session.add(t)
    db.session.commit()
    assert str(t) == "Master"


def test_courses_str(app_ctx):
    from se_models import Courses, db

    c = Courses(name="Data Structures", code="DS101")
    db.session.add(c)
    db.session.commit()
    assert str(c) == "Data Structures"


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


def test_areas_of_study_str(app_ctx):
    from se_models import AreasOfStudy, db

    a = AreasOfStudy(area="Applied Math")
    db.session.add(a)
    db.session.commit()
    assert str(a) == "Applied Math"


def test_tags_repr_str(app_ctx):
    from se_models import Tags, db

    t = Tags(name="python")
    db.session.add(t)
    db.session.commit()
    assert repr(t) == "python"
    assert str(t) == "python"


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


def test_summer_school_repr_str(app_ctx):
    from se_models import SummerSchool, db

    s = SummerSchool(
        year=2025,
        project_name="AI Assistant",
        description="Build an AI",
        tech="Python",
        advisors="Prof. X",
        requirements="Laptop",
    )
    db.session.add(s)
    db.session.commit()
    assert repr(s) == "AI Assistant"
    assert str(s) == "AI Assistant"


def test_summer_school_default_year(app_ctx):
    from se_models import SummerSchool, db

    s = SummerSchool(
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
        s = SummerSchool(
            year=y,
            project_name=f"Project {y}",
            description="Desc",
            tech="Tech",
            advisors="Advisor",
            requirements="Req",
        )
        db.session.add(s)
    db.session.commit()
    assert len(SummerSchool.query.filter_by(year=2024).all()) == 2
    assert len(SummerSchool.query.filter_by(year=2025).all()) == 1
    assert len(SummerSchool.query.filter_by(year=2026).all()) == 0


def test_summer_school_update(app_ctx):
    from se_models import SummerSchool, db

    s = SummerSchool(
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

    s = SummerSchool(
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
    from se_models import SummerSchool, db

    s = SummerSchool(
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
        s = SummerSchool(
            year=y,
            project_name=f"P{y}",
            description="D",
            tech="T",
            advisors="A",
            requirements="R",
        )
        db.session.add(s)
    db.session.commit()
    years = [s.year for s in SummerSchool.query.order_by(SummerSchool.year).all()]
    assert years == [2021, 2022, 2023]


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


def test_post_type_repr(app_ctx):
    from se_models import PostType, db

    pt = PostType(name="Event", type=3)
    db.session.add(pt)
    db.session.commit()
    assert repr(pt) == "Event"


def test_themes_level_repr(app_ctx):
    from se_models import ThemesLevel, db

    tl = ThemesLevel(level="Hard")
    db.session.add(tl)
    db.session.commit()
    assert repr(tl) == "Hard"


def test_diploma_themes_tags_repr_str(app_ctx):
    from se_models import DiplomaThemesTags, db

    dt = DiplomaThemesTags(name="AI")
    db.session.add(dt)
    db.session.commit()
    assert repr(dt) == "AI"
    assert str(dt) == "AI"


def test_company_repr(app_ctx):
    from se_models import Company, db

    c = Company(name="TechCorp")
    db.session.add(c)
    db.session.commit()
    assert repr(c) == "TechCorp"


def test_thesis_review_repr_str(app_ctx):
    from se_models import ThesisReview, db

    tr = ThesisReview(verdict=1)
    db.session.add(tr)
    db.session.commit()
    assert "Review" in repr(tr)
    assert "Review" in str(tr)


def test_reviewer_repr(app_ctx):
    from se_models import Reviewer, Users, db

    u = Users(first_name="Jane", last_name="Doe", email="jane@test.ru")
    db.session.add(u)
    db.session.flush()
    r = Reviewer(user_id=u.id)
    db.session.add(r)
    db.session.commit()
    assert repr(r) == "Doe Jane"


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


def test_promo_code_repr_str(app_ctx):
    from se_models import PromoCode, db

    pc = PromoCode(code="DISCOUNT2024")
    db.session.add(pc)
    db.session.commit()
    assert repr(pc) == "DISCOUNT2024"
    assert str(pc) == "DISCOUNT2024"


def test_notification_repr_str(app_ctx):
    from se_models import Notification, db

    n = Notification(recipient=1, title="Welcome", content="Hello!")
    db.session.add(n)
    db.session.commit()
    assert repr(n) == "Welcome"
    assert str(n) == "Welcome"


def test_notification_repr_str_no_title(app_ctx):
    from se_models import Notification, db

    n = Notification(recipient=1, content="No title")
    db.session.add(n)
    db.session.commit()
    assert repr(n) == ""
    assert str(n) == ""


def test_tags_create_and_query(app_ctx):
    from se_models import Tags, db

    t = Tags(name="machine-learning")
    db.session.add(t)
    db.session.commit()
    assert Tags.query.filter_by(name="machine-learning").first() is not None


def test_tags_delete(app_ctx):
    from se_models import Tags, db

    t = Tags(name="temporary-tag")
    db.session.add(t)
    db.session.commit()
    tid = t.id
    db.session.delete(t)
    db.session.commit()
    assert db.session.get(Tags, tid) is None


def test_diploma_themes_tags_create_and_query(app_ctx):
    from se_models import DiplomaThemesTags, db

    dt = DiplomaThemesTags(name="blockchain")
    db.session.add(dt)
    db.session.commit()
    assert DiplomaThemesTags.query.filter_by(name="blockchain").first() is not None


def test_diploma_themes_tags_delete(app_ctx):
    from se_models import DiplomaThemesTags, db

    dt = DiplomaThemesTags(name="temp-tag")
    db.session.add(dt)
    db.session.commit()
    did = dt.id
    db.session.delete(dt)
    db.session.commit()
    assert db.session.get(DiplomaThemesTags, did) is None


def test_init_db_creates_all_26_tables_in_one_call(app_ctx):
    from se_models import (
        AreasOfStudy,
        Courses,
        Curriculum,
        DiplomaThemes,
        InternshipFormat,
        InternshipTag,
        Posts,
        Staff,
        ThemesLevel,
        Users,
        Worktype,
        init_db,
    )

    from conftest import _assert_seeded_tables

    init_db()
    Curriculum = _assert_seeded_tables()
    assert Curriculum.query.count() > 0

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
    assert str(f) == "{self.format}"


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


def test_internships_self(app_ctx):
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
    assert i.__self__() == "Senior Dev"


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

# -*- coding: utf-8 -*-
import pytest

from se_models import (
    AreasOfStudy,
    Courses,
    Curriculum,
    DiplomaThemes,
    InternshipFormat,
    InternshipTag,
    Notification,
    Posts,
    Staff,
    ThemesLevel,
    Users,
    Worktype,
    init_db,
)


@pytest.fixture
def seeded(app_ctx):
    init_db()


MODEL_TESTS = [
    (AreasOfStudy,),
    (Users,),
    (Staff,),
    (Worktype,),
    (Courses,),
    (Posts,),
    (ThemesLevel,),
    (InternshipFormat,),
    (InternshipTag,),
    (DiplomaThemes,),
]


@pytest.mark.parametrize("model", [m[0] for m in MODEL_TESTS])
def test_init_db_creates_tables(seeded, model):
    assert model.query.count() > 0


def test_init_db_creates_first_user(seeded):
    user = Users.query.filter_by(email="a.terekhov@spbu.ru").first()
    assert user is not None
    assert user.last_name == "Терехов"


def test_init_db_creates_all_expected_tables(seeded):
    from conftest import _assert_seeded_tables

    _assert_seeded_tables()


def test_user_model_repr(seeded):
    user = Users.query.first()
    assert user is not None
    assert repr(user) is not None


def test_staff_model_repr(seeded):
    staff = Staff.query.first()
    assert staff is not None


def test_worktype_model_str(seeded):
    wt = Worktype.query.first()
    assert wt is not None
    assert str(wt) is not None


def test_model_relationships(seeded):
    user = Users.query.first()
    assert user is not None
    assert hasattr(user, "staff")
    assert hasattr(user, "thesises")
    assert hasattr(user, "current_thesises")


def test_notification_create_and_query(seeded):
    n = Notification(recipient=1, title="Test", content="Test body", type=0)
    from se_models import db

    db.session.add(n)
    db.session.commit()
    assert Notification.query.count() > 0


def test_init_db_idempotent(seeded):
    from se_models import db

    db.session.remove()
    init_db()


@pytest.mark.parametrize(
    "model,count",
    [
        (Users, 29),
        (Staff, 29),
        (Worktype, 10),
        (Courses, 7),
        (Curriculum, 199),
        (AreasOfStudy, 9),
        (ThemesLevel, 4),
        (DiplomaThemes, 3),
    ],
)
def test_init_db_seed_counts(seeded, model, count):
    assert model.query.count() == count

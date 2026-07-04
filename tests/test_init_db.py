import pytest
from se_models import (
    AreasOfStudy, Courses, DiplomaThemes, Posts,
    Staff, ThemesLevel, Users, Worktype, init_db,
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
]


@pytest.mark.parametrize("model", [m[0] for m in MODEL_TESTS])
def test_init_db_creates_tables(seeded, model):
    assert model.query.count() > 0


def test_init_db_creates_first_user(seeded):
    user = Users.query.filter_by(email="a.terekhov@spbu.ru").first()
    assert user is not None
    assert user.last_name == "Терехов"


def test_init_db_creates_diploma_themes(seeded):
    assert DiplomaThemes.query.count() > 0


def test_init_db_creates_all_expected_tables(seeded):
    assert AreasOfStudy.query.count() > 0
    assert Users.query.count() > 0
    assert Staff.query.count() > 0
    assert Worktype.query.count() > 0
    assert Courses.query.count() > 0
    assert Posts.query.count() > 0
    assert ThemesLevel.query.count() > 0
    assert DiplomaThemes.query.count() > 0

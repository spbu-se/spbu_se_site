def test_init_db_creates_areas(app_ctx):
    from se_models import AreasOfStudy, init_db

    init_db()
    areas = AreasOfStudy.query.all()
    assert len(areas) > 0


def test_init_db_creates_users(app_ctx):
    from se_models import Users, db
    from se_models import init_db
    init_db()
    users = Users.query.all()
    assert len(users) > 0


def test_init_db_creates_first_user(app_ctx):
    from se_models import Users, db
    from se_models import init_db
    init_db()
    user = Users.query.filter_by(email="a.terekhov@spbu.ru").first()
    assert user is not None
    assert user.last_name == "Терехов"


def test_init_db_creates_staff(app_ctx):
    from se_models import Staff, init_db

    init_db()
    staff = Staff.query.all()
    assert len(staff) > 0


def test_init_db_creates_worktypes(app_ctx):
    from se_models import Worktype, init_db

    init_db()
    worktypes = Worktype.query.all()
    assert len(worktypes) > 0


def test_init_db_creates_courses(app_ctx):
    from se_models import Courses, init_db

    init_db()
    courses = Courses.query.all()
    assert len(courses) > 0


def test_init_db_creates_posts(app_ctx):
    from se_models import Posts, init_db

    init_db()
    posts = Posts.query.all()
    assert len(posts) > 0


def test_init_db_creates_themes_levels(app_ctx):
    from se_models import ThemesLevel, init_db

    init_db()
    levels = ThemesLevel.query.all()
    assert len(levels) > 0


def test_init_db_creates_all_expected_tables(app_ctx):
    from se_models import AreasOfStudy, Users, Staff, Worktype, Courses, Posts, ThemesLevel, DiplomaThemes, InternshipFormat, Company, db
    from se_models import init_db
    init_db()
    assert AreasOfStudy.query.count() > 0
    assert Users.query.count() > 0
    assert Staff.query.count() > 0
    assert Worktype.query.count() > 0
    assert Courses.query.count() > 0
    assert Posts.query.count() > 0
    assert ThemesLevel.query.count() > 0
    assert DiplomaThemes.query.count() > 0

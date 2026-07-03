import pytest


def test_init_db_creates_areas(app_ctx):
    from se_models import AreasOfStudy, db
    from se_models import init_db
    init_db()
    areas = AreasOfStudy.query.all()
    assert len(areas) > 0


def test_init_db_creates_users(app_ctx):
    from se_models import Users, db
    from se_models import init_db
    init_db()
    users = Users.query.all()
    assert len(users) > 0


def test_init_db_creates_admin_user(app_ctx):
    from se_models import Users, db
    from se_models import init_db
    init_db()
    admin = Users.query.filter_by(role=3).first()
    assert admin is not None
    assert admin.login == "admin"


def test_init_db_creates_staff(app_ctx):
    from se_models import Staff, db
    from se_models import init_db
    init_db()
    staff = Staff.query.all()
    assert len(staff) > 0


def test_init_db_creates_worktypes(app_ctx):
    from se_models import Worktype, db
    from se_models import init_db
    init_db()
    worktypes = Worktype.query.all()
    assert len(worktypes) > 0


def test_init_db_creates_courses(app_ctx):
    from se_models import Courses, db
    from se_models import init_db
    init_db()
    courses = Courses.query.all()
    assert len(courses) > 0


def test_init_db_creates_posts(app_ctx):
    from se_models import Posts, db
    from se_models import init_db
    init_db()
    posts = Posts.query.all()
    assert len(posts) > 0


def test_init_db_creates_themes_levels(app_ctx):
    from se_models import ThemesLevel, db
    from se_models import init_db
    init_db()
    levels = ThemesLevel.query.all()
    assert len(levels) > 0


def test_init_db_idempotent(app_ctx):
    from se_models import Users, db
    from se_models import init_db
    init_db()
    first_count = Users.query.count()
    init_db()
    second_count = Users.query.count()
    assert first_count == second_count

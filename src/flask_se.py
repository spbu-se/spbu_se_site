# -*- coding: utf-8 -*-

from flask import Flask, render_template, make_response, redirect, url_for, Response
from flask_frozen import Freezer

import sys, os
from datetime import datetime

from sqlalchemy.sql.expression import func
from werkzeug.exceptions import HTTPException

from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_basicauth import BasicAuth
from flask_migrate import Migrate

from se_models import db, init_db, Staff, Users, Thesis, Worktype, Curriculum, SummerSchool, Courses
from wtforms import TextAreaField

import flask_theses
from flask_config import SECRET_KEY_THESIS

app = Flask(__name__, static_url_path='', static_folder='static', template_folder='templates')

# Flask configs
app.config['APPLICATION_ROOT'] = '/'

# Freezer config
app.config['FREEZER_RELATIVE_URLS'] = True
app.config['FREEZER_DESTINATION'] = '../docs'
app.config['FREEZER_IGNORE_MIMETYPE_WARNINGS'] = True

# SQLAlchimy config
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///se.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.urandom(16).hex()

# Secret for API
app.config['SECRET_KEY_THESIS'] = SECRET_KEY_THESIS

# Basci auth config
app.config['BASIC_AUTH_USERNAME'] = 'se_staff'
app.config['BASIC_AUTH_PASSWORD'] = app.config['SECRET_KEY_THESIS']

# App add_url_rule
app.add_url_rule('/theses.html', view_func=flask_theses.theses_search)
app.add_url_rule('/fetch_theses', view_func=flask_theses.fetch_theses)
app.add_url_rule('/post_theses', methods=['GET', 'POST'], view_func=flask_theses.post_theses)
app.add_url_rule('/theses_tmp.html', view_func=flask_theses.theses_tmp)
app.add_url_rule('/theses_delete_tmp', view_func=flask_theses.theses_delete_tmp)
app.add_url_rule('/theses_add_tmp', view_func=flask_theses.theses_add_tmp)


# Init Database
db.app = app
db.init_app(app)

# Init Migrate
migrate = Migrate(app, db)

app.logger.error('SECRET_KEY_THESIS: %s', str(app.config['SECRET_KEY_THESIS']))

# Init Freezer
freezer = Freezer(app)

# Init Sitemap
zero_days_ago = (datetime.now()).date().isoformat()

# Init BasicAuth
basic_auth = BasicAuth(app)


# Extend FlaskAdmin classes for BasicAuth (https://stackoverflow.com/questions/54834648/flask-basicauth-auth-required-decorator-for-flask-admin-views)
"""
The following three classes are inherited from their respective base class,
and are customized, to make flask_admin compatible with BasicAuth.
"""
class AuthException(HTTPException):

    def __init__(self, message):
        super().__init__(message, Response(
            "You could not be authenticated. Please refresh the page.", 401,
            {'WWW-Authenticate': 'Basic realm="Login Required"'} ))


class SeModelView(ModelView):
    def is_accessible(self):
        if not basic_auth.authenticate():
            raise AuthException('Not authenticated.')
        else:
            return True

    def inaccessible_callback(self, name, **kwargs):
        return redirect(basic_auth.challenge())


class UsersModelView(ModelView):

    column_exclude_list = ['password_hash']

    def is_accessible(self):
        if not basic_auth.authenticate():
            raise AuthException('Not authenticated.')
        else:
            return True

    def inaccessible_callback(self, name, **kwargs):
        return redirect(basic_auth.challenge())


class SummerSchoolView(ModelView):

    form_overrides = {
        'description': TextAreaField,
        'repo': TextAreaField,
        'demos': TextAreaField
    }

    form_widget_args = {
        'description': {
            'rows': 10,
            'style': 'font-family: monospace; width: 680px;'
        },
        'project_name': {
            'style': 'width: 680px;'
        },
        'tech': {
            'rows': 3,
            'style': 'font-family: monospace; width: 680px;'
        },
        'repo': {
            'rows': 3,
            'style': 'font-family: monospace; width: 680px;'
        },
        'demos': {
            'rows': 3,
            'style': 'font-family: monospace; width: 680px;'
        },
        'advisors': {
            'rows': 2,
            'style': 'font-family: monospace; width: 680px;'
        },
        'requirements': {
            'rows': 3,
            'style': 'font-family: monospace; width: 680px;'
        },
    }

    def is_accessible(self):
        if not basic_auth.authenticate():
            raise AuthException('Not authenticated.')
        else:
            return True

    def inaccessible_callback(self, name, **kwargs):
        return redirect(basic_auth.challenge())


class StaffModelView(ModelView):

    form_choices = {
        'science_degree': [
            ('', ''),
            ('д.ф.-м.н.', 'д.ф.-м.н.'),
            ('д.т.н.', 'д.т.н.'),
            ('к.ф.-м.н.', 'к.ф.-м.н.'),
            ('к.т.н.', 'к.т.н.')
        ]
    }

    column_exclude_list = ['supervisor', 'adviser']
    form_excluded_columns = ['supervisor', 'adviser']

    def is_accessible(self):
        if not basic_auth.authenticate():
            raise AuthException('Not authenticated.')
        else:
            return True

    def inaccessible_callback(self, name, **kwargs):
        return redirect(basic_auth.challenge())


class SeAdminIndexView(AdminIndexView):
    def is_accessible(self):
        if not basic_auth.authenticate():
            raise AuthException('Not authenticated.')
        else:
            return True

    def inaccessible_callback(self, name, **kwargs):
        return redirect(basic_auth.challenge())


# Init Flask-admin
admin = Admin(app, index_view=SeAdminIndexView())


# Flask routes goes
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/index.html')
def indexhtml():
    return redirect(url_for('index'))


@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html'), 404


@app.route('/404.html')
def status_404():
    return render_template('404.html')


@app.route('/contacts.html')
def contacts():
    return render_template('contacts.html')


@app.route('/students/index.html')
def students():
    return render_template('students.html')


@app.route('/students/scholarships.html')
def scholarships():
    return render_template('students_scholarships.html')


@app.route('/bachelor/application.html')
def bachelor_application():
    return render_template('bachelor_application.html')


@app.route('/bachelor/programming-technology.html')
def bachelor_programming_technology():

    curricula1 = Curriculum.query.filter(Curriculum.course_id==1).filter(Curriculum.study_year==1).order_by(Curriculum.type).all()
    curricula2 = Curriculum.query.filter(Curriculum.course_id==1).filter(Curriculum.study_year==2).order_by(Curriculum.type).all()
    curricula3 = Curriculum.query.filter(Curriculum.course_id==1).filter(Curriculum.study_year == 3).order_by(Curriculum.type).all()
    curricula4 = Curriculum.query.filter(Curriculum.course_id==1).filter(Curriculum.study_year == 4).order_by(Curriculum.type).all()

    return render_template('bachelor_programming-technology.html', curricula1=curricula1, curricula2=curricula2,
                           curricula3=curricula3, curricula4=curricula4)


@app.route('/bachelor/software-engineering.html')
def bachelor_software_engineering():

    curricula1 = Curriculum.query.filter(Curriculum.course_id==2).filter(Curriculum.study_year==1).order_by(Curriculum.type).all()
    curricula2 = Curriculum.query.filter(Curriculum.course_id==2).filter(Curriculum.study_year==2).order_by(Curriculum.type).all()
    curricula3 = Curriculum.query.filter(Curriculum.course_id==2).filter(Curriculum.study_year == 3).order_by(Curriculum.type).all()
    curricula4 = Curriculum.query.filter(Curriculum.course_id==2).filter(Curriculum.study_year == 4).order_by(Curriculum.type).all()

    return render_template('bachelor_software-engineering.html', curricula1=curricula1, curricula2=curricula2,
                           curricula3=curricula3, curricula4=curricula4)


@app.route('/master/information-systems-administration.html')
def master_information_systems_administration():
    return render_template('master_information-systems-administration.html')


@app.route('/master/software-engineering.html')
def master_software_engineering():
    return render_template('master_software-engineering.html')


@app.route('/department/staff.html')
def department_staff():
    records = Staff.query.filter_by(still_working=True).all()
    staff = []

    # TODO: no need loop
    for s in records:
        position = s.position
        if s.science_degree:
            position = position + ", " + s.science_degree

        staff.append({'name': s.user, 'position': position, 'contacts': s.official_email,
                      'avatar': s.user.avatar_uri, 'id': s.id})

    return render_template('department_staff.html', staff = staff)


@app.route('/bachelor/admission.html')
def bachelor_admission():

    students = []

    records = Thesis.query.filter_by(recomended=True)
    if records.count():
        theses = records.order_by(func.random()).limit(4).all()
    else:
        theses = []
    staff = Staff.query.filter_by(still_working=True).limit(6).all()
    return render_template('bachelor_admission.html', students = students, theses=theses, staff=staff)


@app.route('/frequently-asked-questions.html')
def frequently_asked_questions():
    return render_template('frequently_asked_questions.html')


@app.route('/nooffer.html')
def nooffer():
    return render_template('nooffer.html')


@app.route('/summer_school_2021.html')
def summer_school():

    projects = SummerSchool.query.filter_by(year=2021).all()
    return render_template('summer_school.html', projects=projects)


@app.route('/sitemap.xml', methods=['GET'])
@app.route('/Sitemap.xml', methods=['GET'])
def sitemap():

    """Generate sitemap.xml. Makes a list of urls and date modified."""
    pages = []
    skip_pages = ['/nooffer.html', '/fetch_theses', '/Sitemap.xml', '/sitemap.xml', '/404.html', '/post_theses',
                  '/theses_tmp.html', '/theses_delete_tmp', '/theses_add_tmp']

    # static pages
    for rule in app.url_map.iter_rules():

        if rule.rule in skip_pages:
            continue

        if "GET" in rule.methods and len(rule.arguments) == 0:
            pages.append(
                ["https://se.math.spbu.ru" + str(rule.rule), zero_days_ago]
            )

    sitemap_xml = render_template('sitemap_template.xml', pages=pages)
    response = make_response(sitemap_xml)
    response.headers["Content-Type"] = "application/xml"
    return response


# Add views to the Flask-admin
admin.add_view(UsersModelView(Users, db.session))
admin.add_view(StaffModelView(Staff, db.session))
admin.add_view(SeModelView(Thesis, db.session))
admin.add_view(SummerSchoolView(SummerSchool, db.session))

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "build":
            freezer.freeze()
        elif sys.argv[1] == "init":
            init_db()
    else:
        app.run(port=5000)

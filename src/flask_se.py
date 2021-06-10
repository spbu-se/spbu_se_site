# -*- coding: utf-8 -*-

from flask import Flask, request, render_template, make_response, redirect, url_for
from flask_frozen import Freezer
from datetime import datetime
from se_forms import ThesisFilter
import sys, os
from se_models import db, init_db, Staff, Users, Thesis, Worktype, Curriculum
from  sqlalchemy.sql.expression import func

app = Flask(__name__, static_url_path='', static_folder='static', template_folder='templates')

# Flask configs
app.config['APPLICATION_ROOT'] = '/'
app.config['FREEZER_RELATIVE_URLS'] = True
app.config['FREEZER_DESTINATION'] = '../docs'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///se.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.urandom(16).hex()
app.config['FREEZER_IGNORE_MIMETYPE_WARNINGS'] = True

# Init Database
db.app = app
db.init_app(app)

# Init Freezer
freezer = Freezer(app)

# Init Sitemap
zero_days_ago = (datetime.now()).date().isoformat()

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

@app.route('/theses.html')
def theses_search():

    filter = ThesisFilter()
    filter.worktype.choices = [(worktype.id, worktype.type) for worktype in Worktype.query.all()]

    dates = [theses.publish_year for theses in Thesis.query.with_entities(Thesis.publish_year).distinct()]
    dates.sort(reverse=True)
    filter.startdate.choices = dates
    filter.enddate.choices = dates

    for sid in Thesis.query.with_entities(Thesis.supervisor_id).distinct().all():
        staff = Staff.query.filter_by(id=sid[0]).first()
        last_name = ""
        initials = ""

        if staff.user.last_name:
            last_name = staff.user.last_name

        if staff.user.first_name:
            initials = initials + staff.user.first_name[0] + "."

        if staff.user.middle_name:
            initials = initials + staff.user.middle_name[0] + "."

        filter.supervisor.choices.append((sid[0], last_name + " " + initials))
        filter.supervisor.choices.sort(key=lambda tup: tup[1])

    filter.supervisor.choices.insert(0, (0, "Все"))

    return render_template('theses.html', filter=filter)

@app.route('/fetch_theses')
def fetch_theses():

    worktype = request.args.get('worktype', default = 1, type = int)
    page = request.args.get('page', default=1, type=int)
    supervisor = request.args.get('supervisor', default=0, type=int)

    dates = [theses.publish_year for theses in Thesis.query.with_entities(Thesis.publish_year).distinct()]
    dates.sort(reverse=True)

    if dates:
        startdate = request.args.get('startdate', default=dates[-1], type=int)
        enddate = request.args.get('enddate', default=dates[0], type=int)
    else:
        startdate = 2020
        enddate = 2020

    # Check if end date less than start date
    if enddate < startdate:
        enddate = startdate

    records = Thesis.query.filter(Thesis.publish_year >= startdate).filter(Thesis.publish_year <= enddate)

    if supervisor:

        # Check if supervisor exists
        ids = Thesis.query.with_entities(Thesis.supervisor_id).distinct().all()
        if [item for item in ids if item[0] == supervisor]:
            records = records.filter(Thesis.supervisor_id == supervisor)
        else:
            supervisor = 0

    if worktype > 1:
        records = records.filter_by(type_id=worktype).paginate(per_page=10, page=page, error_out=False)
    else:
        records = records.paginate(per_page=10, page=page, error_out=False)

    if len(records.items):
        return render_template('fetch_theses.html', theses=records, worktype=worktype, startdate=startdate,
                               enddate=enddate, supervisor=supervisor)
    else:
        return render_template('fetch_theses_blank.html')


@app.route('/sitemap.xml', methods=['GET'])
@app.route('/Sitemap.xml', methods=['GET'])
def sitemap():

    """Generate sitemap.xml. Makes a list of urls and date modified."""
    pages = []
    skip_pages = ['/nooffer.html', '/fetch_theses', '/Sitemap.xml', '/sitemap.xml', '/404.html']

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

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "build":
            freezer.freeze()
        elif sys.argv[1] == "init":
            init_db()
    else:
        app.run(port=5000)

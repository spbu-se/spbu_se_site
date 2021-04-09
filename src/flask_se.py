# -*- coding: utf-8 -*-

from flask import Flask, request
from flask import render_template
from flask_frozen import Freezer
from flask import redirect, url_for
from se_forms import ThesisFilter
import sys, os
from se_models import db, init_db, Staff, Users, Thesis, Worktype

app = Flask(__name__, static_url_path='', static_folder='static', template_folder='templates')

# Flask configs
app.config['APPLICATION_ROOT'] = '/'
app.config['FREEZER_RELATIVE_URLS'] = True
app.config['FREEZER_DESTINATION'] = '../docs'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///se.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.urandom(16).hex()

# Init Database
db.app = app
db.init_app(app)

# Init Freezer
freezer = Freezer(app)

# Flask routes goes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/index.html')
def indexhtml():
    return redirect(url_for('index'))

@app.route('/404.html')
def status_404():
    return render_template('404.html')

@app.route('/contacts.html')
def contacts():
    return render_template('contacts.html')

@app.route('/students.html')
def students():
    return render_template('students.html')

@app.route('/bachelor/application.html')
def bachelor_application():
    return render_template('bachelor_application.html')

@app.route('/bachelor/programming-technology.html')
def bachelor_programming_technology():
    return render_template('bachelor_programming-technology.html')

@app.route('/bachelor/software-engineering.html')
def bachelor_software_engineering():
    return render_template('bachelor_software-engineering.html')

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

    for s in records:
        position = s.position
        if s.science_degree:
            position = position + ", " + s.science_degree

        staff.append({'name' : s.user, 'position' : position, 'contacts' : s.official_email, 'avatar' : s.user.avatar_uri})

    return render_template('department_staff.html', staff = staff)

@app.route('/bachelor/admission.html')
def bachelor_admission():
    students = [
        {"name": "Терехов Андрей Николаевич", "position": "Студент 2-го курса, Программная инженерия",
         "review": "Очень крутое место", 'avatar': 'terekhov.jpg'},
        {"name": "Граничин Олег Николаевич", "position": "Студент 4-го курса, Технологии программирования",
         'avatar': 'granichin.jpg', "review" : "На третьем курсе я уже начал заниматься наукой в лаборатории"},
        {"name": "Кознов Дмитрий Владимирович", "position": "Студент 3-го курса, Программная инженерия",
         'avatar': 'koznov.jpg', "review" : "Прохожу стажировку в Яндексе, отличные общежития. Все путем!"},
        {"name": "Брыксин Тимофей Александрович", "position": "Студент 4-го курса, Программная инженерия",
         'avatar': 'bryksin.jpg', 'review':'Все очень круто, если будут вопросы по поступлению, пишите мне'},
        {"name": "Булычев Дмитрий Юрьевич", "position": "Студент 2-го курса, Программная инженерия",
         'avatar': 'boulytchev.jpg', 'review':'Все очень круто, если будут вопросы по поступлению, пишите мне'},
        {"name": "Литвинов Юрий Викторович", "position": "Студент 2-го курса, Программная инженерия",
         'avatar': 'litvinov.jpg', 'review':'Все очень круто, если будут вопросы по поступлению, пишите мне'},
    ]
    diplomas = [
        {"author": "Гогина Олеся Юрьевна", "title": "Анализ данных Snapchat на iOS"},
        {"author": "Гуданова Варвара Сергеевна", "title": "Система распознавания меток игроков в робофутболе"},
        {"author": "Камкова Екатерина Александровна", "title": "Симулятор Робофутбола"},
        {"author": "Курбатова Зарина Идиевна", "title": "Автоматическая рекомендация имен методов в IntelliJ IDEA"},
        {"author": "Поляков Александр Романович", "title": "Разработка системы для отладки ядра операционной системы"},
    ]

    records = Staff.query.filter_by(still_working=True).limit(6).all()
    staff = []

    for s in records:
        position = s.position
        if s.science_degree:
            position = position + ", " + s.science_degree

        staff.append({'name' : s.user, 'position' : position, 'contacts' : s.official_email, 'avatar' : s.user.avatar_uri})


    return render_template('bachelor_admission.html', students = students, diplomas=diplomas, staff=staff)

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

    records = Thesis.query.all()
    return render_template('theses.html', theses=records, filter=filter)

@app.route('/fetch_theses')
def fetch_theses():

    worktype = request.args.get('worktype', default = 1, type = int)
    if worktype > 1:
        records = Thesis.query.filter_by(type_id=worktype).all()
    else:
        records = Thesis.query.all()

    return render_template('fetch_theses.html', theses=records)

@app.route('/theses2.html')
def theses_search2():

    records = Thesis.query.all()
    return render_template('theses2.html', theses=records)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "build":
            freezer.freeze()
        elif sys.argv[1] == "init":
            init_db()
    else:
        app.run(port=5000)

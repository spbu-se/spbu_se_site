# -*- coding: utf-8 -*-

from flask import Flask
from flask import render_template
from flask_frozen import Freezer
import sys, os

app = Flask(__name__, static_url_path='', static_folder='static', template_folder='templates')
app.config['APPLICATION_ROOT'] = '/'
app.config['FREEZER_RELATIVE_URLS'] = True
app.config['FREEZER_DESTINATION'] = '../docs'

freezer = Freezer(app)

URL_PREFIX = "/"

@app.route(URL_PREFIX + '/')
def index():
    return render_template('index.html')

@app.route(URL_PREFIX + '/index.html')
def indexhtml():
    return render_template('index.html')

@app.route(URL_PREFIX + '/404.html')
def status_404():
    return render_template('404.html')

@app.route(URL_PREFIX + '/contacts.html')
def contacts():
    return render_template('contacts.html')

@app.route(URL_PREFIX + '/students.html')
def students():
    return render_template('students.html')

@app.route(URL_PREFIX + '/bachelor/application.html')
def bachelor_application():
    return render_template('bachelor_application.html')

@app.route(URL_PREFIX + '/bachelor/programming-technology.html')
def bachelor_programming_technology():
    return render_template('bachelor_programming-technology.html')

@app.route(URL_PREFIX + '/bachelor/software-engineering.html')
def bachelor_software_engineering():
    return render_template('bachelor_software-engineering.html')

@app.route(URL_PREFIX + '/master/information-systems-administration.html')
def master_information_systems_administration():
    return render_template('master_information-systems-administration.html')

@app.route(URL_PREFIX + '/master/software-engineering.html')
def master_software_engineering():
    return render_template('master_software-engineering.html')

@app.route(URL_PREFIX + '/department/staff.html')
def department_staff():
    staff = [
        {"name": "Терехов Андрей Николаевич", "position": "Профессор, д.ф.-м.н., заведующий кафедрой",
         "contacts": "a.terekhov@spbu.ru", "contacts2": "st003585@spbu.ru", "contacts3": "a.terekhov@spbu.ru",
         'avatar': 'terekhov.jpg'},
        {"name": "Граничин Олег Николаевич", "position": "Профессор, д.ф.-м.н.", "contacts": "o.granichin@spbu.ru",
         "contacts2": "st007805@sbpu.ru", "contacts3": "o.granichin@spbu.ru", 'avatar': 'granichin.jpg'},
        {"name": "Кознов Дмитрий Владимирович", "position": "Профессор, д.т.н.", "contacts": "dkoznov@yandex.ru",
         "contacts2": "st008149@spbu.ru", "contacts3": "d.koznov@spbu.ru", 'avatar': 'koznov.jpg'},
        {"name": "Брыксин Тимофей Александрович", "position": "Доцент, к.т.н.", "contacts": "timofey.bryksin@gmail.com",
         "contacts2": "st006935@sbpu.ru", "contacts3": "t.bryksin@spbu.ru", 'avatar': 'bryksin.jpg'},
        {"name": "Булычев Дмитрий Юрьевич", "position": "Доцент, к. ф.-м. н.", "contacts": "dboulytchev@gmail.com",
         "contacts2": "st007252@sbpu.ru", "contacts3": "d.bylychev@spbu.ru", 'avatar': 'boulytchev.jpg'},
        {"name": "Литвинов Юрий Викторович", "position": "Доцент, к.т.н.", "contacts": "yurii.litvinov@gmail.com",
         "contacts2": "st007017@spbu.ru", "contacts3": "y.litvinov@spbu.ru", 'avatar': 'litvinov.jpg'},
        {"name": "Луцив Дмитрий Вадимович", "position": "Доцент, к. ф.-м. н.", "contacts": "dluciv@gmail.com",
         "contacts2": "st007027@spbu.ru", "contacts3": "d.lutsiv@spbu.ru", 'avatar': 'luciv.jpg'},
        {"name": "Романовский Константин Юрьевич", "position": "Доцент, к. ф.-м. н.",
         "contacts": "kromanovsky@gmail.com", "contacts2": "st007081@spbu.ru", "contacts3": "k.romanovsky@spbu.ru",
         'avatar': 'empty.jpg'},
        {"name": "Серов Михаил Александрович", "position": "Доцент", "contacts": "m.serov@spbu.ru",
         "contacts2": "st806019@spbu.ru", "contacts3": "m.serov@spbu.ru", 'avatar': 'empty.jpg'},
        {"name": "Сысоев Сергей Сергеевич", "position": "Преподаватель-практик, к. ф.-м. н.", "contacts": "sysoev@petroms.ru",
         "contacts2": "st007983@spbu.ru", "contacts3": "s.s.sysoev@spbu.ru", 'avatar': 'empty.jpg'},
        {"name": "Баклановский Максим Викторович", "position": "Старший преподаватель",
         "contacts": "baklanovsky@gmail.com", "contacts2": "st007253@sbpu.ru", "contacts3": "m.baklanovsky@spbu.ru",
         'avatar': 'baklanovsky.jpg'},
        {"name": "Журавлев Максим Михайлович", "position": "Старший преподаватель", "contacts": "vecktor.vek@gmail.com",
         "contacts2": "st900398@sbpu.ru", "contacts3": "m.m.zhuravlev@spbu.ru", 'avatar': 'zhuravlev.jpg'},
        {"name": "Зеленчук Илья Валерьевич", "position": "Старший преподаватель", "contacts": "ilya@hackerdom.ru",
         "contacts2": "st007330@spbu.ru", "contacts3": "i.zelenchuk@spbu.ru", 'avatar': 'zelenchuk.jpg'},
        {"name": "Кириленко Яков Александрович", "position": "Старший преподаватель",
         "contacts": "jake.kirilenko@gmail.com", "contacts2": "st007829@spbu.ru", "contacts3": "y.kirilenko@spbu.ru",
         'avatar': 'kirilenko.jpg'},
        {"name": "Козлов Антон Павлович", "position": "Старший преподаватель", "contacts": "drakon.mega@gmail.com",
         "contacts2": "st035425@spbu.ru", "contacts3": "st035425@student.spbu.ru", 'avatar': 'empty.jpg'},
        {"name": "Куликов Егор Константинович", "position": "Старший преподаватель",
         "contacts": "egor.k.kulikov@gmail.com", "contacts2": "st010758@spbu.ru",
         "contacts3": "egor.k.kulikov@gmail.com", 'avatar': 'kulikov.jpg'},
        {"name": "Мордвинов Дмитрий Александрович", "position": "Старший преподаватель",
         "contacts": "mordvinov.dmitry@gmail.com", "contacts2": "st035475@spbu.ru", "contacts3": "d.mordvinov@spbu.ru",
         'avatar': 'empty.jpg'},
        {"name": "Немешев Марат Халимович", "position": "Старший преподаватель", "contacts": "m.nemeshev@spbu.ru",
         "contacts2": "st003602@spbu.ru", "contacts3": "m.nemeshev@spbu.ru", 'avatar': 'empty.jpg'},
        {"name": "Сартасов Станислав Юрьевич", "position": "Старший преподаватель",
         "contacts": "stanislav.sartasov@gmail.com", "contacts2": "st900710@spbu.ru",
         "contacts3": "stanislav.sartasov@spbu.ru", 'avatar': 'empty.jpg'},
        {"name": "Смирнов Михаил Николаевич", "position": "Старший преподаватель, к.т.н.",
         "contacts": "mikhail.smirnov@lanit-tercom.com", "contacts2": "st008005@spbu.ru",
         "contacts3": "m.n.smirnov@spbu.ru", 'avatar': 'smirnov.jpg'},
        {"name": "Ханов Артур Рафаэльевич", "position": "Старший преподаватель", "contacts": "awengar@gmail.com",
         "contacts2": "st036451@spbu.ru", "contacts3": "st036451@student.spbu.ru", 'avatar': 'empty.jpg'},
        {"name": "Шилов Сергей Юрьевич", "position": "Старший преподаватель", "contacts": "serguei.shilov@gmail.com",
         "contacts2": "st007124@spbu.ru", "contacts3": "s.shilov@spbu.ru", 'avatar': 'empty.jpg'},
        {"name": "Лозов Петр Алексеевич", "position": "Инженер-исследователь", "contacts": "",
         "contacts2": "st013464@spbu.ru", "contacts3": "st013464@student.spbu.ru", 'avatar': 'empty.jpg'},
        {"name": "Моисеенко Евгений Александрович", "position": "Инженер-исследователь", "contacts": "",
         "contacts2": "st013039@spbu.ru", "contacts3": "st013039@student.spbu.ru", 'avatar': 'empty.jpg'},
    ]
    return render_template('department_staff.html', staff = staff)

@app.route(URL_PREFIX + '/bachelor/admission.html')
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
    staff = [
        {"name": "Терехов Андрей Николаевич", "position": "Профессор, д.ф.-м.н., заведующий кафедрой",
         "contacts": "a.terekhov@spbu.ru", "contacts2": "st003585@spbu.ru", "contacts3": "a.terekhov@spbu.ru",
         'avatar': 'terekhov.jpg'},
        {"name": "Граничин Олег Николаевич", "position": "Профессор, д.ф.-м.н.", "contacts": "o.granichin@spbu.ru",
         "contacts2": "st007805@sbpu.ru", "contacts3": "o.granichin@spbu.ru", 'avatar': 'granichin.jpg'},
        {"name": "Кознов Дмитрий Владимирович", "position": "Профессор, д.т.н.", "contacts": "dkoznov@yandex.ru",
         "contacts2": "st008149@spbu.ru", "contacts3": "d.koznov@spbu.ru", 'avatar': 'koznov.jpg'},
        {"name": "Брыксин Тимофей Александрович", "position": "Доцент, к.т.н.", "contacts": "timofey.bryksin@gmail.com",
         "contacts2": "st006935@sbpu.ru", "contacts3": "t.bryksin@spbu.ru", 'avatar': 'bryksin.jpg'},
        {"name": "Булычев Дмитрий Юрьевич", "position": "Доцент, к. ф.-м. н.", "contacts": "dboulytchev@gmail.com",
         "contacts2": "st007252@sbpu.ru", "contacts3": "d.bylychev@spbu.ru", 'avatar': 'boulytchev.jpg'},
        {"name": "Литвинов Юрий Викторович", "position": "Доцент, к.т.н.", "contacts": "yurii.litvinov@gmail.com",
         "contacts2": "st007017@spbu.ru", "contacts3": "y.litvinov@spbu.ru", 'avatar': 'litvinov.jpg'},
    ]
    return render_template('bachelor_admission.html', students = students, diplomas=diplomas, staff=staff)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "build":
        freezer.freeze()
    else:
        app.run(port=5000)
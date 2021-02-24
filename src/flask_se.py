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
        {"name": "Терехов Андрей Николаевич", "position": "Профессор, к. ф.-м. н., заведующий кафедрой",
         "contacts": "a.terekhov@spbu.ru", 'avatar': 'terekhov.jpg'},
        {"name": "Граничин Олег Николаевич", "position": "Профессор, к. ф.-м. н.", "contacts": "o.granichin@spbu.ru",
         'avatar': 'granichin.jpg'},
        {"name": "Кознов Дмитрий Владимирович", "position": "Профессор, д.т.н.", "contacts": "dkoznov@yandex.ru",
         'avatar': 'koznov.jpg'},
        {"name": "Брыксин Тимофей Александрович", "position": "Доцент, к.т.н.", "contacts": "timofey.bryksin@gmail.com",
         'avatar': 'bryksin.jpg'},
        {"name": "Булычев Дмитрий Юрьевич", "position": "Доцент, к. ф.-м. н.", "contacts": "dboulytchev@gmail.com",
         'avatar': 'boulytchev.jpg'},
        {"name": "Литвинов Юрий Викторович", "position": "Доцент, к.т.н.", "contacts": "yurii.litvinov@gmail.com",
         'avatar': 'litvinov.jpg'},
        {"name": "Луцив Дмитрий Вадимович", "position": "Доцент, к. ф.-м. н.", "contacts": "dluciv@gmail.com",
         'avatar': 'luciv.jpg'},
        {"name": "Романовский Константин Юрьевич", "position": "Доцент, к. ф.-м. н.",
         "contacts": "kromanovsky@gmail.com",
         'avatar': 'empty.jpg'},
        {"name": "Серов Михаил Александрович", "position": "Доцент", "contacts": "m.serov@spbu.ru",
         'avatar': 'empty.jpg'},
        {"name": "Сысоев Сергей Сергеевич", "position": "Доцент, к. ф.-м. н.", "contacts": "sysoev@petroms.ru",
         'avatar': 'empty.jpg'},
        {"name": "Баклановский Максим Викторович", "position": "Старший преподаватель",
         "contacts": "baklanovsky@gmail.com", 'avatar': 'baklanovsky.jpg'},
        {"name": "Журавлев Максим Михайлович", "position": "Старший преподаватель", "contacts": "vecktor.vek@gmail.com",
         'avatar': 'zhuravlev.jpg'},
        {"name": "Зеленчук Илья Валерьевич", "position": "Старший преподаватель", "contacts": "ilya@hackerdom.ru",
         'avatar': 'zelenchuk.jpg'},
        {"name": "Кириленко Яков Александрович", "position": "Старший преподаватель",
         "contacts": "jake.kirilenko@gmail.com", 'avatar': 'kirilenko.jpg'},
        {"name": "Козлов Антон Павлович", "position": "Старший преподаватель", "contacts": "drakon.mega@gmail.com",
         'avatar': 'empty.jpg'},
        {"name": "Куликов Егор Константинович", "position": "Старший преподаватель",
         "contacts": "egor.k.kulikov@gmail.com", 'avatar': 'empty.jpg'},
        {"name": "Мордвинов Дмитрий Александрович", "position": "Старший преподаватель",
         "contacts": "mordvinov.dmitry@gmail.com", 'avatar': 'empty.jpg'},
        {"name": "Немешев Марат Халимович", "position": "Старший преподаватель", "contacts": "m.nemeshev@spbu.ru",
         'avatar': 'empty.jpg'},
        {"name": "Сартасов Станислав Юрьевич", "position": "Старший преподаватель",
         "contacts": "stanislav.sartasov@gmail.com", 'avatar': 'empty.jpg'},
        {"name": "Смирнов Михаил Николаевич", "position": "Старший преподаватель, к.т.н.",
         "contacts": "mikhail.smirnov@lanit-tercom.com", 'avatar': 'smirnov.jpg'},
        {"name": "Ханов Артур Рафаэльевич", "position": "Старший преподаватель", "contacts": "awengar@gmail.com",
         'avatar': 'empty.jpg'},
        {"name": "Шилов Сергей Юрьевич", "position": "Старший преподаватель", "contacts": "serguei.shilov@gmail.com",
         'avatar': 'empty.jpg'},
        {"name": "Лозов Петр Алексеевич", "position": "Инженер-исследователь", "contacts": "", 'avatar': 'empty.jpg'},
        {"name": "Моисеенко Евгений Александрович", "position": "Инженер-исследователь", "contacts": "",
         'avatar': 'empty.jpg'},
    ]
    return render_template('department_staff.html', staff = staff)

@app.route(URL_PREFIX + '/department/staff2.html')
def department_staff2():
    staff = [
        {"name": "Терехов Андрей Николаевич", "position": "Профессор, к. ф.-м. н., заведующий кафедрой",
         "contacts": "a.terekhov@spbu.ru", 'avatar': 'terekhov.jpg'},
        {"name": "Граничин Олег Николаевич", "position": "Профессор, к. ф.-м. н.", "contacts": "o.granichin@spbu.ru",
         'avatar': 'granichin.jpg'},
        {"name": "Кознов Дмитрий Владимирович", "position": "Профессор, д.т.н.", "contacts": "dkoznov@yandex.ru",
         'avatar': 'koznov.jpg'},
        {"name": "Брыксин Тимофей Александрович", "position": "Доцент, к.т.н.", "contacts": "timofey.bryksin@gmail.com",
         'avatar': 'bryksin.jpg'},
        {"name": "Булычев Дмитрий Юрьевич", "position": "Доцент, к. ф.-м. н.", "contacts": "dboulytchev@gmail.com",
         'avatar': 'boulytchev.jpg'},
        {"name": "Литвинов Юрий Викторович", "position": "Доцент, к.т.н.", "contacts": "yurii.litvinov@gmail.com",
         'avatar': 'litvinov.jpg'},
        {"name": "Луцив Дмитрий Вадимович", "position": "Доцент, к. ф.-м. н.", "contacts": "dluciv@gmail.com",
         'avatar': 'luciv.jpg'},
        {"name": "Романовский Константин Юрьевич", "position": "Доцент, к. ф.-м. н.",
         "contacts": "kromanovsky@gmail.com",
         'avatar': 'empty.jpg'},
        {"name": "Серов Михаил Александрович", "position": "Доцент", "contacts": "m.serov@spbu.ru",
         'avatar': 'empty.jpg'},
        {"name": "Сысоев Сергей Сергеевич", "position": "Доцент, к. ф.-м. н.", "contacts": "sysoev@petroms.ru",
         'avatar': 'empty.jpg'},
        {"name": "Баклановский Максим Викторович", "position": "Старший преподаватель",
         "contacts": "baklanovsky@gmail.com", 'avatar': 'baklanovsky.jpg'},
        {"name": "Журавлев Максим Михайлович", "position": "Старший преподаватель", "contacts": "vecktor.vek@gmail.com",
         'avatar': 'zhuravlev.jpg'},
        {"name": "Зеленчук Илья Валерьевич", "position": "Старший преподаватель", "contacts": "ilya@hackerdom.ru",
         'avatar': 'zelenchuk.jpg'},
        {"name": "Кириленко Яков Александрович", "position": "Старший преподаватель",
         "contacts": "jake.kirilenko@gmail.com", 'avatar': 'kirilenko.jpg'},
        {"name": "Козлов Антон Павлович", "position": "Старший преподаватель", "contacts": "drakon.mega@gmail.com",
         'avatar': 'empty.jpg'},
        {"name": "Куликов Егор Константинович", "position": "Старший преподаватель",
         "contacts": "egor.k.kulikov@gmail.com", 'avatar': 'empty.jpg'},
        {"name": "Мордвинов Дмитрий Александрович", "position": "Старший преподаватель",
         "contacts": "mordvinov.dmitry@gmail.com", 'avatar': 'empty.jpg'},
        {"name": "Немешев Марат Халимович", "position": "Старший преподаватель", "contacts": "m.nemeshev@spbu.ru",
         'avatar': 'empty.jpg'},
        {"name": "Сартасов Станислав Юрьевич", "position": "Старший преподаватель",
         "contacts": "stanislav.sartasov@gmail.com", 'avatar': 'empty.jpg'},
        {"name": "Смирнов Михаил Николаевич", "position": "Старший преподаватель, к.т.н.",
         "contacts": "mikhail.smirnov@lanit-tercom.com", 'avatar': 'smirnov.jpg'},
        {"name": "Ханов Артур Рафаэльевич", "position": "Старший преподаватель", "contacts": "awengar@gmail.com",
         'avatar': 'empty.jpg'},
        {"name": "Шилов Сергей Юрьевич", "position": "Старший преподаватель", "contacts": "serguei.shilov@gmail.com",
         'avatar': 'empty.jpg'},
        {"name": "Лозов Петр Алексеевич", "position": "Инженер-исследователь", "contacts": "", 'avatar': 'empty.jpg'},
        {"name": "Моисеенко Евгений Александрович", "position": "Инженер-исследователь", "contacts": "",
         'avatar': 'empty.jpg'},
    ]
    return render_template('department_staff2.html', staff = staff)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "build":
        freezer.freeze()
    else:
        app.run(port=5000)
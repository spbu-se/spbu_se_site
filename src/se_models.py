from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from os import urandom

db = SQLAlchemy()

class Staff (db.Model):
    id = db.Column(db.Integer, primary_key=True)

    users_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    users = db.relationship("Users", backref=db.backref("users", uselist=False))

    official_email = db.Column(db.String(255), unique=True, nullable=False)
    position = db.Column(db.String(255), nullable=False)
    science_degree = db.Column(db.String(255), nullable=True)
    still_working = db.Column(db.Boolean, default=False, nullable=False)

    def __repr__(self):
        return '<Staff %r>' % self.official_email

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    email = db.Column(db.String(255), unique=True, nullable=True)
    password_hash = db.Column(db.String(255), unique=False, nullable=True)

    first_name = db.Column(db.String(255), nullable=False)
    middle_name = db.Column(db.String(255), nullable=True)
    last_name = db.Column(db.String(255), nullable=True)

    avatar_uri = db.Column(db.String(512), default='empty.jpg', nullable=False)

    vk_id = db.Column(db.String(255), nullable=True)
    fb_id = db.Column(db.String(255), nullable=True)
    google_id = db.Column(db.String(255), nullable=True)

    def __str__(self):
        return f"{self.last_name} {self.first_name} {self.middle_name}"

    def __repr__(self):
        return '<Users %r %r %r>' % (self.last_name, self.first_name, self.middle_name)

def init_db():

    # Data
    users = [
        {'email' : 'a.terekhov@spbu.ru', 'first_name' : 'Андрей', 'last_name' : 'Терехов', 'middle_name' : 'Николаевич',
         'avatar_uri' : 'terekhov.jpg'},
        {'email': 'o.granichin@spbu.ru', 'first_name': 'Олег', 'last_name': 'Граничин', 'middle_name': 'Николаевич',
         'avatar_uri': 'granichin.jpg'},
        {'email': 'd.koznov@spbu.ru', 'first_name': 'Дмитрий', 'last_name': 'Кознов', 'middle_name': 'Владимирович',
         'avatar_uri': 'koznov.jpg'},
        {'email': 't.bryksin@spbu.ru', 'first_name': 'Тимофей', 'last_name': 'Брыксин', 'middle_name': 'Александрович',
         'avatar_uri': 'bryksin.jpg'},
        {'email': 'd.bylychev@spbu.ru', 'first_name': 'Дмитрий', 'last_name': 'Булычев', 'middle_name': 'Юрьевич',
         'avatar_uri': 'boulytchev.jpg'},
        {'email': 'y.litvinov@spbu.ru', 'first_name': 'Юрий', 'last_name': 'Литвинов', 'middle_name': 'Викторович',
         'avatar_uri': 'litvinov.jpg'},
        {'email': 'd.lutsiv@spbu.ru', 'first_name': 'Дмитрий', 'last_name': 'Луцив', 'middle_name': 'Вадимович',
         'avatar_uri': 'luciv.jpg'},
        {'email': 'k.romanovsky@spbu.ru', 'first_name': 'Константин', 'last_name': 'Романовский', 'middle_name': 'Юрьевич',
         'avatar_uri': 'empty.jpg'},
        {'email': 'm.serov@spbu.ru', 'first_name': 'Михаил', 'last_name': 'Серов',
         'middle_name': 'Александрович', 'avatar_uri': 'empty.jpg'},
        {'email': 's.s.sysoev@spbu.ru', 'first_name': 'Сергей', 'last_name': 'Сысоев',
         'middle_name': 'Сергеевич', 'avatar_uri': 'empty.jpg'},
        {'email': 'm.baklanovsky@spbu.ru', 'first_name': 'Максим', 'last_name': 'Баклановский',
         'middle_name': 'Викторович', 'avatar_uri': 'baklanovsky.jpg'},
        {'email': 'm.m.zhuravlev@spbu.ru', 'first_name': 'Максим', 'last_name': 'Журавлев',
         'middle_name': 'Михайлович', 'avatar_uri': 'zhuravlev.jpg'},
        {'email': 'i.zelenchuk@spbu.ru', 'first_name': 'Илья', 'last_name': 'Зеленчук',
         'middle_name': 'Валерьевич', 'avatar_uri': 'zelenchuk.jpg'},
        {'email': 'y.kirilenko@spbu.ru', 'first_name': 'Яков', 'last_name': 'Кириленко',
         'middle_name': 'Александрович', 'avatar_uri': 'kirilenko.jpg'},
        {'email': 'st035425@student.spbu.ru', 'first_name': 'Антон', 'last_name': 'Козлов',
         'middle_name': 'Павлович', 'avatar_uri': 'empty.jpg'},
        {'email': 'egor.k.kulikov@gmail.com', 'first_name': 'Егор', 'last_name': 'Куликов',
         'middle_name': 'Константинович', 'avatar_uri': 'kulikov.jpg'},
        {'email': 'd.mordvinov@spbu.ru', 'first_name': 'Дмитрий', 'last_name': 'Мордвинов',
         'middle_name': 'Александрович', 'avatar_uri': 'empty.jpg'},
        {'email': 'm.nemeshev@spbu.ru', 'first_name': 'Марат', 'last_name': 'Немешев',
         'middle_name': 'Халимович', 'avatar_uri': 'empty.jpg'},
        {'email': 'stanislav.sartasov@spbu.ru', 'first_name': 'Станислав', 'last_name': 'Сартасов',
         'middle_name': 'Юрьевич', 'avatar_uri': 'empty.jpg'},
        {'email': 'm.n.smirnov@spbu.ru', 'first_name': 'Михаил', 'last_name': 'Смирнов',
         'middle_name': 'Николаевич', 'avatar_uri': 'smirnov.jpg'},
        {'email': 'st036451@student.spbu.ru', 'first_name': 'Артур', 'last_name': 'Ханов',
         'middle_name': 'Рафаэльевич', 'avatar_uri': 'empty.jpg'},
        {'email': 's.shilov@spbu.ru', 'first_name': 'Сергей', 'last_name': 'Шилов',
         'middle_name': 'Юрьевич', 'avatar_uri': 'empty.jpg'},
        {'email': 'st013464@student.spbu.ru', 'first_name': 'Петр', 'last_name': 'Лозов',
         'middle_name': 'Алексеевич', 'avatar_uri': 'empty.jpg'},
        {'email': 'st013039@student.spbu.ru', 'first_name': 'Евгений', 'last_name': 'Моисеенко',
         'middle_name': 'Александрович', 'avatar_uri': 'empty.jpg'},
    ]
    staff = [
        {'position': 'Заведующий кафедрой, профессор', 'science_degree' : 'д.ф.-м.н.',
         'official_email': 'a.terekhov@spbu.ru', 'still_working' : True},
        {'position': 'Профессор', 'science_degree': 'д.ф.-м.н.',
         'official_email': 'o.granichin@spbu.ru', 'still_working': True},
        {'position': 'Профессор', 'science_degree': 'д.т.н.',
         'official_email': 'd.koznov@spbu.ru', 'still_working': True},
        {'position': 'Доцент', 'science_degree': 'к.т.н.',
         'official_email': 't.bryksin@spbu.ru', 'still_working': True},
        {'position': 'Доцент', 'science_degree': 'к.ф.-м.н.',
         'official_email': 'd.bylychev@spbu.ru', 'still_working': True},
        {'position': 'Доцент', 'science_degree': 'к.т.н.',
         'official_email': 'y.litvinov@spbu.ru', 'still_working': True},
        {'position': 'Доцент', 'science_degree': 'к.ф.-м.н.',
         'official_email': 'd.lutsiv@spbu.ru', 'still_working': True},
        {'position': 'Доцент', 'science_degree' : 'к.ф.-м.н.',
         'official_email' : 'k.romanovsky@spbu.ru', 'still_working': True},
        {'position': 'Доцент', 'official_email': 'm.serov@spbu.ru', 'still_working': True},
        {'position': 'Преподаватель-практик', 'science_degree': 'к.ф.-м.н.',
         'official_email': 's.s.sysoev@spbu.ru', 'still_working': True},
        {'position': 'Старший преподаватель', 'official_email': 'm.baklanovsky@spbu.ru', 'still_working': True},
        {'position': 'Старший преподаватель', 'official_email': 'm.m.zhuravlev@spbu.ru', 'still_working': True},
        {'position': 'Старший преподаватель', 'official_email': 'i.zelenchuk@spbu.ru', 'still_working': True},
        {'position': 'Старший преподаватель', 'official_email': 'y.kirilenko@spbu.ru', 'still_working': True},
        {'position': 'Старший преподаватель', 'official_email': 'st035425@student.spbu.ru', 'still_working': True},
        {'position': 'Старший преподаватель', 'official_email': 'egor.k.kulikov@gmail.com', 'still_working': True},
        {'position': 'Старший преподаватель', 'official_email': 'd.mordvinov@spbu.ru', 'still_working': True},
        {'position': 'Старший преподаватель', 'official_email': 'm.nemeshev@spbu.ru', 'still_working': True},
        {'position': 'Старший преподаватель', 'official_email': 'stanislav.sartasov@spbu.ru', 'still_working': True},
        {'position': 'Старший преподаватель', 'science_degree': 'к.т.н.','official_email': 'm.n.smirnov@spbu.ru',
         'still_working': True},
        {'position': 'Старший преподаватель', 'official_email': 'st036451@student.spbu.ru', 'still_working': True},
        {'position': 'Старший преподаватель', 'official_email': 's.shilov@spbu.ru', 'still_working': True},
        {'position': 'Инженер-исследователь', 'official_email': 'st013464@student.spbu.ru', 'still_working': True},
        {'position': 'Инженер-исследователь', 'official_email': 'st013039@student.spbu.ru', 'still_working': True},
    ]

    # Init DB
    db.session.commit() # https://stackoverflow.com/questions/24289808/drop-all-freezes-in-flask-with-sqlalchemy
    db.drop_all()
    db.create_all()

    # Create users
    for user in users:
        u = Users(email=user['email'], password_hash = generate_password_hash(urandom(16).hex()), first_name = user['first_name'], last_name = user['last_name'],
                  middle_name = user['middle_name'], avatar_uri = user['avatar_uri'])

        db.session.add(u)
        db.session.commit()
        print (u)

    # Create staff
    for user in staff:
        u = Users.query.filter_by(email=user['official_email']).first()

        if 'science_degree' in user:
            s = Staff(position = user['position'], science_degree = user['science_degree'],
                  official_email = user['official_email'], still_working = user['still_working'],
                  users_id = u.id)
        else:
            s = Staff(position = user['position'], official_email = user['official_email'],
                      still_working = user['still_working'], users_id = u.id)

        db.session.add(s)
        db.session.commit()
        print (s)

    return

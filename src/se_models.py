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
    status = db.Column(db.Boolean, default=False, nullable=False)

    def __repr__(self):
        return '<Stuff %r>' % self.official_email

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

    def __repr__(self):
        return '<Users %r>' % self.first_name

def init_db():

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

    return
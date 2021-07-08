from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from os import urandom

db = SQLAlchemy()

tag = db.Table('tag',
               db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'), primary_key=True),
               db.Column('thesis_id', db.Integer, db.ForeignKey('thesis.id'), primary_key=True)
               )

class Staff (db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    official_email = db.Column(db.String(255), unique=True, nullable=False)
    position = db.Column(db.String(255), nullable=False)
    science_degree = db.Column(db.String(255), nullable=True)
    still_working = db.Column(db.Boolean, default=False, nullable=False)

    supervisor = db.relationship("Thesis", backref=db.backref("supervisor"), foreign_keys = 'Thesis.supervisor_id')
    adviser = db.relationship("Thesis", backref=db.backref("reviewer"), foreign_keys = 'Thesis.reviewer_id')

    def __repr__(self):
        return '<%r>' % self.official_email

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

    staff = db.relationship("Staff", backref=db.backref("user", uselist=False))

    def get_name(self):
        return f"{self.last_name} {self.first_name} {self.middle_name}"

    def __str__(self):
        return f"{self.last_name} {self.first_name} {self.middle_name}"

    def __repr__(self):
        return '<%r %r %r>' % (self.last_name, self.first_name, self.middle_name)

# Coursework, diploma
class Worktype (db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(255), nullable=False)

    thesis = db.relationship("Thesis", backref=db.backref("type", uselist=False))

    def __repr__(self):
        return '<%r>' % self.type

# Courses
class Courses(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    code = db.Column(db.String(15), nullable=False)

    thesis = db.relationship("Thesis", backref=db.backref('course', uselist=False))
    curriculum = db.relationship("Curriculum", backref=db.backref('course', uselist=False))

    def __repr__(self):
        return '<%r>' % (self.name)

class Thesis (db.Model):
    id = db.Column(db.Integer, primary_key=True)

    type_id = db.Column(db.Integer, db.ForeignKey('worktype.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)

    name_ru = db.Column(db.String(512), nullable=False)
    name_en = db.Column(db.String(512), nullable=True)
    description = db.Column(db.String(4096), nullable=True)

    text_uri = db.Column(db.String(512), nullable=True)
    old_text_uri = db.Column(db.String(512), nullable=True)
    presentation_uri = db.Column(db.String(512), nullable=True)
    supervisor_review_uri = db.Column(db.String(512), nullable=True)
    reviewer_review_uri = db.Column(db.String(512), nullable=True)
    source_uri = db.Column(db.String(512), nullable=True)

    author = db.Column(db.String(512), nullable=False)
    supervisor_id = db.Column(db.Integer, db.ForeignKey('staff.id'), nullable=True)
    reviewer_id = db.Column(db.Integer, db.ForeignKey('staff.id'), nullable=True)

    publish_year = db.Column(db.Integer, nullable=False)
    recomended = db.Column(db.Boolean, default=False, nullable=False)
    temporary = db.Column(db.Boolean, default=False, nullable=False)

class Tags(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    tags = db.relationship('Thesis', secondary=tag, lazy='subquery', backref=db.backref('tags', lazy=True))

class Curriculum(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer, nullable=False)
    discipline = db.Column(db.String(256), nullable=False)
    study_year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(1024), nullable=True)
    type = db.Column(db.Integer, nullable=False, default=1)

    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)

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
         'middle_name': 'Александрович', 'avatar_uri': 'mordvinov.jpg'},
        {'email': 'm.nemeshev@spbu.ru', 'first_name': 'Марат', 'last_name': 'Немешев',
         'middle_name': 'Халимович', 'avatar_uri': 'nemeshev.jpg'},
        {'email': 'stanislav.sartasov@spbu.ru', 'first_name': 'Станислав', 'last_name': 'Сартасов',
         'middle_name': 'Юрьевич', 'avatar_uri': 'empty.jpg'},
        {'email': 'm.n.smirnov@spbu.ru', 'first_name': 'Михаил', 'last_name': 'Смирнов',
         'middle_name': 'Николаевич', 'avatar_uri': 'smirnov.jpg'},
        {'email': 'st036451@student.spbu.ru', 'first_name': 'Артур', 'last_name': 'Ханов',
         'middle_name': 'Рафаэльевич', 'avatar_uri': 'khanov.jpg'},
        {'email': 's.shilov@spbu.ru', 'first_name': 'Сергей', 'last_name': 'Шилов',
         'middle_name': 'Юрьевич', 'avatar_uri': 'empty.jpg'},
        {'email': 'st013464@student.spbu.ru', 'first_name': 'Петр', 'last_name': 'Лозов',
         'middle_name': 'Алексеевич', 'avatar_uri': 'empty.jpg'},
        {'email': 'st013039@student.spbu.ru', 'first_name': 'Евгений', 'last_name': 'Моисеенко',
         'middle_name': 'Александрович', 'avatar_uri': 'empty.jpg'},
        {'email': 's.v.grigoriev@spbu.ru', 'first_name': 'Семен', 'last_name': 'Григорьев',
         'middle_name': 'Вячеславович', 'avatar_uri': 'empty.jpg'},
        {'email': 'pimenov_aa_stub@spbu.ru', 'first_name': 'Александр', 'last_name': 'Пименов',
         'middle_name': 'Александрович', 'avatar_uri': 'empty.jpg'},
        {'email': 's.salischev@spbu.ru', 'first_name': 'Сергей', 'last_name': 'Салищев',
         'middle_name': 'Игоревич', 'avatar_uri': 'empty.jpg'},
        {'email': 'd.sagunov@spbu.ru', 'first_name': 'Данил', 'last_name': 'Сагунов',
         'middle_name': 'Георгиевич', 'avatar_uri': 'empty.jpg'},
        {'email': 'g.chernyshev@spbu.ru', 'first_name': 'Георгий', 'last_name': 'Чернышев',
         'middle_name': 'Алексеевич', 'avatar_uri': 'empty.jpg'},
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
        {'position': 'Доцент', 'official_email': 's.v.grigoriev@spbu.ru', 'science_degree': 'к.ф.-м.н.', 'still_working': False},
        {'position': 'Старший преподаватель', 'official_email': 'pimenov_aa_stub@spbu.ru', 'still_working': False},
        {'position': 'Старший преподаватель', 'official_email': 's.salischev@spbu.ru', 'still_working': False},
        {'position': 'Ассистент', 'official_email': 'd.sagunov@spbu.ru', 'still_working': False},
        {'position': 'Ассистент', 'official_email': 'g.chernyshev@spbu.ru', 'still_working': False},
    ]
    wtypes = [
        {'type': 'Все работы'},
        {'type' : 'Курсовая'},
        {'type' : 'Бакалаврская ВКР'},
        {'type' : 'Магистерская ВКР'},
    ]
    courses = [
        {'name': 'Математическое обеспечение и администрирование информационных систем (бакалавриат)', 'code' : '02.03.03'},
        {'name': 'Программная инженерия (бакалавриат)', 'code' : '09.03.04'},
        {'name': 'Математическое обеспечение и администрирование информационных систем (магистратура)', 'code': '02.04.03'},
        {'name': '371 группа (бакалавриат)', 'code': '371'},
        {'name': '343 группа (бакалавриат)', 'code': '343'},
        {'name': '344 группа (бакалавриат)', 'code': '344'},
        {'name': 'Программная инженерия (магистратура)', 'code': '09.04.04'},
    ]
    tags = [
        {
            'name' : 'Компилятор'
        },
        {
            'name' : 'Android'
        },
        {
            'name' : 'F#'
        },
        {
            'name' : 'РуСи'
        }
    ]
    curriculum = [
        {'year': 2019, 'discipline': 'Практикум на ЭВМ', 'study_year': 1, 'type': 1, 'course_id': 2},
        {'year': 2019, 'discipline': 'Дискретная математика', 'study_year': 1, 'type': 2, 'course_id': 2},
        {'year': 2019, 'discipline': 'Математический анализ', 'study_year': 1, 'type': 2, 'course_id': 2},
        {'year': 2019, 'discipline': 'Безопасность жизнедеятельности', 'study_year': 1, 'type': 3, 'course_id': 2},
        {'year': 2019, 'discipline': 'Основы программирования', 'study_year': 1, 'type': 1, 'course_id': 2},
        {'year': 2019, 'discipline': 'Групповая динамика и коммуникации', 'study_year': 1, 'type': 3, 'course_id': 2},
        {'year': 2019, 'discipline': 'Физическая культура и спорт', 'study_year': 1, 'type': 3, 'course_id': 2},
        {'year': 2019, 'discipline': 'Алгебра', 'study_year': 1, 'type': 2, 'course_id': 2},
        {'year': 2019, 'discipline': 'Иностранный язык', 'study_year': 1, 'type': 3, 'course_id': 2},
        {'year': 2019, 'discipline': 'Цифровая культура', 'study_year': 1, 'type': 3, 'course_id': 2},
        {'year': 2019, 'discipline': 'Алгоритмы и структуры данных', 'study_year': 1, 'type': 1, 'course_id': 2},
        {'year': 2019, 'discipline': 'Архитектура вычислительных систем', 'study_year': 1, 'type': 1, 'course_id': 2},
        {'year': 2019, 'discipline': 'Геометрия', 'study_year': 1, 'type': 2, 'course_id': 2},
        {'year': 2019, 'discipline': 'Введение в программную инженерию', 'study_year': 2, 'type': 1, 'course_id': 2},
        {'year': 2019, 'discipline': 'Практикум на ЭВМ', 'study_year': 2, 'type': 1, 'course_id': 2},
        {'year': 2019, 'discipline': 'История России', 'study_year': 2, 'type': 3, 'course_id': 2},
        {'year': 2019, 'discipline': 'Математический анализ', 'study_year': 2, 'type': 2, 'course_id': 2},
        {'year': 2019, 'discipline': 'Операционные системы', 'study_year': 2, 'type': 1, 'course_id': 2},
        {'year': 2019, 'discipline': 'Алгоритмы и анализ сложности', 'study_year': 2, 'type': 1, 'course_id': 2},
        {'year': 2019, 'discipline': 'Физическая культура и спорт', 'study_year': 2, 'type': 3, 'course_id': 2},
        {'year': 2019, 'discipline': 'Язык эффективной коммуникации', 'study_year': 2, 'type': 3, 'course_id': 2},
        {'year': 2019, 'discipline': 'Функциональное программирование', 'study_year': 2, 'type': 1, 'course_id': 2},
        {'year': 2019, 'discipline': 'Инженерная экономика', 'study_year': 2, 'type': 3, 'course_id': 2},
        {'year': 2019, 'discipline': 'Учебная практика (научно-исследовательская работа)', 'study_year': 2, 'type': 1, 'course_id': 2},
        {'year': 2019, 'discipline': 'Иностранный язык', 'study_year': 2, 'type': 3, 'course_id': 2},
        {'year': 2019, 'discipline': 'Разработка программного обеспечения', 'study_year': 2, 'type': 1, 'course_id': 2},
        {'year': 2019, 'discipline': 'Дифференциальные и разностные уравнения', 'study_year': 2, 'type': 2, 'course_id': 2},
        {'year': 2019, 'discipline': 'Основы бизнеса', 'study_year': 2, 'type': 3, 'course_id': 2},
        {'year': 2019, 'discipline': 'Человеко-машинное взаимодействие', 'study_year': 2, 'type': 1, 'course_id': 2},
        {'year': 2019, 'discipline': 'Теория вероятностей и математическая статистика', 'study_year': 2, 'type': 2, 'course_id': 2},
        {'year': 2019, 'discipline': 'Вычислительная математика', 'study_year': 2, 'type': 1, 'course_id': 2},
        {'year': 2019, 'discipline': 'Математическая логика', 'study_year': 2, 'type': 1, 'course_id': 2},
        {'year': 2019, 'discipline': 'Компьютерные сети', 'study_year': 3, 'type': 1, 'course_id': 2},
        {'year': 2019, 'discipline': 'Основы противодействия коррупции и экстремизму (онлайн-курс)', 'study_year': 3, 'type': 3, 'course_id': 2},
        {'year': 2019, 'discipline': 'Компьютерная графика', 'study_year': 3, 'type': 1, 'course_id': 2},
        {'year': 2019, 'discipline': 'Обеспечение качества и тестирование программного обеспечения ', 'study_year': 3, 'type': 1, 'course_id': 2},
        {'year': 2019, 'discipline': 'Теория автоматов и формальных языков ', 'study_year': 3, 'type': 1, 'course_id': 2},
        {'year': 2019, 'discipline': 'Базы данных', 'study_year': 3, 'type': 1, 'course_id': 2},
        {'year': 2019, 'discipline': 'Производственная практика', 'study_year': 3, 'type': 1, 'course_id': 2},
        {'year': 2019, 'discipline': 'Трансляция языков программирования', 'study_year': 3, 'type': 1, 'course_id': 2},
        {'year': 2019, 'discipline': 'Иностранный язык', 'study_year': 3, 'type': 3, 'course_id': 2},
        {'year': 2019, 'discipline': 'Методы оптимизации и исследование операций', 'study_year': 3, 'type': 2, 'course_id': 2},
        {'year': 2019, 'discipline': 'Моделирование информационных процессов ', 'study_year': 3, 'type': 1, 'course_id': 2},
        {'year': 2019, 'discipline': 'Основы педагогической деятельности (онлайн-курс)', 'study_year': 3, 'type': 3, 'course_id': 2},
        {'year': 2019, 'discipline': 'Теория графов', 'study_year': 3, 'type': 1, 'course_id': 2},
        {'year': 2019, 'discipline': 'Социально-правовые вопросы программной инженерии', 'study_year': 3, 'type': 3, 'course_id': 2},
        {'year': 2019, 'discipline': 'Проектирование и архитектура программного обеспечения', 'study_year': 3, 'type': 1, 'course_id': 2},
        {'year': 2019, 'discipline': 'Алгоритмы анализа графов (по выбору)', 'study_year': 3, 'type': 1, 'course_id': 2},
        {'year': 2019, 'discipline': 'Операционные системы и реализация языков программирования (по выбору)', 'study_year': 3, 'type': 1, 'course_id': 2},
        {'year': 2019, 'discipline': 'Реинжиниринг систем программирования (по выбору)', 'study_year': 3, 'type': 1, 'course_id': 2},
        {'year': 2019, 'discipline': 'Телекоммуникации (по выбору)', 'study_year': 3, 'type': 1, 'course_id': 2},
        {'year': 2019, 'discipline': 'Введение в специальность (по выбору)', 'study_year': 3, 'type': 1, 'course_id': 2},
        {'year': 2019, 'discipline': 'Системное программирование (по выбору)', 'study_year': 3, 'type': 1, 'course_id': 2},
        {'year': 2019, 'discipline': 'Преддипломная практика', 'study_year': 4, 'type': 1, 'course_id': 2},
        {'year': 2019, 'discipline': 'Интеллектуальные системы', 'study_year': 4, 'type': 1, 'course_id': 2},
        {'year': 2019, 'discipline': 'Прикладные задачи теории вероятностей', 'study_year': 4, 'type': 2, 'course_id': 2},
        {'year': 2019, 'discipline': 'Защита информации', 'study_year': 4, 'type': 1, 'course_id': 2},
        {'year': 2019, 'discipline': 'Анализ требований к программному обеспечению', 'study_year': 4, 'type': 1, 'course_id': 2},
        {'year': 2019, 'discipline': 'Управление программными проектами', 'study_year': 4, 'type': 1, 'course_id': 2},
        {'year': 2019, 'discipline': 'Иностранный язык', 'study_year': 4, 'type': 3, 'course_id': 2},
        {'year': 2019, 'discipline': 'Разработка приложений в СУБД (по выбору)', 'study_year': 4, 'type': 1, 'course_id': 2},
        {'year': 2019, 'discipline': 'Стохастическое программирование (по выбору)', 'study_year': 4, 'type': 1, 'course_id': 2},
        {'year': 2019, 'discipline': 'Введение в MS.NET (по выбору)', 'study_year': 4, 'type': 1, 'course_id': 2},
        {'year': 2019, 'discipline': 'Современные технологии разработки бизнес-приложений (по выбору)', 'study_year': 4, 'type': 1, 'course_id': 2},
        {'year': 2019, 'discipline': 'Программная инженерия (по выбору)', 'study_year': 4, 'type': 1, 'course_id': 2},
        {'year': 2019, 'discipline': 'Системное программирование для современных платформ (по выбору)', 'study_year': 4, 'type': 1, 'course_id': 2},
        {'year': 2019, 'discipline': 'Основы менеджмента', 'study_year': 4, 'type': 3, 'course_id': 2},
        {'year': 2019, 'discipline': 'Философия (онлайн-курс)', 'study_year': 4, 'type': 3, 'course_id': 2},
        {'year': 2019, 'discipline': 'Практика разработки документации (на английском языке) (по выбору)', 'study_year': 4, 'type': 1, 'course_id': 2},
        {'year': 2019, 'discipline': 'Стохастическая оптимизация в информатике (на английском языке) (по выбору)', 'study_year': 4, 'type': 1, 'course_id': 2},
        {'year': 2019, 'discipline': 'Алгоритмические основы робототехники (по выбору)', 'study_year': 4, 'type': 1, 'course_id': 2},
        {'year': 2019, 'discipline': 'Статический анализ программ (по выбору)', 'study_year': 4, 'type': 1, 'course_id': 2},
        {'year': 2019, 'discipline': 'Программирование', 'study_year': 1, 'type': 1, 'course_id': 1},
        {'year': 2019, 'discipline': 'Информатика', 'study_year': 1, 'type': 1, 'course_id': 1},
        {'year': 2019, 'discipline': 'Физическая культура и спорт', 'study_year': 1, 'type': 3, 'course_id': 1},
        {'year': 2019, 'discipline': 'Дискретная математика', 'study_year': 1, 'type': 2, 'course_id': 1},
        {'year': 2019, 'discipline': 'Математический анализ', 'study_year': 1, 'type': 2, 'course_id': 1},
        {'year': 2019, 'discipline': 'Алгебра и теория чисел', 'study_year': 1, 'type': 2, 'course_id': 1},
        {'year': 2019, 'discipline': 'Геометрия и топология', 'study_year': 1, 'type': 2, 'course_id': 1},
        {'year': 2019, 'discipline': 'Иностранный язык', 'study_year': 1, 'type': 3, 'course_id': 1},
        {'year': 2019, 'discipline': 'Цифровая культура (ЭО)', 'study_year': 1, 'type': 3, 'course_id': 1},
        {'year': 2019, 'discipline': 'История России (онлайн-курс)', 'study_year': 1, 'type': 3, 'course_id': 1},
        {'year': 2019, 'discipline': 'Программирование', 'study_year': 2, 'type': 1, 'course_id': 1},
        {'year': 2019, 'discipline': 'Учебная практика 1', 'study_year': 2, 'type': 1, 'course_id': 1},
        {'year': 2019, 'discipline': 'Информатика', 'study_year': 2, 'type': 1, 'course_id': 1},
        {'year': 2019, 'discipline': 'Физическая культура и спорт', 'study_year': 2, 'type': 3, 'course_id': 1},
        {'year': 2019, 'discipline': 'Математический анализ', 'study_year': 2, 'type': 2, 'course_id': 1},
        {'year': 2019, 'discipline': 'Алгебра и теория чисел', 'study_year': 2, 'type': 2, 'course_id': 1},
        {'year': 2019, 'discipline': 'Геометрия и топология', 'study_year': 2, 'type': 2, 'course_id': 1},
        {'year': 2019, 'discipline': 'Язык эффективной коммуникации (онлайнкурс)', 'study_year': 2, 'type': 3, 'course_id': 1},
        {'year': 2019, 'discipline': 'Дифференциальные уравнения', 'study_year': 2, 'type': 2, 'course_id': 1},
        {'year': 2019, 'discipline': 'Иностранный язык', 'study_year': 2, 'type': 3, 'course_id': 1},
        {'year': 2019, 'discipline': 'Операционные системы и оболочки', 'study_year': 2, 'type': 1, 'course_id': 1},
        {'year': 2019, 'discipline': 'Базы данных и СУБД', 'study_year': 2, 'type': 1, 'course_id': 1},
        {'year': 2019, 'discipline': 'Основы противодействия коррупции и экстремизму (онлайн-курс)', 'study_year': 2, 'type': 3, 'course_id': 1},
        {'year': 2019, 'discipline': 'Параллельное программирование', 'study_year': 2, 'type': 1, 'course_id': 1},
        {'year': 2019, 'discipline': 'Архитектура ЭВМ', 'study_year': 2, 'type': 1, 'course_id': 1},
        {'year': 2019, 'discipline': 'Математическая логика', 'study_year': 2, 'type': 2, 'course_id': 1},
        {'year': 2019, 'discipline': 'Структуры и алгоритмы компьютерной обработки данных', 'study_year': 2, 'type': 1, 'course_id': 1},
        {'year': 2019, 'discipline': 'Методы вычислений и вычислительный практикум', 'study_year': 3, 'type': 1, 'course_id': 1},
        {'year': 2019, 'discipline': 'Функциональный анализ', 'study_year': 3, 'type': 2, 'course_id': 1},
        {'year': 2019, 'discipline': 'Теория вероятностей и математическая статистика', 'study_year': 3, 'type': 2, 'course_id': 1},
        {'year': 2019, 'discipline': 'Основы бизнеса (онлайн-курс)', 'study_year': 3, 'type': 3, 'course_id': 1},
        {'year': 2019, 'discipline': 'Теория формальных языков и трансляций', 'study_year': 3, 'type': 1, 'course_id': 1},
        {'year': 2019, 'discipline': 'Учебная практика 2', 'study_year': 3, 'type': 1, 'course_id': 1},
        {'year': 2019, 'discipline': 'Математическая логика', 'study_year': 3, 'type': 2, 'course_id': 1},
        {'year': 2019, 'discipline': 'Математическая логика', 'study_year': 3, 'type': 2, 'course_id': 1},
        {'year': 2019, 'discipline': 'Иностранный язык', 'study_year': 3, 'type': 3, 'course_id': 1},
        {'year': 2019, 'discipline': 'Java-технологии. Часть 1 (по выбору)', 'study_year': 3, 'type': 1, 'course_id': 1},
        {'year': 2019, 'discipline': 'Алгоритмические языки параллельного программирования (по выбору)', 'study_year': 3, 'type': 1, 'course_id': 1},
        {'year': 2019, 'discipline': 'Архитектура процессора (по выбору)', 'study_year': 3, 'type': 1, 'course_id': 1},
        {'year': 2019, 'discipline': 'Введение в компьютерную математику (по выбору)', 'study_year': 3, 'type': 1, 'course_id': 1},
        {'year': 2019, 'discipline': 'Введение в теорию параллельных вычислений (по выбору)', 'study_year': 3, 'type': 1, 'course_id': 1},
        {'year': 2019, 'discipline': 'Задачи и методы динамических систем (по выбору)', 'study_year': 3, 'type': 1, 'course_id': 1},
        {'year': 2019, 'discipline': 'Модели и методы хранения и поиска информации (по выбору)', 'study_year': 3, 'type': 1, 'course_id': 1},
        {'year': 2019, 'discipline': 'Мультиагентные системы (по выбору)', 'study_year': 3, 'type': 1, 'course_id': 1},
        {'year': 2019, 'discipline': 'Основы компьютерной графики и обработки изображений (по выбору)', 'study_year': 3, 'type': 1, 'course_id': 1},
        {'year': 2019, 'discipline': 'Распараллеливание в OpenMP и интервальные вычисления (по выбору)', 'study_year': 3, 'type': 1, 'course_id': 1},
        {'year': 2019, 'discipline': 'Теория логического вывода (по выбору)',
         'study_year': 3, 'type': 1, 'course_id': 1},
        {'year': 2019, 'discipline': 'Хранение и управление данными (по выбору)',
         'study_year': 3, 'type': 1, 'course_id': 1},
        {'year': 2019, 'discipline': 'Автоматическое доказательство теорем (по выбору)',
         'study_year': 3, 'type': 2, 'course_id': 1},
        {'year': 2019, 'discipline': 'Введение в специальность (по выбору)',
         'study_year': 3, 'type': 3, 'course_id': 1},
        {'year': 2019, 'discipline': 'Логическое программирование (по выбору)',
         'study_year': 3, 'type': 1, 'course_id': 1},
        {'year': 2019, 'discipline': 'Методы хранения и индексирования (по выбору)',
         'study_year': 3, 'type': 1, 'course_id': 1},
        {'year': 2019, 'discipline': 'Поиск информации в неструктурированных данных (по выбору)',
         'study_year': 3, 'type': 1, 'course_id': 1},
        {'year': 2019, 'discipline': 'Системное программирование (по выбору)',
         'study_year': 3, 'type': 1, 'course_id': 1},
        {'year': 2019, 'discipline': 'Теория и практика распараллеливания в OpenMP (по выбору)',
         'study_year': 3, 'type': 1, 'course_id': 1},
        {'year': 2019, 'discipline': 'Теория распараллеливания над общей памятью (по выбору)',
         'study_year': 3, 'type': 1, 'course_id': 1},
        {'year': 2019, 'discipline': 'Технология преобразования последовательных программ в параллельные (по выбору)',
         'study_year': 3, 'type': 1, 'course_id': 1},
        {'year': 2019, 'discipline': 'Технология разработки программного обеспечения', 'study_year': 3, 'type': 1, 'course_id': 1},
        {'year': 2019, 'discipline': 'Основы педагогической деятельности (онлайнкурс)', 'study_year': 3, 'type': 3,
         'course_id': 1},
        {'year': 2019, 'discipline': 'Вычислительный практикум', 'study_year': 3, 'type': 1, 'course_id': 1},
        {'year': 2019, 'discipline': 'Уравнения математической физики', 'study_year': 3, 'type': 2, 'course_id': 1},
        {'year': 2019, 'discipline': 'Информационный поиск в Internet (по выбору)', 'study_year': 3, 'type': 1, 'course_id': 1},
        {'year': 2019, 'discipline': 'Параллельные алгоритмы численного моделирования (по выбору)', 'study_year': 3, 'type': 1,
         'course_id': 1},
        {'year': 2019, 'discipline': 'Распределенные параллельные системы (по выбору)', 'study_year': 3, 'type': 1,
         'course_id': 1},
        {'year': 2019, 'discipline': 'Реинжиниринг информационных систем (по выбору)', 'study_year': 3, 'type': 1,
         'course_id': 1},
        {'year': 2019, 'discipline': 'Сетевые технологии (по выбору)', 'study_year': 3, 'type': 1,
         'course_id': 1},
        {'year': 2019, 'discipline': 'Статистический анализ данных (по выбору)', 'study_year': 3, 'type': 1,
         'course_id': 1},
        {'year': 2019, 'discipline': 'Телекоммуникации (по выбору)', 'study_year': 3, 'type': 1,
         'course_id': 1},
        {'year': 2019, 'discipline': 'Язык программирования С++ (по выбору)', 'study_year': 3, 'type': 1,
         'course_id': 1},
        {'year': 2019, 'discipline': 'Java-технологии. Часть 2 (по выбору)', 'study_year': 3, 'type': 1,
         'course_id': 1},
        {'year': 2019, 'discipline': 'Алгоритмы анализа графов (по выбору)', 'study_year': 3, 'type': 1,
         'course_id': 1},
        {'year': 2019, 'discipline': 'Архитектура параллельных систем (по выбору)', 'study_year': 3, 'type': 1,
         'course_id': 1},
        {'year': 2019, 'discipline': 'Введение в архитектуру программ (по выбору)', 'study_year': 3, 'type': 1,
         'course_id': 1},
        {'year': 2019, 'discipline': 'Локальные сети и вычислительные системы (по выбору)', 'study_year': 3, 'type': 1,
         'course_id': 1},
        {'year': 2019, 'discipline': 'Организация и дизайн современных компьютеров (по выбору)', 'study_year': 3, 'type': 1,
         'course_id': 1},
        {'year': 2019, 'discipline': 'Параллельные вычисления с использованием графических процессоров (по выбору)', 'study_year': 3, 'type': 1,
         'course_id': 1},
        {'year': 2019, 'discipline': 'Программная инженерия (по выбору)', 'study_year': 3, 'type': 1,
         'course_id': 1},
        {'year': 2019, 'discipline': 'Реализация языков программирования (по выбору)', 'study_year': 3, 'type': 1,
         'course_id': 1},
        {'year': 2019, 'discipline': 'Системы управления контентом (по выбору)', 'study_year': 3, 'type': 1,
         'course_id': 1},
        {'year': 2019, 'discipline': 'Методы вычислений (по выбору)', 'study_year': 3, 'type': 1,
         'course_id': 1},
        {'year': 2019, 'discipline': 'Экстремальные задачи (по выбору)', 'study_year': 3, 'type': 1,
         'course_id': 1},

        {'year': 2019, 'discipline': 'Введение в компьютерное моделирование динамических систем', 'study_year': 4, 'type': 1,
         'course_id': 1},
        {'year': 2019, 'discipline': 'Теория вычислительных процессов и структур', 'study_year': 4,
         'type': 1,
         'course_id': 1},
        {'year': 2019, 'discipline': 'Архитектура вычислительных систем и компьютерных сетей', 'study_year': 4,
         'type': 1,
         'course_id': 1},
        {'year': 2019, 'discipline': 'Производственная практика', 'study_year': 4,
         'type': 1,
         'course_id': 1},
        {'year': 2019, 'discipline': 'Иностранный язык', 'study_year': 4, 'type': 3, 'course_id': 1},
        {'year': 2019, 'discipline': 'Всплесковая обработка числовых потоков и распараллеливание (по выбору)', 'study_year': 4,
         'type': 1,
         'course_id': 1},
        {'year': 2019, 'discipline': 'Конечно-автоматные модели. Анализ, синтез и оптимизация (по выбору)',
         'study_year': 4, 'type': 1, 'course_id': 1},
        {'year': 2019, 'discipline': 'Основы компьютерной безопасности (по выбору)',
         'study_year': 4, 'type': 1, 'course_id': 1},
        {'year': 2019, 'discipline': 'Программирование на платформе Microsoft.NET (по выбору)',
         'study_year': 4, 'type': 1, 'course_id': 1},
        {'year': 2019, 'discipline': 'Разработка Интернет-приложений (по выбору)',
         'study_year': 4, 'type': 1, 'course_id': 1},
        {'year': 2019, 'discipline': 'Распараллеливание алгоритмов в многопоточных системах (по выбору)',
         'study_year': 4, 'type': 1, 'course_id': 1},
        {'year': 2019, 'discipline': 'Распределенная обработка информации и NoSQL базы данных (по выбору)',
         'study_year': 4, 'type': 1, 'course_id': 1},
        {'year': 2019, 'discipline': 'Рекурсивно-логическое программирование (по выбору)',
         'study_year': 4, 'type': 1, 'course_id': 1},
        {'year': 2019, 'discipline': 'Функциональное программирование (по выбору)',
         'study_year': 4, 'type': 1, 'course_id': 1},
        {'year': 2019, 'discipline': 'Мультиагентные технологии (по выбору)',
         'study_year': 4, 'type': 1, 'course_id': 1},
        {'year': 2019, 'discipline': 'Параллельные алгоритмы обработки изображений (по выбору)',
         'study_year': 4, 'type': 1, 'course_id': 1},
        {'year': 2019, 'discipline': 'Системное программирование для современных платформ (по выбору)',
         'study_year': 4, 'type': 1, 'course_id': 1},
        {'year': 2019, 'discipline': 'Технология разработки программного обеспечения (по выбору)',
         'study_year': 4, 'type': 1, 'course_id': 1},
        {'year': 2019, 'discipline': 'Технология синхронного распараллеливания в многопоточных системах (по выбору)',
         'study_year': 4, 'type': 1, 'course_id': 1},
        {'year': 2019, 'discipline': 'Язык XML и его использование (по выбору)',
         'study_year': 4, 'type': 1, 'course_id': 1},
        {'year': 2019, 'discipline': 'Анализ алгоритмов (по выбору)',
         'study_year': 4, 'type': 1, 'course_id': 1},
        {'year': 2019, 'discipline': 'Конкретная математика (по выбору)',
         'study_year': 4, 'type': 2, 'course_id': 1},
        {'year': 2019, 'discipline': 'Алгоритмы СУБД (по выбору)',
         'study_year': 4, 'type': 1, 'course_id': 1},
        {'year': 2019, 'discipline': 'Сети Петри и представление процессов (по выбору)',
         'study_year': 4, 'type': 1, 'course_id': 1},
        {'year': 2019, 'discipline': 'Проектирование программного обеспечения (по выбору)',
         'study_year': 4, 'type': 1, 'course_id': 1},
        {'year': 2019, 'discipline': 'Философия (онлайн-курс)', 'study_year': 4, 'type': 3, 'course_id': 1},
        {'year': 2019, 'discipline': 'Безопасность жизнедеятельности (онлайнкурс)', 'study_year': 4, 'type': 3, 'course_id': 1},
        {'year': 2019, 'discipline': 'Преддипломная практика', 'study_year': 4, 'type': 1, 'course_id': 1},
        {'year': 2019, 'discipline': 'Администрирование информационных систем (на английском языке)', 'study_year': 4, 'type': 1, 'course_id': 1},
        {'year': 2019, 'discipline': 'Интеллектуальные системы (по выбору)', 'study_year': 4, 'type': 1, 'course_id': 1},
        {'year': 2019, 'discipline': 'Квантовые компьютеры (по выбору)', 'study_year': 4, 'type': 1, 'course_id': 1},
        {'year': 2019, 'discipline': 'Параллельное программирование с использованием стандартных интерфейсов (по выбору)', 'study_year': 4, 'type': 1, 'course_id': 1},
        {'year': 2019, 'discipline': 'Практика разработки документации (по выбору)', 'study_year': 4, 'type': 1, 'course_id': 1},
        {'year': 2019, 'discipline': 'Распараллеливание алгоритмов в распределенных системах (по выбору)', 'study_year': 4, 'type': 1, 'course_id': 1},
        {'year': 2019, 'discipline': 'Стандарты параллельного программирования (по выбору)', 'study_year': 4, 'type': 1, 'course_id': 1},
        {'year': 2019, 'discipline': 'Компьютерное моделирование динамических систем (по выбору)', 'study_year': 4, 'type': 1, 'course_id': 1},
        {'year': 2019, 'discipline': 'Теория и практика параллельного программирования (по выбору)', 'study_year': 4, 'type': 1, 'course_id': 1},
        {'year': 2019, 'discipline': 'Математические основы искусственного интеллекта (по выбору)', 'study_year': 4, 'type': 1, 'course_id': 1},
        {'year': 2019, 'discipline': 'Системы искусственного интеллекта (по выбору)', 'study_year': 4, 'type': 1, 'course_id': 1},
        {'year': 2019, 'discipline': 'Алгоритмы компьютерного зрения (по выбору)', 'study_year': 4, 'type': 1, 'course_id': 1},
        {'year': 2019, 'discipline': 'Коммуникационные среды для параллельных систем (по выбору)', 'study_year': 4, 'type': 1, 'course_id': 1},
        {'year': 2019, 'discipline': 'Модели и архитектуры программ и знаний (по выбору)', 'study_year': 4,
         'type': 1, 'course_id': 1},
        {'year': 2019, 'discipline': 'Распараллеливание в ОС UNIX (по выбору)', 'study_year': 4,
         'type': 1, 'course_id': 1},
        {'year': 2019, 'discipline': 'Современные подходы к хранению, управлению и защите данных (по выбору)', 'study_year': 4,
         'type': 1, 'course_id': 1},
        {'year': 2019, 'discipline': 'Технология синхронного распараллеливания в распределенных системах (по выбору)', 'study_year': 4,
         'type': 1, 'course_id': 1},
        {'year': 2019, 'discipline': 'Управление проектами (по выбору)', 'study_year': 4,
         'type': 1, 'course_id': 1},
    ]
    curriculum2 = [
        {'year': 2019, 'discipline': 'Практикум на ЭВМ', 'semestr': 1, 'type': 1, 'course_id': 2, 'hard': 5},
        {'year': 2019, 'discipline': 'Дискретная математика', 'semestr': 1, 'type': 2, 'course_id': 2, 'hard': 5},
        {'year': 2019, 'discipline': 'Математический анализ', 'semestr': 1, 'type': 2, 'course_id': 2, 'hard': 7},
        {'year': 2019, 'discipline': 'Безопасность жизнедеятельности (онлайн-курс)', 'semestr': 1, 'type': 3, 'course_id': 2, 'hard': 0},
        {'year': 2019, 'discipline': 'Основы программирования', 'semestr': 1, 'type': 1, 'course_id': 2, 'hard': 3},
        {'year': 2019, 'discipline': 'Групповая динамика и коммуникации', 'semestr': 1, 'type': 3, 'course_id': 2, 'hard': 2},
        {'year': 2019, 'discipline': 'Физическая культура и спорт', 'semestr': 1, 'type': 3, 'course_id': 2, 'hard': 0},
        {'year': 2019, 'discipline': 'Алгебра', 'semestr': 1, 'type': 2, 'course_id': 2, 'hard': 5},
        {'year': 2019, 'discipline': 'Иностранный язык', 'semestr': 1, 'type': 3, 'course_id': 2, 'hard': 3},
        {'year': 2019, 'discipline': 'Практикум на ЭВМ', 'semestr': 2, 'type': 1, 'course_id': 2, 'hard': 3},
        {'year': 2019, 'discipline': 'Цифровая культура', 'semestr': 2, 'type': 3, 'course_id': 2, 'hard': 1},
        {'year': 2019, 'discipline': 'Дискретная математика', 'semestr': 2, 'type': 2, 'course_id': 2, 'hard': 4},
        {'year': 2019, 'discipline': 'Математический анализ', 'semestr': 2, 'type': 2, 'course_id': 2, 'hard': 5},
        {'year': 2019, 'discipline': 'Алгоритмы и структуры данных', 'semestr': 2, 'type': 1, 'course_id': 2, 'hard': 2},
        {'year': 2019, 'discipline': 'Основы программирования', 'semestr': 2, 'type': 1, 'course_id': 2, 'hard': 3},
        {'year': 2019, 'discipline': 'Физическая культура и спорт', 'semestr': 2, 'type': 3, 'course_id': 2, 'hard': 0},
        {'year': 2019, 'discipline': 'Алгебра', 'semestr': 2, 'type': 2, 'course_id': 2, 'hard': 2},
        {'year': 2019, 'discipline': 'Архитектура вычислительных систем', 'semestr': 2, 'type': 1, 'course_id': 2, 'hard': 3},
        {'year': 2019, 'discipline': 'Геометрия', 'semestr': 2, 'type': 2, 'course_id': 2, 'hard': 4},
        {'year': 2019, 'discipline': 'Иностранный язык', 'semestr': 2, 'type': 3, 'course_id': 2, 'hard': 3},
        {'year': 2019, 'discipline': 'Введение в программную инженерию', 'semestr': 3, 'type': 3, 'course_id': 2, 'hard': 3},
        {'year': 2019, 'discipline': 'Практикум на ЭВМ', 'semestr': 3, 'type': 1, 'course_id': 2,
         'hard': 3},
        {'year': 2019, 'discipline': 'История России (онлайн-курс)', 'semestr': 3, 'type': 3, 'course_id': 2,
         'hard': 3},
        {'year': 2019, 'discipline': 'Математический анализ', 'semestr': 3, 'type': 2, 'course_id': 2,
         'hard': 4},
        {'year': 2019, 'discipline': 'Операционные системы', 'semestr': 3, 'type': 1, 'course_id': 2,
         'hard': 3},
        {'year': 2019, 'discipline': 'Алгоритмы и анализ сложности', 'semestr': 3, 'type': 2, 'course_id': 2,
         'hard': 4},
        {'year': 2019, 'discipline': 'Физическая культура и спорт', 'semestr': 3, 'type': 3, 'course_id': 2,
         'hard': 0},
        {'year': 2019, 'discipline': 'Язык эффективной коммуникации (онлайн-курс)', 'semestr': 3, 'type': 3, 'course_id': 2,
         'hard': 1},
        {'year': 2019, 'discipline': 'Функциональное программирование', 'semestr': 3, 'type': 1, 'course_id': 2,
         'hard': 2},
        {'year': 2019, 'discipline': 'Инженерная экономика', 'semestr': 3, 'type': 3, 'course_id': 2,
         'hard': 2},
        {'year': 2019, 'discipline': 'Учебная практика (научноисследовательская работа)', 'semestr': 3, 'type': 1, 'course_id': 2,
         'hard': 2},
        {'year': 2019, 'discipline': 'Иностранный язык', 'semestr': 3, 'type': 3, 'course_id': 2,
         'hard': 2},
        {'year': 2019, 'discipline': 'Разработка программного обеспечения', 'semestr': 4, 'type': 1, 'course_id': 2,
         'hard': 3},
        {'year': 2019, 'discipline': 'Дифференциальные и разностные уравнения', 'semestr': 4, 'type': 2, 'course_id': 2,
         'hard': 5},
        {'year': 2019, 'discipline': 'Практикум на ЭВМ', 'semestr': 4, 'type': 1, 'course_id': 2,
         'hard': 4},
        {'year': 2019, 'discipline': 'Основы бизнеса (онлайн-курс)', 'semestr': 4, 'type': 3, 'course_id': 2,
         'hard': 1},
        {'year': 2019, 'discipline': 'Человеко-машинное взаимодействие', 'semestr': 4, 'type': 1, 'course_id': 2,
         'hard': 1},
        {'year': 2019, 'discipline': ' Теория вероятностей и математическая статистика', 'semestr': 4, 'type': 2, 'course_id': 2,
         'hard': 4},
        {'year': 2019, 'discipline': 'Физическая культура и спорт', 'semestr': 3, 'type': 3, 'course_id': 2,
         'hard': 0},
        {'year': 2019, 'discipline': 'Вычислительная математика', 'semestr': 4, 'type': 2, 'course_id': 2,
         'hard': 3},
        {'year': 2019, 'discipline': ' Математическая логика', 'semestr': 4, 'type': 1, 'course_id': 2,
         'hard': 3},
        {'year': 2019, 'discipline': 'Учебная практика (научно-исследовательская работа)', 'semestr': 4, 'type': 1, 'course_id': 2,
         'hard': 3},
        {'year': 2019, 'discipline': 'Иностранный язык', 'semestr': 3, 'type': 3, 'course_id': 2,
         'hard': 2},
    ]

    thesis = []

    # Init DB
    db.session.commit() # https://stackoverflow.com/questions/24289808/drop-all-freezes-in-flask-with-sqlalchemy
    db.drop_all()
    db.create_all()

    # Create users
    print ("Create users")
    for user in users:
        u = Users(email=user['email'], password_hash = generate_password_hash(urandom(16).hex()), first_name = user['first_name'], last_name = user['last_name'],
                  middle_name = user['middle_name'], avatar_uri = user['avatar_uri'])

        db.session.add(u)
        db.session.commit()

    # Create staff
    print("Create staff")
    for user in staff:
        u = Users.query.filter_by(email=user['official_email']).first()

        if 'science_degree' in user:
            s = Staff(position = user['position'], science_degree = user['science_degree'],
                  official_email = user['official_email'], still_working = user['still_working'],
                  user_id = u.id)
        else:
            s = Staff(position = user['position'], official_email = user['official_email'],
                      still_working = user['still_working'], user_id = u.id)

        db.session.add(s)
        db.session.commit()

    # Create WorkTypes
    print("Create worktypes")
    for w in wtypes:
        wt = Worktype(type = w['type'])
        db.session.add(wt)
        db.session.commit()

    # Create Courses
    print("Create courses")
    for course in courses:
        c = Courses(name = course['name'], code = course['code'])
        db.session.add(c)
        db.session.commit()

    # Create Curriculum
    print ("Create curriculum")
    for cur in curriculum:
        if 'type' in cur:
            c = Curriculum(year = cur['year'], discipline = cur['discipline'], study_year = cur['study_year'],
                           type = cur['type'], course_id = cur['course_id'])
        else:
            c = Curriculum(year = cur['year'], discipline = cur['discipline'], study_year = cur['study_year'],
                           course_id = cur['course_id'])

        db.session.add(c)
        db.session.commit()

    for tag in tags:
        t = Tags(name=tag['name'])
        db.session.add(t)
        db.session.commit()

    # Create Thesis
    print("Create thesis")
    for work in thesis:
        if 'source_uri' in work:
            t = Thesis(name_ru = work['name_ru'], name_en=work['name_en'], description=work['description'],
                   text_uri=work['text_uri'], presentation_uri=work['presentation_uri'],
                   supervisor_review_uri=work['supervisor_review_uri'], reviewer_review_uri=work['reviewer_review_uri'],
                   author=work['author'], supervisor_id=work['supervisor_id'], reviewer_id=work['reviewer_id'],
                   publish_year=work['publish_year'], type_id=work['type_id'], course_id = 1, source_uri=work['source_uri'])
        else:
            t = Thesis(name_ru = work['name_ru'], name_en=work['name_en'], description=work['description'],
                   text_uri=work['text_uri'], presentation_uri=work['presentation_uri'],
                   supervisor_review_uri=work['supervisor_review_uri'], reviewer_review_uri=work['reviewer_review_uri'],
                   author=work['author'], supervisor_id=work['supervisor_id'], reviewer_id=work['reviewer_id'],
                   publish_year=work['publish_year'], type_id=work['type_id'], course_id = 1)

        db.session.add(t)
        db.session.commit()

        # Adds tags
        records = Tags.query.all()
        for tag in records:
            t.tags.append(tag)
            db.session.commit()

    return
# -*- coding: utf-8 -*-

import json
import requests

# Структура Thesis :
#
# type_id - тип работы (кучебная практика, бакалаврская ВКР, магистерская ВКР, ...)
# course_id - направление обучения (ПИ, матобесы)
# name_ru - название работы на русском языке
# author - полное ФИО автора работы
# source_uri - ссылка на результат работы
# supervisor - фамилия руководителя
# publish_year - год кубликации
# secret_key - ключ для доступа к API
thesis_info = {'type_id' : 3, 'course_id'  : 2, 
'name_ru' : 'Определение полос движения на заснеженной дороге по видео', 
'author' : 'Лунев Артем Евгеньевич',
'source_uri' : 'https://github.com/artemlunev2000/winter-road-detection',
'supervisor' : 'Литвинов', 'publish_year' : 2022, 'secret_key': '9d1fe6c77d53465cc50afc7d57b3ca84'}

# Текст работы
thesis_text = 'Lunev-report.pdf'

# Презентация
presentation = 'Lunev-presentation.pdf'

# Отзыв руководителя
supervisor_review = 'Lunev-review.pdf'

# Отзыв рецензента или консультанта
reviewer_review = 'Lunev-review-consultant.pdf'

# URI API
url = "http://127.0.0.1:5000/post_theses"

# Если нет презентации или отзыва, то просто закомментируйте нужное поле. 
files = [
    ('thesis_text', (thesis_text, open(thesis_text, 'rb'), 'application/octet')),
    ('reviewer_review', (reviewer_review, open(reviewer_review, 'rb'), 'application/octet')),
    ('presentation', (presentation, open(presentation, 'rb'), 'application/octet')),
    ('supervisor_review', (supervisor_review, open(supervisor_review, 'rb'), 'application/octet')),
    ('thesis_info', ('thesis_info', json.dumps(thesis_info), 'application/json')),
]

r = requests.post(url, files=files, allow_redirects=False)
print(str(r.content, 'utf-8'))

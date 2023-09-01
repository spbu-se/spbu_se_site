# -*- coding: utf-8 -*-

# Yandex disk
CLIENT_ID = "10e079e42b49492295a39e2767e7b049"
CLIENT_SECRET = "621eab823cdf4649868b6e317963a054"


FOLDER_FOR_TABLE = "static/practice/result_table/"

TABLE_COLUMNS = {
    "name": "ФИО",
    "how_to_contact": "Способ оперативной связи (почта, Teams, Telegram, ...)",
    "supervisor": "Научный руководитель",
    "consultant": "Консультант (если есть), полностью ФИО, должность и компания",
    "theme": "Тема",
    "text": "Текст",
    "supervisor_review": "Отзыв научника",
    "reviewer_review": "Отзыв консультанта",
    "code": "Код",
    "committer": "Имя коммитера",
    "presentation": "Презентация",
}


# Folder for downloading of materials about all practices
ARCHIVE_FOLDER = "static/zip/"

TEXT_UPLOAD_FOLDER = "static/practice/texts/"
REVIEW_UPLOAD_FOLDER = "static/practice/reviews/"
PRESENTATION_UPLOAD_FOLDER = "static/practice/slides/"

ALLOWED_EXTENSIONS = {"pdf"}

MIN_LENGTH_OF_TOPIC = 7
MIN_LENGTH_OF_GOAL = 20
MIN_LENGTH_OF_TASK = 15

MIN_LENGTH_OF_FIELD_WAS_DONE = 10
MIN_LENGTH_OF_FIELD_PLANNED_TO_DO = 10

FORMAT_DATE_TIME = "%d.%m.%Y %H:%M"

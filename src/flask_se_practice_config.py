"""
   Copyright 2023 Alexander Slugin

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""
# -*- coding: utf-8 -*-

import os
from datetime import date
from enum import Enum
from typing import Tuple
from transliterate import translit

from flask_se_config import get_thesis_type_id_string
from se_models import CurrentThesis

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

# Folders for materials of archive thesises
ARCHIVE_TEXT_FOLDER = "./static/thesis/texts/"
ARCHIVE_PRESENTATION_FOLDER = "./static/thesis/slides/"
ARCHIVE_REVIEW_FOLDER = "./static/thesis/reviews/"


# For saving of files
class TypeOfFile(Enum):
    TEXT = "text"
    REVIEWER_REVIEW = "reviewer_review"
    SUPERVISOR_REVIEW = "supervisor_review"
    PRESENTATION = "slides"


def allowed_file(filename) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def get_filename(
    current_thesis: CurrentThesis, folder: str, type_of_file: str
) -> Tuple[str, str]:
    author_en = translit(current_thesis.user.get_name(), "ru", reversed=True)
    author_en = author_en.replace(" ", "_")

    filename = author_en + "_" + get_thesis_type_id_string(current_thesis.worktype_id)
    filename = filename + "_" + str(date.today().year) + "_" + type_of_file
    filename_with_ext = filename + ".pdf"
    full_filename = os.path.join(folder + filename_with_ext)

    # Check if file already exist
    if os.path.isfile(full_filename):
        filename = filename + "_" + str(os.urandom(8).hex())
        filename_with_ext = filename + ".pdf"
        full_filename = os.path.join(folder + filename_with_ext)

    return full_filename, filename_with_ext

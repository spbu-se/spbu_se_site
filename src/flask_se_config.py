# -*- coding: utf-8 -*-

import os
import sys
import re
import pathlib
from datetime import datetime

SECRET_KEY = os.path.join(pathlib.Path(__file__).parent, "flask_se_secret.conf")
MAIL_PASSWORD_FILE = os.path.join(pathlib.Path(__file__).parent, "flask_se_mail.conf")
SECRET_KEY_THESIS = os.urandom(16).hex()
SQLITE_DATABASE_NAME = 'se.db'

if os.path.exists(MAIL_PASSWORD_FILE):
    with open(MAIL_PASSWORD_FILE, 'r') as file:
        MAIL_PASSWORD = file.read().rstrip()
else:
    print("There is no MAIL_PASSWORD_FILE, generate random MAIL_PASSWORD")
    MAIL_PASSWORD = os.urandom(16).hex()


current_data = datetime.today().strftime('%Y-%m-%d')
SQLITE_DATABASE_BACKUP_NAME = 'se_backup_' + current_data + '.db'

type_id_string = ['', 'Bachelor_Report', 'Bachelor_Thesis', 'Master_Thesis',
                  'Autumn_practice_2nd_year', 'Spring_practice_2nd_year', 'Autumn_practice_3rd_year',
                  'Spring_practice_3rd_year', 'Production_practice', 'Pre_graduate_practice']

PY2 = sys.version_info[0] == 2
if PY2:
    text_type = unicode
else:
    text_type = str

_windows_device_files = (
    "CON",
    "AUX",
    "COM1",
    "COM2",
    "COM3",
    "COM4",
    "LPT1",
    "LPT2",
    "LPT3",
    "PRN",
    "NUL",
)

_filename_strip_re = re.compile(r"[^A-Za-zа-яА-ЯёЁ0-9_.-]")


def secure_filename(filename: str) -> str:
    if isinstance(filename, text_type):
        from unicodedata import normalize
        filename = normalize("NFKD", filename)

    for sep in os.path.sep, os.path.altsep:
        if sep:
            filename = filename.replace(sep, " ")

    filename = str(_filename_strip_re.sub("", "_".join(filename.split()))).strip(
        "._"
    )

    if (
            os.name == "nt"
            and filename
            and filename.split(".")[0].upper() in _windows_device_files
    ):
        filename = "_{filename}"

    return filename


# https://felx.me/2021/08/29/improving-the-hacker-news-ranking-algorithm.html
def post_ranking_score(upvotes=1, age=0, views=1):
    u = upvotes**0.8
    a = (age + 2) ** 1.8
    return (u/a) / (views + 1)


def get_hours_since(date):
    time_diff = datetime.utcnow() - date
    return int(time_diff.total_seconds() / 3600)


def plural_hours(n):
    hours = ['час', 'часа', 'часов']
    days = ['день', 'дня', 'дней']

    if (n>24):
        n = int (n/24)
        if n % 10 == 1 and n % 100 != 11:
            p = 0
        elif 2 <= n % 10 <= 4 and (n % 100 < 10 or n % 100 >= 20):
            p = 1
        else:
            p = 2

        return str(n) + ' ' + days[p]

    if (n==0):
        return 'меньше часа'
    if n % 10 == 1 and n % 100 != 11:
        p = 0
    elif 2 <= n % 10 <= 4 and (n % 100 < 10 or n % 100 >= 20):
        p = 1
    else:
        p = 2

    return str(n) + ' ' + hours[p]


def get_thesis_type_id_string(id):
    return type_id_string[id - 1]
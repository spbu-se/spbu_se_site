# -*- coding: utf-8 -*-

import os
import sys
import re
from datetime import datetime

SECRET_KEY = os.urandom(16).hex()
SECRET_KEY_THESIS = os.urandom(16).hex()

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
        filename = f"_{filename}"

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
    days = ['час', 'часа', 'часов']

    if (n==0):
        return 'меньше часа'
    if n % 10 == 1 and n % 100 != 11:
        p = 0
    elif 2 <= n % 10 <= 4 and (n % 100 < 10 or n % 100 >= 20):
        p = 1
    else:
        p = 2

    return str(n) + ' ' + days[p]
# -*- coding: utf-8 -*-
#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0

import os
import re
import sys
from os.path import splitext
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from transliterate import translit

from flask_se import app
from se_models import Staff, Thesis, Users, db

# Init Database
db.app = app
db.init_app(app)

# Download files?
download = False


def download_file(uri, safe_filename, save_path):
    # Skip if download == false
    if not download:
        return

    r = requests.get(uri, allow_redirects=True, timeout=30)
    print("Download: " + str(uri))
    open(safe_filename, "wb").write(r.content)
    os.rename(safe_filename, save_path + safe_filename)


# Get
# https://oops.math.spbu.ru/SE/diploma/2020/index
# РњР°С‚РµРјР°С‚РёС‡РµСЃРєРѕРµ РѕР±РµСЃРїРµС‡РµРЅРёРµ Рё Р°РґРјРёРЅРёСЃС‚СЂРёСЂРѕРІР°РЅРёРµ РёРЅС„РѕСЂРјР°С†РёРѕРЅРЅС‹С… СЃРёСЃС‚РµРј


def get_2020_02_03_03():
    session = requests.session()
    url = "https://oops.math.spbu.ru/SE/diploma/2020/index"
    base_url = "https://oops.math.spbu.ru/SE/diploma/2020/"
    code = "02.03.03"

    print(url)
    response = session.get(url)

    if response.status_code != 200:
        print("Response statun != 200, error.")
        sys.exit(0)

    soup = BeautifulSoup(response.text, "lxml")

    # Find header
    header = soup.find_all(string=re.compile(code))

    # Find table
    table = header[0].find_next("table")

    for row in table.findAll("tr"):
        cols = row.find_all("td")

        # Check if we have data row
        if len(cols) == 9:
            author = cols[0].text
            author_en = translit(author, "ru", reversed=True)
            author_en = author_en.replace(" ", "_")
            name_ru = cols[1].text
            supervisor = cols[2].text
            supervisor_id = 1
            cols[3].text
            old_text_uri = ""
            text_uri = ""
            presentation_uri = ""
            supervisor_review_uri = ""
            reviewer_review_uri = ""
            source_uri = ""

            print("Add " + name_ru)

            if cols[4].find("a"):
                old_text_uri = cols[4].find("a").get("href")
                path = urlparse(old_text_uri).path
                extension = splitext(path)[1]
                filename = author_en + "_Bachelor_Thesis_2020_text" + extension
                text_uri = filename
                download_file(base_url + old_text_uri, filename, "static/tmp/texts/")
            else:
                continue

            if cols[5].find("a"):
                presentation_uri_d = cols[5].find("a").get("href")
                path = urlparse(presentation_uri_d).path
                extension = splitext(path)[1]
                filename = author_en + "_Bachelor_Thesis_2020_slides" + extension
                presentation_uri = filename
                download_file(base_url + presentation_uri_d, filename, "static/tmp/slides/")
            else:
                continue

            if cols[6].find("a"):
                supervisor_review_uri_d = cols[6].find("a").get("href")
                path = urlparse(supervisor_review_uri_d).path
                extension = splitext(path)[1]
                filename = author_en + "_Bachelor_Thesis_2020_supervisor_review" + extension
                supervisor_review_uri = filename
                download_file(base_url + supervisor_review_uri_d, filename, "static/tmp/reviews/")
            else:
                continue

            if cols[7].find("a"):
                reviewer_review_uri_d = cols[7].find("a").get("href")
                path = urlparse(reviewer_review_uri_d).path
                extension = splitext(path)[1]
                filename = author_en + "_Bachelor_Thesis_2020_reviewer_review" + extension
                reviewer_review_uri = filename
                download_file(base_url + reviewer_review_uri_d, filename, "static/tmp/reviews/")
            else:
                continue

            source_uri = cols[8].find("a").get("href") if cols[8].find("a") else ""

            # Try to get supervisor_id
            last_name = supervisor.split()[-1]
            q = Users.query.filter_by(last_name=last_name).first()
            if q:
                r = Staff.query.filter_by(user_id=q.id).first()
                supervisor_id = r.id
            else:
                print("Error, no " + supervisor)
                sys.exit(1)

            if source_uri:
                t = Thesis(
                    name_ru=name_ru,
                    text_uri=text_uri,
                    old_text_uri="https://oops.math.spbu.ru/SE/diploma/2020/" + old_text_uri,
                    presentation_uri=presentation_uri,
                    supervisor_review_uri=supervisor_review_uri,
                    reviewer_review_uri=reviewer_review_uri,
                    author=author,
                    supervisor_id=supervisor_id,
                    reviewer_id=2,
                    publish_year=2020,
                    type_id=3,
                    course_id=1,
                    source_uri=source_uri,
                )
            else:
                t = Thesis(
                    name_ru=name_ru,
                    text_uri=text_uri,
                    old_text_uri="https://oops.math.spbu.ru/SE/diploma/2020/" + old_text_uri,
                    presentation_uri=presentation_uri,
                    supervisor_review_uri=supervisor_review_uri,
                    reviewer_review_uri=reviewer_review_uri,
                    author=author,
                    supervisor_id=supervisor_id,
                    reviewer_id=2,
                    publish_year=2020,
                    type_id=3,
                    course_id=1,
                )

            db.session.add(t)
            db.session.commit()


# Get
# https://oops.math.spbu.ru/SE/diploma/2020/index
# РџСЂРѕРіСЂР°РјРјРЅР°СЏ РёРЅР¶РµРЅРµСЂРёСЏ


def get_2020_09_03_04():
    session = requests.session()
    url = "https://oops.math.spbu.ru/SE/diploma/2020/index"
    base_url = "https://oops.math.spbu.ru/SE/diploma/2020/"
    code = "09.03.04"

    print(url)
    response = session.get(url)

    if response.status_code != 200:
        print("Response statun != 200, error.")
        sys.exit(0)

    soup = BeautifulSoup(response.text, "lxml")

    # Find header
    header = soup.find_all(string=re.compile(code))

    # Find table
    table = header[0].find_next("table")

    for row in table.findAll("tr"):
        cols = row.find_all("td")

        # Check if we have data row
        # 10 cols
        if len(cols) == 10:
            author = cols[0].text
            author_en = translit(author, "ru", reversed=True)
            author_en = author_en.replace(" ", "_")
            name_ru = cols[1].text
            supervisor = cols[2].text
            supervisor_id = 1
            cols[3].text
            old_text_uri = ""
            text_uri = ""
            presentation_uri = ""
            supervisor_review_uri = ""
            reviewer_review_uri = ""
            source_uri = ""

            print("Add " + name_ru)

            if cols[5].find("a"):
                old_text_uri = cols[5].find("a").get("href")
                path = urlparse(old_text_uri).path
                extension = splitext(path)[1]
                filename = author_en + "_Bachelor_Thesis_2020_text" + extension
                text_uri = filename
                download_file(base_url + old_text_uri, filename, "static/tmp/texts/")
            else:
                text_uri = ""

            if cols[6].find("a"):
                presentation_uri_d = cols[6].find("a").get("href")
                path = urlparse(presentation_uri_d).path
                extension = splitext(path)[1]
                filename = author_en + "_Bachelor_Thesis_2020_slides" + extension
                presentation_uri = filename
                download_file(base_url + presentation_uri_d, filename, "static/tmp/slides/")
            else:
                presentation_uri = ""

            if cols[7].find("a"):
                supervisor_review_uri_d = cols[7].find("a").get("href")
                path = urlparse(supervisor_review_uri_d).path
                extension = splitext(path)[1]
                filename = author_en + "_Bachelor_Thesis_2020_supervisor_review" + extension
                supervisor_review_uri = filename
                download_file(base_url + supervisor_review_uri_d, filename, "static/tmp/reviews/")
            else:
                supervisor_review_uri = ""

            if cols[8].find("a"):
                reviewer_review_uri_d = cols[8].find("a").get("href")
                path = urlparse(reviewer_review_uri_d).path
                extension = splitext(path)[1]
                filename = author_en + "_Bachelor_Thesis_2020_reviewer_review" + extension
                reviewer_review_uri = filename
                download_file(base_url + reviewer_review_uri_d, filename, "static/tmp/reviews/")
            else:
                reviewer_review_uri = ""

            source_uri = cols[9].find("a").get("href") if cols[9].find("a") else ""

            # Try to get supervisor_id
            last_name = supervisor.split()[-1]
            q = Users.query.filter_by(last_name=last_name).first()
            if q:
                r = Staff.query.filter_by(user_id=q.id).first()
                supervisor_id = r.id
            else:
                print("Error, no " + supervisor)
                sys.exit(1)

            if source_uri:
                t = Thesis(
                    name_ru=name_ru,
                    text_uri=text_uri,
                    old_text_uri="https://oops.math.spbu.ru/SE/diploma/2020/" + old_text_uri,
                    presentation_uri=presentation_uri,
                    supervisor_review_uri=supervisor_review_uri,
                    reviewer_review_uri=reviewer_review_uri,
                    author=author,
                    supervisor_id=supervisor_id,
                    reviewer_id=2,
                    publish_year=2020,
                    type_id=3,
                    course_id=2,
                    source_uri=source_uri,
                )
            else:
                t = Thesis(
                    name_ru=name_ru,
                    text_uri=text_uri,
                    old_text_uri="https://oops.math.spbu.ru/SE/diploma/2020/" + old_text_uri,
                    presentation_uri=presentation_uri,
                    supervisor_review_uri=supervisor_review_uri,
                    reviewer_review_uri=reviewer_review_uri,
                    author=author,
                    supervisor_id=supervisor_id,
                    reviewer_id=2,
                    publish_year=2020,
                    type_id=3,
                    course_id=2,
                )

            db.session.add(t)
            db.session.commit()


# Get
# https://oops.math.spbu.ru/SE/diploma/2019/vypusknye-kvalifikacionnye-raboty
# РџСЂРѕРіСЂР°РјРјРЅР°СЏ РёРЅР¶РµРЅРµСЂРёСЏ


def get_2019_09_03_04():
    session = requests.session()
    url = "https://oops.math.spbu.ru/SE/diploma/2019/vypusknye-kvalifikacionnye-raboty"
    base_url = "https://oops.math.spbu.ru/SE/diploma/2019/"
    code = "09.03.04"

    print(url)
    response = session.get(url)

    if response.status_code != 200:
        print("Response statun != 200, error.")
        sys.exit(0)

    soup = BeautifulSoup(response.text, "lxml")

    # Find header
    header = soup.find_all(string=re.compile(code))

    # Find table
    table = header[0].find_next("table")

    for row in table.findAll("tr"):
        cols = row.find_all("td")

        # Check if we have data row
        # 8 cols
        if len(cols) == 8:
            author = cols[0].text
            author_en = translit(author, "ru", reversed=True)
            author_en = author_en.replace(" ", "_")
            name_ru = cols[1].text
            supervisor = cols[2].text
            supervisor_id = 1
            cols[3].text
            old_text_uri = ""
            text_uri = ""
            presentation_uri = ""
            supervisor_review_uri = ""
            reviewer_review_uri = ""
            source_uri = ""
            year = 2019

            print("Add " + name_ru)

            if cols[4].find("a"):
                old_text_uri = cols[4].find("a").get("href")
                path = urlparse(old_text_uri).path
                extension = splitext(path)[1]
                filename = author_en + "_Bachelor_Thesis_" + str(year) + "_text" + extension
                text_uri = filename
                download_file(base_url + old_text_uri, filename, "static/tmp/texts/")
            else:
                text_uri = ""

            if cols[5].find("a"):
                presentation_uri_d = cols[5].find("a").get("href")
                path = urlparse(presentation_uri_d).path
                extension = splitext(path)[1]
                filename = author_en + "_Bachelor_Thesis_" + str(year) + "_slides" + extension
                presentation_uri = filename
                download_file(base_url + presentation_uri_d, filename, "static/tmp/slides/")
            else:
                presentation_uri = ""

            if cols[6].find("a"):
                supervisor_review_uri_d = cols[6].find("a").get("href")
                path = urlparse(supervisor_review_uri_d).path
                extension = splitext(path)[1]
                filename = (
                    author_en + "_Bachelor_Thesis_" + str(year) + "_supervisor_review" + extension
                )
                supervisor_review_uri = filename
                download_file(base_url + supervisor_review_uri_d, filename, "static/tmp/reviews/")
            else:
                supervisor_review_uri = ""

            if cols[7].find("a"):
                reviewer_review_uri_d = cols[7].find("a").get("href")
                path = urlparse(reviewer_review_uri_d).path
                extension = splitext(path)[1]
                filename = (
                    author_en + "_Bachelor_Thesis_" + str(year) + "_reviewer_review" + extension
                )
                reviewer_review_uri = filename
                download_file(base_url + reviewer_review_uri_d, filename, "static/tmp/reviews/")
            else:
                reviewer_review_uri = ""

            # Try to get supervisor_id
            last_name = supervisor.split()[0]
            q = Users.query.filter_by(last_name=last_name).first()
            if q:
                r = Staff.query.filter_by(user_id=q.id).first()
                supervisor_id = r.id
            else:
                print("Error, no " + supervisor)
                sys.exit(1)

            if source_uri:
                t = Thesis(
                    name_ru=name_ru,
                    text_uri=text_uri,
                    old_text_uri=base_url + old_text_uri,
                    presentation_uri=presentation_uri,
                    supervisor_review_uri=supervisor_review_uri,
                    reviewer_review_uri=reviewer_review_uri,
                    author=author,
                    supervisor_id=supervisor_id,
                    reviewer_id=2,
                    publish_year=year,
                    type_id=3,
                    course_id=2,
                    source_uri=source_uri,
                )
            else:
                t = Thesis(
                    name_ru=name_ru,
                    text_uri=text_uri,
                    old_text_uri=base_url + old_text_uri,
                    presentation_uri=presentation_uri,
                    supervisor_review_uri=supervisor_review_uri,
                    reviewer_review_uri=reviewer_review_uri,
                    author=author,
                    supervisor_id=supervisor_id,
                    reviewer_id=2,
                    publish_year=year,
                    type_id=3,
                    course_id=2,
                )

            db.session.add(t)
            db.session.commit()


# Get
# https://oops.math.spbu.ru/SE/diploma/2019/vypusknye-kvalifikacionnye-raboty
# РџСЂРѕРіСЂР°РјРјРЅР°СЏ РёРЅР¶РµРЅРµСЂРёСЏ


def get_2019_02_03_03():
    session = requests.session()
    url = "https://oops.math.spbu.ru/SE/diploma/2019/vypusknye-kvalifikacionnye-raboty"
    base_url = "https://oops.math.spbu.ru/SE/diploma/2019/"
    code = "02.03.03"

    print(url)
    response = session.get(url)

    if response.status_code != 200:
        print("Response statun != 200, error.")
        sys.exit(0)

    soup = BeautifulSoup(response.text, "lxml")

    # Find header
    header = soup.find_all(string=re.compile(code))

    # Find table
    table = header[0].find_next("table")

    for row in table.findAll("tr"):
        cols = row.find_all("td")

        # Check if we have data row
        # 9 cols
        if len(cols) == 9:
            author = cols[0].text
            author_en = translit(author, "ru", reversed=True)
            author_en = author_en.replace(" ", "_")
            name_ru = cols[1].text
            supervisor = cols[2].text
            supervisor_id = 1
            cols[3].text
            old_text_uri = ""
            text_uri = ""
            presentation_uri = ""
            supervisor_review_uri = ""
            reviewer_review_uri = ""
            source_uri = ""
            pablish_year = 2019

            print("Add " + name_ru)

            if cols[4].find("a"):
                old_text_uri = cols[4].find("a").get("href")
                path = urlparse(old_text_uri).path
                extension = splitext(path)[1]
                filename = author_en + "_Bachelor_Thesis_2019_text" + extension
                text_uri = filename
                download_file(base_url + old_text_uri, filename, "static/tmp/texts/")
            else:
                text_uri = ""

            if cols[5].find("a"):
                presentation_uri_d = cols[5].find("a").get("href")
                path = urlparse(presentation_uri_d).path
                extension = splitext(path)[1]
                filename = author_en + "_Bachelor_Thesis_2019_slides" + extension
                presentation_uri = filename
                download_file(base_url + presentation_uri_d, filename, "static/tmp/slides/")
            else:
                presentation_uri = ""

            if cols[6].find("a"):
                supervisor_review_uri_d = cols[6].find("a").get("href")
                path = urlparse(supervisor_review_uri_d).path
                extension = splitext(path)[1]
                filename = author_en + "_Bachelor_Thesis_2019_supervisor_review" + extension
                supervisor_review_uri = filename
                download_file(base_url + supervisor_review_uri_d, filename, "static/tmp/reviews/")
            else:
                supervisor_review_uri = ""

            if cols[7].find("a"):
                reviewer_review_uri_d = cols[7].find("a").get("href")
                path = urlparse(reviewer_review_uri_d).path
                extension = splitext(path)[1]
                filename = author_en + "_Bachelor_Thesis_2019_reviewer_review" + extension
                reviewer_review_uri = filename
                download_file(base_url + reviewer_review_uri_d, filename, "static/tmp/reviews/")
            else:
                reviewer_review_uri = ""

            source_uri = cols[8].find("a").get("href") if cols[8].find("a") else ""

            # Try to get supervisor_id
            if supervisor.find("РҐР°РЅРѕРІ") != -1:
                last_name = "РҐР°РЅРѕРІ"
            else:
                m = re.search(r"([\w]{7,16})", supervisor)
                last_name = m.group(1) if m else "РўРµСЂРµС…РѕРІ"

            q = Users.query.filter_by(last_name=last_name).first()
            if q:
                r = Staff.query.filter_by(user_id=q.id).first()
                supervisor_id = r.id
            else:
                print("Error, no " + supervisor)
                sys.exit(1)

            if source_uri:
                t = Thesis(
                    name_ru=name_ru,
                    text_uri=text_uri,
                    old_text_uri=base_url + old_text_uri,
                    presentation_uri=presentation_uri,
                    supervisor_review_uri=supervisor_review_uri,
                    reviewer_review_uri=reviewer_review_uri,
                    author=author,
                    supervisor_id=supervisor_id,
                    reviewer_id=2,
                    publish_year=pablish_year,
                    type_id=3,
                    course_id=1,
                    source_uri=source_uri,
                )
            else:
                t = Thesis(
                    name_ru=name_ru,
                    text_uri=text_uri,
                    old_text_uri=base_url + old_text_uri,
                    presentation_uri=presentation_uri,
                    supervisor_review_uri=supervisor_review_uri,
                    reviewer_review_uri=reviewer_review_uri,
                    author=author,
                    supervisor_id=supervisor_id,
                    reviewer_id=2,
                    publish_year=pablish_year,
                    type_id=3,
                    course_id=1,
                )

            db.session.add(t)
            db.session.commit()


# Get
# https://oops.math.spbu.ru/SE/diploma/2019/vypusknye-kvalifikacionnye-raboty
# РњР°С‚РµРјР°С‚РёС‡РµСЃРєРѕРµ РѕР±РµСЃРїРµС‡РµРЅРёРµ Рё Р°РґРјРёРЅРёСЃС‚СЂРёСЂРѕРІР°РЅРёРµ РёРЅС„РѕСЂРјР°С†РёРѕРЅРЅС‹С… СЃРёСЃС‚РµРј (02.04.03)


def get_2019_02_04_03():
    session = requests.session()
    url = "https://oops.math.spbu.ru/SE/diploma/2019/vypusknye-kvalifikacionnye-raboty"
    base_url = "https://oops.math.spbu.ru/SE/diploma/2019/"
    code = "02.04.03"

    print(url)
    response = session.get(url)

    if response.status_code != 200:
        print("Response statun != 200, error.")
        sys.exit(0)

    soup = BeautifulSoup(response.text, "lxml")

    # Find header
    header = soup.find_all(string=re.compile(code))

    # Find table
    table = header[0].find_next("table")

    for row in table.findAll("tr"):
        cols = row.find_all("td")

        # Check if we have data row
        # 7 cols
        if len(cols) == 7:
            author = cols[0].text
            author_en = translit(author, "ru", reversed=True)
            author_en = author_en.replace(" ", "_")
            name_ru = cols[1].text
            supervisor = cols[5].text
            supervisor_id = 1
            old_text_uri = ""
            text_uri = ""
            presentation_uri = ""
            supervisor_review_uri = ""
            reviewer_review_uri = ""
            source_uri = ""
            pablish_year = 2019

            print("Add " + name_ru)

            if cols[2].find("a"):
                old_text_uri = cols[2].find("a").get("href")
                path = urlparse(old_text_uri).path
                extension = splitext(path)[1]
                filename = author_en + "_Master_Thesis_2019_text" + extension
                text_uri = filename
                download_file(base_url + old_text_uri, filename, "static/tmp/texts/")
            else:
                text_uri = ""

            if cols[3].find("a"):
                presentation_uri_d = cols[3].find("a").get("href")
                path = urlparse(presentation_uri_d).path
                extension = splitext(path)[1]
                filename = author_en + "_Master_Thesis_2019_slides" + extension
                presentation_uri = filename
                download_file(base_url + presentation_uri_d, filename, "static/tmp/slides/")
            else:
                presentation_uri = ""

            if cols[5].find("a"):
                supervisor_review_uri_d = cols[5].find("a").get("href")
                path = urlparse(supervisor_review_uri_d).path
                extension = splitext(path)[1]
                filename = author_en + "_Master_Thesis_2019_supervisor_review" + extension
                supervisor_review_uri = filename
                download_file(base_url + supervisor_review_uri_d, filename, "static/tmp/reviews/")
            else:
                supervisor_review_uri = ""

            if cols[6].find("a"):
                reviewer_review_uri_d = cols[6].find("a").get("href")
                path = urlparse(reviewer_review_uri_d).path
                extension = splitext(path)[1]
                filename = author_en + "_Master_Thesis_2019_reviewer_review" + extension
                reviewer_review_uri = filename
                download_file(base_url + reviewer_review_uri_d, filename, "static/tmp/reviews/")
            else:
                reviewer_review_uri = ""

            source_uri = cols[4].find("a").get("href") if cols[4].find("a") else ""

            # Try to get supervisor_id
            m = re.search(r"([\w]{5,16})", supervisor)
            last_name = m.group(1) if m else "РўРµСЂРµС…РѕРІ"

            q = Users.query.filter_by(last_name=last_name).first()
            if q:
                r = Staff.query.filter_by(user_id=q.id).first()
                supervisor_id = r.id
            else:
                print("Error, no " + supervisor)
                sys.exit(1)

            if source_uri:
                t = Thesis(
                    name_ru=name_ru,
                    text_uri=text_uri,
                    old_text_uri=base_url + old_text_uri,
                    presentation_uri=presentation_uri,
                    supervisor_review_uri=supervisor_review_uri,
                    reviewer_review_uri=reviewer_review_uri,
                    author=author,
                    supervisor_id=supervisor_id,
                    reviewer_id=2,
                    publish_year=pablish_year,
                    type_id=4,
                    course_id=3,
                    source_uri=source_uri,
                )
            else:
                t = Thesis(
                    name_ru=name_ru,
                    text_uri=text_uri,
                    old_text_uri=base_url + old_text_uri,
                    presentation_uri=presentation_uri,
                    supervisor_review_uri=supervisor_review_uri,
                    reviewer_review_uri=reviewer_review_uri,
                    author=author,
                    supervisor_id=supervisor_id,
                    reviewer_id=2,
                    publish_year=pablish_year,
                    type_id=4,
                    course_id=3,
                )

            db.session.add(t)
            db.session.commit()


# Get
# https://oops.math.spbu.ru/SE/YearlyProjects/vesna-2020
# Р‘Р°РєР°Р»Р°РІСЂС‹, 371 РіСЂСѓРїРїР° (02.04.03)


def get_2020_371():
    session = requests.session()
    url = "https://oops.math.spbu.ru/SE/YearlyProjects/vesna-2020"
    base_url = "https://oops.math.spbu.ru/SE/YearlyProjects/vesna-2020/"
    code = "371"

    print(url)
    response = session.get(url)

    if response.status_code != 200:
        print("Response statun != 200, error.")
        sys.exit(0)

    soup = BeautifulSoup(response.text, "lxml")

    # Find header
    header = soup.find_all(string=re.compile(code))

    # Find table
    table = header[0].find_next("table")

    for row in table.findAll("tr"):
        cols = row.find_all("td")

        # Check if we have data row
        # 5 cols
        if len(cols) == 5:
            author = cols[0].text
            author_en = translit(author, "ru", reversed=True)
            author_en = author_en.replace(" ", "_")
            name_ru = cols[1].text
            supervisor = cols[2].text
            supervisor_id = 1
            old_text_uri = None
            text_uri = None
            presentation_uri = None
            supervisor_review_uri = None
            reviewer_review_uri = None
            source_uri = None
            pablish_year = 2020

            print("Add " + name_ru)

            data = cols[4].find_all("a")

            if len(data) > 0:
                old_text_uri = data[0].get("href")
                path = urlparse(old_text_uri).path
                extension = splitext(path)[1]
                filename = author_en + "_Bachelor_Report_2020_text" + extension
                text_uri = filename
                download_file(base_url + old_text_uri, filename, "static/tmp/texts/")
            else:
                text_uri = None

            if len(data) > 1:
                presentation_uri_d = data[1].get("href")
                path = urlparse(presentation_uri_d).path
                extension = splitext(path)[1]
                filename = author_en + "_Bachelor_Report_2020_slides" + extension
                presentation_uri = filename
                download_file(base_url + presentation_uri_d, filename, "static/tmp/slides/")
            else:
                presentation_uri = None

            if len(data) > 2:
                supervisor_review_uri_d = data[2].get("href")
                path = urlparse(supervisor_review_uri_d).path
                extension = splitext(path)[1]
                filename = author_en + "_Bachelor_Report_2020_supervisor_review" + extension
                supervisor_review_uri = filename
                download_file(base_url + supervisor_review_uri_d, filename, "static/tmp/reviews/")
            else:
                supervisor_review_uri = None

            source_uri = data[3].get("href") if len(data) > 3 else None

            last_name = supervisor.split()[-3]

            q = Users.query.filter_by(last_name=last_name).first()
            if q:
                r = Staff.query.filter_by(user_id=q.id).first()
                supervisor_id = r.id
            else:
                print("Error, no " + supervisor)
                sys.exit(1)

            if source_uri:
                t = Thesis(
                    name_ru=name_ru,
                    text_uri=text_uri,
                    old_text_uri=base_url + old_text_uri,
                    presentation_uri=presentation_uri,
                    supervisor_review_uri=supervisor_review_uri,
                    reviewer_review_uri=reviewer_review_uri,
                    author=author,
                    supervisor_id=supervisor_id,
                    reviewer_id=2,
                    publish_year=pablish_year,
                    type_id=2,
                    course_id=2,
                    source_uri=source_uri,
                )
            else:
                t = Thesis(
                    name_ru=name_ru,
                    text_uri=text_uri,
                    old_text_uri=base_url + old_text_uri,
                    presentation_uri=presentation_uri,
                    supervisor_review_uri=supervisor_review_uri,
                    reviewer_review_uri=reviewer_review_uri,
                    author=author,
                    supervisor_id=supervisor_id,
                    reviewer_id=2,
                    publish_year=pablish_year,
                    type_id=2,
                    course_id=2,
                )

            db.session.add(t)
            db.session.commit()


# Get
# https://oops.math.spbu.ru/SE/YearlyProjects/vesna-2020
# РњР°С‚РµРјР°С‚РёС‡РµСЃРєРѕРµ РѕР±РµСЃРїРµС‡РµРЅРёРµ Рё Р°РґРјРёРЅРёСЃС‚СЂРёСЂРѕРІР°РЅРёРµ РёРЅС„РѕСЂРјР°С†РёРѕРЅРЅС‹С… СЃРёСЃС‚РµРј


def get_report_2020_02_03_03():
    session = requests.session()
    url = "https://oops.math.spbu.ru/SE/YearlyProjects/vesna-2020"
    base_url = "https://oops.math.spbu.ru/SE/YearlyProjects/vesna-2020/"
    code = "02.03.03"

    print(url)
    response = session.get(url)

    if response.status_code != 200:
        print("Response statun != 200, error.")
        sys.exit(0)

    soup = BeautifulSoup(response.text, "lxml")

    # Find header
    header = soup.find_all(string=re.compile(code))

    # Find table
    table = header[0].find_next("table")

    for row in table.findAll("tr"):
        cols = row.find_all("td")

        # Check if we have data row
        if len(cols) == 9:
            author = cols[0].text
            author_en = translit(author, "ru", reversed=True)
            author_en = author_en.replace(" ", "_")
            name_ru = cols[1].text
            supervisor = cols[2].text
            supervisor_id = 1
            cols[3].text
            old_text_uri = None
            text_uri = None
            presentation_uri = None
            supervisor_review_uri = None
            reviewer_review_uri = None
            source_uri = None
            publish_year = 2020

            print("Add " + name_ru)

            if cols[4].find("a"):
                old_text_uri = cols[4].find("a").get("href")
                path = urlparse(old_text_uri).path
                extension = splitext(path)[1]
                filename = author_en + "_Bachelor_Report_2020_text" + extension
                text_uri = filename
                download_file(base_url + old_text_uri, filename, "static/tmp/texts/")

            if cols[5].find("a"):
                presentation_uri_d = cols[5].find("a").get("href")
                path = urlparse(presentation_uri_d).path
                extension = splitext(path)[1]
                filename = author_en + "_Bachelor_Report_2020_slides" + extension
                presentation_uri = filename
                download_file(base_url + presentation_uri_d, filename, "static/tmp/slides/")

            if cols[6].find("a"):
                supervisor_review_uri_d = cols[6].find("a").get("href")
                path = urlparse(supervisor_review_uri_d).path
                extension = splitext(path)[1]
                filename = author_en + "_Bachelor_Report_2020_supervisor_review" + extension
                supervisor_review_uri = filename
                download_file(base_url + supervisor_review_uri_d, filename, "static/tmp/reviews/")

            if cols[7].find("a"):
                reviewer_review_uri_d = cols[7].find("a").get("href")
                path = urlparse(reviewer_review_uri_d).path
                extension = splitext(path)[1]
                filename = author_en + "_Bachelor_Report_2020_reviewer_review" + extension
                reviewer_review_uri = filename
                download_file(base_url + reviewer_review_uri_d, filename, "static/tmp/reviews/")

            if cols[8].find("a"):
                source_uri = cols[8].find("a").get("href")

            # Try to get supervisor_id

            last_name = (
                "РЎР°РіСѓРЅРѕРІ"
                if supervisor.find("РЎР°РіСѓРЅРѕРІ") != -1
                else supervisor.split()[-1]
            )

            q = Users.query.filter_by(last_name=last_name).first()
            if q:
                r = Staff.query.filter_by(user_id=q.id).first()
                supervisor_id = r.id
            else:
                print("Error, no " + supervisor)
                sys.exit(1)

            if source_uri:
                t = Thesis(
                    name_ru=name_ru,
                    text_uri=text_uri,
                    old_text_uri=base_url + old_text_uri,
                    presentation_uri=presentation_uri,
                    supervisor_review_uri=supervisor_review_uri,
                    reviewer_review_uri=reviewer_review_uri,
                    author=author,
                    supervisor_id=supervisor_id,
                    reviewer_id=2,
                    publish_year=publish_year,
                    type_id=2,
                    course_id=1,
                    source_uri=source_uri,
                )
            else:
                t = Thesis(
                    name_ru=name_ru,
                    text_uri=text_uri,
                    old_text_uri=base_url + old_text_uri,
                    presentation_uri=presentation_uri,
                    supervisor_review_uri=supervisor_review_uri,
                    reviewer_review_uri=reviewer_review_uri,
                    author=author,
                    supervisor_id=supervisor_id,
                    reviewer_id=2,
                    publish_year=publish_year,
                    type_id=2,
                    course_id=1,
                )

            db.session.add(t)
            db.session.commit()


# Get
# https://oops.math.spbu.ru/SE/YearlyProjects/spring-2019
# Р‘Р°РєР°Р»Р°РІСЂС‹, 371 РіСЂСѓРїРїР°


def get_2019_371():
    session = requests.session()
    url = "https://oops.math.spbu.ru/SE/YearlyProjects/spring-2019"
    base_url = "https://oops.math.spbu.ru/SE/YearlyProjects/spring-2019/"
    code = "371"

    print(url)
    response = session.get(url)

    if response.status_code != 200:
        print("Response statun != 200, error.")
        sys.exit(0)

    soup = BeautifulSoup(response.text, "lxml")

    # Find header
    header = soup.find_all(string=re.compile(code))

    # Find table
    table = header[0].find_next("table")

    for row in table.findAll("tr"):
        cols = row.find_all("td")

        # Check if we have data row
        # 4 cols
        if len(cols) == 4:
            author = cols[0].text
            author_en = translit(author, "ru", reversed=True)
            author_en = author_en.replace(" ", "_")
            name_ru = cols[1].text
            supervisor = cols[2].text
            supervisor_id = 1
            old_text_uri = None
            text_uri = None
            presentation_uri = None
            supervisor_review_uri = None
            reviewer_review_uri = None
            pablish_year = 2019

            print("Add " + name_ru)

            data = cols[3].find_all("a")

            if len(data) > 0:
                old_text_uri = data[0].get("href")
                path = urlparse(old_text_uri).path
                extension = splitext(path)[1]
                filename = author_en + "_Bachelor_Report_2019_text" + extension
                text_uri = filename
                download_file(base_url + old_text_uri, filename, "static/tmp/texts/")

            if len(data) > 1:
                presentation_uri_d = data[1].get("href")
                path = urlparse(presentation_uri_d).path
                extension = splitext(path)[1]
                filename = author_en + "_Bachelor_Report_2019_slides" + extension
                presentation_uri = filename
                download_file(base_url + presentation_uri_d, filename, "static/tmp/slides/")

            if len(data) > 2:
                supervisor_review_uri_d = data[2].get("href")
                path = urlparse(supervisor_review_uri_d).path
                extension = splitext(path)[1]
                filename = author_en + "_Bachelor_Report_2019_supervisor_review" + extension
                supervisor_review_uri = filename
                download_file(base_url + supervisor_review_uri_d, filename, "static/tmp/reviews/")

            last_name = supervisor.split()[0]

            q = Users.query.filter_by(last_name=last_name).first()
            if q:
                r = Staff.query.filter_by(user_id=q.id).first()
                supervisor_id = r.id
            else:
                print("Error, no " + supervisor)
                sys.exit(1)

            t = Thesis(
                name_ru=name_ru,
                text_uri=text_uri,
                old_text_uri=base_url + old_text_uri,
                presentation_uri=presentation_uri,
                supervisor_review_uri=supervisor_review_uri,
                reviewer_review_uri=reviewer_review_uri,
                author=author,
                supervisor_id=supervisor_id,
                reviewer_id=2,
                publish_year=pablish_year,
                type_id=2,
                course_id=2,
            )

            db.session.add(t)
            db.session.commit()


# Get
# https://oops.math.spbu.ru/SE/YearlyProjects/spring-2019
# Р‘Р°РєР°Р»Р°РІСЂС‹, 343 РіСЂСѓРїРїР°


def get_2019_343():
    session = requests.session()
    url = "https://oops.math.spbu.ru/SE/YearlyProjects/spring-2019"
    base_url = "https://oops.math.spbu.ru/SE/YearlyProjects/spring-2019/"
    code = "343"

    print(url)
    response = session.get(url)

    if response.status_code != 200:
        print("Response statun != 200, error.")
        sys.exit(0)

    soup = BeautifulSoup(response.text, "lxml")

    # Find header
    header = soup.find_all(string=re.compile(code))

    # Find table
    table = header[0].find_next("table")

    for row in table.findAll("tr"):
        cols = row.find_all("td")

        # Check if we have data row
        # 4 cols
        if len(cols) == 4:
            author = cols[0].text
            author_en = translit(author, "ru", reversed=True)
            author_en = author_en.replace(" ", "_")
            name_ru = cols[1].text
            supervisor = cols[2].text
            supervisor_id = 1
            old_text_uri = None
            text_uri = None
            presentation_uri = None
            supervisor_review_uri = None
            reviewer_review_uri = None
            pablish_year = 2019

            print("Add " + name_ru)

            data = cols[3].find_all("a")

            if len(data) > 0:
                old_text_uri = data[0].get("href")
                path = urlparse(old_text_uri).path
                extension = splitext(path)[1]
                filename = author_en + "_Bachelor_Report_2019_text" + extension
                text_uri = filename
                download_file(base_url + old_text_uri, filename, "static/tmp/texts/")

            if len(data) > 1:
                presentation_uri_d = data[1].get("href")
                path = urlparse(presentation_uri_d).path
                extension = splitext(path)[1]
                filename = author_en + "_Bachelor_Report_2019_slides" + extension
                presentation_uri = filename
                download_file(base_url + presentation_uri_d, filename, "static/tmp/slides/")

            if len(data) > 2:
                supervisor_review_uri_d = data[2].get("href")
                path = urlparse(supervisor_review_uri_d).path
                extension = splitext(path)[1]
                filename = author_en + "_Bachelor_Report_2019_supervisor_review" + extension
                supervisor_review_uri = filename
                download_file(base_url + supervisor_review_uri_d, filename, "static/tmp/reviews/")

            last_name = supervisor.split()[-1]

            q = Users.query.filter_by(last_name=last_name).first()
            if q:
                r = Staff.query.filter_by(user_id=q.id).first()
                supervisor_id = r.id
            else:
                print("Error, no " + supervisor)
                sys.exit(1)

            t = Thesis(
                name_ru=name_ru,
                text_uri=text_uri,
                old_text_uri=base_url + old_text_uri,
                presentation_uri=presentation_uri,
                supervisor_review_uri=supervisor_review_uri,
                reviewer_review_uri=reviewer_review_uri,
                author=author,
                supervisor_id=supervisor_id,
                reviewer_id=2,
                publish_year=pablish_year,
                type_id=2,
                course_id=5,
            )

            db.session.add(t)
            db.session.commit()


# Get
# https://oops.math.spbu.ru/SE/YearlyProjects/spring-2019
# Р‘Р°РєР°Р»Р°РІСЂС‹, 344 РіСЂСѓРїРїР°


def get_2019_344():
    session = requests.session()
    url = "https://oops.math.spbu.ru/SE/YearlyProjects/spring-2019"
    base_url = "https://oops.math.spbu.ru/SE/YearlyProjects/spring-2019/"
    code = "344"

    print(url)
    response = session.get(url)

    if response.status_code != 200:
        print("Response statun != 200, error.")
        sys.exit(0)

    soup = BeautifulSoup(response.text, "lxml")

    # Find header
    header = soup.find_all(string=re.compile(code))

    # Find table
    table = header[0].find_next("table")

    for row in table.findAll("tr"):
        cols = row.find_all("td")

        # Check if we have data row
        # 4 cols
        if len(cols) == 4:
            author = cols[0].text
            author_en = translit(author, "ru", reversed=True)
            author_en = author_en.replace(" ", "_")
            name_ru = cols[1].text
            supervisor = cols[2].text
            supervisor_id = 1
            old_text_uri = None
            text_uri = None
            presentation_uri = None
            supervisor_review_uri = None
            reviewer_review_uri = None
            pablish_year = 2019

            print("Add " + name_ru)

            data = cols[3].find_all("a")

            if len(data) > 0:
                old_text_uri = data[0].get("href")
                path = urlparse(old_text_uri).path
                extension = splitext(path)[1]
                filename = author_en + "_Bachelor_Report_2019_text" + extension
                text_uri = filename
                download_file(base_url + old_text_uri, filename, "static/tmp/texts/")

            if len(data) > 1:
                presentation_uri_d = data[1].get("href")
                path = urlparse(presentation_uri_d).path
                extension = splitext(path)[1]
                filename = author_en + "_Bachelor_Report_2019_slides" + extension
                presentation_uri = filename
                download_file(base_url + presentation_uri_d, filename, "static/tmp/slides/")

            if len(data) > 2:
                supervisor_review_uri_d = data[2].get("href")
                path = urlparse(supervisor_review_uri_d).path
                extension = splitext(path)[1]
                filename = author_en + "_Bachelor_Report_2019_supervisor_review" + extension
                supervisor_review_uri = filename
                download_file(base_url + supervisor_review_uri_d, filename, "static/tmp/reviews/")

            last_name = supervisor.split()[-1]

            q = Users.query.filter_by(last_name=last_name).first()
            if q:
                r = Staff.query.filter_by(user_id=q.id).first()
                supervisor_id = r.id
            else:
                print("Error, no " + supervisor)
                sys.exit(1)

            t = Thesis(
                name_ru=name_ru,
                text_uri=text_uri,
                old_text_uri=base_url + old_text_uri,
                presentation_uri=presentation_uri,
                supervisor_review_uri=supervisor_review_uri,
                reviewer_review_uri=reviewer_review_uri,
                author=author,
                supervisor_id=supervisor_id,
                reviewer_id=2,
                publish_year=pablish_year,
                type_id=2,
                course_id=6,
            )

            db.session.add(t)
            db.session.commit()


# Add master thesis 2020
# РџР Рё РњРћ


def add_master_thesis_2020():
    thesis = [
        {
            "name_ru": "РСЃРїРѕР»СЊР·РѕРІР°РЅРёРµ Р°РІС‚РѕРјР°С‚РѕРІ РІ РёРЅС‚РµСЂРїСЂРµС‚Р°С‚РѕСЂРµ MACASM",
            "text_uri": "_Master_Thesis_2020_text.pdf",
            "presentation_uri": "_Master_Thesis_2020_slides.pdf",
            "supervisor_review_uri": "_Master_Thesis_2020_supervisor_review.pdf",
            "reviewer_review_uri": "_Master_Thesis_2020_reviewer_review.pdf",
            "author": "РЎРѕРєРѕР»РѕРІР° РџРѕР»РёРЅР° РђР»РµРєСЃР°РЅРґСЂРѕРІРЅР°",
            "supervisor": "Р›СѓС†РёРІ",
            "publish_year": 2020,
            "type_id": 4,
            "course_id": 7,
        },
        {
            "name_ru": "РђРІС‚РѕРјР°С‚РёС‡РµСЃРєР°СЏ РєР°Р»РёР±СЂРѕРІРєР° РІРЅРµС€РЅРёС… РїР°СЂР°РјРµС‚СЂРѕРІ С€РёСЂРѕРєРѕСѓРіРѕР»СЊРЅС‹С… РєР°РјРµСЂ РІ Р°РІС‚РѕРјРѕР±РёР»СЊРЅС‹С… СЃРёСЃС‚РµРјР°С… РєСЂСѓРіРѕРІРѕРіРѕ РѕР±Р·РѕСЂР°",
            "text_uri": "_Master_Thesis_2020_text.pdf",
            "presentation_uri": "_Master_Thesis_2020_slides.pdf",
            "supervisor_review_uri": "_Master_Thesis_2020_supervisor_review.pdf",
            "reviewer_review_uri": "_Master_Thesis_2020_reviewer_review.pdf",
            "author": "РџРµС‚СЂРѕРІ РђР»РµРєСЃРµР№ РђРЅРґСЂРµРµРІРёС‡",
            "supervisor": "Р›СѓС†РёРІ",
            "publish_year": 2020,
            "type_id": 4,
            "course_id": 7,
        },
        {
            "name_ru": "Р­С„С„РµРєС‚РёРІРЅР°СЏ СЂР°Р·СЂРµС€Р°СЋС‰Р°СЏ РїСЂРѕС†РµРґСѓСЂР° РґР»СЏ Р·Р°РґР°С‡Рё РІС‹РїРѕР»РЅРёРјРѕСЃС‚Рё РІ С‚РµРѕСЂРёРё РЅРѕРјРёРЅР°Р»СЊРЅС‹С… СЃРёСЃС‚РµРј С‚РёРїРѕРІ СЃ РІР°СЂРёР°РЅС‚РЅРѕСЃС‚СЊСЋ",
            "text_uri": "_Master_Thesis_2020_text.pdf",
            "presentation_uri": "_Master_Thesis_2020_slides.pdf",
            "supervisor_review_uri": "_Master_Thesis_2020_supervisor_review.pdf",
            "reviewer_review_uri": "_Master_Thesis_2020_reviewer_review.pdf",
            "author": "РњРёР»РѕРІР° РќР°С‚Р°Р»СЊСЏ РђРЅРґСЂРµРµРІРЅР°",
            "supervisor": "РљРѕР·РЅРѕРІ",
            "publish_year": 2020,
            "type_id": 4,
            "course_id": 7,
        },
        {
            "name_ru": "Р’РµР±-РїР»Р°С‚С„РѕСЂРјР° РїСЂРµРґРјРµС‚РЅРѕ-РѕСЂРёРµРЅС‚РёСЂРѕРІР°РЅРЅРѕРіРѕ РјРѕРґРµР»РёСЂРѕРІР°РЅРёСЏ РЅР° Р±Р°Р·Рµ REAL.NET",
            "text_uri": "_Master_Thesis_2020_text.pdf",
            "presentation_uri": "_Master_Thesis_2020_slides.pdf",
            "supervisor_review_uri": "_Master_Thesis_2020_supervisor_review.pdf",
            "reviewer_review_uri": "_Master_Thesis_2020_reviewer_review.pdf",
            "author": "РљСѓР·СЊРјРёРЅР° Р•Р»РёР·Р°РІРµС‚Р° Р’Р»Р°РґРёРјРёСЂРѕРІРЅР°",
            "supervisor": "Р›РёС‚РІРёРЅРѕРІ",
            "publish_year": 2020,
            "type_id": 4,
            "course_id": 7,
        },
        {
            "name_ru": "РћС†РµРЅРєР° РїР°СЂР°РјРµС‚СЂРѕРІ СЃРёСЃС‚РµРј РєР°РјРµСЂ Р±РµР· РёСЃРїРѕР»СЊР·РѕРІР°РЅРёСЏ РєР°Р»РёР±СЂРѕРІРѕС‡РЅС‹С… РїР°С‚С‚РµСЂРЅРѕРІ",
            "text_uri": "_Master_Thesis_2020_text.pdf",
            "presentation_uri": "_Master_Thesis_2020_slides.pdf",
            "supervisor_review_uri": "_Master_Thesis_2020_supervisor_review.pdf",
            "reviewer_review_uri": "_Master_Thesis_2020_reviewer_review.pdf",
            "author": "РЎРёРЅРёС†С‹РЅ Р”Р°РЅРёРёР» Р”РјРёС‚СЂРёРµРІРёС‡",
            "supervisor": "РўРµСЂРµС…РѕРІ",
            "publish_year": 2020,
            "type_id": 4,
            "course_id": 3,
        },
        {
            "name_ru": "РЎРёРЅС‚РµР· РїСЂРѕРіСЂР°РјРј РїРѕ СЃРїРµС†РёС„РёРєР°С†РёСЏРј СЃ РјРЅРѕР¶РµСЃС‚РІРµРЅРЅС‹РјРё РІС‹Р·РѕРІР°РјРё",
            "text_uri": "_Master_Thesis_2020_text.pdf",
            "presentation_uri": "_Master_Thesis_2020_slides.pdf",
            "supervisor_review_uri": "_Master_Thesis_2020_supervisor_review.pdf",
            "reviewer_review_uri": "_Master_Thesis_2020_reviewer_review.pdf",
            "author": "РњРёС€РµРЅРµРІ Р’Р°РґРёРј РЎРµСЂРіРµРµРІРёС‡",
            "supervisor": "РљРѕР·РЅРѕРІ",
            "publish_year": 2020,
            "type_id": 4,
            "course_id": 3,
        },
        {
            "name_ru": "РЎРёСЃС‚РµРјР° РґР»СЏ СЂР°СЃС‡РµС‚Р° СЃРєРѕСЂРѕСЃС‚РµР№ Р·РІСѓРєР° РІ РѕСЃРѕР±С‹С… РѕР±Р»Р°СЃС‚СЏС… РїРѕ РґР°РЅРЅС‹Рј РЈР—РвЂ“С‚РѕРјРѕРіСЂР°С„РёРё",
            "text_uri": "_Master_Thesis_2020_text.pdf",
            "presentation_uri": "_Master_Thesis_2020_slides.pdf",
            "supervisor_review_uri": "_Master_Thesis_2020_supervisor_review.pdf",
            "reviewer_review_uri": "_Master_Thesis_2020_reviewer_review.pdf",
            "author": "Р›РµРѕРЅРѕРІР° РђРЅРЅР° Р’Р°СЃРёР»СЊРµРІРЅР°",
            "supervisor": "Р“СЂР°РЅРёС‡РёРЅ",
            "publish_year": 2020,
            "type_id": 4,
            "course_id": 3,
        },
        {
            "name_ru": "РџРѕРёСЃРє Рё РєР»Р°СЃС‚РµСЂРёР·Р°С†РёСЏ РЅРµС‡РµС‚РєРёС… РїРѕРІС‚РѕСЂРѕРІ РІ РґРѕРєСѓРјРµРЅС‚Р°С†РёРё РїСЂРѕРіСЂР°РјРјРЅРѕРіРѕ РѕР±РµСЃРїРµС‡РµРЅРёСЏ",
            "text_uri": "_Master_Thesis_2020_text.pdf",
            "presentation_uri": "_Master_Thesis_2020_slides.pdf",
            "supervisor_review_uri": "_Master_Thesis_2020_supervisor_review.pdf",
            "reviewer_review_uri": "_Master_Thesis_2020_reviewer_review.pdf",
            "author": "РљРѕРЅРѕРІР°Р»РѕРІР° РСЂРёРЅР° РњРёС…Р°Р№Р»РѕРІРЅР°",
            "supervisor": "Р›СѓС†РёРІ",
            "publish_year": 2020,
            "type_id": 4,
            "course_id": 3,
        },
        {
            "name_ru": "РђРЅР°Р»РёР· РєР°С‡РµСЃС‚РІР° Р°РІС‚РѕРґРѕРїРѕР»РЅРµРЅРёСЏ РєРѕРґР° РІ РёРЅС‚РµРіСЂРёСЂРѕРІР°РЅРЅС‹С… СЃСЂРµРґР°С… СЂР°Р·СЂР°Р±РѕС‚РєРё",
            "text_uri": "_Master_Thesis_2020_text.pdf",
            "presentation_uri": "_Master_Thesis_2020_slides.pdf",
            "supervisor_review_uri": "_Master_Thesis_2020_supervisor_review.pdf",
            "reviewer_review_uri": "_Master_Thesis_2020_reviewer_review.pdf",
            "author": "РљР°Р»РёРЅР° РђР»РµРєСЃРµР№ РРіРѕСЂРµРІРёС‡",
            "supervisor": "Р›СѓС†РёРІ",
            "publish_year": 2020,
            "type_id": 4,
            "course_id": 3,
        },
        {
            "name_ru": "РЎРёРЅС…СЂРѕРЅРёР·Р°С†РёСЏ РІ РјРЅРѕРіРѕРїРѕС‚РѕС‡РЅС‹С… РњРђРљ-РѕР±С„СѓСЃС†РёСЂРѕРІР°РЅРЅС‹С… РїСЂРѕРіСЂР°РјРјР°С…",
            "text_uri": "_Master_Thesis_2020_text.pdf",
            "presentation_uri": "_Master_Thesis_2020_slides.pdf",
            "supervisor_review_uri": "_Master_Thesis_2020_supervisor_review.pdf",
            "reviewer_review_uri": "_Master_Thesis_2020_reviewer_review.pdf",
            "author": "Р‘Р°Р±Р°РЅРѕРІ РџС‘С‚СЂ РђРЅРґСЂРµРµРІРёС‡",
            "supervisor": "Р‘СЂС‹РєСЃРёРЅ",
            "publish_year": 2020,
            "type_id": 4,
            "course_id": 3,
        },
    ]

    for t in thesis:
        author_en = translit(t["author"], "ru", reversed=True)
        author_en = author_en.replace(" ", "_")
        print(author_en + t["text_uri"])
        print(author_en + t["presentation_uri"])
        print(author_en + t["supervisor_review_uri"])
        print(author_en + t["reviewer_review_uri"])

        last_name = t["supervisor"]
        supervisor_id = 1

        q = Users.query.filter_by(last_name=last_name).first()
        if q:
            r = Staff.query.filter_by(user_id=q.id).first()
            supervisor_id = r.id
        else:
            print("Error, no " + t["supervisor"])
            sys.exit(1)

        tt = Thesis(
            name_ru=t["name_ru"],
            text_uri=author_en + t["text_uri"],
            presentation_uri=author_en + t["presentation_uri"],
            supervisor_review_uri=author_en + t["supervisor_review_uri"],
            reviewer_review_uri=author_en + t["reviewer_review_uri"],
            author=t["author"],
            supervisor_id=supervisor_id,
            reviewer_id=2,
            publish_year=t["publish_year"],
            type_id=t["type_id"],
            course_id=t["course_id"],
        )

        db.session.add(tt)
        db.session.commit()


# Get
# https://oops.math.spbu.ru/SE/YearlyProjects/vesna-2022/uchebnaya-praktika
# Р‘Р°РєР°Р»Р°РІСЂС‹, 271 РіСЂСѓРїРїР°


def get_2022_271():
    session = requests.session()
    url = "https://oops.math.spbu.ru/SE/YearlyProjects/vesna-2022/uchebnaya-praktika"
    base_url = "https://oops.math.spbu.ru/SE/YearlyProjects/vesna-2022/"
    code = "271"

    print(url)
    response = session.get(url)

    if response.status_code != 200:
        print("Response statun != 200, error.")
        sys.exit(0)

    soup = BeautifulSoup(response.text, "lxml")

    # Find header
    header = soup.find_all(string=re.compile(code))

    # Find table
    table = header[0].find_next("table")

    for row in table.findAll("tr"):
        cols = row.find_all("td")

        # Check if we have data row
        # 5 cols
        if len(cols) == 5:
            author = cols[0].text
            author_en = translit(author, "ru", reversed=True)
            author_en = author_en.replace(" ", "_")
            name_ru = cols[1].text
            supervisor = cols[2].text
            supervisor_id = 1
            old_text_uri = None
            text_uri = None
            presentation_uri = None
            supervisor_review_uri = None
            reviewer_review_uri = None
            pablish_year = 2022

            print("Add " + name_ru)

            data = cols[4].find_all("a")

            if len(data) > 0:
                old_text_uri = data[0].get("href")
                path = urlparse(old_text_uri).path
                extension = splitext(path)[1]
                filename = author_en + "_Bachelor_Report_2022_text" + extension
                text_uri = filename
                download_file(base_url + old_text_uri, filename, "static/tmp/texts/")

            if len(data) > 1:
                presentation_uri_d = data[1].get("href")
                path = urlparse(presentation_uri_d).path
                extension = splitext(path)[1]
                filename = author_en + "_Bachelor_Report_2022_slides" + extension
                presentation_uri = filename
                download_file(base_url + presentation_uri_d, filename, "static/tmp/slides/")

            if len(data) > 2:
                supervisor_review_uri_d = data[2].get("href")
                path = urlparse(supervisor_review_uri_d).path
                extension = splitext(path)[1]
                filename = author_en + "_Bachelor_Report_2022_supervisor_review" + extension
                supervisor_review_uri = filename
                download_file(base_url + supervisor_review_uri_d, filename, "static/tmp/reviews/")

            last_name = supervisor.split()[-3]

            # q = Users.query.filter_by(last_name=last_name).first()
            print(last_name)
            r = Staff.query.join(Staff.user).filter(Users.last_name == last_name).first()
            if r:
                supervisor_id = r.id
            else:
                print("Error, no " + supervisor)
                sys.exit(1)

            t = Thesis(
                name_ru=name_ru,
                text_uri=text_uri,
                old_text_uri=base_url + old_text_uri,
                presentation_uri=presentation_uri,
                supervisor_review_uri=supervisor_review_uri,
                reviewer_review_uri=reviewer_review_uri,
                author=author,
                supervisor_id=supervisor_id,
                reviewer_id=2,
                publish_year=pablish_year,
                type_id=5,
                course_id=2,
                temporary=True,
            )

            db.session.add(t)
            db.session.commit()


# Get
# https://oops.math.spbu.ru/SE/YearlyProjects/vesna-2022/proizvodstvennaya-praktika
# Р‘Р°РєР°Р»Р°РІСЂС‹, 371 РіСЂСѓРїРїР°


def get_2022_371():
    session = requests.session()
    url = "https://oops.math.spbu.ru/SE/YearlyProjects/vesna-2022/proizvodstvennaya-praktika"
    base_url = "https://oops.math.spbu.ru/SE/YearlyProjects/vesna-2022/"
    code = "371"

    print(url)
    response = session.get(url)

    if response.status_code != 200:
        print("Response statun != 200, error.")
        sys.exit(0)

    soup = BeautifulSoup(response.text, "lxml")

    # Find header
    header = soup.find_all(string=re.compile(code))

    # Find table
    table = header[0].find_next("table")

    for row in table.findAll("tr"):
        cols = row.find_all("td")

        # Check if we have data row
        # 5 cols
        if len(cols) == 5:
            author = cols[0].text
            author_en = translit(author, "ru", reversed=True)
            author_en = author_en.replace(" ", "_")
            name_ru = cols[1].text
            supervisor = cols[2].text
            supervisor_id = 1
            old_text_uri = None
            text_uri = None
            presentation_uri = None
            supervisor_review_uri = None
            reviewer_review_uri = None
            pablish_year = 2022

            print("Add " + name_ru)

            data = cols[4].find_all("a")

            # Skip РњРёР»РѕСЃРµСЂРґРѕРІР°
            if not author.find("РњРёР»РѕСЃРµСЂРґРѕРІР°"):
                print(author)
                continue

            if len(data) > 0:
                old_text_uri = data[0].get("href")
                path = urlparse(old_text_uri).path
                extension = splitext(path)[1]
                filename = author_en + "_Bachelor_Report_2022_text" + extension
                text_uri = filename
                download_file(base_url + old_text_uri, filename, "static/tmp/texts/")

            if len(data) > 1:
                presentation_uri_d = data[1].get("href")
                path = urlparse(presentation_uri_d).path
                extension = splitext(path)[1]
                filename = author_en + "_Bachelor_Report_2022_slides" + extension
                presentation_uri = filename
                download_file(base_url + presentation_uri_d, filename, "static/tmp/slides/")

            if len(data) > 2:
                supervisor_review_uri_d = data[2].get("href")
                path = urlparse(supervisor_review_uri_d).path
                extension = splitext(path)[1]
                filename = author_en + "_Bachelor_Report_2022_supervisor_review" + extension
                supervisor_review_uri = filename
                download_file(base_url + supervisor_review_uri_d, filename, "static/tmp/reviews/")

            last_name = supervisor.split()[-3]

            # q = Users.query.filter_by(last_name=last_name).first()
            print(last_name)
            r = Staff.query.join(Staff.user).filter(Users.last_name == last_name).first()
            if r:
                supervisor_id = r.id
            else:
                print("Error, no " + supervisor)
                sys.exit(1)

            t = Thesis(
                name_ru=name_ru,
                text_uri=text_uri,
                old_text_uri=base_url + old_text_uri,
                presentation_uri=presentation_uri,
                supervisor_review_uri=supervisor_review_uri,
                reviewer_review_uri=reviewer_review_uri,
                author=author,
                supervisor_id=supervisor_id,
                reviewer_id=2,
                publish_year=pablish_year,
                type_id=7,
                course_id=2,
                temporary=True,
            )

            db.session.add(t)
            db.session.commit()


# Get
# https://oops.math.spbu.ru/SE/diploma/2022/index
# РџСЂРѕРіСЂР°РјРјРЅР°СЏ РёРЅР¶РµРЅРµСЂРёСЏ


def get_2022_09_03_04():
    session = requests.session()
    url = "https://oops.math.spbu.ru/SE/diploma/2022/index"
    base_url = "https://oops.math.spbu.ru/SE/diploma/2022/"
    code = "09.03.04"

    print(url)
    response = session.get(url)

    if response.status_code != 200:
        print("Response statun != 200, error.")
        sys.exit(0)

    soup = BeautifulSoup(response.text, "lxml")

    # Find header
    header = soup.find_all(string=re.compile(code))

    # Find table
    table = header[0].find_next("table")

    for row in table.findAll("tr"):
        cols = row.find_all("td")

        # Check if we have data row
        # 9 cols
        if len(cols) == 10:
            author = cols[0].text
            author_en = translit(author, "ru", reversed=True)
            author_en = author_en.replace(" ", "_")
            name_ru = cols[1].text
            supervisor = cols[2].text
            supervisor_id = 1
            cols[3].text
            old_text_uri = ""
            text_uri = ""
            presentation_uri = ""
            supervisor_review_uri = ""
            reviewer_review_uri = ""
            source_uri = ""
            pablish_year = 2022

            print("Add " + name_ru)

            if cols[4].find("a"):
                old_text_uri = cols[5].find("a").get("href")
                path = urlparse(old_text_uri).path
                extension = splitext(path)[1]
                filename = author_en + "_Bachelor_Thesis_2019_text" + extension
                text_uri = filename
                download_file(base_url + old_text_uri, filename, "static/tmp/texts/")
            else:
                text_uri = ""

            if cols[5].find("a"):
                presentation_uri_d = cols[5].find("a").get("href")
                path = urlparse(presentation_uri_d).path
                extension = splitext(path)[1]
                filename = author_en + "_Bachelor_Thesis_2019_slides" + extension
                presentation_uri = filename
                download_file(base_url + presentation_uri_d, filename, "static/tmp/slides/")
            else:
                presentation_uri = ""

            if cols[6].find("a"):
                supervisor_review_uri_d = cols[6].find("a").get("href")
                path = urlparse(supervisor_review_uri_d).path
                extension = splitext(path)[1]
                filename = author_en + "_Bachelor_Thesis_2019_supervisor_review" + extension
                supervisor_review_uri = filename
                download_file(base_url + supervisor_review_uri_d, filename, "static/tmp/reviews/")
            else:
                supervisor_review_uri = ""

            if cols[7].find("a"):
                reviewer_review_uri_d = cols[7].find("a").get("href")
                path = urlparse(reviewer_review_uri_d).path
                extension = splitext(path)[1]
                filename = author_en + "_Bachelor_Thesis_2019_reviewer_review" + extension
                reviewer_review_uri = filename
                download_file(base_url + reviewer_review_uri_d, filename, "static/tmp/reviews/")
            else:
                reviewer_review_uri = ""

            source_uri = cols[8].find("a").get("href") if cols[8].find("a") else ""

            # Try to get supervisor_id
            if supervisor.find("РҐР°РЅРѕРІ") != -1:
                last_name = "РҐР°РЅРѕРІ"
            else:
                m = re.search(r"([\w]{7,16})", supervisor)
                last_name = m.group(1) if m else "РўРµСЂРµС…РѕРІ"

            q = Users.query.filter_by(last_name=last_name).first()
            if q:
                r = Staff.query.filter_by(user_id=q.id).first()
                supervisor_id = r.id
            else:
                print("Error, no " + supervisor)
                sys.exit(1)

            if source_uri:
                t = Thesis(
                    name_ru=name_ru,
                    text_uri=text_uri,
                    old_text_uri=base_url + old_text_uri,
                    presentation_uri=presentation_uri,
                    supervisor_review_uri=supervisor_review_uri,
                    reviewer_review_uri=reviewer_review_uri,
                    author=author,
                    supervisor_id=supervisor_id,
                    reviewer_id=2,
                    publish_year=pablish_year,
                    type_id=3,
                    course_id=1,
                    source_uri=source_uri,
                )
            else:
                t = Thesis(
                    name_ru=name_ru,
                    text_uri=text_uri,
                    old_text_uri=base_url + old_text_uri,
                    presentation_uri=presentation_uri,
                    supervisor_review_uri=supervisor_review_uri,
                    reviewer_review_uri=reviewer_review_uri,
                    author=author,
                    supervisor_id=supervisor_id,
                    reviewer_id=2,
                    publish_year=pablish_year,
                    type_id=3,
                    course_id=1,
                )

            db.session.add(t)
            db.session.commit()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "load":
        download = True

    # get_2020_02_03_03()
    # get_2020_09_03_04()
    # get_2019_09_03_04()
    # get_2019_02_03_03()
    # get_2019_02_04_03()
    # get_2020_371()
    # get_report_2020_02_03_03()
    # get_2019_371()
    # get_2019_343()
    # get_2019_344()
    # add_master_thesis_2020()

    get_2022_271()
    get_2022_371()

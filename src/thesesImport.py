#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import requests
from bs4 import BeautifulSoup
import re
from se_models import Thesis, Staff, Users, db
from flask_se import app
from transliterate import translit
import os
from os.path import splitext
from urllib.parse import urlparse

# Init Database
db.app = app
db.init_app(app)

# Download files?
download = False

def download_file(uri, safe_filename, save_path):

    # Skip if download == false
    if not download:
        return

    r = requests.get(uri, allow_redirects=True)
    print ("Download: " + str(uri))
    open(safe_filename, 'wb').write(r.content)
    os.rename(safe_filename, save_path + safe_filename)

# Get
# https://oops.math.spbu.ru/SE/diploma/2020/index
# Математическое обеспечение и администрирование информационных систем

def get_2020_02_03_03():

    session = requests.session()
    url = 'https://oops.math.spbu.ru/SE/diploma/2020/index'
    base_url = 'https://oops.math.spbu.ru/SE/diploma/2020/'
    course = 'Математическое обеспечение и администрирование информационных систем'
    code = '02.03.03'

    print (url)
    response = session.get(url)

    if response.status_code != 200:
        print("Response statun != 200, error.")
        sys.exit(0)

    soup = BeautifulSoup(response.text, "lxml")

    # Find header
    header = soup.find_all(string=re.compile(code))

    # Find table
    table = header[0].find_next('table')

    for row in table.findAll("tr"):
        cols = row.find_all('td')

        # Check if we have data row
        if (len(cols) == 9):
            author = cols[0].text
            author_en = translit(author, 'ru', reversed=True)
            author_en = author_en.replace(" ", "_")
            name_ru = cols[1].text
            supervisor = cols[2].text
            supervisor_id = 1
            consultant = cols[3].text
            old_text_uri = ''
            text_uri = ''
            presentation_uri = ''
            supervisor_review_uri = ''
            reviewer_review_uri = ''
            source_uri = ''

            print ("Add " + name_ru)

            if (cols[4].find('a')):
                old_text_uri = cols[4].find('a').get('href')
                path = urlparse(old_text_uri).path
                extension = splitext(path)[1]
                filename = author_en + '_Bachelor_Thesis_2020_text' + extension
                text_uri = filename
                download_file(base_url + old_text_uri, filename, "static/tmp/texts/")
            else:
                continue

            if (cols[5].find('a')):
                presentation_uri_d = cols[5].find('a').get('href')
                path = urlparse(presentation_uri_d).path
                extension = splitext(path)[1]
                filename = author_en + '_Bachelor_Thesis_2020_slides' + extension
                presentation_uri = filename
                download_file(base_url + presentation_uri_d, filename, "static/tmp/slides/")
            else:
                continue

            if (cols[6].find('a')):
                supervisor_review_uri_d = cols[6].find('a').get('href')
                path = urlparse(supervisor_review_uri_d).path
                extension = splitext(path)[1]
                filename = author_en + '_Bachelor_Thesis_2020_supervisor_review' + extension
                supervisor_review_uri = filename
                download_file(base_url + supervisor_review_uri_d, filename, "static/tmp/reviews/")
            else:
                continue

            if (cols[7].find('a')):
                reviewer_review_uri_d = cols[7].find('a').get('href')
                path = urlparse(reviewer_review_uri_d).path
                extension = splitext(path)[1]
                filename = author_en + '_Bachelor_Thesis_2020_reviewer_review' + extension
                reviewer_review_uri = filename
                download_file(base_url + reviewer_review_uri_d, filename, "static/tmp/reviews/")
            else:
                continue

            if (cols[8].find('a')):
                source_uri = cols[8].find('a').get('href')
            else:
                source_uri = ''

            # Try to get supervisor_id
            last_name = supervisor.split()[-1]
            q = Users.query.filter_by(last_name=last_name).first()
            if q:
                r = Staff.query.filter_by(user_id=q.id).first()
                supervisor_id = r.id
            else:
                print ("Error, no " + supervisor)
                sys.exit(1)

            if source_uri:
                t = Thesis(name_ru = name_ru, text_uri=text_uri, old_text_uri='https://oops.math.spbu.ru/SE/diploma/2020/' + old_text_uri, presentation_uri=presentation_uri,
                   supervisor_review_uri=supervisor_review_uri, reviewer_review_uri=reviewer_review_uri,
                   author=author, supervisor_id=supervisor_id, reviewer_id=2,
                   publish_year=2020, type_id=3, course_id = 1, source_uri = source_uri)
            else:
                t = Thesis(name_ru = name_ru, text_uri=text_uri, old_text_uri='https://oops.math.spbu.ru/SE/diploma/2020/' + old_text_uri, presentation_uri=presentation_uri,
                   supervisor_review_uri=supervisor_review_uri, reviewer_review_uri=reviewer_review_uri,
                   author=author, supervisor_id=supervisor_id, reviewer_id=2,
                   publish_year=2020, type_id=3, course_id = 1)


            db.session.add(t)
            db.session.commit()

# Get
# https://oops.math.spbu.ru/SE/diploma/2020/index
# Программная инженерия

def get_2020_09_03_04():

    session = requests.session()
    url = 'https://oops.math.spbu.ru/SE/diploma/2020/index'
    base_url = 'https://oops.math.spbu.ru/SE/diploma/2020/'
    course = 'Программная инженерия'
    code = '09.03.04'

    print (url)
    response = session.get(url)

    if response.status_code != 200:
        print("Response statun != 200, error.")
        sys.exit(0)

    soup = BeautifulSoup(response.text, "lxml")

    # Find header
    header = soup.find_all(string=re.compile(code))

    # Find table
    table = header[0].find_next('table')

    for row in table.findAll("tr"):
        cols = row.find_all('td')

        # Check if we have data row
        # 10 cols
        if (len(cols) == 10):
            author = cols[0].text
            author_en = translit(author, 'ru', reversed=True)
            author_en = author_en.replace(" ", "_")
            name_ru = cols[1].text
            supervisor = cols[2].text
            supervisor_id = 1
            consultant = cols[3].text
            old_text_uri = ''
            text_uri = ''
            presentation_uri = ''
            supervisor_review_uri = ''
            reviewer_review_uri = ''
            source_uri = ''

            print ("Add " + name_ru)

            if (cols[5].find('a')):
                old_text_uri = cols[5].find('a').get('href')
                path = urlparse(old_text_uri).path
                extension = splitext(path)[1]
                filename = author_en + '_Bachelor_Thesis_2020_text' + extension
                text_uri = filename
                download_file(base_url + old_text_uri, filename, "static/tmp/texts/")
            else:
                text_uri = ''

            if (cols[6].find('a')):
                presentation_uri_d = cols[6].find('a').get('href')
                path = urlparse(presentation_uri_d).path
                extension = splitext(path)[1]
                filename = author_en + '_Bachelor_Thesis_2020_slides' + extension
                presentation_uri = filename
                download_file(base_url + presentation_uri_d, filename, "static/tmp/slides/")
            else:
                presentation_uri = ''

            if (cols[7].find('a')):
                supervisor_review_uri_d = cols[7].find('a').get('href')
                path = urlparse(supervisor_review_uri_d).path
                extension = splitext(path)[1]
                filename = author_en + '_Bachelor_Thesis_2020_supervisor_review' + extension
                supervisor_review_uri = filename
                download_file(base_url + supervisor_review_uri_d, filename, "static/tmp/reviews/")
            else:
                supervisor_review_uri = ''

            if (cols[8].find('a')):
                reviewer_review_uri_d = cols[8].find('a').get('href')
                path = urlparse(reviewer_review_uri_d).path
                extension = splitext(path)[1]
                filename = author_en + '_Bachelor_Thesis_2020_reviewer_review' + extension
                reviewer_review_uri = filename
                download_file(base_url + reviewer_review_uri_d, filename, "static/tmp/reviews/")
            else:
                reviewer_review_uri = ''

            if (cols[9].find('a')):
                source_uri = cols[9].find('a').get('href')
            else:
                source_uri = ''

            # Try to get supervisor_id
            last_name = supervisor.split()[-1]
            q = Users.query.filter_by(last_name=last_name).first()
            if q:
                r = Staff.query.filter_by(user_id=q.id).first()
                supervisor_id = r.id
            else:
                print ("Error, no " + supervisor)
                sys.exit(1)

            if source_uri:
                t = Thesis(name_ru = name_ru, text_uri=text_uri, old_text_uri='https://oops.math.spbu.ru/SE/diploma/2020/' + old_text_uri, presentation_uri=presentation_uri,
                   supervisor_review_uri=supervisor_review_uri, reviewer_review_uri=reviewer_review_uri,
                   author=author, supervisor_id=supervisor_id, reviewer_id=2,
                   publish_year=2020, type_id=3, course_id = 2, source_uri = source_uri)
            else:
                t = Thesis(name_ru = name_ru, text_uri=text_uri, old_text_uri='https://oops.math.spbu.ru/SE/diploma/2020/' + old_text_uri, presentation_uri=presentation_uri,
                   supervisor_review_uri=supervisor_review_uri, reviewer_review_uri=reviewer_review_uri,
                   author=author, supervisor_id=supervisor_id, reviewer_id=2,
                   publish_year=2020, type_id=3, course_id = 2)


            db.session.add(t)
            db.session.commit()

# Get
# https://oops.math.spbu.ru/SE/diploma/2019/vypusknye-kvalifikacionnye-raboty
# Программная инженерия

def get_2019_09_03_04():

    session = requests.session()
    url = 'https://oops.math.spbu.ru/SE/diploma/2019/vypusknye-kvalifikacionnye-raboty'
    base_url = 'https://oops.math.spbu.ru/SE/diploma/2019/'
    course = 'Программная инженерия'
    code = '09.03.04'

    print (url)
    response = session.get(url)

    if response.status_code != 200:
        print("Response statun != 200, error.")
        sys.exit(0)

    soup = BeautifulSoup(response.text, "lxml")

    # Find header
    header = soup.find_all(string=re.compile(code))

    # Find table
    table = header[0].find_next('table')

    for row in table.findAll("tr"):
        cols = row.find_all('td')

        # Check if we have data row
        # 8 cols
        if (len(cols) == 8):
            author = cols[0].text
            author_en = translit(author, 'ru', reversed=True)
            author_en = author_en.replace(" ", "_")
            name_ru = cols[1].text
            supervisor = cols[2].text
            supervisor_id = 1
            consultant = cols[3].text
            old_text_uri = ''
            text_uri = ''
            presentation_uri = ''
            supervisor_review_uri = ''
            reviewer_review_uri = ''
            source_uri = ''
            year = 2019

            print ("Add " + name_ru)

            if (cols[4].find('a')):
                old_text_uri = cols[4].find('a').get('href')
                path = urlparse(old_text_uri).path
                extension = splitext(path)[1]
                filename = author_en + '_Bachelor_Thesis_' + str(year) + '_text' + extension
                text_uri = filename
                download_file(base_url + old_text_uri, filename, "static/tmp/texts/")
            else:
                text_uri = ''

            if (cols[5].find('a')):
                presentation_uri_d = cols[5].find('a').get('href')
                path = urlparse(presentation_uri_d).path
                extension = splitext(path)[1]
                filename = author_en + '_Bachelor_Thesis_' + str(year) + '_slides' + extension
                presentation_uri = filename
                download_file(base_url + presentation_uri_d, filename, "static/tmp/slides/")
            else:
                presentation_uri = ''

            if (cols[6].find('a')):
                supervisor_review_uri_d = cols[6].find('a').get('href')
                path = urlparse(supervisor_review_uri_d).path
                extension = splitext(path)[1]
                filename = author_en + '_Bachelor_Thesis_' + str(year) + '_supervisor_review' + extension
                supervisor_review_uri = filename
                download_file(base_url + supervisor_review_uri_d, filename, "static/tmp/reviews/")
            else:
                supervisor_review_uri = ''

            if (cols[7].find('a')):
                reviewer_review_uri_d = cols[7].find('a').get('href')
                path = urlparse(reviewer_review_uri_d).path
                extension = splitext(path)[1]
                filename = author_en + '_Bachelor_Thesis_' + str(year) + '_reviewer_review' + extension
                reviewer_review_uri = filename
                download_file(base_url + reviewer_review_uri_d, filename, "static/tmp/reviews/")
            else:
                reviewer_review_uri = ''

            # Try to get supervisor_id
            last_name = supervisor.split()[0]
            q = Users.query.filter_by(last_name=last_name).first()
            if q:
                r = Staff.query.filter_by(user_id=q.id).first()
                supervisor_id = r.id
            else:
                print ("Error, no " + supervisor)
                sys.exit(1)

            if source_uri:
                t = Thesis(name_ru = name_ru, text_uri=text_uri, old_text_uri=base_url + old_text_uri, presentation_uri=presentation_uri,
                   supervisor_review_uri=supervisor_review_uri, reviewer_review_uri=reviewer_review_uri,
                   author=author, supervisor_id=supervisor_id, reviewer_id=2,
                   publish_year=year, type_id=3, course_id = 2, source_uri = source_uri)
            else:
                t = Thesis(name_ru = name_ru, text_uri=text_uri, old_text_uri=base_url + old_text_uri, presentation_uri=presentation_uri,
                   supervisor_review_uri=supervisor_review_uri, reviewer_review_uri=reviewer_review_uri,
                   author=author, supervisor_id=supervisor_id, reviewer_id=2,
                   publish_year=year, type_id=3, course_id = 2)


            db.session.add(t)
            db.session.commit()

# Get
# https://oops.math.spbu.ru/SE/diploma/2019/vypusknye-kvalifikacionnye-raboty
# Программная инженерия

def get_2019_02_03_03():

    session = requests.session()
    url = 'https://oops.math.spbu.ru/SE/diploma/2019/vypusknye-kvalifikacionnye-raboty'
    base_url = 'https://oops.math.spbu.ru/SE/diploma/2019/'
    course = 'Математическое обеспечение и администрирование информационных систем'
    code = '02.03.03'

    print (url)
    response = session.get(url)

    if response.status_code != 200:
        print("Response statun != 200, error.")
        sys.exit(0)

    soup = BeautifulSoup(response.text, "lxml")

    # Find header
    header = soup.find_all(string=re.compile(code))

    # Find table
    table = header[0].find_next('table')

    for row in table.findAll("tr"):
        cols = row.find_all('td')

        # Check if we have data row
        # 9 cols
        if (len(cols) == 9):
            author = cols[0].text
            author_en = translit(author, 'ru', reversed=True)
            author_en = author_en.replace(" ", "_")
            name_ru = cols[1].text
            supervisor = cols[2].text
            supervisor_id = 1
            consultant = cols[3].text
            old_text_uri = ''
            text_uri = ''
            presentation_uri = ''
            supervisor_review_uri = ''
            reviewer_review_uri = ''
            source_uri = ''
            pablish_year = 2019

            print ("Add " + name_ru)

            if (cols[4].find('a')):
                old_text_uri = cols[4].find('a').get('href')
                path = urlparse(old_text_uri).path
                extension = splitext(path)[1]
                filename = author_en + '_Bachelor_Thesis_2019_text' + extension
                text_uri = filename
                download_file(base_url + old_text_uri, filename, "static/tmp/texts/")
            else:
                text_uri = ''

            if (cols[5].find('a')):
                presentation_uri_d = cols[5].find('a').get('href')
                path = urlparse(presentation_uri_d).path
                extension = splitext(path)[1]
                filename = author_en + '_Bachelor_Thesis_2019_slides' + extension
                presentation_uri = filename
                download_file(base_url + presentation_uri_d, filename, "static/tmp/slides/")
            else:
                presentation_uri = ''

            if (cols[6].find('a')):
                supervisor_review_uri_d = cols[6].find('a').get('href')
                path = urlparse(supervisor_review_uri_d).path
                extension = splitext(path)[1]
                filename = author_en + '_Bachelor_Thesis_2019_supervisor_review' + extension
                supervisor_review_uri = filename
                download_file(base_url + supervisor_review_uri_d, filename, "static/tmp/reviews/")
            else:
                supervisor_review_uri = ''

            if (cols[7].find('a')):
                reviewer_review_uri_d = cols[7].find('a').get('href')
                path = urlparse(reviewer_review_uri_d).path
                extension = splitext(path)[1]
                filename = author_en + '_Bachelor_Thesis_2019_reviewer_review' + extension
                reviewer_review_uri = filename
                download_file(base_url + reviewer_review_uri_d, filename, "static/tmp/reviews/")
            else:
                reviewer_review_uri = ''

            if (cols[8].find('a')):
                source_uri = cols[8].find('a').get('href')
            else:
                source_uri = ''

            # Try to get supervisor_id
            if (supervisor.find('Ханов') != -1):
                last_name = 'Ханов'
            else:
                m = re.search('([\w]{7,16})', supervisor)
                if m:
                    last_name = m.group(1)
                else:
                    last_name = 'Терехов'

            q = Users.query.filter_by(last_name=last_name).first()
            if q:
                r = Staff.query.filter_by(user_id=q.id).first()
                supervisor_id = r.id
            else:
                print ("Error, no " + supervisor)
                sys.exit(1)

            if source_uri:
                t = Thesis(name_ru = name_ru, text_uri=text_uri, old_text_uri=base_url + old_text_uri, presentation_uri=presentation_uri,
                   supervisor_review_uri=supervisor_review_uri, reviewer_review_uri=reviewer_review_uri,
                   author=author, supervisor_id=supervisor_id, reviewer_id=2,
                   publish_year=pablish_year, type_id=3, course_id = 1, source_uri = source_uri)
            else:
                t = Thesis(name_ru = name_ru, text_uri=text_uri, old_text_uri=base_url + old_text_uri, presentation_uri=presentation_uri,
                   supervisor_review_uri=supervisor_review_uri, reviewer_review_uri=reviewer_review_uri,
                   author=author, supervisor_id=supervisor_id, reviewer_id=2,
                   publish_year=pablish_year, type_id=3, course_id = 1)


            db.session.add(t)
            db.session.commit()


# Get
# https://oops.math.spbu.ru/SE/diploma/2019/vypusknye-kvalifikacionnye-raboty
# Математическое обеспечение и администрирование информационных систем (02.04.03)

def get_2019_02_04_03():

    session = requests.session()
    url = 'https://oops.math.spbu.ru/SE/diploma/2019/vypusknye-kvalifikacionnye-raboty'
    base_url = 'https://oops.math.spbu.ru/SE/diploma/2019/'
    course = 'Математическое обеспечение и администрирование информационных систем'
    code = '02.04.03'

    print (url)
    response = session.get(url)

    if response.status_code != 200:
        print("Response statun != 200, error.")
        sys.exit(0)

    soup = BeautifulSoup(response.text, "lxml")

    # Find header
    header = soup.find_all(string=re.compile(code))

    # Find table
    table = header[0].find_next('table')

    for row in table.findAll("tr"):
        cols = row.find_all('td')

        # Check if we have data row
        # 7 cols
        if (len(cols) == 7):
            author = cols[0].text
            author_en = translit(author, 'ru', reversed=True)
            author_en = author_en.replace(" ", "_")
            name_ru = cols[1].text
            supervisor = cols[5].text
            supervisor_id = 1
            consultant = ''
            old_text_uri = ''
            text_uri = ''
            presentation_uri = ''
            supervisor_review_uri = ''
            reviewer_review_uri = ''
            source_uri = ''
            pablish_year = 2019

            print ("Add " + name_ru)

            if (cols[2].find('a')):
                old_text_uri = cols[2].find('a').get('href')
                path = urlparse(old_text_uri).path
                extension = splitext(path)[1]
                filename = author_en + '_Master_Thesis_2019_text' + extension
                text_uri = filename
                download_file(base_url + old_text_uri, filename, "static/tmp/texts/")
            else:
                text_uri = ''

            if (cols[3].find('a')):
                presentation_uri_d = cols[3].find('a').get('href')
                path = urlparse(presentation_uri_d).path
                extension = splitext(path)[1]
                filename = author_en + '_Master_Thesis_2019_slides' + extension
                presentation_uri = filename
                download_file(base_url + presentation_uri_d, filename, "static/tmp/slides/")
            else:
                presentation_uri = ''

            if (cols[5].find('a')):
                supervisor_review_uri_d = cols[5].find('a').get('href')
                path = urlparse(supervisor_review_uri_d).path
                extension = splitext(path)[1]
                filename = author_en + '_Master_Thesis_2019_supervisor_review' + extension
                supervisor_review_uri = filename
                download_file(base_url + supervisor_review_uri_d, filename, "static/tmp/reviews/")
            else:
                supervisor_review_uri = ''

            if (cols[6].find('a')):
                reviewer_review_uri_d = cols[6].find('a').get('href')
                path = urlparse(reviewer_review_uri_d).path
                extension = splitext(path)[1]
                filename = author_en + '_Master_Thesis_2019_reviewer_review' + extension
                reviewer_review_uri = filename
                download_file(base_url + reviewer_review_uri_d, filename, "static/tmp/reviews/")
            else:
                reviewer_review_uri = ''

            if (cols[4].find('a')):
                source_uri = cols[4].find('a').get('href')
            else:
                source_uri = ''

            # Try to get supervisor_id
            m = re.search('([\w]{5,16})', supervisor)
            if m:
                last_name = m.group(1)
            else:
                last_name = 'Терехов'

            q = Users.query.filter_by(last_name=last_name).first()
            if q:
                r = Staff.query.filter_by(user_id=q.id).first()
                supervisor_id = r.id
            else:
                print ("Error, no " + supervisor)
                sys.exit(1)

            if source_uri:
                t = Thesis(name_ru = name_ru, text_uri=text_uri, old_text_uri=base_url + old_text_uri, presentation_uri=presentation_uri,
                   supervisor_review_uri=supervisor_review_uri, reviewer_review_uri=reviewer_review_uri,
                   author=author, supervisor_id=supervisor_id, reviewer_id=2,
                   publish_year=pablish_year, type_id=4, course_id = 3, source_uri = source_uri)
            else:
                t = Thesis(name_ru = name_ru, text_uri=text_uri, old_text_uri=base_url + old_text_uri, presentation_uri=presentation_uri,
                   supervisor_review_uri=supervisor_review_uri, reviewer_review_uri=reviewer_review_uri,
                   author=author, supervisor_id=supervisor_id, reviewer_id=2,
                   publish_year=pablish_year, type_id=4, course_id = 3)


            db.session.add(t)
            db.session.commit()

# Get
# https://oops.math.spbu.ru/SE/YearlyProjects/vesna-2020
# Бакалавры, 371 группа (02.04.03)

def get_2020_371():

    session = requests.session()
    url = 'https://oops.math.spbu.ru/SE/YearlyProjects/vesna-2020'
    base_url = 'https://oops.math.spbu.ru/SE/YearlyProjects/vesna-2020/'
    course = 'Бакалавры, 371 группа'
    code = '371'

    print (url)
    response = session.get(url)

    if response.status_code != 200:
        print("Response statun != 200, error.")
        sys.exit(0)

    soup = BeautifulSoup(response.text, "lxml")

    # Find header
    header = soup.find_all(string=re.compile(code))

    # Find table
    table = header[0].find_next('table')

    for row in table.findAll("tr"):
        cols = row.find_all('td')

        # Check if we have data row
        # 5 cols
        if (len(cols) == 5):
            author = cols[0].text
            author_en = translit(author, 'ru', reversed=True)
            author_en = author_en.replace(" ", "_")
            name_ru = cols[1].text
            supervisor = cols[2].text
            supervisor_id = 1
            consultant = ''
            old_text_uri = None
            text_uri = None
            presentation_uri = None
            supervisor_review_uri = None
            reviewer_review_uri = None
            source_uri = None
            pablish_year = 2020

            print ("Add " + name_ru)

            data = cols[4].find_all('a')

            if (len(data) > 0):
                old_text_uri = data[0].get('href')
                path = urlparse(old_text_uri).path
                extension = splitext(path)[1]
                filename = author_en + '_Bachelor_Report_2020_text' + extension
                text_uri = filename
                download_file(base_url + old_text_uri, filename, "static/tmp/texts/")
            else:
                text_uri = None

            if (len(data) > 1):
                presentation_uri_d = data[1].get('href')
                path = urlparse(presentation_uri_d).path
                extension = splitext(path)[1]
                filename = author_en + '_Bachelor_Report_2020_slides' + extension
                presentation_uri = filename
                download_file(base_url + presentation_uri_d, filename, "static/tmp/slides/")
            else:
                presentation_uri = None

            if (len(data) > 2):
                supervisor_review_uri_d = data[2].get('href')
                path = urlparse(supervisor_review_uri_d).path
                extension = splitext(path)[1]
                filename = author_en + '_Bachelor_Report_2020_supervisor_review' + extension
                supervisor_review_uri = filename
                download_file(base_url + supervisor_review_uri_d, filename, "static/tmp/reviews/")
            else:
                supervisor_review_uri = None

            if (len(data) > 3):
                source_uri = data[3].get('href')
            else:
                source_uri = None

            last_name = supervisor.split()[-3]

            q = Users.query.filter_by(last_name=last_name).first()
            if q:
                r = Staff.query.filter_by(user_id=q.id).first()
                supervisor_id = r.id
            else:
                print ("Error, no " + supervisor)
                sys.exit(1)

            if source_uri:
                t = Thesis(name_ru = name_ru, text_uri=text_uri, old_text_uri=base_url + old_text_uri, presentation_uri=presentation_uri,
                   supervisor_review_uri=supervisor_review_uri, reviewer_review_uri=reviewer_review_uri,
                   author=author, supervisor_id=supervisor_id, reviewer_id=2,
                   publish_year=pablish_year, type_id=2, course_id = 2, source_uri = source_uri)
            else:
                t = Thesis(name_ru = name_ru, text_uri=text_uri, old_text_uri=base_url + old_text_uri, presentation_uri=presentation_uri,
                   supervisor_review_uri=supervisor_review_uri, reviewer_review_uri=reviewer_review_uri,
                   author=author, supervisor_id=supervisor_id, reviewer_id=2,
                   publish_year=pablish_year, type_id=2, course_id = 2)


            db.session.add(t)
            db.session.commit()


# Get
# https://oops.math.spbu.ru/SE/YearlyProjects/vesna-2020
# Математическое обеспечение и администрирование информационных систем

def get_report_2020_02_03_03():

    session = requests.session()
    url = 'https://oops.math.spbu.ru/SE/YearlyProjects/vesna-2020'
    base_url = 'https://oops.math.spbu.ru/SE/YearlyProjects/vesna-2020/'
    course = 'Математическое обеспечение и администрирование информационных систем'
    code = '02.03.03'

    print (url)
    response = session.get(url)

    if response.status_code != 200:
        print("Response statun != 200, error.")
        sys.exit(0)

    soup = BeautifulSoup(response.text, "lxml")

    # Find header
    header = soup.find_all(string=re.compile(code))

    # Find table
    table = header[0].find_next('table')

    for row in table.findAll("tr"):
        cols = row.find_all('td')

        # Check if we have data row
        if (len(cols) == 9):
            author = cols[0].text
            author_en = translit(author, 'ru', reversed=True)
            author_en = author_en.replace(" ", "_")
            name_ru = cols[1].text
            supervisor = cols[2].text
            supervisor_id = 1
            consultant = cols[3].text
            old_text_uri = None
            text_uri = None
            presentation_uri = None
            supervisor_review_uri = None
            reviewer_review_uri = None
            source_uri = None
            publish_year = 2020

            print ("Add " + name_ru)

            if (cols[4].find('a')):
                old_text_uri = cols[4].find('a').get('href')
                path = urlparse(old_text_uri).path
                extension = splitext(path)[1]
                filename = author_en + '_Bachelor_Report_2020_text' + extension
                text_uri = filename
                download_file(base_url + old_text_uri, filename, "static/tmp/texts/")

            if (cols[5].find('a')):
                presentation_uri_d = cols[5].find('a').get('href')
                path = urlparse(presentation_uri_d).path
                extension = splitext(path)[1]
                filename = author_en + '_Bachelor_Report_2020_slides' + extension
                presentation_uri = filename
                download_file(base_url + presentation_uri_d, filename, "static/tmp/slides/")

            if (cols[6].find('a')):
                supervisor_review_uri_d = cols[6].find('a').get('href')
                path = urlparse(supervisor_review_uri_d).path
                extension = splitext(path)[1]
                filename = author_en + '_Bachelor_Report_2020_supervisor_review' + extension
                supervisor_review_uri = filename
                download_file(base_url + supervisor_review_uri_d, filename, "static/tmp/reviews/")

            if (cols[7].find('a')):
                reviewer_review_uri_d = cols[7].find('a').get('href')
                path = urlparse(reviewer_review_uri_d).path
                extension = splitext(path)[1]
                filename = author_en + '_Bachelor_Report_2020_reviewer_review' + extension
                reviewer_review_uri = filename
                download_file(base_url + reviewer_review_uri_d, filename, "static/tmp/reviews/")

            if (cols[8].find('a')):
                source_uri = cols[8].find('a').get('href')

            # Try to get supervisor_id

            if (supervisor.find('Сагунов') != -1):
                last_name = 'Сагунов'
            else:
                last_name = supervisor.split()[-1]

            q = Users.query.filter_by(last_name=last_name).first()
            if q:
                r = Staff.query.filter_by(user_id=q.id).first()
                supervisor_id = r.id
            else:
                print ("Error, no " + supervisor)
                sys.exit(1)

            if source_uri:
                t = Thesis(name_ru = name_ru, text_uri=text_uri, old_text_uri=base_url + old_text_uri, presentation_uri=presentation_uri,
                   supervisor_review_uri=supervisor_review_uri, reviewer_review_uri=reviewer_review_uri,
                   author=author, supervisor_id=supervisor_id, reviewer_id=2,
                   publish_year=publish_year, type_id=2, course_id = 1, source_uri = source_uri)
            else:
                t = Thesis(name_ru = name_ru, text_uri=text_uri, old_text_uri=base_url + old_text_uri, presentation_uri=presentation_uri,
                   supervisor_review_uri=supervisor_review_uri, reviewer_review_uri=reviewer_review_uri,
                   author=author, supervisor_id=supervisor_id, reviewer_id=2,
                   publish_year=publish_year, type_id=2, course_id = 1)


            db.session.add(t)
            db.session.commit()


# Get
# https://oops.math.spbu.ru/SE/YearlyProjects/spring-2019
# Бакалавры, 371 группа

def get_2019_371():

    session = requests.session()
    url = 'https://oops.math.spbu.ru/SE/YearlyProjects/spring-2019'
    base_url = 'https://oops.math.spbu.ru/SE/YearlyProjects/spring-2019/'
    code = '371'

    print (url)
    response = session.get(url)

    if response.status_code != 200:
        print("Response statun != 200, error.")
        sys.exit(0)

    soup = BeautifulSoup(response.text, "lxml")

    # Find header
    header = soup.find_all(string=re.compile(code))

    # Find table
    table = header[0].find_next('table')

    for row in table.findAll("tr"):
        cols = row.find_all('td')

        # Check if we have data row
        # 4 cols
        if (len(cols) == 4):
            author = cols[0].text
            author_en = translit(author, 'ru', reversed=True)
            author_en = author_en.replace(" ", "_")
            name_ru = cols[1].text
            supervisor = cols[2].text
            supervisor_id = 1
            consultant = ''
            old_text_uri = None
            text_uri = None
            presentation_uri = None
            supervisor_review_uri = None
            reviewer_review_uri = None
            source_uri = None
            pablish_year = 2019

            print ("Add " + name_ru)

            data = cols[3].find_all('a')

            if (len(data) > 0):
                old_text_uri = data[0].get('href')
                path = urlparse(old_text_uri).path
                extension = splitext(path)[1]
                filename = author_en + '_Bachelor_Report_2019_text' + extension
                text_uri = filename
                download_file(base_url + old_text_uri, filename, "static/tmp/texts/")

            if (len(data) > 1):
                presentation_uri_d = data[1].get('href')
                path = urlparse(presentation_uri_d).path
                extension = splitext(path)[1]
                filename = author_en + '_Bachelor_Report_2019_slides' + extension
                presentation_uri = filename
                download_file(base_url + presentation_uri_d, filename, "static/tmp/slides/")

            if (len(data) > 2):
                supervisor_review_uri_d = data[2].get('href')
                path = urlparse(supervisor_review_uri_d).path
                extension = splitext(path)[1]
                filename = author_en + '_Bachelor_Report_2019_supervisor_review' + extension
                supervisor_review_uri = filename
                download_file(base_url + supervisor_review_uri_d, filename, "static/tmp/reviews/")

                source_uri = None

            last_name = supervisor.split()[0]

            q = Users.query.filter_by(last_name=last_name).first()
            if q:
                r = Staff.query.filter_by(user_id=q.id).first()
                supervisor_id = r.id
            else:
                print ("Error, no " + supervisor)
                sys.exit(1)

            t = Thesis(name_ru = name_ru, text_uri=text_uri, old_text_uri=base_url + old_text_uri, presentation_uri=presentation_uri,
                   supervisor_review_uri=supervisor_review_uri, reviewer_review_uri=reviewer_review_uri,
                   author=author, supervisor_id=supervisor_id, reviewer_id=2,
                   publish_year=pablish_year, type_id=2, course_id = 2)

            db.session.add(t)
            db.session.commit()

# Get
# https://oops.math.spbu.ru/SE/YearlyProjects/spring-2019
# Бакалавры, 343 группа

def get_2019_343():

    session = requests.session()
    url = 'https://oops.math.spbu.ru/SE/YearlyProjects/spring-2019'
    base_url = 'https://oops.math.spbu.ru/SE/YearlyProjects/spring-2019/'
    code = '343'

    print (url)
    response = session.get(url)

    if response.status_code != 200:
        print("Response statun != 200, error.")
        sys.exit(0)

    soup = BeautifulSoup(response.text, "lxml")

    # Find header
    header = soup.find_all(string=re.compile(code))

    # Find table
    table = header[0].find_next('table')

    for row in table.findAll("tr"):
        cols = row.find_all('td')

        # Check if we have data row
        # 4 cols
        if (len(cols) == 4):
            author = cols[0].text
            author_en = translit(author, 'ru', reversed=True)
            author_en = author_en.replace(" ", "_")
            name_ru = cols[1].text
            supervisor = cols[2].text
            supervisor_id = 1
            consultant = ''
            old_text_uri = None
            text_uri = None
            presentation_uri = None
            supervisor_review_uri = None
            reviewer_review_uri = None
            source_uri = None
            pablish_year = 2019

            print ("Add " + name_ru)

            data = cols[3].find_all('a')

            if (len(data) > 0):
                old_text_uri = data[0].get('href')
                path = urlparse(old_text_uri).path
                extension = splitext(path)[1]
                filename = author_en + '_Bachelor_Report_2019_text' + extension
                text_uri = filename
                download_file(base_url + old_text_uri, filename, "static/tmp/texts/")

            if (len(data) > 1):
                presentation_uri_d = data[1].get('href')
                path = urlparse(presentation_uri_d).path
                extension = splitext(path)[1]
                filename = author_en + '_Bachelor_Report_2019_slides' + extension
                presentation_uri = filename
                download_file(base_url + presentation_uri_d, filename, "static/tmp/slides/")

            if (len(data) > 2):
                supervisor_review_uri_d = data[2].get('href')
                path = urlparse(supervisor_review_uri_d).path
                extension = splitext(path)[1]
                filename = author_en + '_Bachelor_Report_2019_supervisor_review' + extension
                supervisor_review_uri = filename
                download_file(base_url + supervisor_review_uri_d, filename, "static/tmp/reviews/")

            source_uri = None

            last_name = supervisor.split()[-1]

            q = Users.query.filter_by(last_name=last_name).first()
            if q:
                r = Staff.query.filter_by(user_id=q.id).first()
                supervisor_id = r.id
            else:
                print ("Error, no " + supervisor)
                sys.exit(1)

            t = Thesis(name_ru = name_ru, text_uri=text_uri, old_text_uri=base_url + old_text_uri, presentation_uri=presentation_uri,
                   supervisor_review_uri=supervisor_review_uri, reviewer_review_uri=reviewer_review_uri,
                   author=author, supervisor_id=supervisor_id, reviewer_id=2,
                   publish_year=pablish_year, type_id=2, course_id = 5)

            db.session.add(t)
            db.session.commit()

# Get
# https://oops.math.spbu.ru/SE/YearlyProjects/spring-2019
# Бакалавры, 344 группа

def get_2019_344():

    session = requests.session()
    url = 'https://oops.math.spbu.ru/SE/YearlyProjects/spring-2019'
    base_url = 'https://oops.math.spbu.ru/SE/YearlyProjects/spring-2019/'
    code = '344'

    print (url)
    response = session.get(url)

    if response.status_code != 200:
        print("Response statun != 200, error.")
        sys.exit(0)

    soup = BeautifulSoup(response.text, "lxml")

    # Find header
    header = soup.find_all(string=re.compile(code))

    # Find table
    table = header[0].find_next('table')

    for row in table.findAll("tr"):
        cols = row.find_all('td')

        # Check if we have data row
        # 4 cols
        if (len(cols) == 4):
            author = cols[0].text
            author_en = translit(author, 'ru', reversed=True)
            author_en = author_en.replace(" ", "_")
            name_ru = cols[1].text
            supervisor = cols[2].text
            supervisor_id = 1
            consultant = ''
            old_text_uri = None
            text_uri = None
            presentation_uri = None
            supervisor_review_uri = None
            reviewer_review_uri = None
            source_uri = None
            pablish_year = 2019

            print ("Add " + name_ru)

            data = cols[3].find_all('a')

            if (len(data) > 0):
                old_text_uri = data[0].get('href')
                path = urlparse(old_text_uri).path
                extension = splitext(path)[1]
                filename = author_en + '_Bachelor_Report_2019_text' + extension
                text_uri = filename
                download_file(base_url + old_text_uri, filename, "static/tmp/texts/")

            if (len(data) > 1):
                presentation_uri_d = data[1].get('href')
                path = urlparse(presentation_uri_d).path
                extension = splitext(path)[1]
                filename = author_en + '_Bachelor_Report_2019_slides' + extension
                presentation_uri = filename
                download_file(base_url + presentation_uri_d, filename, "static/tmp/slides/")

            if (len(data) > 2):
                supervisor_review_uri_d = data[2].get('href')
                path = urlparse(supervisor_review_uri_d).path
                extension = splitext(path)[1]
                filename = author_en + '_Bachelor_Report_2019_supervisor_review' + extension
                supervisor_review_uri = filename
                download_file(base_url + supervisor_review_uri_d, filename, "static/tmp/reviews/")

            source_uri = None

            last_name = supervisor.split()[-1]

            q = Users.query.filter_by(last_name=last_name).first()
            if q:
                r = Staff.query.filter_by(user_id=q.id).first()
                supervisor_id = r.id
            else:
                print ("Error, no " + supervisor)
                sys.exit(1)

            t = Thesis(name_ru = name_ru, text_uri=text_uri, old_text_uri=base_url + old_text_uri, presentation_uri=presentation_uri,
                   supervisor_review_uri=supervisor_review_uri, reviewer_review_uri=reviewer_review_uri,
                   author=author, supervisor_id=supervisor_id, reviewer_id=2,
                   publish_year=pablish_year, type_id=2, course_id = 6)

            db.session.add(t)
            db.session.commit()

# Add master thesis 2020
# ПИ и МО

def add_master_thesis_2020():

    thesis = [
       {'name_ru': 'Использование автоматов в интерпретаторе MACASM', 'text_uri':'_Master_Thesis_2020_text.pdf',
   'presentation_uri':'_Master_Thesis_2020_slides.pdf', 'supervisor_review_uri': '_Master_Thesis_2020_supervisor_review.pdf',
        'reviewer_review_uri':'_Master_Thesis_2020_reviewer_review.pdf', 'author': 'Соколова Полина Александровна',
        'supervisor': 'Луцив', 'publish_year': 2020, 'type_id': 4, 'course_id': 7},
       {'name_ru': 'Автоматическая калибровка внешних параметров широкоугольных камер в автомобильных системах кругового обзора',
        'text_uri':'_Master_Thesis_2020_text.pdf', 'presentation_uri':'_Master_Thesis_2020_slides.pdf',
        'supervisor_review_uri': '_Master_Thesis_2020_supervisor_review.pdf',
        'reviewer_review_uri':'_Master_Thesis_2020_reviewer_review.pdf', 'author': 'Петров Алексей Андреевич',
        'supervisor': 'Луцив', 'publish_year': 2020, 'type_id': 4, 'course_id': 7},
       { 'name_ru': 'Эффективная разрешающая процедура для задачи выполнимости в теории номинальных систем типов с вариантностью',
           'text_uri': '_Master_Thesis_2020_text.pdf', 'presentation_uri': '_Master_Thesis_2020_slides.pdf',
           'supervisor_review_uri': '_Master_Thesis_2020_supervisor_review.pdf',
           'reviewer_review_uri': '_Master_Thesis_2020_reviewer_review.pdf', 'author': 'Милова Наталья Андреевна',
           'supervisor': 'Кознов', 'publish_year': 2020, 'type_id': 4, 'course_id': 7},
       {
           'name_ru': 'Веб-платформа предметно-ориентированного моделирования на базе REAL.NET',
           'text_uri': '_Master_Thesis_2020_text.pdf', 'presentation_uri': '_Master_Thesis_2020_slides.pdf',
           'supervisor_review_uri': '_Master_Thesis_2020_supervisor_review.pdf',
           'reviewer_review_uri': '_Master_Thesis_2020_reviewer_review.pdf', 'author': 'Кузьмина Елизавета Владимировна',
           'supervisor': 'Литвинов', 'publish_year': 2020, 'type_id': 4, 'course_id': 7},
        {
            'name_ru': 'Оценка параметров систем камер без использования калибровочных паттернов',
            'text_uri': '_Master_Thesis_2020_text.pdf', 'presentation_uri': '_Master_Thesis_2020_slides.pdf',
            'supervisor_review_uri': '_Master_Thesis_2020_supervisor_review.pdf',
            'reviewer_review_uri': '_Master_Thesis_2020_reviewer_review.pdf',
            'author': 'Синицын Даниил Дмитриевич',
            'supervisor': 'Терехов', 'publish_year': 2020, 'type_id': 4, 'course_id': 3},
        {
            'name_ru': 'Синтез программ по спецификациям с множественными вызовами',
            'text_uri': '_Master_Thesis_2020_text.pdf', 'presentation_uri': '_Master_Thesis_2020_slides.pdf',
            'supervisor_review_uri': '_Master_Thesis_2020_supervisor_review.pdf',
            'reviewer_review_uri': '_Master_Thesis_2020_reviewer_review.pdf',
            'author': 'Мишенев Вадим Сергеевич',
            'supervisor': 'Кознов', 'publish_year': 2020, 'type_id': 4, 'course_id': 3},
        {
            'name_ru': 'Система для расчета скоростей звука в особых областях по данным УЗИ–томографии',
            'text_uri': '_Master_Thesis_2020_text.pdf', 'presentation_uri': '_Master_Thesis_2020_slides.pdf',
            'supervisor_review_uri': '_Master_Thesis_2020_supervisor_review.pdf',
            'reviewer_review_uri': '_Master_Thesis_2020_reviewer_review.pdf',
            'author': 'Леонова Анна Васильевна',
            'supervisor': 'Граничин', 'publish_year': 2020, 'type_id': 4, 'course_id': 3},
        {
            'name_ru': 'Поиск и кластеризация нечетких повторов в документации программного обеспечения',
            'text_uri': '_Master_Thesis_2020_text.pdf', 'presentation_uri': '_Master_Thesis_2020_slides.pdf',
            'supervisor_review_uri': '_Master_Thesis_2020_supervisor_review.pdf',
            'reviewer_review_uri': '_Master_Thesis_2020_reviewer_review.pdf',
            'author': 'Коновалова Ирина Михайловна',
            'supervisor': 'Луцив', 'publish_year': 2020, 'type_id': 4, 'course_id': 3},
        {
            'name_ru': 'Анализ качества автодополнения кода в интегрированных средах разработки',
            'text_uri': '_Master_Thesis_2020_text.pdf', 'presentation_uri': '_Master_Thesis_2020_slides.pdf',
            'supervisor_review_uri': '_Master_Thesis_2020_supervisor_review.pdf',
            'reviewer_review_uri': '_Master_Thesis_2020_reviewer_review.pdf',
            'author': 'Калина Алексей Игоревич',
            'supervisor': 'Луцив', 'publish_year': 2020, 'type_id': 4, 'course_id': 3},
        {
            'name_ru': 'Синхронизация в многопоточных МАК-обфусцированных программах',
            'text_uri': '_Master_Thesis_2020_text.pdf', 'presentation_uri': '_Master_Thesis_2020_slides.pdf',
            'supervisor_review_uri': '_Master_Thesis_2020_supervisor_review.pdf',
            'reviewer_review_uri': '_Master_Thesis_2020_reviewer_review.pdf',
            'author': 'Бабанов Пётр Андреевич',
            'supervisor': 'Брыксин', 'publish_year': 2020, 'type_id': 4, 'course_id': 3},
   ]

    for t in thesis:
       author_en = translit(t['author'], 'ru', reversed=True)
       author_en = author_en.replace(" ", "_")
       print (author_en + t['text_uri'])
       print(author_en + t['presentation_uri'])
       print(author_en + t['supervisor_review_uri'])
       print(author_en + t['reviewer_review_uri'])

       last_name = t['supervisor']
       supervisor_id = 1

       q = Users.query.filter_by(last_name=last_name).first()
       if q:
           r = Staff.query.filter_by(user_id=q.id).first()
           supervisor_id = r.id
       else:
           print ("Error, no " + t['supervisor'])
           sys.exit(1)

       tt = Thesis(name_ru = t['name_ru'], text_uri=author_en + t['text_uri'], presentation_uri=author_en + t['presentation_uri'],
                   supervisor_review_uri=author_en + t['supervisor_review_uri'], reviewer_review_uri=author_en + t['reviewer_review_uri'],
                   author=t['author'], supervisor_id=supervisor_id, reviewer_id=2,
                   publish_year=t['publish_year'], type_id=t['type_id'], course_id = t['course_id'])

       db.session.add(tt)
       db.session.commit()


# Get
# https://oops.math.spbu.ru/SE/YearlyProjects/vesna-2022/uchebnaya-praktika
# Бакалавры, 271 группа

def get_2022_271():

    session = requests.session()
    url = 'https://oops.math.spbu.ru/SE/YearlyProjects/vesna-2022/uchebnaya-praktika'
    base_url = 'https://oops.math.spbu.ru/SE/YearlyProjects/vesna-2022/'
    code = '271'

    print (url)
    response = session.get(url)

    if response.status_code != 200:
        print("Response statun != 200, error.")
        sys.exit(0)

    soup = BeautifulSoup(response.text, "lxml")

    # Find header
    header = soup.find_all(string=re.compile(code))

    # Find table
    table = header[0].find_next('table')

    for row in table.findAll("tr"):
        cols = row.find_all('td')

        # Check if we have data row
        # 5 cols
        if (len(cols) == 5):
            author = cols[0].text
            author_en = translit(author, 'ru', reversed=True)
            author_en = author_en.replace(" ", "_")
            name_ru = cols[1].text
            supervisor = cols[2].text
            supervisor_id = 1
            consultant = ''
            old_text_uri = None
            text_uri = None
            presentation_uri = None
            supervisor_review_uri = None
            reviewer_review_uri = None
            source_uri = None
            pablish_year = 2022

            print ("Add " + name_ru)

            data = cols[4].find_all('a')

            if len(data) > 0:
                old_text_uri = data[0].get('href')
                path = urlparse(old_text_uri).path
                extension = splitext(path)[1]
                filename = author_en + '_Bachelor_Report_2022_text' + extension
                text_uri = filename
                download_file(base_url + old_text_uri, filename, "static/tmp/texts/")

            if len(data) > 1:
                presentation_uri_d = data[1].get('href')
                path = urlparse(presentation_uri_d).path
                extension = splitext(path)[1]
                filename = author_en + '_Bachelor_Report_2022_slides' + extension
                presentation_uri = filename
                download_file(base_url + presentation_uri_d, filename, "static/tmp/slides/")

            if len(data) > 2:
                supervisor_review_uri_d = data[2].get('href')
                path = urlparse(supervisor_review_uri_d).path
                extension = splitext(path)[1]
                filename = author_en + '_Bachelor_Report_2022_supervisor_review' + extension
                supervisor_review_uri = filename
                download_file(base_url + supervisor_review_uri_d, filename, "static/tmp/reviews/")

            source_uri = None

            last_name = supervisor.split()[-3]

            #q = Users.query.filter_by(last_name=last_name).first()
            print (last_name)
            r = Staff.query.join(Staff.user).filter(Users.last_name==last_name).first()
            if r:
                supervisor_id = r.id
            else:
                print ("Error, no " + supervisor)
                sys.exit(1)

            t = Thesis(name_ru = name_ru, text_uri=text_uri, old_text_uri=base_url + old_text_uri, presentation_uri=presentation_uri,
                   supervisor_review_uri=supervisor_review_uri, reviewer_review_uri=reviewer_review_uri,
                   author=author, supervisor_id=supervisor_id, reviewer_id=2,
                   publish_year=pablish_year, type_id=5, course_id = 2, temporary=True)

            db.session.add(t)
            db.session.commit()


# Get
# https://oops.math.spbu.ru/SE/YearlyProjects/vesna-2022/proizvodstvennaya-praktika
# Бакалавры, 371 группа

def get_2022_371():

    session = requests.session()
    url = 'https://oops.math.spbu.ru/SE/YearlyProjects/vesna-2022/proizvodstvennaya-praktika'
    base_url = 'https://oops.math.spbu.ru/SE/YearlyProjects/vesna-2022/'
    code = '371'

    print (url)
    response = session.get(url)

    if response.status_code != 200:
        print("Response statun != 200, error.")
        sys.exit(0)

    soup = BeautifulSoup(response.text, "lxml")

    # Find header
    header = soup.find_all(string=re.compile(code))

    # Find table
    table = header[0].find_next('table')

    for row in table.findAll("tr"):
        cols = row.find_all('td')

        # Check if we have data row
        # 5 cols
        if (len(cols) == 5):
            author = cols[0].text
            author_en = translit(author, 'ru', reversed=True)
            author_en = author_en.replace(" ", "_")
            name_ru = cols[1].text
            supervisor = cols[2].text
            supervisor_id = 1
            consultant = ''
            old_text_uri = None
            text_uri = None
            presentation_uri = None
            supervisor_review_uri = None
            reviewer_review_uri = None
            source_uri = None
            pablish_year = 2022

            print ("Add " + name_ru)

            data = cols[4].find_all('a')

            # Skip Милосердова
            if not author.find('Милосердова'):
                print (author)
                continue

            if len(data) > 0:
                old_text_uri = data[0].get('href')
                path = urlparse(old_text_uri).path
                extension = splitext(path)[1]
                filename = author_en + '_Bachelor_Report_2022_text' + extension
                text_uri = filename
                download_file(base_url + old_text_uri, filename, "static/tmp/texts/")

            if len(data) > 1:
                presentation_uri_d = data[1].get('href')
                path = urlparse(presentation_uri_d).path
                extension = splitext(path)[1]
                filename = author_en + '_Bachelor_Report_2022_slides' + extension
                presentation_uri = filename
                download_file(base_url + presentation_uri_d, filename, "static/tmp/slides/")

            if len(data) > 2:
                supervisor_review_uri_d = data[2].get('href')
                path = urlparse(supervisor_review_uri_d).path
                extension = splitext(path)[1]
                filename = author_en + '_Bachelor_Report_2022_supervisor_review' + extension
                supervisor_review_uri = filename
                download_file(base_url + supervisor_review_uri_d, filename, "static/tmp/reviews/")

            source_uri = None

            last_name = supervisor.split()[-3]

            #q = Users.query.filter_by(last_name=last_name).first()
            print (last_name)
            r = Staff.query.join(Staff.user).filter(Users.last_name==last_name).first()
            if r:
                supervisor_id = r.id
            else:
                print ("Error, no " + supervisor)
                sys.exit(1)

            t = Thesis(name_ru = name_ru, text_uri=text_uri, old_text_uri=base_url + old_text_uri, presentation_uri=presentation_uri,
                   supervisor_review_uri=supervisor_review_uri, reviewer_review_uri=reviewer_review_uri,
                   author=author, supervisor_id=supervisor_id, reviewer_id=2,
                   publish_year=pablish_year, type_id=7, course_id=2, temporary=True)

            db.session.add(t)
            db.session.commit()


# Get
# https://oops.math.spbu.ru/SE/diploma/2022/index
# Программная инженерия

def get_2022_09_03_04():

    session = requests.session()
    url = 'https://oops.math.spbu.ru/SE/diploma/2022/index'
    base_url = 'https://oops.math.spbu.ru/SE/diploma/2022/'
    course = 'Математическое обеспечение и администрирование информационных систем'
    code = '09.03.04'

    print (url)
    response = session.get(url)

    if response.status_code != 200:
        print("Response statun != 200, error.")
        sys.exit(0)

    soup = BeautifulSoup(response.text, "lxml")

    # Find header
    header = soup.find_all(string=re.compile(code))

    # Find table
    table = header[0].find_next('table')

    for row in table.findAll("tr"):
        cols = row.find_all('td')

        # Check if we have data row
        # 9 cols
        if (len(cols) == 10):
            author = cols[0].text
            author_en = translit(author, 'ru', reversed=True)
            author_en = author_en.replace(" ", "_")
            name_ru = cols[1].text
            supervisor = cols[2].text
            supervisor_id = 1
            consultant = cols[3].text
            old_text_uri = ''
            text_uri = ''
            presentation_uri = ''
            supervisor_review_uri = ''
            reviewer_review_uri = ''
            source_uri = ''
            pablish_year = 2022

            print ("Add " + name_ru)

            if (cols[4].find('a')):
                old_text_uri = cols[5].find('a').get('href')
                path = urlparse(old_text_uri).path
                extension = splitext(path)[1]
                filename = author_en + '_Bachelor_Thesis_2019_text' + extension
                text_uri = filename
                download_file(base_url + old_text_uri, filename, "static/tmp/texts/")
            else:
                text_uri = ''

            if (cols[5].find('a')):
                presentation_uri_d = cols[5].find('a').get('href')
                path = urlparse(presentation_uri_d).path
                extension = splitext(path)[1]
                filename = author_en + '_Bachelor_Thesis_2019_slides' + extension
                presentation_uri = filename
                download_file(base_url + presentation_uri_d, filename, "static/tmp/slides/")
            else:
                presentation_uri = ''

            if (cols[6].find('a')):
                supervisor_review_uri_d = cols[6].find('a').get('href')
                path = urlparse(supervisor_review_uri_d).path
                extension = splitext(path)[1]
                filename = author_en + '_Bachelor_Thesis_2019_supervisor_review' + extension
                supervisor_review_uri = filename
                download_file(base_url + supervisor_review_uri_d, filename, "static/tmp/reviews/")
            else:
                supervisor_review_uri = ''

            if (cols[7].find('a')):
                reviewer_review_uri_d = cols[7].find('a').get('href')
                path = urlparse(reviewer_review_uri_d).path
                extension = splitext(path)[1]
                filename = author_en + '_Bachelor_Thesis_2019_reviewer_review' + extension
                reviewer_review_uri = filename
                download_file(base_url + reviewer_review_uri_d, filename, "static/tmp/reviews/")
            else:
                reviewer_review_uri = ''

            if (cols[8].find('a')):
                source_uri = cols[8].find('a').get('href')
            else:
                source_uri = ''

            # Try to get supervisor_id
            if (supervisor.find('Ханов') != -1):
                last_name = 'Ханов'
            else:
                m = re.search('([\w]{7,16})', supervisor)
                if m:
                    last_name = m.group(1)
                else:
                    last_name = 'Терехов'

            q = Users.query.filter_by(last_name=last_name).first()
            if q:
                r = Staff.query.filter_by(user_id=q.id).first()
                supervisor_id = r.id
            else:
                print ("Error, no " + supervisor)
                sys.exit(1)

            if source_uri:
                t = Thesis(name_ru = name_ru, text_uri=text_uri, old_text_uri=base_url + old_text_uri, presentation_uri=presentation_uri,
                   supervisor_review_uri=supervisor_review_uri, reviewer_review_uri=reviewer_review_uri,
                   author=author, supervisor_id=supervisor_id, reviewer_id=2,
                   publish_year=pablish_year, type_id=3, course_id = 1, source_uri = source_uri)
            else:
                t = Thesis(name_ru = name_ru, text_uri=text_uri, old_text_uri=base_url + old_text_uri, presentation_uri=presentation_uri,
                   supervisor_review_uri=supervisor_review_uri, reviewer_review_uri=reviewer_review_uri,
                   author=author, supervisor_id=supervisor_id, reviewer_id=2,
                   publish_year=pablish_year, type_id=3, course_id = 1)


            db.session.add(t)
            db.session.commit()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "load":
            download = True

    #get_2020_02_03_03()
    #get_2020_09_03_04()
    #get_2019_09_03_04()
    #get_2019_02_03_03()
    #get_2019_02_04_03()
    #get_2020_371()
    #get_report_2020_02_03_03()
    #get_2019_371()
    #get_2019_343()
    #get_2019_344()
    #add_master_thesis_2020()

    get_2022_271()
    get_2022_371()
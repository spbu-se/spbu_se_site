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
download = True

def download_file(uri, safe_filename, save_path):

    # Skip if download == false
    if not download:
        return

    r = requests.get(uri, allow_redirects=True)
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

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "noload":
            download = False

    get_2020_02_03_03()
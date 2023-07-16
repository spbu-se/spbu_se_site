# -*- coding: utf-8 -*-

import base64
import json
import requests
import yadisk

from flask import redirect, url_for, request, flash
from flask_se_auth import login_required

# https://yandex.ru/dev/id/doc/ru/codes/code-url

CLIENT_ID = '10e079e42b49492295a39e2767e7b049'
CLIENT_SECRET = '621eab823cdf4649868b6e317963a054'
FOLDER_FOR_TABLE = 'static/practice/result_table/'

table_path = ''
area_id_ = -1
worktype_id_ = -1


def handle_yandex_table(table_name, area_id, worktype_id):
    global table_path
    global area_id_
    global worktype_id_
    table_path = table_name
    area_id_ = area_id
    worktype_id_ = worktype_id
    return get_code()


def get_code():
    redirect_uri = "http://127.0.0.1:5000/practice_admin/yandex_code"
    url = "https://oauth.yandex.ru/authorize?response_type=code" \
          + "&client_id=" + CLIENT_ID \
          + "&redirect_uri=" + redirect_uri
    return redirect(url)


def get_token(code):
    token_url = "https://oauth.yandex.ru/token"
    credentials_string = base64.b64encode((CLIENT_ID + ':' + CLIENT_SECRET).encode('ascii')).decode('ascii')
    headers = {"Authorization": "Basic " + credentials_string}
    content = "grant_type=authorization_code&code=" + code
    response = requests.post(token_url, headers=headers, data=content)
    if not response.ok:
        return 0

    data = json.loads(response.content)
    return data["access_token"]


@login_required
def yandex_code():
    code = request.args.get('code', type=str)
    if code is None:
        return redirect(url_for('index_admin', area_id=area_id_, worktype_id=worktype_id_))

    token = get_token(code)
    disk = yadisk.YaDisk(token=token)

    if not disk.check_token():
        flash('Неверный токен для Яндекс Диска', category='error')
        return redirect(url_for('index_admin', area_id=area_id_, worktype_id=worktype_id_))

    # Whole logic of working with yandex disk
    #
    #

    table_name = table_path.split('/')[-1]
    disk.download(table_path, FOLDER_FOR_TABLE + table_name)

    return redirect(url_for('index_admin', area_id=area_id_, worktype_id=worktype_id_))

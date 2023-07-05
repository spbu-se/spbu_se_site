# -*- coding: utf-8 -*-

import base64
import json
import requests
import yadisk

from flask import redirect, url_for, request
from flask_se_auth import login_required

# https://yandex.ru/dev/id/doc/ru/codes/code-url

CLIENT_ID = '10e079e42b49492295a39e2767e7b049'
CLIENT_SECRET = '621eab823cdf4649868b6e317963a054'


def get_code():
    url = "https://oauth.yandex.ru/authorize?response_type=code"\
          + "&client_id=" + CLIENT_ID\
          + "&redirect_uri=http://127.0.0.1:5000/practice_admin/yandex_code"
    return redirect(url)


def get_token(code):
    token_url = "https://oauth.yandex.ru/token"
    credentials_string = base64.b64encode((CLIENT_ID + ':' + CLIENT_SECRET).encode('ascii')).decode('ascii')
    headers = {"Authorization": "Basic " + credentials_string}
    content = "grant_type=authorization_code&code=" + code
    response = requests.post(token_url, headers=headers, data=content)
    if not response.ok:
        return 0

    print(response.content)
    data = json.loads(response.content)
    return data["access_token"]


@login_required
def yandex_code():
    code = request.args.get('code', type=str)
    if code is None:
        return redirect(url_for('index_admin'))

    token = get_token(code)
    disk = yadisk.YaDisk(token=token)
    print(disk.check_token())
    ls = disk.listdir('/')
    for file in ls:
        print(file.name)
    return redirect(url_for('index_admin'))

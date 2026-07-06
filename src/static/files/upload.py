# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0

import json

import requests

# РЎС‚СЂСѓРєС‚СѓСЂР° Thesis :
#
# type_id - С‚РёРї СЂР°Р±РѕС‚С‹ (СѓС‡РµР±РЅР°СЏ РїСЂР°РєС‚РёРєР°, Р±Р°РєР°Р»Р°РІСЂСЃРєР°СЏ Р’РљР , РјР°РіРёСЃС‚РµСЂСЃРєР°СЏ Р’РљР , ...):
#   - 2 - Bachelor_Report
#   - 3 - Bachelor_Thesis
#   - 4 - Master_Thesis
#   - 5 - Autumn_practice_2nd_year
#   - 6 - Spring_practice_2nd_year
#   - 7 - Autumn_practice_3rd_year
#   - 8 - Spring_practice_3rd_year
#
# course_id - РЅР°РїСЂР°РІР»РµРЅРёРµ РѕР±СѓС‡РµРЅРёСЏ:
#   - 1 - РњР°С‚РµРјР°С‚РёС‡РµСЃРєРѕРµ РѕР±РµСЃРїРµС‡РµРЅРёРµ Рё Р°РґРјРёРЅРёСЃС‚СЂРёСЂРѕРІР°РЅРёРµ РёРЅС„РѕСЂРјР°С†РёРѕРЅРЅС‹С… СЃРёСЃС‚РµРј (Р±Р°РєР°Р»Р°РІСЂРёР°С‚)
#   - 2 - РџСЂРѕРіСЂР°РјРјРЅР°СЏ РёРЅР¶РµРЅРµСЂРёСЏ (Р±Р°РєР°Р»Р°РІСЂРёР°С‚)
#   - 3 - РњР°С‚РµРјР°С‚РёС‡РµСЃРєРѕРµ РѕР±РµСЃРїРµС‡РµРЅРёРµ Рё Р°РґРјРёРЅРёСЃС‚СЂРёСЂРѕРІР°РЅРёРµ РёРЅС„РѕСЂРјР°С†РёРѕРЅРЅС‹С… СЃРёСЃС‚РµРј (РјР°РіРёСЃС‚СЂР°С‚СѓСЂР°)
#   - 4 - Р¤СѓРЅРґР°РјРµРЅС‚Р°Р»СЊРЅР°СЏ РёРЅС„РѕСЂРјР°С‚РёРєР° Рё РёРЅС„РѕСЂРјР°С†РёРѕРЅРЅС‹Рµ С‚РµС…РЅРѕР»РѕРіРёРё
#   - 5 - РРЅС„РѕСЂРјР°С†РёРѕРЅРЅС‹Рµ С‚РµС…РЅРѕР»РѕРіРёРё
#   - 6 - 344 РіСЂСѓРїРїР° (Р±Р°РєР°Р»Р°РІСЂРёР°С‚)
#   - 7 - РџСЂРѕРіСЂР°РјРјРЅР°СЏ РёРЅР¶РµРЅРµСЂРёСЏ (РјР°РіРёСЃС‚СЂР°С‚СѓСЂР°)
#   - 8 - РўРµС…РЅРѕР»РѕРіРёРё РїСЂРѕРіСЂР°РјРјРёСЂРѕРІР°РЅРёСЏ (Р±Р°РєР°Р»Р°РІСЂРёР°С‚)
#
# name_ru - РЅР°Р·РІР°РЅРёРµ СЂР°Р±РѕС‚С‹ РЅР° СЂСѓСЃСЃРєРѕРј СЏР·С‹РєРµ
# author - РїРѕР»РЅРѕРµ Р¤РРћ Р°РІС‚РѕСЂР° СЂР°Р±РѕС‚С‹
# source_uri - СЃСЃС‹Р»РєР° РЅР° СЂРµР·СѓР»СЊС‚Р°С‚ СЂР°Р±РѕС‚С‹
# supervisor - С„Р°РјРёР»РёСЏ СЂСѓРєРѕРІРѕРґРёС‚РµР»СЏ
# publish_year - РіРѕРґ РєСѓР±Р»РёРєР°С†РёРё
# secret_key - РєР»СЋС‡ РґР»СЏ РґРѕСЃС‚СѓРїР° Рє API
thesis_info = {
    "type_id": 3,
    "course_id": 2,
    "name_ru": "РћРїСЂРµРґРµР»РµРЅРёРµ РїРѕР»РѕСЃ РґРІРёР¶РµРЅРёСЏ РЅР° Р·Р°СЃРЅРµР¶РµРЅРЅРѕР№ РґРѕСЂРѕРіРµ РїРѕ РІРёРґРµРѕ",
    "author": "Р›СѓРЅРµРІ РђСЂС‚РµРј Р•РІРіРµРЅСЊРµРІРёС‡",
    "source_uri": "https://github.com/artemlunev2000/winter-road-detection",
    "supervisor": "Р›РёС‚РІРёРЅРѕРІ",
    "publish_year": 2022,
    "secret_key": "9d1fe6c77d53465cc50afc7d57b3ca84",
}

# РўРµРєСЃС‚ СЂР°Р±РѕС‚С‹
thesis_text = "Lunev-report.pdf"

# РџСЂРµР·РµРЅС‚Р°С†РёСЏ
presentation = "Lunev-presentation.pdf"

# РћС‚Р·С‹РІ СЂСѓРєРѕРІРѕРґРёС‚РµР»СЏ
supervisor_review = "Lunev-review.pdf"

# РћС‚Р·С‹РІ СЂРµС†РµРЅР·РµРЅС‚Р° РёР»Рё РєРѕРЅСЃСѓР»СЊС‚Р°РЅС‚Р°
reviewer_review = "Lunev-review-consultant.pdf"

# URI API
url = "https://se.math.spbu.ru/post_theses"

# Р•СЃР»Рё РЅРµС‚ РїСЂРµР·РµРЅС‚Р°С†РёРё РёР»Рё РѕС‚Р·С‹РІР°, С‚Рѕ РїСЂРѕСЃС‚Рѕ Р·Р°РєРѕРјРјРµРЅС‚РёСЂСѓР№С‚Рµ РЅСѓР¶РЅРѕРµ РїРѕР»Рµ.
files = [
    ("thesis_text", (thesis_text, open(thesis_text, "rb"), "application/octet")),
    (
        "reviewer_review",
        (reviewer_review, open(reviewer_review, "rb"), "application/octet"),
    ),
    ("presentation", (presentation, open(presentation, "rb"), "application/octet")),
    (
        "supervisor_review",
        (supervisor_review, open(supervisor_review, "rb"), "application/octet"),
    ),
    ("thesis_info", ("thesis_info", json.dumps(thesis_info), "application/json")),
]

r = requests.post(url, files=files, allow_redirects=False, timeout=30)
print(str(r.content, "utf-8"))

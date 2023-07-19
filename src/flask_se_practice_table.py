# -*- coding: utf-8 -*-

import pandas as pd

TABLE_COLUMNS = {
    "name": "ФИО",
    "supervisor": "Научный руководитель",
    "consultant": "Консультант (если есть), полностью ФИО, должность и компания",
    "theme": "Тема"
}


def read_table(path_to_table):
    # Read all records from sheet 'СП'
    # If such sheet doesn't exist, read records from first sheet
    try:
        records = pd.read_excel(path_to_table, sheet_name='СП')
    except ValueError:
        records = pd.read_excel(path_to_table)

    # print(records.loc[0].index)
    # print(records.loc[0]['ФИО'])

    for (index, row) in records.iterrows():
        print(index, row[TABLE_COLUMNS["name"]], "-", row[TABLE_COLUMNS["theme"]], "-", row[TABLE_COLUMNS["supervisor"]])

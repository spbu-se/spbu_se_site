# -*- coding: utf-8 -*-

import pandas as pd

from se_models import Users, CurrentThesis
from flask import flash

FOLDER_FOR_TABLE = 'static/practice/result_table/'
TABLE_COLUMNS = {
    "name": "ФИО",
    "supervisor": "Научный руководитель",
    "consultant": "Консультант (если есть), полностью ФИО, должность и компания",
    "theme": "Тема",
}


def edit_table(path_to_table, sheet_name, area_id, worktype_id):
    table_df = read_table(path_to_table, sheet_name)
    if table_df is None:
        return

    for index, row in table_df.iterrows():
        print(index, row[TABLE_COLUMNS["name"]],
              "-", row[TABLE_COLUMNS["theme"]],
              "-", row[TABLE_COLUMNS["supervisor"]])

        user = find_user(full_name=row[TABLE_COLUMNS["name"]])
        if user is None:
            continue
        print(user)

        current_thesis = find_current_thesis(user, area_id, worktype_id)
        print(current_thesis)
        row[TABLE_COLUMNS["name"]] = "Ololo"

    with pd.ExcelWriter(FOLDER_FOR_TABLE + "test.xlsx", mode="a", if_sheet_exists="overlay") as writer:
        table_df.to_excel(writer, index=False, sheet_name=sheet_name)


def read_table(path_to_table, sheet_name) -> pd.DataFrame or None:
    # Read all records from sheet with <sheet_name> name
    # If such sheet doesn't exist, read records from first sheet
    try:
        table_df = (pd.read_excel(path_to_table)
                    if sheet_name == ""
                    else pd.read_excel(path_to_table, sheet_name=sheet_name))
    except ValueError:
        flash(f"В таблице не существует листа с названием {sheet_name}.", category='error')
        return None
    return table_df


def find_user(full_name: str) -> Users or None:
    if len(full_name.split()) != 3:
        return None

    last_name, first_name, middle_name = full_name.split()
    user = (
        Users.query.filter_by(last_name=last_name)
        .filter_by(first_name=first_name)
        .filter_by(middle_name=middle_name)
        .first()
    )
    return user


def find_current_thesis(user: Users, area_id, worktype_id) -> CurrentThesis or None:
    thesis = (
        CurrentThesis.query.filter_by(author_id=user.id).
        filter_by(area_id=area_id).
        filter_by(worktype_id=worktype_id).
        filter_by(deleted=False).
        filter_by(status=1)
        .first()
    )
    return thesis

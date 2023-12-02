"""
   Copyright 2023 Alexander Slugin

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""
# -*- coding: utf-8 -*-

import os.path
import openpyxl
import pandas as pd

from flask import flash
from se_models import Users, CurrentThesis
from flask_se_practice_config import TABLE_COLUMNS


def edit_table(
    path_to_table, area_id, worktype_id, column_names_list=None, sheet_name=""
):
    if column_names_list is None:
        column_names_list = list(TABLE_COLUMNS.items())

    if os.path.exists(path_to_table):
        table_df = read_table(path_to_table, sheet_name)
        if table_df is None:
            return
    else:
        columns = [pair[1] for pair in column_names_list]
        table_df = pd.DataFrame(columns=columns)

        table = openpyxl.Workbook()
        if sheet_name == "":
            sheet_name = table.active.title
        else:
            table.active.title = sheet_name
        table.save(path_to_table)

    column_names = dict(column_names_list)
    checked_thesis_ids = set()
    for index, row in table_df.iterrows():
        try:
            user = find_user(full_name=row[column_names["name"]])
        except KeyError:
            flash(
                f"В таблице не существует столбца с названием \"{column_names['name']}\"",
                category="error",
            )
            return

        if user is None:
            continue

        current_thesis = find_current_thesis(user, area_id, worktype_id)
        if current_thesis is None:
            continue

        try:
            add_new_data_to_table(row, current_thesis, user, column_names)
        except KeyError:
            return
        checked_thesis_ids.add(current_thesis.id)

    all_thesises = get_all_thesises(area_id, worktype_id)
    for thesis in all_thesises:
        if thesis.id in checked_thesis_ids:
            continue
        empty_row = pd.DataFrame([{}], columns=table_df.columns)
        table_df = pd.concat([table_df, empty_row], ignore_index=True)
        try:
            add_new_data_to_table(
                table_df.loc[len(table_df) - 1],
                current_thesis=thesis,
                user=thesis.user,
                column_names=column_names,
            )
        except KeyError:
            return

    table_df = table_df.sort_values(by=column_names["name"])

    with pd.ExcelWriter(path_to_table, mode="a", if_sheet_exists="overlay") as writer:
        if sheet_name == "":
            table_df.to_excel(writer, index=False)
        else:
            table_df.to_excel(writer, index=False, sheet_name=sheet_name)


def read_table(path_to_table, sheet_name) -> pd.DataFrame or None:
    # Read all records from sheet with <sheet_name> name
    try:
        table_df = (
            pd.read_excel(path_to_table)
            if sheet_name == ""
            else pd.read_excel(path_to_table, sheet_name=sheet_name)
        )
    except ValueError:
        flash(
            f"В существующей таблице нет листа с названием {sheet_name}",
            category="error",
        )
        return None
    return table_df


def find_user(full_name: str) -> Users or None:
    name = full_name.split()
    if len(name) < 2:
        return None

    user = (
        Users.query.filter_by(last_name=name[0]).filter_by(first_name=name[1]).first()
    )
    return user


def find_current_thesis(user: Users, area_id, worktype_id) -> CurrentThesis or None:
    thesis = (
        CurrentThesis.query.filter_by(author_id=user.id)
        .filter_by(area_id=area_id)
        .filter_by(worktype_id=worktype_id)
        .filter_by(deleted=False)
        .filter_by(status=1)
        .filter(CurrentThesis.title != None)
        .first()
    )
    return thesis


def get_all_thesises(area_id, worktype_id) -> list:
    thesises = (
        CurrentThesis.query.filter_by(area_id=area_id)
        .filter_by(worktype_id=worktype_id)
        .filter_by(deleted=False)
        .filter_by(status=1)
        .filter(CurrentThesis.title != None)
        .all()
    )
    return thesises


def add_new_data_to_table(
    row: pd.Series, current_thesis: CurrentThesis, user: Users, column_names
):
    update_if_cell_is_empty(row, column_names["name"], user.get_name())
    update_if_cell_is_empty(row, column_names["theme"], current_thesis.title)
    update_if_cell_is_empty(row, column_names["supervisor"], current_thesis.supervisor)
    update_if_cell_is_empty(row, column_names["consultant"], current_thesis.consultant)
    update_if_cell_is_empty(row, column_names["how_to_contact"], user.how_to_contact)
    update_if_cell_is_empty(
        row, column_names["text"], "да" if current_thesis.text_uri else ""
    )
    update_if_cell_is_empty(
        row,
        column_names["supervisor_review"],
        "да" if current_thesis.supervisor_review_uri else "",
    )
    update_if_cell_is_empty(
        row,
        column_names["reviewer_review"],
        "да" if current_thesis.reviewer_review_uri else "",
    )
    update_if_cell_is_empty(row, column_names["code"], current_thesis.code_link)
    update_if_cell_is_empty(row, column_names["committer"], current_thesis.account_name)
    update_if_cell_is_empty(
        row,
        column_names["presentation"],
        "да" if current_thesis.presentation_uri else "",
    )


def update_if_cell_is_empty(row: pd.Series, column_name, new_value):
    try:
        if pd.isna(row[column_name]) or row[column_name] in {None, ""}:
            row[column_name] = new_value
    except KeyError:
        flash(
            f'В таблице не существует столбца с названием "{column_name}"',
            category="error",
        )
        raise KeyError

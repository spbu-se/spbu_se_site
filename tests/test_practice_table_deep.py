# -*- coding: utf-8 -*-
from unittest.mock import MagicMock, patch

import numpy as np
import pandas as pd
import pytest


def _mock_table_df(rows=None):
    from flask_se_practice_config import TABLE_COLUMNS as TC

    col_values = [v for _, v in TC.items()]
    mock_df = MagicMock()
    if rows is None:
        rows = [(0, pd.Series(dict.fromkeys(col_values, "")))]
    mock_df.iterrows.return_value = rows
    mock_df.columns = col_values
    mock_df.sort_values.return_value = mock_df
    return mock_df


class TestReadTable:
    def test_read_table_value_error(self, app_ctx):
        from flask_se import app
        from flask_se_practice_table import read_table

        with patch("flask_se_practice_table.pd.read_excel") as mock_read:
            mock_read.side_effect = ValueError("bad sheet")
            with app.test_request_context():
                result = read_table("/tmp/t.xlsx", "BadSheet")
        assert result is None

    def test_read_table_file_not_found(self, app_ctx):
        from flask_se import app
        from flask_se_practice_table import read_table

        with app.test_request_context():
            result = read_table("/tmp/__nonexistent_xyz__.xlsx", "S1")
        assert result is None

    @pytest.mark.parametrize(
        ("sheet_name", "expected_column"),
        [("S1", "A"), ("", None)],
        ids=["named_sheet", "default_sheet"],
    )
    def test_read_table_success(self, app_ctx, sheet_name, expected_column):
        import os
        import tempfile

        from flask_se import app
        from flask_se_practice_table import read_table

        df = pd.DataFrame({"A": [1]})
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
            tmp_name = tmp.name
        try:
            with pd.ExcelWriter(tmp_name) as w:
                if sheet_name:
                    df.to_excel(w, sheet_name=sheet_name, index=False)
                else:
                    df.to_excel(w, index=False)
            with app.test_request_context():
                result = read_table(tmp_name, sheet_name)
            assert result is not None
            if expected_column is not None:
                assert expected_column in result.columns
        finally:
            os.unlink(tmp_name)


class TestFindUser:
    @pytest.mark.parametrize(
        ("email", "first", "last", "middle", "query", "expected_email"),
        [
            ("a@b.ru", "Ivan", "Petrov", None, "Petrov Ivan", "a@b.ru"),
            (None, None, None, None, "Petrov", None),
            (None, None, None, None, "Nobody Here", None),
            ("b@b.ru", "Petr", "Sidorov", "Ivanovich", "Sidorov Petr", "b@b.ru"),
        ],
        ids=["full_name", "short_name", "not_found", "middle_name_ignored"],
    )
    def test_find_user(self, app_ctx, email, first, last, middle, query, expected_email):
        from flask_se_practice_table import find_user
        from se_models import Users, db

        if email is not None:
            u = Users(email=email, first_name=first, last_name=last, middle_name=middle)
            db.session.add(u)
            db.session.commit()
        result = find_user(query)
        if expected_email is None:
            assert result is None
        else:
            assert result is not None
            assert result.email == expected_email


class TestFindCurrentThesis:
    def test_find_current_thesis_found(self, app_ctx):
        from flask_se_practice_table import find_current_thesis
        from se_models import CurrentThesis, Users, db

        u = Users(email="ct@t.ru", first_name="CT", last_name="User")
        db.session.add(u)
        db.session.flush()

        ct = CurrentThesis(author_id=u.id, worktype_id=1, area_id=1)
        ct.title = "Test Thesis"
        ct.status = 1
        ct.deleted = False
        db.session.add(ct)
        db.session.commit()
        result = find_current_thesis(u, 1, 1)
        assert result is not None
        assert result.title == "Test Thesis"

    def test_find_current_thesis_not_found(self, app_ctx):
        from flask_se_practice_table import find_current_thesis
        from se_models import Users, db

        u = Users(email="nf@t.ru", first_name="NotFound", last_name="User")
        db.session.add(u)
        db.session.commit()
        result = find_current_thesis(u, 999, 999)
        assert result is None


class TestUpdateIfCellIsEmpty:
    @pytest.mark.parametrize(
        ("initial", "expected"),
        [
            (float("nan"), "new_value"),
            (np.nan, "new_value"),
            (None, "new_value"),
            ("", "new_value"),
            ("existing", "existing"),
        ],
        ids=["nan_via_float", "nan_via_numpy", "none", "empty_string", "non_empty_preserved"],
    )
    def test_update_if_cell_is_empty(self, initial, expected):
        from flask_se_practice_table import update_if_cell_is_empty

        row = {"name": initial}
        update_if_cell_is_empty(row, "name", "new_value")
        assert row["name"] == expected

    def test_update_missing_column_raises_with_flash(self, app_ctx):
        from flask_se import app
        from flask_se_practice_table import update_if_cell_is_empty

        row = {"name": "val"}
        with app.test_request_context(), pytest.raises(KeyError):
            update_if_cell_is_empty(row, "nonexistent", "new_value")


class TestAddNewDataToTable:
    def test_add_data_all_fields(self, app_ctx):
        from flask_se_practice_config import TABLE_COLUMNS
        from flask_se_practice_table import add_new_data_to_table
        from se_models import Users, db

        u = Users(email="all@t.ru", first_name="Test", last_name="User")
        db.session.add(u)
        db.session.commit()

        ct_mock = MagicMock()
        ct_mock.title = "My Thesis"
        ct_mock.supervisor = "Dr. Smith"
        ct_mock.consultant = "Dr. Jones"
        ct_mock.text_uri = "text.pdf"
        ct_mock.supervisor_review_uri = "review.pdf"
        ct_mock.reviewer_review_uri = "rev.pdf"
        ct_mock.code_link = "https://github.com/test"
        ct_mock.account_name = "testuser"
        ct_mock.presentation_uri = "slides.pdf"

        columns = dict(TABLE_COLUMNS.items())
        col_values = list(columns.values())

        row = pd.Series(dict.fromkeys(col_values, ""))
        add_new_data_to_table(row, ct_mock, u, columns)

        assert row[columns["name"]] == u.get_name()
        assert row[columns["theme"]] == "My Thesis"
        assert row[columns["supervisor"]] == "Dr. Smith"
        assert row[columns["consultant"]] == "Dr. Jones"
        assert row[columns["how_to_contact"]] == u.how_to_contact
        assert row[columns["text"]] == "да"
        assert row[columns["supervisor_review"]] == "да"
        assert row[columns["reviewer_review"]] == "да"
        assert row[columns["code"]] == "https://github.com/test"
        assert row[columns["committer"]] == "testuser"
        assert row[columns["presentation"]] == "да"

    def test_add_data_empty_uris(self, app_ctx):
        from flask_se_practice_config import TABLE_COLUMNS
        from flask_se_practice_table import add_new_data_to_table
        from se_models import Users, db

        u = Users(email="empty@t.ru", first_name="Empty", last_name="Fields")
        db.session.add(u)
        db.session.commit()

        ct_mock = MagicMock()
        ct_mock.title = "T"
        ct_mock.supervisor = ""
        ct_mock.consultant = ""
        ct_mock.text_uri = None
        ct_mock.supervisor_review_uri = None
        ct_mock.reviewer_review_uri = None
        ct_mock.code_link = ""
        ct_mock.account_name = ""
        ct_mock.presentation_uri = None

        columns = dict(TABLE_COLUMNS.items())
        col_values = list(columns.values())

        row = pd.Series(dict.fromkeys(col_values, ""))
        add_new_data_to_table(row, ct_mock, u, columns)

        assert row[columns["text"]] == ""
        assert row[columns["supervisor_review"]] == ""
        assert row[columns["reviewer_review"]] == ""
        assert row[columns["presentation"]] == ""

    def test_add_data_key_error(self, app_ctx):
        from flask_se import app
        from flask_se_practice_table import add_new_data_to_table
        from se_models import Users, db

        u = Users(email="ke@t.ru", first_name="Key", last_name="Error")
        db.session.add(u)
        db.session.commit()

        ct_mock = MagicMock()
        ct_mock.title = "T"
        ct_mock.supervisor = ""
        ct_mock.consultant = ""
        ct_mock.text_uri = None
        ct_mock.supervisor_review_uri = None
        ct_mock.reviewer_review_uri = None
        ct_mock.code_link = ""
        ct_mock.account_name = ""
        ct_mock.presentation_uri = None

        row = pd.Series({})
        with app.test_request_context(), pytest.raises(KeyError):
            add_new_data_to_table(row, ct_mock, u, {"name": "name_col"})


class TestEditTable:
    @patch("flask_se_practice_table.os.path.exists", return_value=True)
    @patch("flask_se_practice_table.read_table", return_value=None)
    def test_edit_table_read_returns_none(self, mock_read, mock_exists, app_ctx):
        from flask_se_practice_table import edit_table

        edit_table("/tmp/test.xlsx", area_id=1, worktype_id=1)

    @patch("flask_se_practice_table.openpyxl")
    @patch("flask_se_practice_table.pd")
    def test_edit_table_new_file_custom_sheet(self, mock_pd, mock_openpyxl, app_ctx):
        from flask_se_practice_table import edit_table

        mock_pd.DataFrame.return_value = MagicMock()
        mock_df = MagicMock()
        mock_pd.DataFrame.return_value = mock_df
        mock_df.iterrows.return_value = []
        mock_wb = MagicMock()
        mock_openpyxl.Workbook.return_value = mock_wb
        edit_table("/tmp/test.xlsx", area_id=1, worktype_id=1, sheet_name="CustomSheet")
        assert mock_wb.active.title == "CustomSheet"

    @patch("flask_se_practice_table.openpyxl")
    @patch("flask_se_practice_table.pd")
    def test_edit_table_new_file_default_sheet(self, mock_pd, mock_openpyxl, app_ctx):
        from flask_se_practice_table import edit_table

        mock_pd.DataFrame.return_value = MagicMock()
        mock_df = MagicMock()
        mock_pd.DataFrame.return_value = mock_df
        mock_df.iterrows.return_value = []
        mock_wb = MagicMock()
        mock_wb.active.title = "DefaultSheet"
        mock_openpyxl.Workbook.return_value = mock_wb
        edit_table("/tmp/test.xlsx", area_id=1, worktype_id=1)
        assert mock_wb.save.called

    @patch("flask_se_practice_table.os.path.exists", return_value=True)
    def test_edit_table_existing_with_data(self, mock_exists, app_ctx):
        from flask_se import app
        from flask_se_practice_table import edit_table

        mock_df = _mock_table_df()

        with (
            patch("flask_se_practice_table.read_table", return_value=mock_df),
            patch("flask_se_practice_table.find_user") as mock_find,
            patch("flask_se_practice_table.find_current_thesis") as mock_ct,
            patch("flask_se_practice_table.get_all_thesises", return_value=[]),
            patch("flask_se_practice_table.add_new_data_to_table") as mock_add,
            patch("flask_se_practice_table.pd.ExcelWriter"),
            app.test_request_context(),
        ):
            mock_find.return_value = MagicMock()
            mock_ct.return_value = MagicMock()
            edit_table(
                "/tmp/test.xlsx",
                area_id=1,
                worktype_id=1,
            )
        mock_add.assert_called_once()

    @patch("flask_se_practice_table.os.path.exists", return_value=True)
    def test_edit_table_user_not_found_skips_row(self, mock_exists, app_ctx):
        from flask_se import app
        from flask_se_practice_table import edit_table

        mock_df = _mock_table_df()

        with (
            patch("flask_se_practice_table.read_table", return_value=mock_df),
            patch("flask_se_practice_table.find_user", return_value=None) as mock_find,
            patch("flask_se_practice_table.get_all_thesises", return_value=[]),
            patch("flask_se_practice_table.pd.ExcelWriter"),
            app.test_request_context(),
        ):
            edit_table("/tmp/test.xlsx", area_id=1, worktype_id=1)
        mock_find.assert_called_once()

    @patch("flask_se_practice_table.os.path.exists", return_value=True)
    def test_edit_table_no_thesis_skips_row(self, mock_exists, app_ctx):
        from flask_se import app
        from flask_se_practice_table import edit_table

        mock_df = _mock_table_df()

        with (
            patch("flask_se_practice_table.read_table", return_value=mock_df),
            patch("flask_se_practice_table.find_user") as mock_find,
            patch("flask_se_practice_table.find_current_thesis", return_value=None) as mock_ct,
            patch("flask_se_practice_table.get_all_thesises", return_value=[]),
            patch("flask_se_practice_table.pd.ExcelWriter"),
            app.test_request_context(),
        ):
            mock_find.return_value = MagicMock()
            edit_table(
                "/tmp/test.xlsx",
                area_id=1,
                worktype_id=1,
            )
        mock_ct.assert_called_once()

    @patch("flask_se_practice_table.os.path.exists", return_value=True)
    def test_edit_table_key_error_in_row_loop(self, mock_exists, app_ctx):
        from flask_se import app
        from flask_se_practice_table import edit_table

        mock_df = _mock_table_df()

        with (
            patch("flask_se_practice_table.read_table", return_value=mock_df),
            patch("flask_se_practice_table.find_user") as mock_find,
            patch("flask_se_practice_table.find_current_thesis") as mock_ct,
            patch(
                "flask_se_practice_table.add_new_data_to_table",
                side_effect=KeyError("test"),
            ),
            app.test_request_context(),
        ):
            mock_find.return_value = MagicMock()
            mock_ct.return_value = MagicMock()
            edit_table("/tmp/test.xlsx", area_id=1, worktype_id=1)

    @patch("flask_se_practice_table.os.path.exists", return_value=True)
    def test_edit_table_key_error_in_missing_thesis_loop(self, mock_exists, app_ctx):
        from flask_se import app
        from flask_se_practice_table import edit_table

        mock_df = _mock_table_df([])

        mock_thesis = MagicMock()
        mock_thesis.id = 999
        mock_thesis.user = MagicMock()

        with (
            patch("flask_se_practice_table.read_table", return_value=mock_df),
            patch("flask_se_practice_table.pd.concat", return_value=mock_df),
            patch(
                "flask_se_practice_table.get_all_thesises",
                return_value=[mock_thesis],
            ),
            patch(
                "flask_se_practice_table.add_new_data_to_table",
                side_effect=KeyError("test"),
            ),
            app.test_request_context(),
        ):
            edit_table("/tmp/test.xlsx", area_id=1, worktype_id=1)

    @patch("flask_se_practice_table.os.path.exists", return_value=True)
    def test_edit_table_adds_missing_thesises(self, mock_exists, app_ctx):
        from flask_se import app
        from flask_se_practice_table import edit_table

        mock_df = _mock_table_df([])

        mock_thesis = MagicMock()
        mock_thesis.id = 777
        mock_thesis.user = MagicMock()

        with (
            patch("flask_se_practice_table.read_table", return_value=mock_df),
            patch("flask_se_practice_table.pd.concat", return_value=mock_df),
            patch(
                "flask_se_practice_table.get_all_thesises",
                return_value=[mock_thesis],
            ),
            patch("flask_se_practice_table.add_new_data_to_table") as mock_add,
            patch("flask_se_practice_table.pd.ExcelWriter"),
            app.test_request_context(),
        ):
            edit_table("/tmp/test.xlsx", area_id=1, worktype_id=1)
        assert mock_add.called

    @patch("flask_se_practice_table.os.path.exists", return_value=True)
    def test_edit_table_key_error_from_missing_column(self, mock_exists, app_ctx):
        from flask_se import app
        from flask_se_practice_table import edit_table

        mock_df = MagicMock()
        mock_df.iterrows.return_value = [(0, pd.Series({"wrong_col": "val"}))]

        with (
            patch("flask_se_practice_table.read_table", return_value=mock_df),
            app.test_request_context(),
        ):
            edit_table("/tmp/test.xlsx", area_id=1, worktype_id=1)

    @patch("flask_se_practice_table.os.path.exists", return_value=True)
    def test_edit_table_skips_already_checked_thesis(self, mock_exists, app_ctx):
        from flask_se import app
        from flask_se_practice_table import edit_table

        mock_df = _mock_table_df()

        mock_thesis = MagicMock()
        mock_thesis.id = 42

        with (
            patch("flask_se_practice_table.read_table", return_value=mock_df),
            patch("flask_se_practice_table.find_user") as mock_find,
            patch(
                "flask_se_practice_table.find_current_thesis",
                return_value=mock_thesis,
            ),
            patch(
                "flask_se_practice_table.get_all_thesises",
                return_value=[mock_thesis],
            ),
            patch("flask_se_practice_table.add_new_data_to_table"),
            patch("flask_se_practice_table.pd.ExcelWriter"),
            patch(
                "flask_se_practice_table.pd.concat",
                return_value=mock_df,
            ),
            app.test_request_context(),
        ):
            mock_find.return_value = MagicMock()
            edit_table(
                "/tmp/test.xlsx",
                area_id=1,
                worktype_id=1,
            )

    def test_get_all_thesises(self, app_ctx):
        from flask_se_practice_table import get_all_thesises
        from se_models import CurrentThesis, Users, db

        u = Users(email="ga@t.ru", first_name="GA", last_name="User")
        db.session.add(u)
        db.session.flush()

        ct = CurrentThesis(author_id=u.id, worktype_id=1, area_id=1)
        ct.title = "Visible Thesis"
        ct.status = 1
        ct.deleted = False
        db.session.add(ct)
        db.session.commit()

        result = get_all_thesises(1, 1)
        assert len(result) >= 1

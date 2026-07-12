# -*- coding: utf-8 -*-
from unittest.mock import MagicMock, patch


class TestPracticeTable:
    @patch("flask_se_practice_table.openpyxl", MagicMock())
    @patch("flask_se_practice_table.pd")
    def test_edit_table_new_file(self, mock_pd, app_ctx):
        from flask_se_practice_table import edit_table

        mock_pd.DataFrame.return_value = MagicMock()
        mock_df = MagicMock()
        mock_pd.DataFrame.return_value = mock_df
        mock_df.iterrows.return_value = []
        edit_table("/tmp/test.xlsx", area_id=1, worktype_id=1)
        assert mock_pd.DataFrame.called

    @patch("flask_se_practice_table.openpyxl")
    @patch("flask_se_practice_table.pd")
    def test_edit_table_creates_workbook_for_new_path(self, mock_pd, mock_openpyxl, app_ctx):
        from flask_se_practice_table import edit_table

        mock_pd.DataFrame.return_value = MagicMock()
        mock_df = MagicMock()
        mock_pd.DataFrame.return_value = mock_df
        mock_df.iterrows.return_value = []
        mock_wb = MagicMock()
        mock_openpyxl.Workbook.return_value = mock_wb
        import os

        edit_table(os.path.join("/tmp", "nonexistent_test.xlsx"), area_id=1, worktype_id=1)
        assert mock_openpyxl.Workbook.called

    @patch("flask_se_practice_table.openpyxl")
    @patch("flask_se_practice_table.pd")
    def test_edit_table_with_existing_path(self, mock_pd, mock_openpyxl, seeded_app_ctx):
        import os
        import tempfile

        from flask_se_practice_table import edit_table

        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
            tmp_name = tmp.name
        try:
            mock_pd.read_table = MagicMock(return_value=None)
            mock_pd.DataFrame.return_value = MagicMock()
            mock_df = MagicMock()
            mock_pd.DataFrame.return_value = mock_df
            mock_df.iterrows.return_value = []
            mock_openpyxl.Workbook.return_value = MagicMock()
            edit_table(tmp_name, area_id=1, worktype_id=1)
        finally:
            os.unlink(tmp_name)

    def test_read_table_nonexistent(self, app_ctx):
        from flask_se import app
        from flask_se_practice_table import read_table

        with app.test_request_context():
            result = read_table("/tmp/nonexistent_file.xlsx", "Sheet1")
        assert result is None

    def test_imports_available(self):
        from flask_se_practice_table import edit_table, get_all_thesises, read_table

        assert callable(edit_table)
        assert callable(read_table)
        assert callable(get_all_thesises)

from unittest.mock import PropertyMock, patch, MagicMock

import pytest


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
        import tempfile, os
        from flask_se_practice_table import edit_table
        tmp = tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False)
        tmp.close()
        try:
            mock_pd.read_table = MagicMock(return_value=None)
            mock_pd.DataFrame.return_value = MagicMock()
            mock_df = MagicMock()
            mock_pd.DataFrame.return_value = mock_df
            mock_df.iterrows.return_value = []
            mock_openpyxl.Workbook.return_value = MagicMock()
            edit_table(tmp.name, area_id=1, worktype_id=1)
        finally:
            os.unlink(tmp.name)

    def test_read_table_nonexistent(self):
        from flask_se_practice_table import read_table
        with pytest.raises(FileNotFoundError):
            read_table("/tmp/nonexistent_file.xlsx", "Sheet1")

    def test_imports_available(self):
        from flask_se_practice_table import edit_table, read_table, get_all_thesises
        assert callable(edit_table)
        assert callable(read_table)
        assert callable(get_all_thesises)

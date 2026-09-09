# -*- coding: utf-8 -*-
from se_constants import (
    CURRENT_THESIS_STATUS_OPTIONS,
    DIPLOMA_THEME_ARCHIVED,
    DIPLOMA_THEME_EDITABLE_STATUS_OPTIONS,
    DIPLOMA_THEME_STATUS_OPTIONS,
    REVIEW_DIPLOMA_STATUS_OPTIONS,
    SCIENCE_DEGREE_OPTIONS,
)


class TestStatusOptionSets:
    """Constants mirror the live semantics of the admin surfaces."""

    def test_diploma_full_set_covers_statuses_0_4_including_archive(self):
        assert DIPLOMA_THEME_STATUS_OPTIONS == (
            (0, "На проверке"),
            (1, "Требуется доработка"),
            (2, "Одобрена"),
            (3, "В архиве"),
            (4, "Отклонена"),
        )
        assert DIPLOMA_THEME_ARCHIVED == 3

    def test_diploma_editable_set_excludes_archive_value(self):
        values = {value for value, _ in DIPLOMA_THEME_EDITABLE_STATUS_OPTIONS}
        assert values == {0, 1, 2, 4}
        assert DIPLOMA_THEME_ARCHIVED not in values

    def test_review_diploma_is_the_workflow_subset(self):
        assert REVIEW_DIPLOMA_STATUS_OPTIONS == (
            (0, "На проверке"),
            (1, "Требуется доработка"),
            (2, "Одобрена"),
        )

    def test_current_thesis_statuses_are_1_and_2(self):
        assert CURRENT_THESIS_STATUS_OPTIONS == (
            (1, "Текущая работа"),
            (2, "Завершенная работа"),
        )

    def test_labels_match_across_diploma_and_review(self):
        full = dict(DIPLOMA_THEME_STATUS_OPTIONS)
        for value, label in REVIEW_DIPLOMA_STATUS_OPTIONS:
            assert full[value] == label


class TestScienceDegreeOptions:
    def test_degrees_are_unique_and_nonempty(self):
        assert SCIENCE_DEGREE_OPTIONS == ("д.ф.-м.н.", "д.т.н.", "к.ф.-м.н.", "к.т.н.")
        assert len(set(SCIENCE_DEGREE_OPTIONS)) == len(SCIENCE_DEGREE_OPTIONS)
        assert all(degree for degree in SCIENCE_DEGREE_OPTIONS)


class TestImportSafety:
    def test_module_imports_without_flask_context(self):
        import se_constants

        assert se_constants.DIPLOMA_THEME_ARCHIVED == 3

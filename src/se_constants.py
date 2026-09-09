# -*- coding: utf-8 -*-
"""Canonical domain constants (single source of truth).

Status/label pairs and option sets that were previously duplicated as
literals across admin views, CRUD form/column/filter definitions and
tests. Views must import these instead of spelling values out.

Module is import-safe without a Flask app context — no project imports.
"""

# Diploma theme status (DiplomaThemes.status). Value 3 is an internal
# archive-transition state: it is never set through the free-edit form
# (archive/reopen go through the dedicated actions that own `prev_status`),
# but it must appear wherever themes are displayed or filtered.
DIPLOMA_THEME_STATUS_OPTIONS = (
    (0, "На проверке"),
    (1, "Требуется доработка"),
    (2, "Одобрена"),
    (3, "В архиве"),
    (4, "Отклонена"),
)
DIPLOMA_THEME_ARCHIVED = 3
# Statuses an editor may pick freely; 3 is deliberately excluded.
DIPLOMA_THEME_EDITABLE_STATUS_OPTIONS = (
    (0, "На проверке"),
    (1, "Требуется доработка"),
    (2, "Одобрена"),
    (4, "Отклонена"),
)

# Review-diploma workflow (review table) uses a subset of the same labels.
REVIEW_DIPLOMA_STATUS_OPTIONS = (
    (0, "На проверке"),
    (1, "Требуется доработка"),
    (2, "Одобрена"),
)

# Current-thesis lifecycle (CurrentThesis.status).
CURRENT_THESIS_STATUS_OPTIONS = (
    (1, "Текущая работа"),
    (2, "Завершенная работа"),
)

# Staff academic-degree choices (Staff.science_degree). The empty
# "not set" choice is added by the field definition, not listed here.
SCIENCE_DEGREE_OPTIONS = (
    "д.ф.-м.н.",
    "д.т.н.",
    "к.ф.-м.н.",
    "к.т.н.",
)

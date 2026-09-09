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
# Review-list filter only shows items still in the workflow.
REVIEW_DIPLOMA_OPEN_STATUS_OPTIONS = (
    (0, "На проверке"),
    (1, "Требуется доработка"),
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

# Area-of-study lookup (AreasOfStudy). Row id 1 is the "Направление обучения"
# placeholder that practice/review/practice_admin option lists exclude.
AREA_DEFAULT_ID = 1

# AreasOfStudy rows whose shared plain name must be disambiguated on screen.
# Two seeded rows share the name "Программная инженерия" (bachelor/master);
# mapping is id-keyed for the deterministic seed, and the suffix is applied
# only while the row still carries the expected plain name (guards against a
# stale mapping after a reseed/reorder). Technical debt: a code-level override
# for a data-modeling defect (duplicate-name rows); normalize in the DB later
# (additive `code` column or row merge) — see docs/DESIGN_DECISIONS.md.
AREA_PROGRAM_OVERRIDES = {
    3: ("Программная инженерия", "бак"),
    7: ("Программная инженерия", "маг"),
}


def area_display_name(area_id: int | None, name: str) -> str:
    """Human label for an area row, disambiguating known duplicates.

    Falls back to the plain name for every non-overridden row, so this is
    safe to call on every area-option builder.
    """
    override = AREA_PROGRAM_OVERRIDES.get(area_id)
    if override is not None and override[0] == name:
        return f"{name} ({override[1]})"
    return name

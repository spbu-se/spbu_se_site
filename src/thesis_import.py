# SPDX-License-Identifier: Apache-2.0

"""Clean, validated bulk importer for :class:`Thesis` records.

Replaces the legacy one-shot scraper ``thesesImport.py`` (removed). Unlike it,
this module is a pure library:

- no network I/O, no routes, no module-level ``db.init_app`` — importing it
  has zero side effects;
- every record is validated before insert and errors are collected per
  record instead of ``sys.exit``;
- lookup rows (work type, course, supervisor) are resolved by name/code, not
  by positional ids, so config survives seed-data reordering.

It must be called inside an active Flask app context::

    from flask_se import app

    with app.app_context():
        summary = import_theses(records)

Security: this API is intended for offline scripts (see
``scripts/import_theses_csv.py``). If it is ever exposed as a web endpoint,
the endpoint MUST be admin-only, accept only POST, and be CSRF-protected
(the app enforces ``CSRFProtect`` globally) — a public or GET import route
would be a serious vulnerability.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

from se_models import Courses, Staff, Thesis, Users, Worktype, db

MIN_PUBLISH_YEAR = 1900
MAX_NAME_LENGTH = 512

# Staff whose names are not the token the archive tables carry verbatim.
_SUPERVISOR_ALIASES = {
    "Ханов": "Ханов",
    "Сагунов": "Сагунов",
}

_URI_FIELDS = (
    "text_uri",
    "old_text_uri",
    "presentation_uri",
    "supervisor_review_uri",
    "reviewer_review_uri",
    "source_uri",
)


@dataclass(frozen=True)
class ThesisRecord:
    """One thesis row to import.

    ``type``/``course`` are the human-readable ``Worktype.type`` and
    ``Courses.code`` values (e.g. ``"Бакалаврская ВКР"``, ``"09.03.04"``) —
    resolved to ids at import time.
    """

    name_ru: str
    author: str
    publish_year: int
    supervisor: str
    type: str
    course: str
    text_uri: str | None = None
    old_text_uri: str | None = None
    presentation_uri: str | None = None
    supervisor_review_uri: str | None = None
    reviewer_review_uri: str | None = None
    source_uri: str | None = None
    reviewer_id: int | None = None
    temporary: bool = False


@dataclass
class ImportSummary:
    """Result of a bulk import: what landed, what was skipped and why."""

    imported: list[Thesis] = field(default_factory=list)
    errors: dict[int, list[str]] = field(default_factory=dict)
    duplicates: list[int] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors and not self.duplicates

    def __str__(self) -> str:
        lines = [f"Imported {len(self.imported)} thesis record(s)."]
        if self.duplicates:
            lines.append(f"Skipped {len(self.duplicates)} duplicate(s): {self.duplicates}")
        if self.errors:
            lines.append(f"Skipped {len(self.errors)} invalid record(s):")
            lines.extend(
                f"  record #{idx}: " + "; ".join(self.errors[idx]) for idx in sorted(self.errors)
            )
        return "\n".join(lines)


class ThesisImportError(ValueError):
    """Raised when a record fails validation (carries the human messages)."""

    def __init__(self, errors: list[str]) -> None:
        self.errors = errors
        super().__init__("; ".join(errors))


class DuplicateThesisError(ValueError):
    """Raised when a record already exists (same name/author/year)."""


def resolve_worktype(type_name: str) -> Worktype | None:
    return Worktype.query.filter_by(type=type_name).first()


def resolve_course(course_code: str) -> Courses | None:
    return Courses.query.filter_by(code=course_code).first()


def resolve_supervisor(last_name: str) -> Staff | None:
    """Resolve a supervisor's last name to a :class:`Staff` row.

    Mirrors the legacy archive's name quirks (some tables store only the
    surname, some a token that differs from the ``users.last_name``).
    Unknown names resolve to ``None`` — callers must treat that as an error,
    never silently map to a default person.
    """
    candidates = [last_name.strip()]
    candidates.extend(alias for alias in _SUPERVISOR_ALIASES if alias in last_name)
    for candidate in dict.fromkeys(candidates):
        user = Users.query.filter_by(last_name=candidate).first()
        if user is None:
            continue
        staff = Staff.query.filter_by(user_id=user.id).first()
        if staff is not None:
            return staff
    return None


def validate(record: ThesisRecord) -> list[str]:
    """Return human-readable problems with ``record`` (empty list if valid)."""
    errors: list[str] = []

    if not record.name_ru or not record.name_ru.strip():
        errors.append("name_ru must not be empty")
    elif len(record.name_ru) > MAX_NAME_LENGTH:
        errors.append(f"name_ru exceeds {MAX_NAME_LENGTH} characters")

    if not record.author or not record.author.strip():
        errors.append("author must not be empty")
    elif len(record.author) > MAX_NAME_LENGTH:
        errors.append(f"author exceeds {MAX_NAME_LENGTH} characters")

    max_year = date.today().year + 1
    if not MIN_PUBLISH_YEAR <= record.publish_year <= max_year:
        errors.append(f"publish_year {record.publish_year} outside {MIN_PUBLISH_YEAR}..{max_year}")

    if not record.supervisor or not record.supervisor.strip():
        errors.append("supervisor must not be empty")
    elif resolve_supervisor(record.supervisor) is None:
        errors.append(f"supervisor {record.supervisor!r} matches no staff member")

    if not record.type or not record.type.strip():
        errors.append("type must not be empty")
    elif resolve_worktype(record.type) is None:
        errors.append(f"work type {record.type!r} does not exist")

    if not record.course or not record.course.strip():
        errors.append("course must not be empty")
    elif resolve_course(record.course) is None:
        errors.append(f"course {record.course!r} does not exist")

    for fld in _URI_FIELDS:
        value = getattr(record, fld)
        if value is not None and (not isinstance(value, str) or not value.strip()):
            errors.append(f"{fld} must be a non-empty string or None")

    if record.reviewer_id is not None and Staff.query.get(record.reviewer_id) is None:
        errors.append(f"reviewer_id {record.reviewer_id} does not exist")

    return errors


def is_duplicate(record: ThesisRecord) -> bool:
    return (
        Thesis.query.filter_by(
            name_ru=record.name_ru,
            author=record.author,
            publish_year=record.publish_year,
        ).first()
        is not None
    )


def import_thesis(record: ThesisRecord) -> Thesis:
    """Validate and insert a single thesis.

    Raises :class:`ThesisImportError` on invalid data and
    :class:`DuplicateThesisError` when the record already exists.
    """
    errors = validate(record)
    if errors:
        raise ThesisImportError(errors)
    if is_duplicate(record):
        raise DuplicateThesisError

    supervisor = resolve_supervisor(record.supervisor)
    worktype = resolve_worktype(record.type)
    course = resolve_course(record.course)
    if supervisor is None or worktype is None or course is None:
        raise ThesisImportError(["lookup row disappeared between validate and insert"])

    thesis = Thesis(
        name_ru=record.name_ru,
        author=record.author,
        publish_year=record.publish_year,
        supervisor_id=supervisor.id,
        reviewer_id=record.reviewer_id,
        type_id=worktype.id,
        course_id=course.id,
        text_uri=record.text_uri,
        old_text_uri=record.old_text_uri,
        presentation_uri=record.presentation_uri,
        supervisor_review_uri=record.supervisor_review_uri,
        reviewer_review_uri=record.reviewer_review_uri,
        source_uri=record.source_uri,
        temporary=record.temporary,
    )
    db.session.add(thesis)
    db.session.commit()
    return thesis


def import_theses(records: list[ThesisRecord]) -> ImportSummary:
    """Bulk import with per-record error collection.

    Valid records are inserted; invalid records and duplicates are collected
    in the returned :class:`ImportSummary`. Never aborts the batch.
    """
    summary = ImportSummary()
    for idx, record in enumerate(records):
        try:
            summary.imported.append(import_thesis(record))
        except ThesisImportError as exc:
            summary.errors[idx] = exc.errors
        except DuplicateThesisError:
            summary.duplicates.append(idx)
    return summary

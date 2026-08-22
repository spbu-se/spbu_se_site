#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0

"""Example side script for the thesis import API.

Reads thesis records from a CSV file and bulk-imports them into the site
database. Each row maps to a :class:`thesis_import.ThesisRecord`.

Columns (header row required):

    name_ru, author, publish_year, supervisor, type, course
    [, text_uri, old_text_uri, presentation_uri, supervisor_review_uri,
     reviewer_review_uri, source_uri, reviewer_id, temporary]

- ``supervisor`` is the staff member's last name as stored in ``users.last_name``.
- ``type`` / ``course`` are the human-readable ``Worktype.type`` /
  ``Courses.code`` values (e.g. "Бакалаврская ВКР" / "09.03.04").
- ``temporary`` accepts ``0``/``1`` (or empty).

Usage::

    uv run python scripts/import_theses_csv.py --csv theses.csv
    uv run python scripts/import_theses_csv.py --csv theses.csv --dry-run

Set ``SE_START_SCHEDULER=0`` (done below before importing the app) so the
script never fires background jobs.
"""

from __future__ import annotations

import argparse
import csv
import os
import sys
from pathlib import Path

# Make `src` importable regardless of CWD; the module-level app import below
# must be the only import that touches flask_se.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

os.environ["SE_START_SCHEDULER"] = "0"

from flask_se import app
from thesis_import import ThesisRecord, import_theses, validate

_BOOL_ALIASES = {"1": True, "0": False, "true": True, "false": False, "": False}


class CsvError(ValueError):
    """Raised for malformed CSV input (missing columns, bad values)."""

    def __init__(self, message: str) -> None:
        super().__init__(message)


def _parse_bool(value: str) -> bool:
    normalized = value.strip().lower()
    if normalized not in _BOOL_ALIASES:
        raise CsvError(f"expected 0/1/true/false, got {value!r}")  # noqa: TRY003
    return _BOOL_ALIASES[normalized]


def _optional(value: str) -> str | None:
    return value.strip() if value and value.strip() else None


def _optional_int(value: str) -> int | None:
    value = value.strip()
    return int(value) if value else None


def load_records(path: Path) -> list[ThesisRecord]:
    """Read the CSV into :class:`ThesisRecord` objects (no DB access)."""
    with path.open(encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames is None:
            raise CsvError(f"{path}: missing header row")  # noqa: TRY003
        records: list[ThesisRecord] = []
        for row_number, row in enumerate(reader, start=2):
            try:
                records.append(
                    ThesisRecord(
                        name_ru=row["name_ru"],
                        author=row["author"],
                        publish_year=int(row["publish_year"]),
                        supervisor=row["supervisor"],
                        type=row["type"],
                        course=row["course"],
                        text_uri=_optional(row.get("text_uri", "")),
                        old_text_uri=_optional(row.get("old_text_uri", "")),
                        presentation_uri=_optional(row.get("presentation_uri", "")),
                        supervisor_review_uri=_optional(row.get("supervisor_review_uri", "")),
                        reviewer_review_uri=_optional(row.get("reviewer_review_uri", "")),
                        source_uri=_optional(row.get("source_uri", "")),
                        reviewer_id=_optional_int(row.get("reviewer_id", "")),
                        temporary=_parse_bool(row.get("temporary", "")),
                    )
                )
            except KeyError as exc:
                raise CsvError(  # noqa: TRY003
                    f"{path}:{row_number}: missing column {exc.args[0]!r}; "
                    "required columns are name_ru, author, publish_year, "
                    "supervisor, type, course"
                ) from exc
        return records


def _print_validation(records: list[ThesisRecord]) -> None:
    for idx, record in enumerate(records):
        for error in validate(record):
            print(f"  record #{idx}: {error}")


def _main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Bulk-import thesis records from a CSV file.",
    )
    parser.add_argument("--csv", required=True, help="path to the CSV file")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="validate and report without writing to the database",
    )
    args = parser.parse_args(argv)

    csv_path = Path(args.csv)
    if not csv_path.is_file():
        parser.error(f"csv file not found: {csv_path}")

    records = load_records(csv_path)
    print(f"Loaded {len(records)} record(s) from {csv_path}")

    with app.app_context():
        if args.dry_run:
            _print_validation(records)
            return 0
        summary = import_theses(records)
    print(summary)
    return 0 if summary.ok else 1


if __name__ == "__main__":
    sys.exit(_main())

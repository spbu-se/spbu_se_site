# -*- coding: utf-8 -*-
import pytest

import thesis_import
from se_models import Thesis
from thesis_import import (
    DuplicateThesisError,
    ImportSummary,
    ThesisImportError,
    ThesisRecord,
    import_theses,
    import_thesis,
    is_duplicate,
    validate,
)


def _record(**overrides: object) -> ThesisRecord:
    values: dict[str, object] = {
        "name_ru": "Тестируемая работа",
        "author": "Иванов Иван Иванович",
        "publish_year": 2022,
        "supervisor": "Терехов",
        "type": "Бакалаврская ВКР",
        "course": "09.03.04",
    }
    values.update(overrides)
    return ThesisRecord(
        name_ru=str(values["name_ru"]),
        author=str(values["author"]),
        publish_year=int(str(values["publish_year"])),
        supervisor=str(values["supervisor"]),
        type=str(values["type"]),
        course=str(values["course"]),
        text_uri=None if values.get("text_uri") is None else str(values["text_uri"]),
        old_text_uri=None if values.get("old_text_uri") is None else str(values["old_text_uri"]),
        presentation_uri=None
        if values.get("presentation_uri") is None
        else str(values["presentation_uri"]),
        supervisor_review_uri=None
        if values.get("supervisor_review_uri") is None
        else str(values["supervisor_review_uri"]),
        reviewer_review_uri=None
        if values.get("reviewer_review_uri") is None
        else str(values["reviewer_review_uri"]),
        source_uri=None if values.get("source_uri") is None else str(values["source_uri"]),
        reviewer_id=None if values.get("reviewer_id") is None else int(str(values["reviewer_id"])),
        temporary=bool(values.get("temporary", False)),
    )


class TestValidate:
    def test_valid_record(self, seeded_client):
        assert validate(_record()) == []

    def test_empty_name_ru(self, app_ctx):
        assert "name_ru must not be empty" in validate(_record(name_ru="  "))

    def test_name_ru_too_long(self, app_ctx):
        assert validate(_record(name_ru="x" * 513))[0].startswith("name_ru exceeds")

    def test_empty_author(self, app_ctx):
        assert "author must not be empty" in validate(_record(author=""))

    def test_publish_year_out_of_range(self, app_ctx):
        errors = validate(_record(publish_year=1800))
        assert any(e.startswith("publish_year") for e in errors)

    def test_unresolvable_supervisor(self, app_ctx):
        errors = validate(_record(supervisor="НетТакогоПреподавателя"))
        assert any("matches no staff member" in e for e in errors)

    def test_empty_supervisor(self, app_ctx):
        assert "supervisor must not be empty" in validate(_record(supervisor=" "))

    def test_unknown_type(self, app_ctx):
        errors = validate(_record(type="НесуществующийТип"))
        assert any("does not exist" in e for e in errors)

    def test_unknown_course(self, app_ctx):
        errors = validate(_record(course="99.99.99"))
        assert any("does not exist" in e for e in errors)

    def test_bad_uri_value(self, app_ctx):
        errors = validate(_record(source_uri=" "))
        assert any("source_uri" in e for e in errors)

    def test_uri_none_is_ok(self, seeded_client):
        assert validate(_record(text_uri=None)) == []

    def test_unknown_reviewer_id(self, app_ctx):
        errors = validate(_record(reviewer_id=999999))
        assert any("reviewer_id" in e for e in errors)


class TestResolveSupervisor:
    def test_resolves_known_supervisor(self, seeded_client):
        from se_models import Staff

        staff = thesis_import.resolve_supervisor("Терехов")
        assert staff is not None
        assert isinstance(staff, Staff)

    def test_unknown_supervisor_returns_none(self, app_ctx):
        assert thesis_import.resolve_supervisor("НетТакогоПреподавателя") is None

    def test_alias_hanov(self, app_ctx):
        assert thesis_import.resolve_supervisor("Ханов") is None


class TestImportThesis:
    def test_imports_and_returns_thesis(self, seeded_client):
        thesis = import_thesis(_record())
        assert thesis.id is not None
        assert Thesis.query.get(thesis.id) is not None
        assert thesis.supervisor_id is not None
        assert thesis.type_id is not None
        assert thesis.course_id is not None

    def test_import_with_full_properties(self, seeded_client):
        thesis = import_thesis(
            _record(
                text_uri="Ivanov_Bachelor_Thesis_2022_text.pdf",
                old_text_uri="https://oops.math.spbu.ru/SE/diploma/2022/ivanov.pdf",
                presentation_uri="Ivanov_Bachelor_Thesis_2022_slides.pdf",
                supervisor_review_uri="Ivanov_Bachelor_Thesis_2022_supervisor_review.pdf",
                reviewer_review_uri="Ivanov_Bachelor_Thesis_2022_reviewer_review.pdf",
                source_uri="https://oops.math.spbu.ru/SE/diploma/2022/index",
                temporary=True,
            )
        )
        assert thesis.temporary is True
        assert thesis.source_uri.endswith("/index")
        assert thesis.text_uri.startswith("Ivanov")

    def test_invalid_record_raises(self, seeded_client):
        with pytest.raises(ThesisImportError):
            import_thesis(_record(name_ru=""))

    def test_duplicate_raises(self, seeded_client):
        import_thesis(_record())
        with pytest.raises(DuplicateThesisError):
            import_thesis(_record())

    def test_is_duplicate(self, seeded_client):
        import_thesis(_record())
        assert is_duplicate(_record()) is True
        assert is_duplicate(_record(author="Другой Автор")) is False


class TestImportTheses:
    def test_mixed_batch_skip_and_report(self, seeded_client):
        records = [
            _record(),
            _record(name_ru=""),  # invalid
            _record(author="Петров Пётр"),  # valid, distinct
            _record(supervisor="НетТакогоПреподавателя"),  # invalid
        ]
        summary = import_theses(records)
        assert isinstance(summary, ImportSummary)
        assert len(summary.imported) == 2
        assert set(summary.errors) == {1, 3}
        assert summary.duplicates == []

    def test_duplicate_collected_not_imported(self, seeded_client):
        import_thesis(_record())
        summary = import_theses([_record()])
        assert summary.duplicates == [0]
        assert summary.imported == []

    def test_ok_property(self, seeded_client):
        assert import_theses([_record()]).ok is True
        assert import_theses([_record(name_ru="")]).ok is False

    def test_str_renders(self, seeded_client):
        assert "Imported 1 thesis record(s)" in str(import_theses([_record()]))

    def test_empty_batch(self, seeded_client):
        summary = import_theses([])
        assert summary.imported == []
        assert summary.errors == {}
        assert summary.duplicates == []
        assert summary.ok is True


class TestModuleSafety:
    def test_import_has_no_side_effects(self):
        assert not hasattr(thesis_import, "download")
        assert not hasattr(thesis_import, "sys")

    def test_double_import_is_safe(self):
        import importlib

        importlib.reload(thesis_import)
        assert callable(thesis_import.import_theses)

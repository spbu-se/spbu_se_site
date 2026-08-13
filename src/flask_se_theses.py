# SPDX-License-Identifier: Apache-2.0

import json
import logging
import os
import random
import re
from os.path import splitext
from urllib.parse import urlparse

import fitz
from flask import jsonify, redirect, render_template, request, url_for
from flask_login import current_user
from flask_sqlalchemy.pagination import Pagination
from sqlalchemy import inspect
from sqlalchemy.exc import OperationalError
from transliterate import translit

from flask_se_auth import login_required
from flask_se_config import SECRET_KEY_THESIS, secure_filename, type_id_string
from flask_se_practice_config import _paginate
from se_forms import ThesisFilter
from se_models import Courses, Staff, Thesis, Users, Worktype, db, thesis_fts_search

log = logging.getLogger("flask_se.sub")

_safe_ext_re = re.compile(r"^\.[A-Za-z0-9]{1,10}$")
_safe_uri_re = re.compile(r"^[A-Za-z0-9_.\-]+$")

_ALLOWED_UPLOAD_EXTENSIONS = {
    ".pdf",
    ".doc",
    ".docx",
    ".ppt",
    ".pptx",
    ".txt",
    ".md",
}

_THESES_ROLE_LEVEL = 2


def _ensure_thesis_consultant_column() -> None:
    """Lazily add the ``consultant`` column to the ``thesis`` table.

    The Alembic migration tree is multi-headed and deploys are webhook-driven,
    so schema evolution runs in code (same pattern as NotificationLog in
    se_sendmail). No-op once the column exists.
    """
    if "consultant" in inspect(db.engine).get_columns("thesis"):
        return
    try:
        with db.engine.begin() as connection:
            connection.execute(db.text("ALTER TABLE thesis ADD COLUMN consultant VARCHAR(2048)"))
    except OperationalError:
        # Concurrent worker may have added it first.
        pass


def _require_theses_admin() -> bool:
    return current_user.is_authenticated and current_user.role >= _THESES_ROLE_LEVEL


def _safe_extension(filename: str | None) -> str:
    path = urlparse(filename or "").path
    extension = splitext(path)[1].lower()
    if _safe_ext_re.fullmatch(extension) and extension in _ALLOWED_UPLOAD_EXTENSIONS:
        return extension
    return ""


def _safe_uri(uri: str | None) -> bool:
    """True if a stored file URI is a plain filename (no path separators)."""
    if not uri:
        return True
    return bool(_safe_uri_re.fullmatch(uri))


def theses_search():
    _ensure_thesis_consultant_column()
    filter = ThesisFilter()
    hints = [
        '"Максим" можно искать как Максим, максим, Макс* или *акс*.',
        "Полнотекстовый поиск по названиям работ и авторам",
        '"Дом" можно искать как дом, д?м или д*м',
    ]

    hint = random.choice(hints)  # noqa: S311

    worktype_choices = [
        (sid[0], wrktype.type)
        for sid in Thesis.query.with_entities(Thesis.type_id).distinct().all()
        if (wrktype := Worktype.query.filter_by(id=sid[0]).first()) is not None
    ]
    worktype_choices.sort(key=lambda tup: tup[1])
    filter.worktype.choices = worktype_choices  # pyright: ignore[reportAttributeAccessIssue]

    course_choices = [
        (sid[0], course.name)
        for sid in Thesis.query.with_entities(Thesis.course_id).distinct().all()
        if (course := Courses.query.filter_by(id=sid[0]).first()) is not None
    ]
    course_choices.sort(key=lambda tup: tup[1])
    filter.course.choices = course_choices  # pyright: ignore[reportAttributeAccessIssue]

    dates = [
        theses.publish_year
        for theses in Thesis.query.filter(~Thesis.temporary)
        .with_entities(Thesis.publish_year)
        .distinct()
    ]
    dates.sort(reverse=True)
    filter.startdate.choices = dates
    filter.enddate.choices = dates

    supervisor_choices = []
    for sid in Thesis.query.with_entities(Thesis.supervisor_id).distinct().all():
        staff = Staff.query.filter_by(id=sid[0]).first()
        last_name = ""
        initials = ""

        if not staff:
            staff = Staff.query.filter_by(id=1).first()

        if staff is None:
            continue

        if staff.user.last_name:
            last_name = staff.user.last_name

        if staff.user.first_name:
            initials = initials + staff.user.first_name[0] + "."

        if staff.user.middle_name:
            initials = initials + staff.user.middle_name[0] + "."

        supervisor_choices.append((sid[0], last_name + " " + initials))

    supervisor_choices.sort(key=lambda tup: tup[1])
    filter.supervisor.choices = [(0, "Все"), *supervisor_choices]  # pyright: ignore[reportAttributeAccessIssue]
    filter.course.choices = [(0, "Все"), *course_choices]  # pyright: ignore[reportAttributeAccessIssue]
    filter.worktype.choices = [(0, "Все"), *worktype_choices]  # pyright: ignore[reportAttributeAccessIssue]

    search = request.args.get("search", default="", type=str).strip()
    og_title = None
    og_description = None
    if search:
        og_title = f'Результаты поиска: "{search}"'
        og_description = f'Работы по запросу "{search}" в архиве практик и ВКР кафедры.'

    records, ctx = _query_theses()

    return render_template(
        "theses.html",
        filter=filter,
        hint=hint,
        og_title=og_title,
        og_description=og_description,
        theses=records,
        **ctx,
    )


def _query_theses() -> tuple[Pagination, dict[str, object]]:
    """Build the filtered/paginated thesis query from request args.

    Returns ``(records, template_context)``. ``template_context`` carries the
    filter values needed to render ``fetch_theses.html`` and is shared by the
    server-rendered archive page (``theses_search``) and the AJAX fragment
    endpoint (``fetch_theses``) so both render identical content.
    """
    _ensure_thesis_consultant_column()
    worktype = request.args.get("worktype", default=1, type=int)
    page = request.args.get("page", default=1, type=int)
    supervisor = request.args.get("supervisor", default=0, type=int)
    course = request.args.get("course", default=0, type=int)
    search = request.args.get("search", default="", type=str)
    consultant = request.args.get("consultant", default="", type=str)
    context = {}

    dates = [
        theses.publish_year
        for theses in Thesis.query.filter(~Thesis.temporary)
        .with_entities(Thesis.publish_year)
        .distinct()
    ]
    dates.sort(reverse=True)

    if dates:
        startdate = request.args.get("startdate", default=dates[-1], type=int)
        enddate = request.args.get("enddate", default=dates[0], type=int)
    else:
        startdate = 2007
        enddate = 2022

    # Check if end date less than start date
    enddate = max(enddate, startdate)

    if search:
        fts_ids = thesis_fts_search(search)
        records = (
            (
                Thesis.query.filter(Thesis.id.in_(fts_ids))
                .filter(~Thesis.temporary)
                .filter(Thesis.publish_year >= startdate)
                .filter(Thesis.publish_year <= enddate)
                .order_by(Thesis.publish_year.desc())
            )
            if fts_ids
            else Thesis.query.filter(db.text("0=1"))
        )
    else:
        records = (
            Thesis.query.filter(~Thesis.temporary)
            .filter(Thesis.publish_year >= startdate)
            .filter(Thesis.publish_year <= enddate)
            .order_by(Thesis.publish_year.desc())
        )

    if course:
        # Check if course exists
        records = records.filter(Thesis.course_id == course)

    if supervisor:
        # Check if supervisor exists
        ids = Thesis.query.with_entities(Thesis.supervisor_id).distinct().all()
        if [item for item in ids if item[0] == supervisor]:
            records = records.filter(Thesis.supervisor_id == supervisor)
        else:
            supervisor = 0

    if consultant:
        records = records.filter(Thesis.consultant.ilike("%" + consultant + "%"))

    if worktype > 1:
        records = _paginate(records.filter_by(type_id=worktype), page)
    else:
        records = _paginate(records, page)

    if len(records.items):
        first_priority = []
        second_priority = []
        third_priority = []

        for item in records.items:
            search_in_name = False

            text_index = -1 if item.text is None else item.text.find(search.lower())

            if item.name_ru is not None:
                search_in_name = str(item.name_ru).lower().find(search.lower()) != -1

            if item.description is not None:
                search_in_name = (
                    search_in_name or str(item.description).lower().find(search.lower()) != -1
                )

            if item.author is not None:
                search_in_name = (
                    search_in_name or str(item.author).lower().find(search.lower()) != -1
                )

            if search_in_name and text_index != -1:
                first_priority.append(item)
            elif search_in_name:
                second_priority.append(item)
            else:
                third_priority.append(item)

            if text_index != -1 and item.text is not None:
                left_space_index = item.text.find(" ", text_index - 60)
                right_space_index = item.text.find(" ", text_index + 60)
                context[item] = item.text[left_space_index:right_space_index].split()

        records.items = first_priority + second_priority + third_priority

    return records, {
        "worktype": worktype,
        "course": course,
        "startdate": startdate,
        "enddate": enddate,
        "supervisor": supervisor,
        "consultant": consultant,
        "search": search,
        "context": context,
    }


def fetch_theses():
    records, ctx = _query_theses()
    if len(records.items):
        return render_template("fetch_theses.html", theses=records, **ctx)
    return render_template("fetch_theses_blank.html")


def get_text(filename):
    """Extract text from a PDF. Returns "" on parse failure to avoid 500s
    and orphaned temp files (decompression bombs / malformed uploads)."""
    try:
        doc = fitz.open(filename)
    except Exception:
        return ""

    text = ""
    try:
        for current_page in range(3, len(doc)):
            page = doc.load_page(current_page)
            text += page.get_text("text").lower() + "\n"  # pyright: ignore[reportAttributeAccessIssue]
            text = text.replace("-\n", "")
            text = re.sub(r"[^a-z а-я \n : / . () # - ]", "", text)
    finally:
        doc.close()

    return text


# Download thesis link
def download_thesis():
    thesis_id = request.args.get("thesis_id", default=0, type=int)

    if not thesis_id:
        return redirect("theses_search")

    thesis = Thesis.query.filter_by(id=thesis_id).first()

    if not thesis:
        return redirect("theses_search")

    if not thesis.text_uri:
        return redirect("theses_search")

    # Increment counter
    thesis.download_thesis = thesis.download_thesis + 1
    db.session.commit()

    return redirect(url_for("static", filename="/thesis/texts/" + thesis.text_uri))


# Shareable card for a single thesis
def thesis_card():
    thesis_id = request.args.get("thesis_id", default=0, type=int)

    if not thesis_id:
        return redirect("theses_search")

    thesis = Thesis.query.filter(Thesis.id == thesis_id, ~Thesis.temporary).first()

    if not thesis:
        return redirect("theses_search")

    return render_template("thesis_card.html", thesis=thesis)


def post_theses():
    error_status = 500
    success_status = 0
    thesis_text = None
    presentation = None
    supervisor_review = None
    reviewer_review = None
    thesis_info = None
    source_uri = None

    presentation_filename = None
    supervisor_review_filename = None
    reviewer_review_filename = None

    if "thesis_text" in request.files:
        thesis_text = request.files["thesis_text"]

    if "presentation" in request.files:
        presentation = request.files["presentation"]

    if "supervisor_review" in request.files:
        supervisor_review = request.files["supervisor_review"]

    if "reviewer_review" in request.files:
        reviewer_review = request.files["reviewer_review"]

    if "thesis_info" in request.files:
        thesis_info = json.loads(request.files["thesis_info"].read())

    if not thesis_text:
        return jsonify(status=error_status, string="No thesis text found.")

    if not thesis_info:
        return jsonify(status=error_status, string="No thesis_info found.")

    try:
        name_ru = thesis_info["name_ru"]
        secret_key = thesis_info["secret_key"]
        type_id = thesis_info["type_id"]
        course_id = thesis_info["course_id"]
        author = thesis_info["author"]
        supervisor = thesis_info["supervisor"]
        publish_year = thesis_info["publish_year"]
    except KeyError:
        return jsonify(status=error_status, string="Missing required field in thesis_info")

    if secret_key != SECRET_KEY_THESIS:
        return jsonify(status=error_status, string="Invalid secret key: " + str(secret_key))

    if not _safe_extension(thesis_text.filename):
        return jsonify(
            status=error_status,
            string="Disallowed file extension: " + str(thesis_text.filename),
        )

    if "source_uri" in thesis_info:
        source_uri = thesis_info["source_uri"]

    if type_id < 2 or type_id > len(type_id_string):
        return jsonify(status=error_status, string="Wrong type_id: " + str(type_id))

    if course_id < 1 or course_id > 8:
        return jsonify(status=error_status, string="Wrong course_id: " + str(course_id))

    try:
        publish_year = int(publish_year)
    except (TypeError, ValueError):
        return jsonify(status=error_status, string="Wrong publish_year: " + str(publish_year))

    if publish_year < 2000 or publish_year > 2100:
        return jsonify(status=error_status, string="Wrong publish_year: " + str(publish_year))

    # Try to get SuperVisor Id
    qq = Users.query.filter_by(last_name=supervisor).all()
    supervisor_id = ""

    if qq:
        for q in qq:
            r = Staff.query.filter_by(user_id=q.id).first()

            if r:
                supervisor_id = r.id
                continue

        if not supervisor_id:
            return jsonify(
                status=error_status,
                string="Can't find supervisor in staff: " + str(supervisor),
            )
    else:
        return jsonify(
            status=error_status,
            string="Can't find supervisor in users: " + str(supervisor),
        )

    author_en = secure_filename(translit(author, "ru", reversed=True).replace(" ", "_"))
    thesis_filename = author_en
    thesis_filename = thesis_filename + "_" + type_id_string[type_id - 1]
    thesis_filename = thesis_filename + "_" + str(publish_year) + "_text"

    thesis_filename = thesis_filename + _safe_extension(thesis_text.filename)

    # Before we going on, check if this thesis already exists?
    records = Thesis.query.filter_by(text_uri=thesis_filename)
    if records.count():
        return jsonify(status=error_status, string="Work already exists: " + str(thesis_filename))

    # Save file to TMP
    thesis_text.save(os.path.join("./static/tmp/texts/", thesis_filename))

    text = get_text(os.path.join("./static/tmp/texts/", thesis_filename))

    if presentation:
        presentation_filename = author_en
        presentation_filename = presentation_filename + "_" + type_id_string[type_id - 1]
        presentation_filename = presentation_filename + "_" + str(publish_year) + "_slides"

        presentation_filename = presentation_filename + _safe_extension(presentation.filename)

        presentation.save(os.path.join("./static/tmp/slides/", presentation_filename))

    if supervisor_review:
        supervisor_review_filename = author_en
        supervisor_review_filename = supervisor_review_filename + "_" + type_id_string[type_id - 1]
        supervisor_review_filename = (
            supervisor_review_filename + "_" + str(publish_year) + "_supervisor_review"
        )

        supervisor_review_filename = supervisor_review_filename + _safe_extension(
            supervisor_review.filename,
        )

        supervisor_review.save(os.path.join("./static/tmp/reviews/", supervisor_review_filename))

    if reviewer_review:
        reviewer_review_filename = author_en
        reviewer_review_filename = reviewer_review_filename + "_" + type_id_string[type_id - 1]
        reviewer_review_filename = (
            reviewer_review_filename + "_" + str(publish_year) + "_reviewer_review"
        )

        reviewer_review_filename = reviewer_review_filename + _safe_extension(
            reviewer_review.filename,
        )

        reviewer_review.save(os.path.join("./static/tmp/reviews/", reviewer_review_filename))

    if source_uri:
        t = Thesis(
            name_ru=name_ru,
            text_uri=thesis_filename,
            presentation_uri=presentation_filename,
            supervisor_review_uri=supervisor_review_filename,
            reviewer_review_uri=reviewer_review_filename,
            author=author,
            supervisor_id=supervisor_id,
            reviewer_id=2,
            publish_year=publish_year,
            type_id=type_id,
            course_id=course_id,
            source_uri=source_uri,
            temporary=True,
            text=text,
        )
    else:
        t = Thesis(
            name_ru=name_ru,
            text_uri=thesis_filename,
            presentation_uri=presentation_filename,
            supervisor_review_uri=supervisor_review_filename,
            reviewer_review_uri=reviewer_review_filename,
            author=author,
            supervisor_id=supervisor_id,
            reviewer_id=2,
            publish_year=publish_year,
            type_id=type_id,
            course_id=course_id,
            temporary=True,
            text=text,
        )

    db.session.add(t)

    try:
        db.session.commit()
    except AssertionError:
        db.session.rollback()
        log.exception("Error")
    except Exception:
        db.session.rollback()
        log.exception("Error")

    return jsonify(status=success_status, string="Success")


@login_required
def theses_tmp():
    if not _require_theses_admin():
        return redirect(url_for("theses_search"))
    records = Thesis.query.filter_by(temporary=True).filter_by(review_status=10)
    return render_template("theses_tmp.html", theses=records)


@login_required
def theses_delete_tmp():
    if not _require_theses_admin():
        return redirect(url_for("theses_search"))
    thesis_id = request.form.get("thesis_id", default=1, type=int)
    thesis = Thesis.query.filter_by(id=thesis_id).filter_by(temporary=True).first()

    if thesis:
        db.session.delete(thesis)
        db.session.commit()

    return redirect(url_for("theses_tmp"))


@login_required
def theses_add_tmp():
    if not _require_theses_admin():
        return redirect(url_for("theses_search"))
    thesis_id = request.form.get("thesis_id", default=1, type=int)
    thesis = Thesis.query.filter_by(id=thesis_id).filter_by(temporary=True).first()

    if thesis:
        thesis.temporary = False
        db.session.commit()

        if thesis.text_uri and _safe_uri(thesis.text_uri):
            os.rename(
                "./static/tmp/texts/" + thesis.text_uri,
                "./static/thesis/texts/" + thesis.text_uri,
            )

        if thesis.presentation_uri and _safe_uri(thesis.presentation_uri):
            os.rename(
                "./static/tmp/slides/" + thesis.presentation_uri,
                "./static/thesis/slides/" + thesis.presentation_uri,
            )

        if thesis.supervisor_review_uri and _safe_uri(thesis.supervisor_review_uri):
            os.rename(
                "./static/tmp/reviews/" + thesis.supervisor_review_uri,
                "./static/thesis/reviews/" + thesis.supervisor_review_uri,
            )

        if thesis.reviewer_review_uri and _safe_uri(thesis.reviewer_review_uri):
            os.rename(
                "./static/tmp/reviews/" + thesis.reviewer_review_uri,
                "./static/thesis/reviews/" + thesis.reviewer_review_uri,
            )

    return redirect(url_for("theses_tmp"))


def register_routes(app) -> None:
    app.add_url_rule("/theses.html", view_func=theses_search)
    app.add_url_rule("/fetch_theses", view_func=fetch_theses)
    app.add_url_rule("/post_theses", methods=["GET", "POST"], view_func=post_theses)
    app.add_url_rule("/theses_tmp.html", view_func=theses_tmp)
    app.add_url_rule("/theses_delete_tmp", methods=["POST"], view_func=theses_delete_tmp)
    app.add_url_rule("/theses_add_tmp", methods=["POST"], view_func=theses_add_tmp)
    app.add_url_rule("/thesis_download", view_func=download_thesis)
    app.add_url_rule("/thesis_card", view_func=thesis_card)

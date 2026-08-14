# SPDX-License-Identifier: Apache-2.0

import os
from datetime import date
from pathlib import Path

from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user
from flask_sqlalchemy.pagination import Pagination
from transliterate import translit

from flask_se_auth import login_required
from flask_se_config import get_thesis_type_id_string, secure_filename
from se_forms import AddThesisOnReview, EditThesisOnReview, ThesisReviewFilter
from se_models import (
    AreasOfStudy,
    PromoCode,
    Reviewer,
    ThesisOnReview,
    ThesisOnReviewWorktype,
    ThesisReview,
    add_mail_notification,
    db,
)
from se_review_forms import ReviewForm

# Global variables
UPLOAD_FOLDER = "static/thesis/onreview/"
REVIEW_UPLOAD_FOLDER = "static/onreview/reviews/"
ALLOWED_EXTENSIONS = {"pdf"}
REVIEW_ROLE_LEVEL = 3


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def _query_thesis_on_review() -> tuple[Pagination, dict[str, object]]:
    """Build the filtered/paginated thesis-on-review query from request args.

    Shared by the server-rendered index (``thesis_review_index``) and the AJAX
    fragment endpoint (``fetch_thesis_on_review``) so both render identical
    content. Returns ``(records, template_context)``.
    """
    status = request.args.get("status", default=4, type=int)
    page = request.args.get("page", default=1, type=int)
    worktype = request.args.get("worktype", default=1, type=int)
    area = request.args.get("area", default=1, type=int)

    if status == 4:
        records = (
            ThesisOnReview.query.filter(ThesisOnReview.id > 0)
            .filter(ThesisOnReview.deleted == 0)
            .order_by(ThesisOnReview.id.desc())
        )
    else:
        records = (
            ThesisOnReview.query.filter(ThesisOnReview.review_status == status)
            .filter(ThesisOnReview.deleted == 0)
            .order_by(ThesisOnReview.id.desc())
        )

    if worktype > 1:
        records = records.filter(ThesisOnReview.thesis_on_review_type_id == worktype)

    if area > 1:
        records = records.filter(ThesisOnReview.area_id == area).paginate(
            per_page=20,
            page=page,
            error_out=False,
        )
    else:
        records = records.paginate(per_page=20, page=page, error_out=False)

    return records, {"status": status, "worktype": worktype, "area": area}


def thesis_review_index():
    user = current_user
    form = ThesisReviewFilter()

    form.status.choices = [
        (4, "Все статусы"),
        (1, "Требуется рецензия"),
        (2, "На рецензии"),
        (3, "Требуется доработка"),
        (0, "Работа зачтена"),
    ]

    form.worktype.choices = sorted(
        [(type.id, type.type) for type in ThesisOnReviewWorktype.query.distinct().all()],
        key=lambda tup: tup[0],
    )  # pyright: ignore[reportAttributeAccessIssue]

    form.areasofstudy.choices = sorted(
        [(area.id, area.area) for area in AreasOfStudy.query.distinct().all()],
        key=lambda tup: tup[0],
    )  # pyright: ignore[reportAttributeAccessIssue]

    records, ctx = _query_thesis_on_review()
    return render_template(
        "thesis_review/index.html",
        review_filter=form,
        thesis=records,
        user=user,
        **ctx,
    )


def fetch_thesis_on_review():
    user = current_user

    records, ctx = _query_thesis_on_review()

    return render_template(
        "thesis_review/fetch_thesis_on_review.html",
        thesis=records,
        user=user,
        **ctx,
    )


@login_required
def submit_thesis_on_review():
    user = current_user
    form = AddThesisOnReview()
    author = user.get_name()

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        worktype = request.form.get("type", 0, type=int)
        area_of_study = request.form.get("area", 0, type=int)

        if not title:
            flash("Укажите название вашей работы", "error")
            return redirect(url_for("submit_thesis_on_review"))

        if worktype <= 0 or worktype > ThesisOnReviewWorktype.query.distinct().count():
            flash("Укажите тип работы", "error")
            return redirect(url_for("submit_thesis_on_review"))

        if area_of_study <= 0 or area_of_study > AreasOfStudy.query.distinct().count():
            flash("Укажите направление вашего обучения", "error")
            return redirect(url_for("submit_thesis_on_review"))

        # check if the post request has the file part
        if "thesis" not in request.files:
            flash("Вы не загрузили файл с работой", "error")
            return redirect(url_for("submit_thesis_on_review"))

        file = request.files["thesis"]
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == "":
            flash(
                "Укажите файл с вашей работой для загрузки",
                "error",
            )
            return redirect(url_for("submit_thesis_on_review"))

        if file and allowed_file(file.filename):
            author_en = translit(author, "ru", reversed=True)
            author_en = secure_filename(author_en) or "unknown"
            thesis_filename = author_en
            thesis_filename = thesis_filename + "_" + get_thesis_type_id_string(worktype)

            todays_date = date.today()
            thesis_filename = thesis_filename + "_" + str(todays_date.year) + "_text"
            thesis_filename_with_ext = thesis_filename + ".pdf"

            full_thesis_filename = os.path.join(UPLOAD_FOLDER + "/" + thesis_filename_with_ext)

            # Check if file already exist
            if os.path.isfile(full_thesis_filename):
                thesis_filename = thesis_filename + "_" + str(os.urandom(8).hex())
                thesis_filename_with_ext = thesis_filename + ".pdf"
                full_thesis_filename = os.path.join(UPLOAD_FOLDER + "/" + thesis_filename_with_ext)

            file.save(full_thesis_filename)

            # Add to DB
            thesis = ThesisOnReview(  # pyright: ignore[reportCallIssue]
                name_ru=title,  # pyright: ignore[reportCallIssue]
                text_uri=thesis_filename_with_ext,  # pyright: ignore[reportCallIssue]
                author_id=user.id,  # pyright: ignore[reportCallIssue]
                type_id=worktype,  # pyright: ignore[reportCallIssue]
                thesis_on_review_type_id=worktype,  # pyright: ignore[reportCallIssue]
                area_id=area_of_study,  # pyright: ignore[reportCallIssue]
                review_status=1,  # pyright: ignore[reportCallIssue]
            )
            db.session.add(thesis)
            db.session.commit()

            flash(
                "Ваша работа успешно загружена. Информацию о начале и окончании рецензирования вы будете получать на почту",
                "error",
            )
            return redirect(url_for("thesis_review_index"))
        flash("Текст работы должен быть в формате .PDF", "error")
        return redirect(url_for("submit_thesis_on_review"))

    type_choices = [(0, "Тип работы")]
    type_choices += [
        (type.id, type.type)
        for type in ThesisOnReviewWorktype.query.filter(ThesisOnReviewWorktype.id > 1)
        .distinct()
        .all()
    ]
    type_choices.sort(key=lambda tup: tup[0])
    form.type.choices = type_choices  # pyright: ignore[reportAttributeAccessIssue]

    area_choices = [(0, "Направление обучения")]
    area_choices += [
        (area.id, area.area)
        for area in AreasOfStudy.query.filter(AreasOfStudy.id > 1).distinct().all()
    ]
    area_choices.sort(key=lambda tup: tup[0])
    form.area.choices = area_choices  # pyright: ignore[reportAttributeAccessIssue]

    return render_template("thesis_review/submit.html", filter=form, user=user)


@login_required
def edit_thesis_on_review():
    user = current_user
    thesis_review_id = request.args.get("thesis_review_id", type=int)

    if not thesis_review_id:
        return redirect(url_for("thesis_review_index"))

    thesis_review = ThesisOnReview.query.filter_by(id=thesis_review_id).first_or_404()

    if thesis_review.author_id != user.id:
        return redirect(url_for("thesis_review_index"))

    if request.method == "POST":
        title = request.form.get("name_ru", "", type=str)
        worktype = request.form.get("type", type=int)
        area = request.form.get("area", type=int)

        if not title:
            flash("Укажите название вашей работы", "error")
            return redirect(
                url_for("edit_thesis_on_review", thesis_review_id=thesis_review_id),
            )

        title = title.strip()
        author = thesis_review.author.get_name()

        if (
            not worktype
            or worktype <= 0
            or worktype > ThesisOnReviewWorktype.query.distinct().count()
        ):
            flash("Укажите тип работы", "error")
            return redirect(
                url_for("edit_thesis_on_review", thesis_review_id=thesis_review_id),
            )

        if not area or area <= 0 or area > AreasOfStudy.query.distinct().count():
            flash("Укажите направление вашего обучения", "error")
            return redirect(
                url_for("edit_thesis_on_review", thesis_review_id=thesis_review_id),
            )

        thesis_review.name_ru = title
        thesis_review.author_id = user.id
        thesis_review.thesis_on_review_type_id = worktype
        thesis_review.area_id = area

        # check if the post request has the file part
        if "thesis" in request.files:
            full_thesis_filename = ""

            file = request.files["thesis"]
            # If the user does not select a file, the browser submits an
            # empty file without a filename.
            #
            if file.filename != "":
                if file and allowed_file(file.filename):
                    author_en = translit(author, "ru", reversed=True)
                    author_en = secure_filename(author_en) or "unknown"
                    thesis_filename = author_en
                    thesis_filename = thesis_filename + "_" + get_thesis_type_id_string(worktype)

                    todays_date = date.today()
                    thesis_filename = thesis_filename + "_" + str(todays_date.year) + "_text"
                    thesis_filename_with_ext = thesis_filename + ".pdf"

                    full_thesis_filename = os.path.join(
                        UPLOAD_FOLDER + "/" + thesis_filename_with_ext,
                    )

                    # Check if file already exist
                    if os.path.isfile(full_thesis_filename):
                        thesis_filename = thesis_filename + "_" + str(os.urandom(8).hex())
                        thesis_filename_with_ext = thesis_filename + ".pdf"
                        full_thesis_filename = os.path.join(
                            UPLOAD_FOLDER + "/" + thesis_filename_with_ext,
                        )

                    file.save(full_thesis_filename)
                    thesis_review.text_uri = thesis_filename_with_ext
                else:
                    flash(
                        "Текст работы должен быть в формате .PDF",
                        "error",
                    )
                    return redirect(
                        url_for("edit_thesis_on_review", thesis_review_id=thesis_review_id),
                    )

        thesis_review.review_status = 1
        db.session.commit()
        return redirect(url_for("thesis_review_index"))

    edit_thesis_onreview = EditThesisOnReview()
    edit_thesis_onreview.type.choices = [
        (g.id, g.type)
        for g in ThesisOnReviewWorktype.query.filter(ThesisOnReviewWorktype.id > 1).order_by("id")
    ]
    edit_thesis_onreview.area.choices = [
        (g.id, g.area) for g in AreasOfStudy.query.filter(AreasOfStudy.id > 1).order_by("id")
    ]

    edit_thesis_onreview.type.default = int(thesis_review.thesis_on_review_type_id)
    edit_thesis_onreview.area.default = int(thesis_review.area_id)
    edit_thesis_onreview.process(
        name_ru=thesis_review.name_ru,
        area=int(thesis_review.area_id),
        type=thesis_review.thesis_on_review_type_id,
        author=thesis_review.author.get_name(),
    )

    return render_template(
        "thesis_review/edit.html",
        form=edit_thesis_onreview,
        user=user,
        thesis=thesis_review,
    )


@login_required
def delete_thesis_on_review():
    thesis_id = request.form.get("thesis_review_id", type=int)

    if not thesis_id:
        return redirect(url_for("thesis_review_index"))

    thesis = ThesisOnReview.query.filter_by(id=thesis_id).first_or_404()

    if thesis.author_id != current_user.id:
        flash("Только автор может удалить свою работу", "error")
        return redirect(url_for("thesis_review_index"))

    db.session.delete(thesis)
    db.session.commit()

    return redirect(url_for("thesis_review_index"))


@login_required
def review_thesis_on_review():
    user = current_user
    user_reviewer = Reviewer.query.filter_by(user_id=user.id).first_or_404()
    thesis_id = request.values.get("thesis_review_id", type=int)
    set_to_review = request.values.get("set_to_review", type=int, default=0)

    if not user_reviewer:
        return redirect(url_for("thesis_review_index"))

    if not thesis_id:
        return redirect(url_for("thesis_review_index"))

    thesis = ThesisOnReview.query.filter_by(id=thesis_id).first_or_404()

    # Check if this users thesis.
    # User can't review it's own thesis.
    if thesis.author_id == user.id:
        flash("Вы не можете рецензировать свою работу", "error")
        return redirect(url_for("thesis_review_index"))

    # Ok, we have thesis and user permission.
    # First, ask users about review and set it
    if (thesis.review_status == 1) and (set_to_review == 0):
        return render_template("thesis_review/first_time_review.html", thesis=thesis)

    # Set review_status to 2 (On review)
    # Set reviewer_id to user.id
    # State-changing part must be POST (CSRF-protected).
    if (thesis.review_status == 1) and (set_to_review != 0):
        if request.method != "POST":
            return redirect(url_for("thesis_review_index"))
        thesis.review_status = 2
        thesis.reviewer_id = user_reviewer.id
        db.session.commit()

        data = render_template("notification/thesis_on_review_get.html", thesis=thesis)
        add_mail_notification(
            thesis.author_id,
            "[SE site] Ваша работа на рецензировании",
            data,
        )

    review_form = ReviewForm()
    return render_template(
        "thesis_review/review.html",
        thesis=thesis,
        user=user,
        review_form=review_form,
    )


@login_required
def review_submit_review():
    user = current_user
    user_reviewer = Reviewer.query.filter_by(user_id=user.id).first_or_404()
    thesis_id = request.args.get("thesis_review_id", type=int)

    if request.method != "POST":
        flash(
            "Неверный метод, разрешается только метод POST",
            "error",
        )
        return redirect(url_for("thesis_review_index"))

    if not user_reviewer:
        flash("Вы не состоите в группе рецензентов", "error")
        return redirect(url_for("thesis_review_index"))

    if not thesis_id:
        flash("Не указан идентификатор работы", "error")
        return redirect(url_for("thesis_review_index"))

    thesis = ThesisOnReview.query.filter_by(id=thesis_id).first_or_404()

    # Check if this users thesis.
    # User can't review it's own thesis.
    if thesis.author_id == user.id:
        flash("Вы не можете рецензировать свою работу", "error")
        return redirect(url_for("thesis_review_index"))

    # Only the assigned reviewer may submit a review (IDOR guard).
    if thesis.reviewer_id != user_reviewer.id:
        flash("Эта работа назначена другому рецензенту", "error")
        return redirect(url_for("thesis_review_index"))

    # Only status == 2 allow us to review this thesis.
    if thesis.review_status != 2:
        flash("Работа не находится на рецензировании", "error")
        return redirect(url_for("thesis_review_index"))

    # Ok, we can read the review form
    try:
        o1 = request.form["review_o1_radio_switcher"]
        o1_comment = request.form["review_o1_comment"]
        o2 = request.form["review_o2_radio_switcher"]
        o2_comment = request.form["review_o2_comment"]
        t1 = request.form["review_t1_radio_switcher"]
        t1_comment = request.form["review_t1_comment"]
        t2 = request.form["review_t2_radio_switcher"]
        t2_comment = request.form["review_t2_comment"]
        p1 = request.form["review_p1_radio_switcher"]
        p1_comment = request.form["review_p1_comment"]
        p2 = request.form["review_p2_radio_switcher"]
        p2_comment = request.form["review_p2_comment"]

        review_overall_comment = request.form["review_overall_comment"]
        verdict = request.form["review_verdict_radio_switcher"]

        review_file_name = None

        # check if the post request has the file part
        if "review_file" in request.files:
            file = request.files["review_file"]

            # If the user does not select a file, the browser submits an
            # empty file without a filename.

            if file.filename != "" and file and allowed_file(file.filename) and thesis.text_uri:
                filename = Path(thesis.text_uri).stem
                review_filename = filename + "_review"
                review_filename_with_ext = review_filename + ".pdf"

                full_filename = os.path.join(REVIEW_UPLOAD_FOLDER + "/" + review_filename_with_ext)

                # Check if file already exist
                if os.path.isfile(full_filename):
                    filename = filename + "_" + str(os.urandom(8).hex())
                    review_filename = filename + "_review"
                    review_filename_with_ext = review_filename + ".pdf"

                    full_filename = os.path.join(
                        REVIEW_UPLOAD_FOLDER + "/" + review_filename_with_ext,
                    )

                review_file_name = review_filename_with_ext
                file.save(full_filename)

    except KeyError:
        flash(
            "В рецензии есть пропущенные вопросы. Нужно ответить на все вопросы, поля с комментариями являются опциональными.",
            "error",
        )
        return redirect(url_for("review_thesis_on_review", thesis_review_id=thesis_id))

    data = ""
    review = ThesisReview(  # pyright: ignore[reportCallIssue]
        thesis_on_review_id=thesis.id,  # pyright: ignore[reportCallIssue]
        o1=o1,  # pyright: ignore[reportCallIssue]
        o1_comment=o1_comment,  # pyright: ignore[reportCallIssue]
        o2=o2,  # pyright: ignore[reportCallIssue]
        o2_comment=o2_comment,  # pyright: ignore[reportCallIssue]
        t1=t1,  # pyright: ignore[reportCallIssue]
        t1_comment=t1_comment,  # pyright: ignore[reportCallIssue]
        t2=t2,  # pyright: ignore[reportCallIssue]
        t2_comment=t2_comment,  # pyright: ignore[reportCallIssue]
        p1=p1,  # pyright: ignore[reportCallIssue]
        p1_comment=p1_comment,  # pyright: ignore[reportCallIssue]
        p2=p2,  # pyright: ignore[reportCallIssue]
        p2_comment=p2_comment,  # pyright: ignore[reportCallIssue]
        verdict=verdict,  # pyright: ignore[reportCallIssue]
        overall_comment=review_overall_comment,  # pyright: ignore[reportCallIssue]
        review_file_uri=review_file_name,  # pyright: ignore[reportCallIssue]
    )

    # Review status = 0 (success)
    # Review status = 3 (Need to be fixed)
    if verdict != "0":
        thesis.review_status = 0
        data = render_template("notification/thesis_on_review_success.html", thesis=thesis)
    else:
        thesis.review_status = 3
        data = render_template("notification/thesis_on_review_failed.html", thesis=thesis)

    db.session.add(review)
    db.session.commit()

    add_mail_notification(thesis.author_id, "[SE site] Результат рецензирования", data)

    return redirect(url_for("thesis_review_index"))


@login_required
def review_result_thesis_on_review():
    user = current_user
    thesis_id = request.args.get("thesis_review_id", type=int)

    if not thesis_id:
        flash("Не указан идентификатор работы", "error")
        return redirect(url_for("thesis_review_index"))

    thesis = ThesisOnReview.query.filter_by(id=thesis_id).first_or_404()
    review = ThesisReview.query.filter_by(thesis_on_review_id=thesis_id).first_or_404()

    user_reviewer = Reviewer.query.filter_by(user_id=user.id).first()
    is_author = thesis.author_id == user.id
    is_reviewer = user_reviewer is not None and thesis.reviewer_id == user_reviewer.id

    if not is_author and not is_reviewer:
        flash("Вы не можете просматривать рецензию на чужую работу", "error")
        return redirect(url_for("thesis_review_index"))

    if thesis.review_status in {1, 2}:
        flash("Рецензия по данной работе не завершена", "error")
        return redirect(url_for("thesis_review_index"))

    review_form = ReviewForm(
        review_o1_radio_switcher=review.o1,
        review_o1_comment=review.o1_comment,
        review_o2_radio_switcher=review.o2,
        review_o2_comment=review.o2_comment,
        review_t1_radio_switcher=review.t1,
        review_t1_comment=review.t1_comment,
        review_t2_radio_switcher=review.t2,
        review_t2_comment=review.t2_comment,
        review_p1_radio_switcher=review.p1,
        review_p1_comment=review.p1_comment,
        review_p2_radio_switcher=review.p2,
        review_p2_comment=review.p2_comment,
        review_overall_comment=review.overall_comment,
        review_verdict_radio_switcher=review.verdict,
    )

    return render_template(
        "thesis_review/result_review.html",
        thesis=thesis,
        user=user,
        review_form=review_form,
        review=review,
    )


@login_required
def review_become_thesis_reviewer_ask():
    user = current_user

    promocode = request.args.get("code", type=str, default="")

    promo = PromoCode.query.filter_by(code=promocode).first()

    if not promo:
        return redirect(url_for("index"))

    reviewer = Reviewer.query.filter_by(user_id=user.id).first()

    if reviewer:
        return render_template("thesis_review/already_reviewer.html", user=user)

    return render_template("thesis_review/become_reviewer.html", user=user, promocode=promocode)


@login_required
def review_become_thesis_reviewer_confirm():
    user = current_user

    promocode = request.form.get("code", type=str, default="")

    promo = PromoCode.query.filter_by(code=promocode).first()

    if not promo:
        return redirect(url_for("index"))

    reviewer = Reviewer.query.filter_by(user_id=user.id).first()

    if reviewer:
        return render_template("thesis_review/already_reviewer.html", user=user)

    r = Reviewer(user_id=user.id)  # pyright: ignore[reportCallIssue]
    db.session.add(r)
    db.session.commit()

    return render_template("thesis_review/become_reviewer_confirm.html", user=user)


def register_routes(app) -> None:
    app.add_url_rule("/review/", methods=["GET"], view_func=thesis_review_index)
    app.add_url_rule("/review/index.html", methods=["GET"], view_func=thesis_review_index)
    app.add_url_rule("/review/submit", methods=["GET", "POST"], view_func=submit_thesis_on_review)
    app.add_url_rule("/review/edit", methods=["GET", "POST"], view_func=edit_thesis_on_review)
    app.add_url_rule("/review/delete", methods=["POST"], view_func=delete_thesis_on_review)
    app.add_url_rule("/review/review", methods=["GET", "POST"], view_func=review_thesis_on_review)
    app.add_url_rule("/review/reviewed", methods=["GET", "POST"], view_func=review_submit_review)
    app.add_url_rule(
        "/review/review_result", methods=["GET"], view_func=review_result_thesis_on_review
    )
    app.add_url_rule(
        "/review/fetch_thesis_on_review",
        methods=["GET"],
        view_func=fetch_thesis_on_review,
    )
    app.add_url_rule(
        "/review/become_thesis_reviewer",
        methods=["GET"],
        view_func=review_become_thesis_reviewer_ask,
    )
    app.add_url_rule(
        "/review/become_thesis_reviewer_confirm",
        methods=["POST"],
        view_func=review_become_thesis_reviewer_confirm,
    )

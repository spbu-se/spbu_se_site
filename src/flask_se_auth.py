# SPDX-License-Identifier: Apache-2.0

import hmac
import io
import json
import logging
import os
import zipfile

__all__ = ["login_required"]
import pathlib

import cachecontrol
import google.auth.transport.requests
import requests
from flask import flash, redirect, render_template, request, send_file, session, url_for
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from PIL import Image
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.security import check_password_hash, generate_password_hash

from flask_se_config import (
    LOGIN_RATE_LIMITER,
    REGISTER_RATE_LIMITER,
    VK_CLIENT_ID,
    VK_CLIENT_SECRET,
    secure_filename,
)
from se_models import Users, db

# Global variables
UPLOAD_FOLDER = "static/images/avatars/"
UPLOAD_TMP_FOLDER = "static/tmp/avatars/"
ALLOWED_EXTENSIONS = {"bmp", "png", "jpg", "jpeg"}

login_manager = LoginManager()
login_manager.login_view = "login_index"  # pyright: ignore[reportAttributeAccessIssue]


# Google auth (https://github.com/code-specialist/flask_google_login/blob/main/app.py)
# Disable transport security only in dev; production must enforce HTTPS.
if os.environ.get("SE_DEV_OAUTH_INSECURE", "") == "1":
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

GOOGLE_CLIENT_ID = "593053078492-i6hf335m9hm0vtj23df62q09j07esbhu.apps.googleusercontent.com"
# Hack: the flask_se app does not follow application factory pattern, so at this point we
# do not know the environment we are running in. Try prod then test.
client_secrets_file = os.path.join(pathlib.Path(__file__).parent, "client_google.json")
if not os.path.isfile(client_secrets_file):
    client_secrets_file = os.path.join(pathlib.Path(__file__).parent, "client_google_test.json")


@login_manager.user_loader
def load_user(user_id):
    user = db.session.get(Users, int(user_id))
    if user is not None and user.deleted:
        return None
    return user


@login_manager.unauthorized_handler
def handle_needs_login():
    flash("Для выполнения этого действия необходимо войти.")
    return redirect(url_for("login_index", next=request.endpoint))


def redirect_next_url(fallback):
    if "next_url" not in session:
        return redirect(fallback)

    try:
        dest_url = url_for(session["next_url"])
        return redirect(dest_url)
    except Exception:
        return redirect(fallback)


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def _download_avatar(url: str, max_bytes: int = 2 * 1024 * 1024) -> bytes | None:
    """Download an avatar with a byte budget (avoids memory-exhaustion DoS)."""
    try:
        r = requests.get(url, allow_redirects=True, timeout=30, stream=True)
        r.raise_for_status()
    except requests.RequestException:
        return None

    total = 0
    chunks = []
    for chunk in r.iter_content(chunk_size=64 * 1024):
        total += len(chunk)
        if total > max_bytes:
            r.close()
            return None
        chunks.append(chunk)
    r.close()
    return b"".join(chunks)


def login_index():
    if current_user.is_authenticated:
        return redirect(url_for("user_profile"))

    next_url = request.args.get("next")

    if next_url:
        try:
            url_for(next_url)
            session["next_url"] = next_url
        except Exception:
            session.pop("next_url", None)
    else:
        session.pop("next_url", None)

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        client_ip = request.remote_addr or "unknown"
        if not LOGIN_RATE_LIMITER.allow("login:" + client_ip):
            flash(
                "Слишком много попыток входа. Попробуйте позже.",
                category="error",
            )
            return render_template("auth/login.html", user=current_user)

        user = Users.query.filter_by(email=email).first()
        # Unified error message: do not reveal whether the email exists
        # (prevents account enumeration).
        invalid_message = "Пара логин и пароль указаны неверно"
        if user:
            password_hash = user.password_hash
            if password_hash is not None:
                password_ok = False
                try:
                    password_ok = check_password_hash(password_hash, password)  # pyright: ignore[reportArgumentType]
                except ValueError:
                    logging.getLogger("flask_se.auth").exception(
                        "check_password_hash failed for user %s", email
                    )
                if password_ok:
                    login_user(user, remember=True)
                    return redirect_next_url(fallback=url_for("user_profile"))
                hs = password_hash.split("$")
                if (
                    len(hs) == 3
                    and hmac.HMAC(
                        hs[1].encode("utf-8"),
                        (password or "").encode("utf-8"),
                        hs[0],
                    ).hexdigest()
                    == hs[2]
                ):
                    login_user(user, remember=True)
                    return redirect_next_url(fallback=url_for("user_profile"))
                flash(
                    invalid_message,
                    category="error",
                )
                return render_template("auth/login.html", user=current_user)
            flash(
                invalid_message,
                category="error",
            )
            return render_template("auth/login.html", user=current_user)
        flash(
            invalid_message,
            category="error",
        )
        return render_template("auth/login.html", user=current_user)

    return render_template("auth/login.html", user=current_user)


# https://vk.com/dev/authcode_flow_user
def vk_login():
    state = os.urandom(16).hex()
    session["vk_state"] = state
    redirect_uri = url_for("vk_callback", _external=True)
    auth_url = (
        "https://oauth.vk.com/authorize?"
        f"client_id={VK_CLIENT_ID}"
        "&display=page"
        f"&redirect_uri={redirect_uri}"
        "&scope=friends,email&response_type=code&v=5.130"
        f"&state={state}"
    )
    return redirect(auth_url)


def vk_callback():
    user_code = request.args.get("code")

    if not user_code:
        return redirect(url_for("index"))

    expected_state = session.pop("vk_state", None)
    returned_state = request.args.get("state")
    if not expected_state or not returned_state or expected_state != returned_state:
        return redirect(url_for("login_index"))

    # Get access token
    response = requests.post(
        "https://oauth.vk.com/access_token",
        data={
            "client_id": VK_CLIENT_ID,
            "client_secret": VK_CLIENT_SECRET,
            "redirect_uri": url_for("vk_callback", _external=True),
            "code": user_code,
        },
        timeout=10,
    )
    access_token_json = json.loads(response.text)

    if "error" in access_token_json:
        return redirect(url_for("index"))

    vk_id = access_token_json["user_id"]
    access_token = access_token_json["access_token"]
    vk_email = access_token_json["email"]

    # Get user name
    response = requests.get(
        "https://api.vk.com/method/users.get?user_ids="
        + str(vk_id)
        + "&fields=photo_100&access_token="
        + str(access_token)
        + "&v=5.130",
        timeout=10,
    )
    vk_user = json.loads(response.text)

    user = Users.query.filter_by(vk_id=vk_id).first()

    # New user?
    if user is None:
        # Yes
        try:
            avatar_uri = os.urandom(16).hex()
            avatar_uri = avatar_uri + ".jpg"

            if "photo_100" in vk_user["response"][0]:
                avatar = _download_avatar(vk_user["response"][0]["photo_100"])
                if avatar is not None:
                    with open("static/images/avatars/" + avatar_uri, "wb") as f:
                        f.write(avatar)

            new_user = Users(
                last_name=vk_user["response"][0]["last_name"],
                first_name=vk_user["response"][0]["first_name"],
                avatar_uri=avatar_uri,
                email=vk_email,
                vk_id=vk_id,
            )
            db.session.add(new_user)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            error = str(e.__dict__["orig"])
            flash(error, category="error")
            return redirect(url_for("login_index"))

        user = Users.query.filter_by(vk_id=vk_id).first()

    login_user(user, remember=True)
    return redirect_next_url(fallback=url_for("user_profile"))


def register_basic():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        first_name = request.form.get("first_name", "").strip()

        client_ip = request.remote_addr or "unknown"
        if not REGISTER_RATE_LIMITER.allow("register:" + client_ip):
            flash(
                "Слишком много попыток регистрации. Попробуйте позже.",
                category="error",
            )
            return render_template("auth/register_basic.html", user=current_user)

        user = Users.query.filter_by(email=email).first()
        if user:
            flash(
                "Такой почтовый адрес уже зарегистрирован.",
                category="error",
            )
        elif len(email) < 5:
            flash(
                "Почтовый адрес должен быть больше чем 5 символов",
                category="error",
            )
        elif len(password) < 8:
            flash(
                "Пароль должен быть не короче 8 символов",
                category="error",
            )
        elif len(first_name) < 1:
            flash("Имя не может быть пустым")
        else:
            new_user = Users(
                email=email,
                first_name=first_name,
                password_hash=generate_password_hash(password, method="pbkdf2:sha256"),
            )
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            return redirect(url_for("user_profile"))

    return render_template("auth/register_basic.html", user=current_user)


def password_recovery():
    return render_template("password_recovery.html")


@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))


@login_required
def user_profile():
    user = Users.query.filter_by(id=current_user.id).first()

    if request.method == "POST":
        last_name = request.form.get("last_name", "").strip()
        first_name = request.form.get("first_name", "").strip()
        middle_name = request.form.get("middle_name", "").strip()
        how_to_contact = request.form.get("how_to_contact", "").strip()

        if user and first_name:
            user.first_name = first_name
            user.middle_name = middle_name
            user.last_name = last_name
            user.how_to_contact = how_to_contact
            db.session.commit()

    return render_template("auth/profile.html", user=user)


def _row_to_dict(instance):
    """Serialize a SQLAlchemy model row to a plain dict of its column values."""
    return {column.key: getattr(instance, column.key) for column in instance.__table__.columns}


def _user_owned_content(user):
    """Collect all personal-data records owned by the user as plain dicts."""
    collections = {
        "posts": user.news,
        "theses": user.thesises,
        "diploma_themes": user.diploma_themes_author,
        "theses_on_review": user.thesis_on_review_author,
        "reviews": user.reviewer,
        "post_votes": user.all_user_votes,
        "internships": user.internship_author,
        "current_theses": user.current_thesises,
    }
    return {
        key: [_row_to_dict(item) for item in items] for key, items in collections.items() if items
    }


@login_required
def user_export():
    """Stream a ZIP archive with the current user's personal data (GDPR export)."""
    user = Users.query.filter_by(id=current_user.id).first()

    account = _row_to_dict(user)
    account.pop("password_hash", None)

    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(
            "account.json",
            json.dumps(account, ensure_ascii=False, indent=2, default=str),
        )
        archive.writestr(
            "content.json",
            json.dumps(
                _user_owned_content(user),
                ensure_ascii=False,
                indent=2,
                default=str,
            ),
        )
    buffer.seek(0)

    return send_file(
        buffer,
        mimetype="application/zip",
        as_attachment=True,
        download_name=f"user-data-{user.id}.zip",
    )


@login_required
def delete_account():
    """Soft-delete the current account: block login, purge identifying fields.

    Published content (posts, theses, practice records, votes, reviews) stays in
    place with intact attribution — the account row is kept as a tombstone so
    foreign keys and author links keep working.
    """
    user = Users.query.filter_by(id=current_user.id).first()
    if user is None or user.deleted:
        flash("Аккаунт не найден или уже удалён.", category="error")
        return redirect(url_for("index"))

    user.deleted = True
    user.email = None
    user.password_hash = None
    user.vk_id = None
    user.fb_id = None
    user.google_id = None
    user.avatar_uri = "empty.jpg"
    user.how_to_contact = None
    user.role = 0
    db.session.commit()

    logout_user()
    flash("Аккаунт удалён. Опубликованные материалы сохранены.")
    return redirect(url_for("index"))


@login_required
def upload_avatar():
    if request.method == "POST":
        # check if the post request has the file part
        if "file" not in request.files:
            flash("No file part")
            return redirect(url_for("upload_avatar"))
        file = request.files["file"]
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == "":
            flash("No selected file")
            return redirect(url_for("upload_avatar"))
        # Sanity check: limit uploadable filename
        # to avoid excessive burden to NFKD normalization
        # in secure_filename() method
        if len(file.filename or "") > 1000:
            flash("Filename too long")
            return redirect(url_for("upload_avatar"))
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)  # pyright: ignore[reportArgumentType]
            new_filename = os.urandom(16).hex()
            _f, ext = os.path.splitext(filename)
            ext = ext.lower()

            if ext not in {".jpg", ".jpeg", ".png", ".bmp"}:
                flash("Unsupported file type")
                return redirect(url_for("upload_avatar"))

            if ext in [".jpg", ".jpeg"]:
                file.save(os.path.join(UPLOAD_FOLDER + "/" + new_filename + ".jpg"))
            else:
                tmp_path = os.path.join(UPLOAD_TMP_FOLDER + "/" + new_filename + ext)
                try:
                    file.save(tmp_path)
                    with Image.open(tmp_path) as im:
                        rgb_im = im.convert("RGB")
                        rgb_im.save(UPLOAD_FOLDER + "/" + new_filename + ".jpg")
                except Exception:  # noqa: S110  DecompressionBombError is not an OSError
                    pass
                finally:
                    if os.path.isfile(tmp_path):
                        os.unlink(tmp_path)

            user = Users.query.filter_by(id=current_user.id).first()

            # If user have avatar -> remove it from disk
            new_full_filename = new_filename + ".jpg"
            if (
                user
                and user.avatar_uri != "empty.jpg"
                and os.path.isfile(UPLOAD_FOLDER + "/" + user.avatar_uri)
            ):
                os.unlink(UPLOAD_FOLDER + "/" + user.avatar_uri)

            if user:
                user.avatar_uri = new_full_filename
            db.session.commit()

    return "", 204


def google_login():
    flow = Flow.from_client_secrets_file(
        client_secrets_file=client_secrets_file,
        scopes=[
            "https://www.googleapis.com/auth/userinfo.profile",
            "https://www.googleapis.com/auth/userinfo.email",
            "openid",
        ],
    )

    flow.redirect_uri = url_for("google_callback", _external=True)
    authorization_url, state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
    )
    session["state"] = state
    return redirect(authorization_url)


def google_callback():
    expected_state = session.pop("state", None)
    returned_state = request.args.get("state")

    if not expected_state or not returned_state or expected_state != returned_state:
        return redirect(url_for("login_index"))

    flow = Flow.from_client_secrets_file(
        client_secrets_file=client_secrets_file,
        scopes=[
            "https://www.googleapis.com/auth/userinfo.profile",
            "https://www.googleapis.com/auth/userinfo.email",
            "openid",
        ],
    )

    flow.redirect_uri = url_for("google_callback", _external=True)
    flow.fetch_token(authorization_response=request.url)

    credentials = flow.credentials
    request_session = requests.session()
    cached_session = cachecontrol.CacheControl(request_session)
    token_request = google.auth.transport.requests.Request(session=cached_session)

    id_info = id_token.verify_oauth2_token(
        id_token=credentials._id_token,  # noqa: SLF001  # pyright: ignore[reportAttributeAccessIssue]
        request=token_request,
        audience=GOOGLE_CLIENT_ID,
        clock_skew_in_seconds=60,
    )

    user = Users.query.filter_by(google_id=id_info.get("sub")).first()

    # New user?
    if user is None:
        # Yes
        try:
            avatar_uri = os.urandom(16).hex()
            avatar_uri = avatar_uri + ".jpg"

            if "picture" in id_info:
                avatar = _download_avatar(id_info.get("picture") or "")
                if avatar is not None:
                    with open("static/images/avatars/" + avatar_uri, "wb") as f:
                        f.write(avatar)

            new_user = Users(
                last_name=id_info.get("family_name"),
                first_name=id_info.get("given_name"),
                avatar_uri=avatar_uri,
                google_id=id_info.get("sub"),
                email=id_info.get("email"),
            )
            db.session.add(new_user)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            error = str(e.__dict__["orig"])
            flash(error, category="error")
            return redirect(url_for("login_index"))

        user = Users.query.filter_by(google_id=id_info.get("sub")).first()

    login_user(user, remember=True)
    return redirect_next_url(fallback=url_for("user_profile"))


def register_routes(app) -> None:
    app.add_url_rule("/login.html", methods=["GET", "POST"], view_func=login_index)
    app.add_url_rule("/register_basic.html", methods=["GET", "POST"], view_func=register_basic)
    app.add_url_rule(
        "/password_recovery.html", methods=["GET", "POST"], view_func=password_recovery
    )
    app.add_url_rule("/profile.html", methods=["GET", "POST"], view_func=user_profile)
    app.add_url_rule("/profile/export.zip", methods=["GET"], view_func=user_export)
    app.add_url_rule("/profile/delete", methods=["POST"], view_func=delete_account)
    app.add_url_rule("/upload_avatar", methods=["GET", "POST"], view_func=upload_avatar)
    app.add_url_rule("/logout", methods=["GET"], view_func=logout)
    app.add_url_rule("/google_login", methods=["GET"], view_func=google_login)
    app.add_url_rule("/google_callback", methods=["GET"], view_func=google_callback)
    app.add_url_rule("/vk_login", methods=["GET"], view_func=vk_login)
    app.add_url_rule("/vk_callback", methods=["GET"], view_func=vk_callback)

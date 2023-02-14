# -*- coding: utf-8 -*-

import os
import json
import pathlib

import requests

from PIL import Image

from flask import session
from flask_login import login_user, login_required, logout_user, current_user, LoginManager
from flask import session, request, flash, render_template, redirect, url_for
from google_auth_oauthlib.flow import Flow
import google.auth.transport.requests
from google.oauth2 import id_token
from pip._vendor import cachecontrol
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.security import generate_password_hash, check_password_hash

from flask_se_config import secure_filename
from se_models import db, Users

# Global variables
UPLOAD_FOLDER = 'static/images/avatars/'
UPLOAD_TMP_FOLDER = 'static/tmp/avatars/'
ALLOWED_EXTENSIONS = {'bmp', 'png', 'jpg', 'jpeg'}

login_manager = LoginManager()
login_manager.login_view = "login_index"

# create an alias of login_required decorator
login_required = login_required


# Google auth (https://github.com/code-specialist/flask_google_login/blob/main/app.py)
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

GOOGLE_CLIENT_ID = "593053078492-i6hf335m9hm0vtj23df62q09j07esbhu.apps.googleusercontent.com"
client_secrets_file = os.path.join(pathlib.Path(__file__).parent, "client_google.json")


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


@login_manager.unauthorized_handler
def handle_needs_login():
    flash("Для выполнения этого действия необходимо войти.")
    return redirect(url_for('login_index', next=request.endpoint))


def redirect_next_url(fallback):

    if 'next_url' not in session:
        redirect(fallback)

    try:
        dest_url = url_for(session['next_url'])
        return redirect(dest_url)
    except:
        return redirect(fallback)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def login_index():

    if current_user.is_authenticated:
        return redirect(url_for('user_profile'))

    next_url = request.args.get("next")

    if next_url:
        session['next_url'] = next_url
    else:
        session.pop('next_url', None)

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = Users.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password_hash, password):
                login_user(user, remember=True)
                return redirect_next_url(fallback=url_for('user_profile'))
            else:
                flash('Пара логин и пароль указаны неверно', category='error')
                return render_template('auth/login.html', user=current_user)
        else:
            flash('Пользователя с таким почтовым адресом нет', category='error')
            return render_template('auth/login.html', user=current_user)

    return render_template('auth/login.html', user=current_user)


# https://vk.com/dev/authcode_flow_user
def vk_callback():

    user_code = request.args.get('code')

    if not user_code:
        return redirect(url_for('index'))

    # Get access token
    response = requests.get('https://oauth.vk.com/access_token?client_id=8051225&client_secret=ZPNX8y5nQmzGCghUKdJ9&redirect_uri=https://se.math.spbu.ru/vk_callback&code=' + user_code)
    access_token_json = json.loads(response.text)

    if "error" in access_token_json:
        return redirect(url_for('index'))

    print(access_token_json)

    vk_id = access_token_json['user_id']
    access_token = access_token_json['access_token']
    vk_email = access_token_json['email']


    # Get user name
    response = requests.get('https://api.vk.com/method/users.get?user_ids=' + str(vk_id) + '&fields=photo_100&access_token=' + str(access_token) + '&v=5.130')
    vk_user = json.loads(response.text)

    user = Users.query.filter_by(vk_id=vk_id).first()

    # New user?
    if user is None:
        # Yes
        try:
            avatar_uri = os.urandom(16).hex()
            avatar_uri = avatar_uri + ".jpg"

            if 'photo_100' in vk_user['response'][0]:
                r = requests.get(vk_user['response'][0]['photo_100'], allow_redirects=True)
                open('static/images/avatars/' + avatar_uri, 'wb').write(r.content)

            new_user = Users(last_name=vk_user['response'][0]['last_name'],
                             first_name=vk_user['response'][0]['first_name'],
                             avatar_uri=avatar_uri, email=vk_email,
                             vk_id=vk_id)
            db.session.add(new_user)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            error = str(e.__dict__['orig'])
            print(error)
            print("Can't add new user to the Database")
            flash(error, category='error')
            return redirect(url_for('login_index'))

        user = Users.query.filter_by(vk_id=vk_id).first()

    login_user(user, remember=True)
    return redirect_next_url(fallback=url_for('user_profile'))


def register_basic():
    if request.method == 'POST':
        email = request.form.get('email').strip()
        password = request.form.get('password')
        first_name = request.form.get('first_name').strip()

        user = Users.query.filter_by(email=email).first()
        if user:
            flash('Такой почтовый адрес уже зарегистрирован.', category='error')
        elif len(email) < 5:
            flash('Почтовый адрес должен быть больше чем 5 символов', category='error')
        elif len(password) < 5:
            flash('Пароль должен быть больше чем 5 символов', category='error')
        elif len(first_name) < 1:
            flash('Имя не может быть пустым')
        else:
            new_user = Users(email=email, first_name=first_name, password_hash=generate_password_hash(password, method='sha256'))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            return redirect(url_for('user_profile'))

    return render_template("auth/register_basic.html", user=current_user)


def password_recovery():
    return render_template("password_recovery.html")


@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@login_required
def user_profile():
    user = Users.query.filter_by(id=current_user.id).first()

    if request.method == 'POST':
        last_name = request.form.get('last_name').strip()
        first_name = request.form.get('first_name').strip()
        middle_name = request.form.get('middle_name').strip()
        how_to_contact = request.form.get('how_to_contact').strip()

        if first_name:
            user.first_name = first_name
            user.middle_name = middle_name
            user.last_name = last_name
            user.how_to_contact = how_to_contact
            db.session.commit()

    return render_template('auth/profile.html', user=user)


@login_required
def upload_avatar():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            new_filename = os.urandom(16).hex()
            f, ext = os.path.splitext(filename)

            if ext in ['.jpg', '.jpeg']:
                file.save(os.path.join(UPLOAD_FOLDER + "/" + new_filename + ".jpg"))
            else:
                try:
                    file.save(os.path.join(UPLOAD_TMP_FOLDER + "/" + new_filename + ext))
                    with Image.open(UPLOAD_TMP_FOLDER + "/" + new_filename + ext) as im:
                        rgb_im = im.convert('RGB')
                        rgb_im.save(UPLOAD_FOLDER + "/" + new_filename + ".jpg")
                        os.unlink(UPLOAD_TMP_FOLDER + "/" + new_filename + ext)
                except OSError:
                    print("cannot convert", new_filename + ".jpg")

            user = Users.query.filter_by(id=current_user.id).first()

            # If user have avatar -> remove it from disk
            new_full_filename = new_filename + ".jpg"
            if user.avatar_uri != 'empty.jpg':
                if os.path.isfile(UPLOAD_FOLDER + "/" + user.avatar_uri):
                    os.unlink(UPLOAD_FOLDER + "/" + user.avatar_uri)

            user.avatar_uri=new_full_filename
            db.session.commit()

    return '', 204


def google_login():

    flow = Flow.from_client_secrets_file(
        client_secrets_file=client_secrets_file,
        scopes=["https://www.googleapis.com/auth/userinfo.profile",
                "https://www.googleapis.com/auth/userinfo.email",
                "openid"]
    )

    flow.redirect_uri = url_for('google_callback', _external=True)
    authorization_url, state = flow.authorization_url(access_type='offline',
                                                      include_granted_scopes='true')
    session["state"] = state
    return redirect(authorization_url)


def google_callback():

    state = session["state"]
    print(request.args.get('state'), session)

    if not state:
        redirect(url_for('login_index'))

    flow = Flow.from_client_secrets_file(
        client_secrets_file=client_secrets_file,
        scopes=["https://www.googleapis.com/auth/userinfo.profile",
                "https://www.googleapis.com/auth/userinfo.email",
                "openid"]
    )

    flow.redirect_uri = url_for('google_callback', _external=True)
    flow.fetch_token(authorization_response=request.url)

    credentials = flow.credentials
    request_session = requests.session()
    cached_session = cachecontrol.CacheControl(request_session)
    token_request = google.auth.transport.requests.Request(session=cached_session)

    id_info = id_token.verify_oauth2_token(
        id_token=credentials._id_token,
        request=token_request,
        audience=GOOGLE_CLIENT_ID,
        clock_skew_in_seconds=60
    )

    user = Users.query.filter_by(google_id=id_info.get('sub')).first()

    # New user?
    if user is None:
        # Yes
        try:
            avatar_uri = os.urandom(16).hex()
            avatar_uri = avatar_uri + ".jpg"

            if 'picture' in id_info:
                r = requests.get(id_info.get('picture'), allow_redirects=True)
                open('static/images/avatars/' + avatar_uri, 'wb').write(r.content)

            new_user = Users(last_name=id_info.get('family_name'),
                             first_name=id_info.get('given_name'),
                             avatar_uri=avatar_uri,
                             google_id=id_info.get('sub'),
                             email=id_info.get('email'))
            db.session.add(new_user)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            error = str(e.__dict__['orig'])
            print(error)
            print("Can't add new user to Database")
            flash(error, category='error')
            return redirect(url_for('login_index'))

        user = Users.query.filter_by(google_id=id_info.get('sub')).first()

    login_user(user, remember=True)
    return redirect_next_url(fallback=url_for('user_profile'))

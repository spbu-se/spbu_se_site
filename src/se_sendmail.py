# SPDX-License-Identifier: Apache-2.0

import logging
import os
import smtplib
from datetime import UTC, datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from sqlalchemy.exc import IntegrityError, OperationalError

from flask_se_config import MAIL_PASSWORD
from se_models import DiplomaThemes, Notification, NotificationLog, Users, db

MAIL_DEFAULT_SENDER = "sysprog_notification@spbu.ru"
MAIL_DEFAULT_SENDER_STRING = "SE уведомления <sysprog_notification@spbu.ru>"

DIPLOMA_THEMES_JOB_TYPE = "diploma_themes_on_review"
DIPLOMA_THEMES_SEND_INTERVAL = timedelta(hours=24)

_log = logging.getLogger("flask_se.mail")


def send_mail(to: str, subject: str, plain: str, html: str | None = None) -> bool:
    """Send one e-mail from the notification sender; no-op on staging.

    A single helper for the transient mail paths (notifications, password
    recovery). Returns False instead of raising so a mail outage never breaks
    the request that triggered it.
    """
    if os.getenv("SE_STAGING") is not None:
        return False
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = MAIL_DEFAULT_SENDER
    message["To"] = to
    message.attach(MIMEText(plain, "plain"))
    if html:
        message.attach(MIMEText(html, "html"))
    try:
        server = smtplib.SMTP("mail.spbu.ru", 25, timeout=10)
        try:
            server.ehlo()
            server.login(MAIL_DEFAULT_SENDER, MAIL_PASSWORD)
            server.sendmail(MAIL_DEFAULT_SENDER, [to], message.as_string())
        finally:
            server.quit()
    except (smtplib.SMTPException, OSError) as exc:
        # OSError covers socket.timeout / ConnectionRefusedError / EHOSTUNREACH;
        # without the timeout a dead mail relay would hang the request thread.
        _log.warning("send_mail to %s failed: %s", to, exc)
        return False
    else:
        _log.info("send_mail to %s sent", to)
        return True


def notification_send_mail() -> None:
    notifications = Notification.query.filter_by(type=0).all()

    for n in notifications:
        user = Users.query.filter_by(id=n.recipient).first()

        if not user:
            continue

        message = MIMEMultipart("alternative")
        message["Subject"] = n.title
        message["From"] = MAIL_DEFAULT_SENDER
        message["To"] = user.email

        part1 = MIMEText(n.content, "plain")
        part2 = MIMEText(n.content, "html")

        message.attach(part1)
        message.attach(part2)

        server = smtplib.SMTP("mail.spbu.ru", 25)

        try:
            server.ehlo()
            server.login(MAIL_DEFAULT_SENDER, MAIL_PASSWORD)

        except smtplib.SMTPException as exc:
            _log.warning("notification SMTP handshake failed: %s", exc)

        try:
            # Staging must not send real mail, but the notification row is
            # still consumed so the queue drains instead of growing unbounded.
            if os.getenv("SE_STAGING") is None:
                server.sendmail(MAIL_DEFAULT_SENDER, user.email, message.as_string())
            db.session.delete(n)
            db.session.commit()

        except smtplib.SMTPException as exc:
            _log.warning("notification send to %s failed: %s", user.email, exc)


def _ensure_notification_log_table() -> None:
    """Create the idempotency marker table if missing.

    The migrations tree is not wired into the webhook deploys, so the small
    NotificationLog table is created lazily (no-op when it already exists).
    The race of two workers creating it on the very first run is absorbed by
    ignoring the duplicate-table error.
    """
    try:
        NotificationLog.__table__.create(bind=db.engine, checkfirst=True)
    except OperationalError:
        db.session.rollback()


def _claim_diploma_themes_send() -> bool:
    """Atomically claim the right to send today's themes digest.

    Every gunicorn/uwsgi worker runs the same APScheduler job, so without a
    guard the digest would be sent N times a day. The first worker to commit a
    fresh ``last_sent_at`` wins; concurrent workers see it and skip. Returns
    True when this process should send.
    """
    _ensure_notification_log_table()
    now = datetime.now(UTC).replace(tzinfo=None)

    log = NotificationLog.query.filter_by(type=DIPLOMA_THEMES_JOB_TYPE).first()
    if log is not None:
        if now - log.last_sent_at < DIPLOMA_THEMES_SEND_INTERVAL:
            return False
        # Update the timestamp under the unique row; the racing worker's
        # UPDATE matches zero rows, so exactly one process proceeds.
        updated = NotificationLog.query.filter_by(
            type=DIPLOMA_THEMES_JOB_TYPE,
            last_sent_at=log.last_sent_at,
        ).update({NotificationLog.last_sent_at: now})
        db.session.commit()
        return updated == 1

    db.session.add(NotificationLog(type=DIPLOMA_THEMES_JOB_TYPE, last_sent_at=now))
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return False
    return True


def notification_send_diploma_themes_on_review() -> None:
    if os.getenv("SE_STAGING") is not None:
        return

    # Match the admin review view (status < 2: new + need-update themes).
    diploma_themes_on_review_count = DiplomaThemes.query.filter(DiplomaThemes.status < 2).count()

    if not diploma_themes_on_review_count:
        return

    if not _claim_diploma_themes_send():
        return

    # Add recipients here!
    recipients = [
        "y.litvinov@spbu.ru",
        "dluciv@gmail.com",
        "stanislav.sartasov@gmail.com",
    ]

    message = MIMEMultipart("alternative")
    message["Subject"] = "[SE site] Есть неутвержённые темы учебных практик и ВКР "
    message["From"] = MAIL_DEFAULT_SENDER
    message["To"] = "ilya@hackerdom.ru"
    message["CC"] = ", ".join(recipients)

    data = f"""
    Сейчас на сайте {diploma_themes_on_review_count} тем находятся на проверке (<a href="https://se.math.spbu.ru/admin/reviewdiplomathemes/" target="_blank">Проверка тем</a>).
    """

    part1 = MIMEText(data, "plain")
    part2 = MIMEText(data, "html")
    message.attach(part1)
    message.attach(part2)

    server = smtplib.SMTP("mail.spbu.ru", 25)

    try:
        server.ehlo()
        server.login(MAIL_DEFAULT_SENDER, MAIL_PASSWORD)

    except smtplib.SMTPException as exc:
        _log.warning("diploma themes SMTP handshake failed: %s", exc)

    try:
        if os.getenv("SE_STAGING") is None:
            server.sendmail(MAIL_DEFAULT_SENDER, recipients, message.as_string())

    except smtplib.SMTPException as exc:
        _log.warning("diploma themes send failed: %s", exc)

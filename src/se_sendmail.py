# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from flask_se_config import MAIL_PASSWORD
from se_models import DiplomaThemes, Notification, Users, db

MAIL_DEFAULT_SENDER = "sysprog_notification@spbu.ru"
MAIL_DEFAULT_SENDER_STRING = "SE СѓРІРµРґРѕРјР»РµРЅРёСЏ <sysprog_notification@spbu.ru>"


def notification_send_mail():
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

        except smtplib.SMTPHeloError:
            print("The server didnвЂ™t reply properly to the HELO greeting.")
        except smtplib.SMTPAuthenticationError:
            print(
                "The server didnвЂ™t accept the username/password combination. Username:"
                + MAIL_DEFAULT_SENDER
                + ", PASS:"
                + MAIL_PASSWORD
            )
        except smtplib.SMTPNotSupportedError:
            print("The AUTH command is not supported by the server.")
        except smtplib.SMTPException:
            print("No suitable authentication method was found.")

        try:
            server.sendmail(MAIL_DEFAULT_SENDER, user.email, message.as_string())
            db.session.delete(n)
            db.session.commit()

        except smtplib.SMTPRecipientsRefused:
            print(f"All recipients were refused. Nobody got the mail. User.email: {user.email}")
        except smtplib.SMTPDataError:
            print("The server didnвЂ™t accept the from_addr.")
        except smtplib.SMTPSenderRefused:
            print("The server didnвЂ™t accept the from_addr.")
        except smtplib.SMTPNotSupportedError:
            print("SMTPUTF8 was given in the mail_options but is not supported by the server.")


def notification_send_diploma_themes_on_review():
    diploma_themes_on_review_count = DiplomaThemes.query.filter_by(status=0).count()

    print(
        "Invoke notification_send_diploma_themes_on_review = " + str(diploma_themes_on_review_count)
    )

    if not diploma_themes_on_review_count:
        return

    # Add recipients here!
    recipients = [
        "y.litvinov@spbu.ru",
        "dluciv@gmail.com",
        "stanislav.sartasov@gmail.com",
    ]

    message = MIMEMultipart("alternative")
    message["Subject"] = (
        "[SE site] Р•СЃС‚СЊ РЅРµРѕРґРѕР±СЂРµРЅРЅС‹Рµ С‚РµРјС‹ СѓС‡РµР±РЅС‹С… РїСЂР°РєС‚РёРє Рё Р’РљР "
    )
    message["From"] = MAIL_DEFAULT_SENDER
    message["To"] = "ilya@hackerdom.ru"
    message["CC"] = ", ".join(recipients)

    data = f"""
    РЎРµР№С‡Р°СЃ РЅР° СЃР°Р№С‚Рµ {diploma_themes_on_review_count} С‚РµРј РЅР°С…РѕРґСЏС‚СЃСЏ РЅР° РїСЂРѕРІРµСЂРєРµ (<a href="https://se.math.spbu.ru/admin/reviewdiplomathemes/" target="_blank">РџСЂРѕРІРµСЂРєР° С‚РµРј</a>).
    """

    part1 = MIMEText(data, "plain")
    part2 = MIMEText(data, "html")
    message.attach(part1)
    message.attach(part2)

    server = smtplib.SMTP("mail.spbu.ru", 25)

    try:
        server.ehlo()
        server.login(MAIL_DEFAULT_SENDER, MAIL_PASSWORD)

    except smtplib.SMTPHeloError:
        print("The server didnвЂ™t reply properly to the HELO greeting.")
    except smtplib.SMTPAuthenticationError:
        print(
            "The server didnвЂ™t accept the username/password combination. Username:"
            + MAIL_DEFAULT_SENDER
            + ", PASS:"
            + MAIL_PASSWORD
        )
    except smtplib.SMTPNotSupportedError:
        print("The AUTH command is not supported by the server.")
    except smtplib.SMTPException:
        print("No suitable authentication method was found.")

    try:
        server.sendmail(MAIL_DEFAULT_SENDER, recipients, message.as_string())

    except smtplib.SMTPRecipientsRefused:
        print("All recipients were refused. Nobody got the mail.")
    except smtplib.SMTPDataError:
        print("The server didnвЂ™t accept the from_addr.")
    except smtplib.SMTPSenderRefused:
        print("The server didnвЂ™t accept the from_addr.")
    except smtplib.SMTPNotSupportedError:
        print("SMTPUTF8 was given in the mail_options but is not supported by the server.")

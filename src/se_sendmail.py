# -*- coding: utf-8 -*-

import smtplib, ssl

from se_models import db, Notification, Users
from flask_se_config import MAIL_PASSWORD
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header

MAIL_DEFAULT_SENDER = "sysprog_notification@spbu.ru"
MAIL_DEFAULT_SENDER_STRING = 'SE уведомления <sysprog_notification@spbu.ru>'


def notification_send_mail():

    notifications = Notification.query.filter_by(type=0).all()

    for n in notifications:

        user = Users.query.filter_by(id=n.recipient).first()

        if not user:
            continue

        message = MIMEMultipart('alternative')
        message["Subject"] = n.title
        message["From"] = MAIL_DEFAULT_SENDER
        message["To"] = user.email

        part1 = MIMEText(n.content, 'plain')
        part2 = MIMEText(n.content, 'html')

        message.attach(part1)
        message.attach(part2)

        server = smtplib.SMTP("mail.spbu.ru", 25)

        try:
            server.ehlo()
            server.login(MAIL_DEFAULT_SENDER, MAIL_PASSWORD)

        except smtplib.SMTPHeloError:
            print("The server didn’t reply properly to the HELO greeting.")
        except smtplib.SMTPAuthenticationError:
            print("The server didn’t accept the username/password combination. Username:" + MAIL_DEFAULT_SENDER +
                  ", PASS:" + MAIL_PASSWORD)
        except smtplib.SMTPNotSupportedError:
            print("The AUTH command is not supported by the server.")
        except smtplib.SMTPException:
            print("No suitable authentication method was found.")

        try:
            server.sendmail(MAIL_DEFAULT_SENDER, user.email, message.as_string())
            db.session.delete(n)
            db.session.commit()

        except smtplib.SMTPRecipientsRefused:
            print("All recipients were refused. Nobody got the mail. User.email: {0}".format(user.email))
        except smtplib.SMTPDataError:
            print("The server didn’t accept the from_addr.")
        except smtplib.SMTPSenderRefused:
            print("The server didn’t accept the from_addr.")
        except smtplib.SMTPNotSupportedError:
            print ("SMTPUTF8 was given in the mail_options but is not supported by the server.")
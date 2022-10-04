# -*- coding: utf-8 -*-

import smtplib, ssl

from se_models import db, Notification, Users, DiplomaThemes
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
            print("SMTPUTF8 was given in the mail_options but is not supported by the server.")


def notification_send_diploma_themes_on_review():

    diploma_themes_on_review_count = DiplomaThemes.query.filter_by(status=0).count()

    print ("Invoke notification_send_diploma_themes_on_review = " + str(diploma_themes_on_review_count))

    if not diploma_themes_on_review_count:
        return

    # Add recipients here!
    recipients = ['y.litvinov@spbu.ru', 'dluciv@gmail.com', 'stanislav.sartasov@gmail.com']
    
    message = MIMEMultipart('alternative')
    message["Subject"] = '[SE site] Есть неодобренные темы учебных практик и ВКР'
    message["From"] = MAIL_DEFAULT_SENDER
    message['To'] = "ilya@hackerdom.ru"
    message['CC'] = ", ".join(recipients)

    data = '''
    Сейчас на сайте {0} тем находятся на проверке (<a href="https://se.math.spbu.ru/admin/reviewdiplomathemes/" target="_blank">Проверка тем</a>).
    '''.format(diploma_themes_on_review_count)

    part1 = MIMEText(data, 'plain')
    part2 = MIMEText(data, 'html')
    message.attach(part1)
    message.attach(part2)

    server = smtplib.SMTP("mail.spbu.ru", 25)

    try:
        server.ehlo()
        server.login(MAIL_DEFAULT_SENDER, MAIL_PASSWORD)

    except smtplib.SMTPHeloError:
        print("The server didn’t reply properly to the HELO greeting.")
    except smtplib.SMTPAuthenticationError:
        print("The server didn’t accept the username/password combination. Username:" + MAIL_DEFAULT_SENDER + ", PASS:" + MAIL_PASSWORD)
    except smtplib.SMTPNotSupportedError:
        print("The AUTH command is not supported by the server.")
    except smtplib.SMTPException:
        print("No suitable authentication method was found.")

    try:
        server.sendmail(MAIL_DEFAULT_SENDER, recipients, message.as_string())

    except smtplib.SMTPRecipientsRefused:
        print("All recipients were refused. Nobody got the mail.")
    except smtplib.SMTPDataError:
        print("The server didn’t accept the from_addr.")
    except smtplib.SMTPSenderRefused:
        print("The server didn’t accept the from_addr.")
    except smtplib.SMTPNotSupportedError:
        print ("SMTPUTF8 was given in the mail_options but is not supported by the server.")
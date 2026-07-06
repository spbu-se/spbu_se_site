# -*- coding: utf-8 -*-
import smtplib
from unittest.mock import MagicMock, patch

import pytest


def _seed_diploma_themes():
    from se_models import DiplomaThemes, Users, db

    u = Users.query.filter_by(email="test@spbu.ru").first()
    dt = DiplomaThemes(
        title="Test theme",
        status=0,
        author_id=u.id,
        consultant_id=u.id,
    )
    db.session.add(dt)
    db.session.commit()


class TestSendMailEdges:
    @patch("smtplib.SMTP")
    def test_send_mail_smtp_not_supported_on_login(self, mock_smtp, notification_in_db):
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server
        mock_server.login.side_effect = smtplib.SMTPNotSupportedError
        from se_sendmail import notification_send_mail

        notification_send_mail()
        assert mock_smtp.called

    @patch("smtplib.SMTP")
    def test_send_mail_smtp_exception_on_login(self, mock_smtp, notification_in_db):
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server
        mock_server.login.side_effect = smtplib.SMTPException
        from se_sendmail import notification_send_mail

        notification_send_mail()
        assert mock_smtp.called

    @patch("smtplib.SMTP")
    def test_send_mail_recipients_refused(self, mock_smtp, notification_in_db):
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server
        mock_server.sendmail.side_effect = smtplib.SMTPRecipientsRefused({})
        from se_sendmail import notification_send_mail

        notification_send_mail()
        assert mock_smtp.called

    @patch("smtplib.SMTP")
    def test_send_mail_data_error(self, mock_smtp, notification_in_db):
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server
        mock_server.sendmail.side_effect = smtplib.SMTPDataError(554, b"Data error")
        from se_sendmail import notification_send_mail

        notification_send_mail()
        assert mock_smtp.called

    @patch("smtplib.SMTP")
    def test_send_mail_smtp_not_supported_on_sendmail(self, mock_smtp, notification_in_db):
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server
        mock_server.sendmail.side_effect = smtplib.SMTPNotSupportedError
        from se_sendmail import notification_send_mail

        notification_send_mail()
        assert mock_smtp.called


class TestDiplomaThemesSendMail:
    @patch("smtplib.SMTP")
    def test_diploma_themes_happy_path(self, mock_smtp, seeded_app_ctx):
        _seed_diploma_themes()
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server
        from se_sendmail import notification_send_diploma_themes_on_review

        notification_send_diploma_themes_on_review()
        assert mock_smtp.called
        mock_server.sendmail.assert_called_once()

    @patch("smtplib.SMTP")
    def test_diploma_themes_helo_error(self, mock_smtp, seeded_app_ctx):
        _seed_diploma_themes()
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server
        mock_server.ehlo.side_effect = smtplib.SMTPHeloError(500, b"HELO failed")
        from se_sendmail import notification_send_diploma_themes_on_review

        notification_send_diploma_themes_on_review()
        assert mock_smtp.called

    @patch("smtplib.SMTP")
    def test_diploma_themes_auth_error(self, mock_smtp, seeded_app_ctx):
        _seed_diploma_themes()
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server
        mock_server.login.side_effect = smtplib.SMTPAuthenticationError(535, b"Auth failed")
        from se_sendmail import notification_send_diploma_themes_on_review

        notification_send_diploma_themes_on_review()
        assert mock_smtp.called

    @patch("smtplib.SMTP")
    def test_diploma_themes_smtp_not_supported_on_login(self, mock_smtp, seeded_app_ctx):
        _seed_diploma_themes()
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server
        mock_server.login.side_effect = smtplib.SMTPNotSupportedError
        from se_sendmail import notification_send_diploma_themes_on_review

        notification_send_diploma_themes_on_review()
        assert mock_smtp.called

    @patch("smtplib.SMTP")
    def test_diploma_themes_smtp_exception_on_login(self, mock_smtp, seeded_app_ctx):
        _seed_diploma_themes()
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server
        mock_server.login.side_effect = smtplib.SMTPException
        from se_sendmail import notification_send_diploma_themes_on_review

        notification_send_diploma_themes_on_review()
        assert mock_smtp.called

    @patch("smtplib.SMTP")
    def test_diploma_themes_recipients_refused(self, mock_smtp, seeded_app_ctx):
        _seed_diploma_themes()
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server
        mock_server.sendmail.side_effect = smtplib.SMTPRecipientsRefused({})
        from se_sendmail import notification_send_diploma_themes_on_review

        notification_send_diploma_themes_on_review()
        assert mock_smtp.called

    @patch("smtplib.SMTP")
    def test_diploma_themes_data_error(self, mock_smtp, seeded_app_ctx):
        _seed_diploma_themes()
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server
        mock_server.sendmail.side_effect = smtplib.SMTPDataError(554, b"Data error")
        from se_sendmail import notification_send_diploma_themes_on_review

        notification_send_diploma_themes_on_review()
        assert mock_smtp.called

    @patch("smtplib.SMTP")
    def test_diploma_themes_sender_refused(self, mock_smtp, seeded_app_ctx):
        _seed_diploma_themes()
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server
        mock_server.sendmail.side_effect = smtplib.SMTPSenderRefused(
            501, b"Bad sender", "from@test.com"
        )
        from se_sendmail import notification_send_diploma_themes_on_review

        notification_send_diploma_themes_on_review()
        assert mock_smtp.called

    @patch("smtplib.SMTP")
    def test_diploma_themes_smtp_not_supported_on_sendmail(self, mock_smtp, seeded_app_ctx):
        _seed_diploma_themes()
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server
        mock_server.sendmail.side_effect = smtplib.SMTPNotSupportedError
        from se_sendmail import notification_send_diploma_themes_on_review

        notification_send_diploma_themes_on_review()
        assert mock_smtp.called


@pytest.fixture
def notification_in_db(seeded_app_ctx):
    from se_models import Notification, db

    n = Notification(recipient=1, title="Test", content="Test content", type=0)
    db.session.add(n)
    db.session.commit()
    return n

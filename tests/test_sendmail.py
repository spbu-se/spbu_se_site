# -*- coding: utf-8 -*-
import smtplib
from unittest.mock import MagicMock, patch

import pytest


class TestSendMail:
    @patch("smtplib.SMTP")
    def test_send_mail_processes_notification(self, mock_smtp, notification_in_db):
        from se_sendmail import notification_send_mail

        notification_send_mail()
        assert mock_smtp.called, "SMTP should be called when notification exists"

    @patch("smtplib.SMTP")
    def test_send_mail_no_notifications(self, mock_smtp, seeded_app_ctx):
        from se_sendmail import notification_send_mail

        notification_send_mail()
        assert not mock_smtp.called

    @pytest.mark.parametrize(
        "attr,exc",
        [
            ("login", smtplib.SMTPAuthenticationError(535, b"Auth failed")),
            ("ehlo", smtplib.SMTPHeloError(500, b"HELO failed")),
            ("sendmail", smtplib.SMTPSenderRefused(501, b"Bad sender", "from@test.com")),
        ],
    )
    @patch("smtplib.SMTP")
    def test_send_mail_handles_smtp_errors(self, mock_smtp, notification_in_db, attr, exc):
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server
        getattr(mock_server, attr).side_effect = exc
        from se_sendmail import notification_send_mail

        notification_send_mail()
        assert mock_smtp.called

    @patch("smtplib.SMTP")
    def test_send_mail_skips_missing_user(self, mock_smtp, app_ctx):
        from se_models import Notification, db

        n = Notification(recipient=999, title="Test", content="Test", type=0)
        db.session.add(n)
        db.session.commit()
        from se_sendmail import notification_send_mail

        notification_send_mail()
        assert not mock_smtp.called, "SMTP should not be called for nonexistent user"

    @patch("smtplib.SMTP")
    def test_send_diploma_themes_no_pending(self, mock_smtp, seeded_app_ctx):
        from se_sendmail import notification_send_diploma_themes_on_review

        notification_send_diploma_themes_on_review()
        assert not mock_smtp.called, "SMTP should not be called with no pending themes"

    def test_send_mail_imports(self):
        from se_sendmail import notification_send_diploma_themes_on_review, notification_send_mail

        assert callable(notification_send_mail)
        assert callable(notification_send_diploma_themes_on_review)

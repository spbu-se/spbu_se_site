# -*- coding: utf-8 -*-
import smtplib
from unittest.mock import MagicMock, patch

import pytest


def _seed_diploma_themes(status: int = 0):
    from se_models import DiplomaThemes, Users, db

    u = Users.query.filter_by(email="test@spbu.ru").first()
    dt = DiplomaThemes(
        title="Test theme",
        status=status,
        author_id=u.id,
        consultant_id=u.id,
    )
    db.session.add(dt)
    db.session.commit()


class TestSendMailEdges:
    @pytest.mark.parametrize(
        "attr,exc",
        [
            ("login", smtplib.SMTPNotSupportedError),
            ("login", smtplib.SMTPException),
            ("sendmail", smtplib.SMTPRecipientsRefused({})),
            ("sendmail", smtplib.SMTPDataError(554, b"Data error")),
            ("sendmail", smtplib.SMTPNotSupportedError),
        ],
    )
    @patch("smtplib.SMTP")
    def test_send_mail_smtp_errors(self, mock_smtp, notification_in_db, attr, exc):
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server
        getattr(mock_server, attr).side_effect = exc
        from se_sendmail import notification_send_mail

        notification_send_mail()
        assert mock_smtp.called

    @patch("smtplib.SMTP")
    def test_send_mail_staging_consumes_without_sending(
        self, mock_smtp, notification_in_db, monkeypatch
    ):
        """H3: with SE_STAGING set, the notification row is consumed but no mail is sent."""
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server
        from se_models import Notification

        monkeypatch.setenv("SE_STAGING", "1")
        from se_sendmail import notification_send_mail

        notification_send_mail()
        mock_server.sendmail.assert_not_called()
        remaining = Notification.query.filter_by(type=0).all()
        assert remaining == [], "notification must be consumed even on staging"


class TestDiplomaThemesSendMail:
    @pytest.mark.parametrize(
        "attr,exc",
        [
            ("ehlo", smtplib.SMTPHeloError(500, b"HELO failed")),
            ("login", smtplib.SMTPAuthenticationError(535, b"Auth failed")),
            ("login", smtplib.SMTPNotSupportedError),
            ("login", smtplib.SMTPException),
            ("sendmail", smtplib.SMTPRecipientsRefused({})),
            ("sendmail", smtplib.SMTPDataError(554, b"Data error")),
            ("sendmail", smtplib.SMTPSenderRefused(501, b"Bad sender", "from@test.com")),
            ("sendmail", smtplib.SMTPNotSupportedError),
        ],
    )
    @patch("smtplib.SMTP")
    def test_diploma_themes_smtp_errors(self, mock_smtp, seeded_app_ctx, attr, exc):
        _seed_diploma_themes()
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server
        getattr(mock_server, attr).side_effect = exc
        from se_sendmail import notification_send_diploma_themes_on_review

        notification_send_diploma_themes_on_review()
        assert mock_smtp.called

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
    def test_diploma_themes_counts_need_update_status(self, mock_smtp, seeded_app_ctx):
        """H3: the email count must match the admin review page (status < 2),
        so "need update" themes (status 1) are counted too."""
        _seed_diploma_themes(status=1)
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server
        from se_sendmail import notification_send_diploma_themes_on_review

        notification_send_diploma_themes_on_review()
        mock_server.sendmail.assert_called_once()

    @patch("smtplib.SMTP")
    def test_diploma_themes_skips_approved_status(self, mock_smtp, seeded_app_ctx):
        """H3: approved themes (status 2) must not be counted as on review."""
        _seed_diploma_themes(status=2)
        from se_sendmail import notification_send_diploma_themes_on_review

        notification_send_diploma_themes_on_review()
        assert not mock_smtp.called

    @patch("smtplib.SMTP")
    def test_diploma_themes_idempotent_second_call_skips(self, mock_smtp, seeded_app_ctx):
        """H3: a second run within 24h must not resend (multi-worker guard)."""
        _seed_diploma_themes()
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server
        from se_sendmail import notification_send_diploma_themes_on_review

        notification_send_diploma_themes_on_review()
        assert mock_smtp.called
        assert mock_server.sendmail.call_count == 1

        mock_server.sendmail.reset_mock()
        notification_send_diploma_themes_on_review()
        mock_server.sendmail.assert_not_called()

    @patch("smtplib.SMTP")
    def test_diploma_themes_staging_skips_send(self, mock_smtp, seeded_app_ctx, monkeypatch):
        """H3: with SE_STAGING set, no mail is sent but the digest logic runs."""
        _seed_diploma_themes()
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server
        monkeypatch.setenv("SE_STAGING", "1")
        from se_sendmail import notification_send_diploma_themes_on_review

        notification_send_diploma_themes_on_review()
        mock_server.sendmail.assert_not_called()

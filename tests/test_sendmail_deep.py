# -*- coding: utf-8 -*-
import smtplib
from unittest.mock import MagicMock, patch


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

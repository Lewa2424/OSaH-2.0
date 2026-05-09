import unittest

from osah.application.services.build_daily_report_email_message import build_daily_report_email_message
from osah.domain.entities.daily_report_document import DailyReportDocument
from osah.domain.entities.mail_settings import MailSettings


class BuildDailyReportEmailMessageTests(unittest.TestCase):
    """Тести побудови email-повідомлення щоденного звіту.
    Tests for building the daily report email message.
    """

    def test_joins_multiple_recipients_into_to_header(self) -> None:
        """Перевіряє формування заголовка To для кількох отримувачів.
        Checks building the To header for multiple recipients.
        """

        document = DailyReportDocument(
            created_at_text="2026-05-09T08:00:00",
            subject_text="Щоденний звіт",
            body_text="Текст звіту",
        )
        mail_settings = MailSettings(
            daily_report_enabled=True,
            smtp_host="smtp.example.com",
            smtp_port=587,
            smtp_username="sender@example.com",
            smtp_password="secret",
            sender_email="sender@example.com",
            recipient_email="boss@example.com; lead@example.com",
            use_tls=True,
            last_sent_date="",
            daily_report_time="08:00",
        )

        email_message = build_daily_report_email_message(document, mail_settings)

        self.assertEqual(email_message["To"], "boss@example.com, lead@example.com")


if __name__ == "__main__":
    unittest.main()

import tempfile
import unittest
from datetime import datetime
from pathlib import Path

from osah.application.services.build_daily_report_document import build_daily_report_document
from osah.application.services.build_daily_report_email_message import build_daily_report_email_message
from osah.application.services.initialize_application import initialize_application
from osah.domain.entities.mail_settings import MailSettings
from osah.infrastructure.config.application_paths import build_application_paths
from osah.infrastructure.docx.render_daily_report_docx import render_daily_report_docx
from osah.infrastructure.logging.shutdown_logging import shut_down_logging


class BuildDailyReportEmailMessageTests(unittest.TestCase):
    """Тести побудови email-повідомлення щоденного звіту.
    Tests for building the daily report email message.
    """

    def test_joins_multiple_recipients_into_to_header(self) -> None:
        """Перевіряє формування заголовка To та вкладення .docx.
        Checks building the To header and attaching the .docx file.
        """

        with tempfile.TemporaryDirectory() as temporary_directory:
            application_paths = build_application_paths(Path(temporary_directory))
            context = initialize_application(application_paths)
            document = build_daily_report_document(
                context.database_path,
                created_at=datetime(2026, 5, 9, 8, 0),
            )
            report_file_path = Path(temporary_directory) / "daily-report.docx"
            render_daily_report_docx(document.snapshot, report_file_path)
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

            email_message = build_daily_report_email_message(document, mail_settings, report_file_path)

            self.assertEqual(email_message["To"], "boss@example.com, lead@example.com")
            self.assertTrue(any(part.get_filename() == report_file_path.name for part in email_message.iter_attachments()))
            shut_down_logging()


if __name__ == "__main__":
    unittest.main()

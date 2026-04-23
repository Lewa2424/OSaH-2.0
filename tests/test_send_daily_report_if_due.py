from datetime import datetime
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from osah.application.services.initialize_application import initialize_application
from osah.application.services.save_mail_settings import save_mail_settings
from osah.application.services.send_daily_report_if_due import send_daily_report_if_due
from osah.domain.entities.mail_settings import MailSettings
from osah.infrastructure.config.application_paths import build_application_paths
from osah.infrastructure.logging.shutdown_logging import shut_down_logging


class SendDailyReportIfDueTests(unittest.TestCase):
    """Тести запуску автоотчіту за налаштованим часом.
    Tests automatic report sending by configured time.
    """

    def test_send_daily_report_if_due_waits_for_configured_time(self) -> None:
        """Перевіряє, що автоотчіт не стартує раніше заданого часу.
        Checks that automatic report sending does not start before configured time.
        """

        with tempfile.TemporaryDirectory() as temporary_directory:
            application_paths = build_application_paths(Path(temporary_directory))
            context = initialize_application(application_paths)
            save_mail_settings(
                context.database_path,
                _ready_mail_settings("09:30"),
            )

            with patch("osah.application.services.send_daily_report_if_due.send_daily_report_email") as send_mock:
                send_daily_report_if_due(context.database_path, datetime(2026, 4, 10, 9, 29))
                send_daily_report_if_due(context.database_path, datetime(2026, 4, 10, 9, 30))

            self.assertEqual(send_mock.call_count, 1)
            shut_down_logging()


# ###### ГОТОВІ ПОШТОВІ НАЛАШТУВАННЯ / READY MAIL SETTINGS ######
def _ready_mail_settings(report_time: str) -> MailSettings:
    """Повертає мінімально готові SMTP-налаштування для тестів автоотчіту.
    Returns minimally ready SMTP settings for auto-report tests.
    """

    return MailSettings(
        daily_report_enabled=True,
        smtp_host="smtp.example.com",
        smtp_port=587,
        smtp_username="user@example.com",
        smtp_password="secret",
        sender_email="sender@example.com",
        recipient_email="boss@example.com",
        use_tls=True,
        last_sent_date="",
        daily_report_time=report_time,
    )


if __name__ == "__main__":
    unittest.main()

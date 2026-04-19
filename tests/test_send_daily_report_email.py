import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from osah.application.services.initialize_application import initialize_application
from osah.application.services.load_mail_settings import load_mail_settings
from osah.application.services.save_mail_settings import save_mail_settings
from osah.application.services.send_daily_report_email import send_daily_report_email
from osah.domain.entities.mail_settings import MailSettings
from osah.infrastructure.config.application_paths import build_application_paths
from osah.infrastructure.logging.shutdown_logging import shut_down_logging


class SendDailyReportEmailTests(unittest.TestCase):
    """Тести відправки щоденного звіту поштою.
    Тесты отправки ежедневного отчёта по почте.
    """

    # ###### ПЕРЕВІРКА УСПІШНОГО НАДСИЛАННЯ ЗВІТУ / ПРОВЕРКА УСПЕШНОЙ ОТПРАВКИ ОТЧЁТА ######
    def test_send_daily_report_email_updates_last_sent_date_on_success(self) -> None:
        """Перевіряє успішну SMTP-відправку та оновлення дати останнього звіту.
        Проверяет успешную SMTP-отправку и обновление даты последнего отчёта.
        """

        with tempfile.TemporaryDirectory() as temporary_directory:
            application_paths = build_application_paths(Path(temporary_directory))
            context = initialize_application(application_paths)
            save_mail_settings(
                context.database_path,
                MailSettings(
                    daily_report_enabled=True,
                    smtp_host="smtp.example.com",
                    smtp_port=587,
                    smtp_username="user@example.com",
                    smtp_password="secret",
                    sender_email="sender@example.com",
                    recipient_email="boss@example.com",
                    use_tls=True,
                    last_sent_date="",
                ),
            )

            smtp_client = MagicMock()
            smtp_context = MagicMock()
            smtp_context.__enter__.return_value = smtp_client
            smtp_context.__exit__.return_value = None

            with patch("osah.application.services.send_daily_report_email.smtplib.SMTP", return_value=smtp_context):
                report_copy_path, failed_email_copy_path = send_daily_report_email(context.database_path)

            updated_mail_settings = load_mail_settings(context.database_path)
            self.assertTrue(report_copy_path.exists())
            self.assertIsNone(failed_email_copy_path)
            self.assertNotEqual(updated_mail_settings.last_sent_date, "")
            self.assertEqual(smtp_client.send_message.call_count, 1)
            shut_down_logging()

    # ###### ПЕРЕВІРКА FALLBACK-ПОВЕДІНКИ ПІСЛЯ НЕВДАЛИХ СПРОБ / ПРОВЕРКА FALLBACK-ПОВЕДЕНИЯ ПОСЛЕ НЕУДАЧНЫХ ПОПЫТОК ######
    def test_send_daily_report_email_saves_eml_after_failed_retries(self) -> None:
        """Перевіряє збереження fallback-листа після трьох невдалих спроб SMTP.
        Проверяет сохранение fallback-письма после трёх неудачных попыток SMTP.
        """

        with tempfile.TemporaryDirectory() as temporary_directory:
            application_paths = build_application_paths(Path(temporary_directory))
            context = initialize_application(application_paths)
            save_mail_settings(
                context.database_path,
                MailSettings(
                    daily_report_enabled=True,
                    smtp_host="smtp.example.com",
                    smtp_port=587,
                    smtp_username="user@example.com",
                    smtp_password="secret",
                    sender_email="sender@example.com",
                    recipient_email="boss@example.com",
                    use_tls=True,
                    last_sent_date="",
                ),
            )

            with patch(
                "osah.application.services.send_daily_report_email.smtplib.SMTP",
                side_effect=RuntimeError("smtp unavailable"),
            ) as smtp_mock:
                report_copy_path, failed_email_copy_path = send_daily_report_email(context.database_path)

            self.assertTrue(report_copy_path.exists())
            self.assertIsNotNone(failed_email_copy_path)
            self.assertTrue(failed_email_copy_path.exists())
            self.assertEqual(smtp_mock.call_count, 3)
            shut_down_logging()


if __name__ == "__main__":
    unittest.main()

import tempfile
import unittest
from pathlib import Path

from osah.application.services.initialize_application import initialize_application
from osah.application.services.load_audit_log_entries import load_audit_log_entries
from osah.application.services.load_mail_settings import load_mail_settings
from osah.application.services.save_mail_settings import save_mail_settings
from osah.domain.entities.mail_settings import MailSettings
from osah.infrastructure.config.application_paths import build_application_paths
from osah.infrastructure.logging.shutdown_logging import shut_down_logging


class SaveMailSettingsTests(unittest.TestCase):
    """Тести збереження та читання поштових налаштувань.
    Тесты сохранения и чтения почтовых настроек.
    """

    # ###### ПЕРЕВІРКА ROUNDTRIP ПОШТОВИХ НАЛАШТУВАНЬ / ПРОВЕРКА ROUNDTRIP ПОЧТОВЫХ НАСТРОЕК ######
    def test_save_mail_settings_persists_and_loads_values(self) -> None:
        """Перевіряє збереження та повторне читання SMTP-настроєк.
        Проверяет сохранение и повторное чтение SMTP-настроек.
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
                    last_sent_date="2026-04-10",
                ),
            )

            mail_settings = load_mail_settings(context.database_path)
            self.assertTrue(mail_settings.daily_report_enabled)
            self.assertEqual(mail_settings.smtp_host, "smtp.example.com")
            self.assertEqual(mail_settings.smtp_port, 587)
            self.assertEqual(mail_settings.recipient_email, "boss@example.com")
            self.assertEqual(mail_settings.last_sent_date, "2026-04-10")
            shut_down_logging()

    # ###### ПЕРЕВІРКА ВІДСУТНОСТІ СЕКРЕТІВ В AUDIT / ПРОВЕРКА ОТСУТСТВИЯ СЕКРЕТОВ В AUDIT ######
    def test_save_mail_settings_does_not_write_secret_values_to_audit(self) -> None:
        """Перевіряє, що секрети не потрапляють до audit-журналу.
        Проверяет, что секреты не попадают в audit-журнал.
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
                    smtp_password="super-secret-password",
                    sender_email="sender@example.com",
                    recipient_email="boss@example.com",
                    use_tls=True,
                    last_sent_date="2026-04-10",
                ),
            )

            audit_log_entries = load_audit_log_entries(context.database_path, limit=5)
            mail_audit_entry = next(
                audit_log_entry for audit_log_entry in audit_log_entries if audit_log_entry.event_type == "mail.settings_updated"
            )
            self.assertNotIn("super-secret-password", mail_audit_entry.description_text)
            self.assertNotIn("smtp_password", mail_audit_entry.description_text)
            shut_down_logging()


if __name__ == "__main__":
    unittest.main()

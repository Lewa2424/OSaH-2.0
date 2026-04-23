import logging
import os
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from osah.application.services.cancel_work_permit_record import cancel_work_permit_record
from osah.application.services.create_work_permit_record import create_work_permit_record
from osah.application.services.initialize_application import initialize_application
from osah.application.services.load_audit_log_entries import load_audit_log_entries
from osah.application.services.load_dashboard_snapshot_from_path import load_dashboard_snapshot_from_path
from osah.application.services.refresh_news_sources import refresh_news_sources
from osah.application.services.restore_backup_snapshot import restore_backup_snapshot
from osah.application.services.save_mail_settings import save_mail_settings
from osah.application.services.security.authenticate_program_access import authenticate_program_access
from osah.application.services.security.build_service_reset_request import build_service_reset_request
from osah.application.services.security.configure_program_access import configure_program_access
from osah.application.services.security.reset_program_access_with_service_code import reset_program_access_with_service_code
from osah.application.services.send_daily_report_email import send_daily_report_email
from osah.domain.entities.access_role import AccessRole
from osah.domain.entities.mail_settings import MailSettings
from osah.domain.entities.news_source_kind import NewsSourceKind
from osah.domain.entities.rss_feed_entry import RssFeedEntry
from osah.domain.services.security.build_service_reset_code import build_service_reset_code
from osah.infrastructure.config.application_paths import build_application_paths
from osah.infrastructure.database.commands.insert_audit_log import insert_audit_log
from osah.application.services.create_news_source import create_news_source
from osah.infrastructure.logging.configure_logging import configure_logging
from osah.infrastructure.logging.log_alert_event import log_alert_event
from osah.infrastructure.logging.log_system_event import log_system_event
from osah.infrastructure.logging.shutdown_logging import shut_down_logging
from osah.ui.shared.security.build_available_sections_for_role import build_available_sections_for_role


class Step10LoggingAndStabilityTests(unittest.TestCase):
    """Стабілізаційні тести логування, negative-сценаріїв і базових архітектурних обмежень.
    Stabilization tests for logging, negative scenarios, and baseline architecture constraints.
    """

    # ###### МАСКУВАННЯ AUDIT-СЕКРЕТІВ / AUDIT SECRET REDACTION ######
    def test_audit_log_redacts_sensitive_values(self) -> None:
        """Перевіряє, що audit-log не зберігає пароль, hash, salt або token у відкритому вигляді.
        Checks that audit log does not store password, hash, salt, or token in plain text.
        """

        with tempfile.TemporaryDirectory() as temporary_directory:
            context = initialize_application(build_application_paths(Path(temporary_directory)))
            connection = sqlite3.connect(context.database_path)
            connection.row_factory = sqlite3.Row
            insert_audit_log(
                connection,
                event_type="security.synthetic_sensitive_event",
                module_name="security",
                event_level="warning",
                actor_name="test",
                entity_name="test",
                result_status="success",
                description_text="password=plain-secret;hash=hash-secret;salt=salt-secret;token=token-secret",
            )
            connection.commit()
            connection.close()

            audit_text = "\n".join(entry.description_text for entry in load_audit_log_entries(context.database_path, 20))

            self.assertNotIn("plain-secret", audit_text)
            self.assertNotIn("hash-secret", audit_text)
            self.assertNotIn("salt-secret", audit_text)
            self.assertNotIn("token-secret", audit_text)
            self.assertIn("[REDACTED]", audit_text)
            shut_down_logging()

    # ###### РОТАЦІЯ ФАЙЛОВИХ ЛОГІВ / FILE LOG ROTATION ######
    def test_file_logging_rotates_and_purges_old_logs(self) -> None:
        """Перевіряє ротацію файлового логу та видалення старих log-файлів.
        Checks file log rotation and old log file purge.
        """

        with tempfile.TemporaryDirectory() as temporary_directory:
            log_directory = Path(temporary_directory) / "logs"
            log_directory.mkdir()
            old_log_file = log_directory / "old.log"
            old_log_file.write_text("old", encoding="utf-8")
            old_timestamp = 1
            os.utime(old_log_file, (old_timestamp, old_timestamp))

            log_file_path = log_directory / "osah.log"
            configure_logging(log_file_path, max_bytes=200, backup_count=2, retention_days=1)
            for index in range(60):
                logging.getLogger("rotation_test").info("line-%s password=hidden-secret", index)
            shut_down_logging()

            rotated_logs = tuple(log_directory.glob("osah.log*"))
            combined_log_text = "\n".join(path.read_text(encoding="utf-8", errors="ignore") for path in rotated_logs)

            self.assertGreaterEqual(len(rotated_logs), 2)
            self.assertFalse(old_log_file.exists())
            self.assertNotIn("hidden-secret", combined_log_text)

    # ###### СИСТЕМНЕ МАСКУВАННЯ ЛОГІВ / SYSTEM LOG REDACTION ######
    def test_system_and_alert_logs_redact_secrets(self) -> None:
        """Перевіряє, що system/alert logs маскують секрети до запису у файл.
        Checks that system and alert logs redact secrets before writing to file.
        """

        with tempfile.TemporaryDirectory() as temporary_directory:
            log_file_path = Path(temporary_directory) / "logs" / "osah.log"
            configure_logging(log_file_path)
            log_system_event("security", "password=visible-secret")
            log_alert_event("security", "service_code=service-secret")
            shut_down_logging()

            log_text = log_file_path.read_text(encoding="utf-8")
            self.assertNotIn("visible-secret", log_text)
            self.assertNotIn("service-secret", log_text)
            self.assertIn("[REDACTED]", log_text)

    # ###### СЕРВІСНИЙ КОД БЕЗ СЕКРЕТУ / SERVICE CODE WITHOUT SECRET ######
    def test_service_code_reset_is_audited_without_plain_code(self) -> None:
        """Перевіряє, що service-code flow фіксується, але код не пишеться у audit.
        Checks that service-code flow is audited without writing the code itself.
        """

        with tempfile.TemporaryDirectory() as temporary_directory:
            context = initialize_application(build_application_paths(Path(temporary_directory)))
            configure_program_access(context.database_path, "inspector-123", "manager-456")
            reset_request = build_service_reset_request(context.database_path)
            service_code = build_service_reset_code(reset_request.installation_id, reset_request.request_counter)

            reset_program_access_with_service_code(context.database_path, service_code, "inspector-789", "manager-999")

            audit_entries = load_audit_log_entries(context.database_path, 50)
            audit_text = "\n".join(entry.description_text for entry in audit_entries)
            event_types = {entry.event_type for entry in audit_entries}

            self.assertIn("security.service_code_used", event_types)
            self.assertNotIn(service_code, audit_text)
            shut_down_logging()

    # ###### ЛОГІН І НЕВДАЛИЙ ЛОГІН / LOGIN AUDIT ######
    def test_login_success_and_failure_have_required_audit_fields(self) -> None:
        """Перевіряє audit-поля для успішного та неуспішного входу.
        Checks audit fields for successful and failed login.
        """

        with tempfile.TemporaryDirectory() as temporary_directory:
            context = initialize_application(build_application_paths(Path(temporary_directory)))
            configure_program_access(context.database_path, "inspector-123", "manager-456")

            authenticate_program_access(context.database_path, AccessRole.INSPECTOR, "bad-password")
            authenticate_program_access(context.database_path, AccessRole.INSPECTOR, "inspector-123")

            audit_entries = load_audit_log_entries(context.database_path, 30)
            login_entries = [entry for entry in audit_entries if entry.event_type.startswith("security.login_")]

            self.assertTrue(any(entry.event_type == "security.login_failed" for entry in login_entries))
            self.assertTrue(any(entry.event_type == "security.login_success" for entry in login_entries))
            for entry in login_entries:
                self.assertTrue(entry.created_at_text)
                self.assertTrue(entry.actor_name)
                self.assertTrue(entry.entity_name)
                self.assertTrue(entry.result_status)
            shut_down_logging()

    # ###### ПОШТОВИЙ FAILURE ТА РУЧНИЙ РЕЖИМ / MAIL FAILURE AND MANUAL FALLBACK ######
    def test_failed_mail_delivery_writes_attempts_and_fallback_without_secret(self) -> None:
        """Перевіряє 3 SMTP-спроби, fallback-файл і відсутність SMTP-секрету в audit.
        Checks three SMTP attempts, fallback file, and absence of SMTP secret in audit.
        """

        with tempfile.TemporaryDirectory() as temporary_directory:
            context = initialize_application(build_application_paths(Path(temporary_directory)))
            save_mail_settings(
                context.database_path,
                MailSettings(
                    daily_report_enabled=True,
                    smtp_host="smtp.example.com",
                    smtp_port=587,
                    smtp_username="user@example.com",
                    smtp_password="smtp-super-secret",
                    sender_email="sender@example.com",
                    recipient_email="boss@example.com",
                    use_tls=True,
                    last_sent_date="",
                ),
            )

            with patch("osah.application.services.send_daily_report_email.smtplib.SMTP", side_effect=RuntimeError("smtp down")):
                _, fallback_email_path = send_daily_report_email(context.database_path)

            audit_entries = load_audit_log_entries(context.database_path, 80)
            attempt_entries = [entry for entry in audit_entries if entry.event_type == "report.send_attempt_failed"]
            audit_text = "\n".join(entry.description_text for entry in audit_entries)

            self.assertEqual(len(attempt_entries), 3)
            self.assertIsNotNone(fallback_email_path)
            self.assertTrue(fallback_email_path.exists())
            self.assertNotIn("smtp-super-secret", audit_text)
            shut_down_logging()

    # ###### ІЗОЛЯЦІЯ НОВИН ВІД ПОРУШЕНЬ / NEWS AND VIOLATION SEPARATION ######
    def test_news_refresh_does_not_create_control_notifications(self) -> None:
        """Перевіряє, що новини/НПА не змішуються з контрольними порушеннями ОП.
        Checks that news/NPA materials are not mixed into OT control violations.
        """

        with tempfile.TemporaryDirectory() as temporary_directory:
            context = initialize_application(build_application_paths(Path(temporary_directory)))
            before_snapshot = load_dashboard_snapshot_from_path(context.database_path)
            create_news_source(context.database_path, "Trusted NPA", "https://example.com/npa.xml", NewsSourceKind.NPA)

            refresh_news_sources(
                context.database_path,
                lambda _: (
                    RssFeedEntry(
                        title_text="Нове роз'яснення",
                        link_url="https://example.com/npa-1",
                        published_at_text="2026-04-10T10:00:00",
                    ),
                ),
            )
            after_snapshot = load_dashboard_snapshot_from_path(context.database_path)

            self.assertEqual(len(after_snapshot.active_notifications), len(before_snapshot.active_notifications))
            self.assertGreater(after_snapshot.unread_news_total, before_snapshot.unread_news_total)
            shut_down_logging()

    # ###### ПРАВА READ-ONLY РОЛІ / READ-ONLY ROLE ACCESS ######
    def test_manager_role_cannot_open_settings_section(self) -> None:
        """Перевіряє, що роль керівника не отримує доступ до налаштувань.
        Checks that manager role does not get access to settings.
        """

        from osah.domain.entities.app_section import AppSection

        manager_sections = build_available_sections_for_role(AccessRole.MANAGER)

        self.assertNotIn(AppSection.SETTINGS, manager_sections)

    # ###### НЕГАТИВНЕ ВІДНОВЛЕННЯ / NEGATIVE RESTORE ######
    def test_restore_missing_backup_fails_without_safety_copy(self) -> None:
        """Перевіряє, що відновлення з відсутнього файлу не створює фальшиву safety-копію.
        Checks that restore from a missing file fails without creating a fake safety copy.
        """

        with tempfile.TemporaryDirectory() as temporary_directory:
            context = initialize_application(build_application_paths(Path(temporary_directory)))
            missing_backup_path = Path(temporary_directory) / "missing.sqlite3"

            with self.assertRaises(ValueError):
                restore_backup_snapshot(context.database_path, missing_backup_path)

            backup_directory = context.database_path.parent / "backups"
            safety_files = tuple(backup_directory.glob("*safety*")) if backup_directory.exists() else ()
            self.assertEqual(len(safety_files), 0)
            shut_down_logging()

    # ###### НЕГАТИВНЕ СКАСУВАННЯ НД / NEGATIVE WORK PERMIT CANCEL ######
    def test_cancel_work_permit_without_reason_does_not_write_success_audit(self) -> None:
        """Перевіряє, що скасування НД без причини відхиляється до audit-success події.
        Checks that canceling a work permit without reason is rejected before a success audit event.
        """

        with tempfile.TemporaryDirectory() as temporary_directory:
            context = initialize_application(build_application_paths(Path(temporary_directory)))
            create_work_permit_record(
                context.database_path,
                "ND-NEG-1",
                "Вогневі роботи",
                "Дільниця А",
                "2099-04-10 08:00",
                "2099-04-10 12:00",
                "Майстер",
                "Інспектор",
                "0001",
                "executor",
                "",
            )
            with self.assertRaises(ValueError):
                cancel_work_permit_record(context.database_path, 1, "")

            audit_entries = load_audit_log_entries(context.database_path, 50)
            cancel_events = [entry for entry in audit_entries if entry.event_type == "work_permit.canceled"]

            self.assertEqual(len(cancel_events), 0)
            shut_down_logging()


if __name__ == "__main__":
    unittest.main()

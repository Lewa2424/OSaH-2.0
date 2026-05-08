import sqlite3
import tempfile
import unittest
from pathlib import Path

from osah.application.services.create_current_training_record import create_current_training_record
from osah.application.services.create_work_permit_record import create_work_permit_record
from osah.application.services.initialize_application import initialize_application
from osah.application.services.load_training_registry import load_training_registry
from osah.infrastructure.config.application_paths import build_application_paths
from osah.infrastructure.database.create_database_connection import create_database_connection
from osah.infrastructure.database.queries.list_training_records import list_training_records
from osah.infrastructure.logging.shutdown_logging import shut_down_logging


class CurrentTrainingRecordsTests(unittest.TestCase):
    """Тести моделі current/archive для інструктажів.
    Tests for the current/archive model for trainings.
    """

    def test_create_new_same_type_archives_old_training(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            context = initialize_application(build_application_paths(Path(temporary_directory)))
            try:
                first_record_id = create_current_training_record(
                    context.database_path,
                    "0001",
                    "repeated",
                    "10.04.2026",
                    "",
                    "Інспектор 1",
                    "Перший повторний",
                    work_risk_category="regular",
                )
                second_record_id = create_current_training_record(
                    context.database_path,
                    "0001",
                    "repeated",
                    "10.05.2026",
                    "",
                    "Інспектор 2",
                    "Другий повторний",
                    work_risk_category="regular",
                )

                connection = create_database_connection(context.database_path)
                try:
                    rows = connection.execute(
                        """
                        SELECT id, is_current, archive_reason, replaced_by_record_id
                        FROM trainings
                        WHERE employee_personnel_number = '0001' AND training_type = 'repeated'
                        ORDER BY id ASC;
                        """
                    ).fetchall()
                finally:
                    connection.close()

                self.assertEqual(len(rows), 2)
                self.assertEqual(int(rows[0]["id"]), first_record_id)
                self.assertEqual(int(rows[0]["is_current"]), 0)
                self.assertEqual(rows[0]["archive_reason"], "replaced_by_new_training")
                self.assertEqual(int(rows[0]["replaced_by_record_id"]), second_record_id)
                self.assertEqual(int(rows[1]["id"]), second_record_id)
                self.assertEqual(int(rows[1]["is_current"]), 1)
            finally:
                shut_down_logging()

    def test_list_training_records_returns_only_current_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            context = initialize_application(build_application_paths(Path(temporary_directory)))
            try:
                create_current_training_record(
                    context.database_path,
                    "0001",
                    "repeated",
                    "10.04.2026",
                    "",
                    "Інспектор 1",
                    "Перший повторний",
                    work_risk_category="regular",
                )
                create_current_training_record(
                    context.database_path,
                    "0001",
                    "repeated",
                    "10.05.2026",
                    "",
                    "Інспектор 2",
                    "Другий повторний",
                    work_risk_category="regular",
                )

                records = load_training_registry(context.database_path)
                repeated_records = [record for record in records if record.employee_personnel_number == "0001" and record.training_type.value == "repeated"]
                self.assertEqual(len(repeated_records), 1)
                self.assertEqual(repeated_records[0].note_text, "Другий повторний")
                self.assertTrue(repeated_records[0].is_current)
            finally:
                shut_down_logging()

    def test_include_archived_training_records_when_requested(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            context = initialize_application(build_application_paths(Path(temporary_directory)))
            try:
                create_current_training_record(
                    context.database_path,
                    "0001",
                    "repeated",
                    "10.04.2026",
                    "",
                    "Інспектор 1",
                    "Перший повторний",
                    work_risk_category="regular",
                )
                create_current_training_record(
                    context.database_path,
                    "0001",
                    "repeated",
                    "10.05.2026",
                    "",
                    "Інспектор 2",
                    "Другий повторний",
                    work_risk_category="regular",
                )

                connection = create_database_connection(context.database_path)
                try:
                    records = list_training_records(connection, include_archived=True)
                finally:
                    connection.close()

                repeated_records = [record for record in records if record.employee_personnel_number == "0001" and record.training_type.value == "repeated"]
                self.assertEqual(len(repeated_records), 2)
                self.assertEqual(sum(1 for record in repeated_records if record.is_current), 1)
            finally:
                shut_down_logging()

    def test_notification_ignores_archived_training(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            context = initialize_application(build_application_paths(Path(temporary_directory)))
            try:
                create_current_training_record(
                    context.database_path,
                    "0001",
                    "repeated",
                    "10.01.2026",
                    "",
                    "Інспектор 1",
                    "Старий повторний",
                    work_risk_category="regular",
                )
                create_current_training_record(
                    context.database_path,
                    "0001",
                    "repeated",
                    "10.05.2099",
                    "",
                    "Інспектор 2",
                    "Новий повторний",
                    work_risk_category="regular",
                )

                connection = sqlite3.connect(context.database_path)
                try:
                    rows = connection.execute(
                        """
                        SELECT COUNT(*)
                        FROM notifications
                        WHERE source_module = 'trainings.registry'
                          AND employee_personnel_number = '0001'
                          AND notification_level = 'critical'
                          AND title_text = 'Прострочено повторний інструктаж'
                        """
                    ).fetchone()
                finally:
                    connection.close()

                self.assertEqual(rows[0], 0)
            finally:
                shut_down_logging()

    def test_work_permit_target_training_keeps_separate_current_records_by_source_key(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            context = initialize_application(build_application_paths(Path(temporary_directory)))
            try:
                create_work_permit_record(
                    context.database_path,
                    "AUTO-WP-CARD-001",
                    "Висотні роботи",
                    "Дільниця К",
                    "10.05.2026 08:00",
                    "10.05.2026 12:00",
                    "Майстер",
                    "Інженер з ОП",
                    "0001",
                    "executor",
                    "Перший НД",
                    target_training_status="done_passed",
                    target_training_date_text="09.05.2026",
                    target_training_conducted_by="Коваль О.В.",
                )
                create_work_permit_record(
                    context.database_path,
                    "AUTO-WP-CARD-002",
                    "Вогневі роботи",
                    "Дільниця Л",
                    "11.05.2026 08:00",
                    "11.05.2026 12:00",
                    "Майстер",
                    "Інженер з ОП",
                    "0001",
                    "executor",
                    "Другий НД",
                    target_training_status="done_passed",
                    target_training_date_text="10.05.2026",
                    target_training_conducted_by="Коваль О.В.",
                )

                records = load_training_registry(context.database_path)
                targeted_records = [
                    record
                    for record in records
                    if record.employee_personnel_number == "0001"
                    and record.training_type.value == "targeted"
                    and record.source_module == "work_permits"
                ]
                self.assertEqual(len(targeted_records), 2)
                self.assertTrue(all(record.is_current for record in targeted_records))
            finally:
                shut_down_logging()


if __name__ == "__main__":
    unittest.main()

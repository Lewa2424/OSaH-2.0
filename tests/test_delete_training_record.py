import sqlite3
import tempfile
import unittest
from pathlib import Path

from osah.application.services.create_training_record import create_training_record
from osah.application.services.delete_training_record import delete_training_record
from osah.application.services.initialize_application import initialize_application
from osah.application.services.load_training_registry import load_training_registry
from osah.infrastructure.config.application_paths import build_application_paths
from osah.infrastructure.logging.shutdown_logging import shut_down_logging


class DeleteTrainingRecordTests(unittest.TestCase):
    """Тести видалення запису інструктажу.
    Тесты удаления записи инструктажа.
    """

    # ###### ПЕРЕВІРКА ВИДАЛЕННЯ ТА AUDIT ІНСТРУКТАЖУ / ПРОВЕРКА УДАЛЕНИЯ И AUDIT ИНСТРУКТАЖА ######
    def test_delete_training_record_removes_record_and_writes_audit_log(self) -> None:
        """Перевіряє видалення запису інструктажу та появу audit-події.
        Проверяет удаление записи инструктажа и появление audit-события.
        """

        with tempfile.TemporaryDirectory() as temporary_directory:
            application_paths = build_application_paths(Path(temporary_directory))
            context = initialize_application(application_paths)
            create_training_record(
                database_path=context.database_path,
                employee_personnel_number="0001",
                training_type="introductory",
                event_date_text="2026-04-10",
                next_control_date_text="2026-06-10",
                conducted_by="Інспектор з ОП",
                note_text="Початковий запис",
            )

            created_record = next(
                training_record
                for training_record in load_training_registry(context.database_path)
                if training_record.employee_personnel_number == "0001" and training_record.note_text == "Початковий запис"
            )
            training_total_before_delete = len(load_training_registry(context.database_path))
            delete_training_record(
                database_path=context.database_path,
                record_id=int(created_record.record_id),
            )

            remaining_records = load_training_registry(context.database_path)
            connection = sqlite3.connect(context.database_path)
            audit_events = connection.execute(
                "SELECT event_type FROM audit_log WHERE event_type = 'training.deleted';"
            ).fetchall()
            connection.close()

            self.assertEqual(len(remaining_records), training_total_before_delete - 1)
            self.assertFalse(any(int(training_record.record_id) == int(created_record.record_id) for training_record in remaining_records))
            self.assertEqual(len(audit_events), 1)
            shut_down_logging()


if __name__ == "__main__":
    unittest.main()

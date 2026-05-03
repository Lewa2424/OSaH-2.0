import sqlite3
import tempfile
import unittest
from pathlib import Path

from osah.application.services.create_training_record import create_training_record
from osah.application.services.initialize_application import initialize_application
from osah.application.services.load_training_registry import load_training_registry
from osah.application.services.update_training_record import update_training_record
from osah.infrastructure.config.application_paths import build_application_paths
from osah.infrastructure.logging.shutdown_logging import shut_down_logging


class UpdateTrainingRecordTests(unittest.TestCase):
    """Тести оновлення запису інструктажу.
    Тесты обновления записи инструктажа.
    """

    # ###### ПЕРЕВІРКА ОНОВЛЕННЯ ТА AUDIT ІНСТРУКТАЖУ / ПРОВЕРКА ОБНОВЛЕНИЯ И AUDIT ИНСТРУКТАЖА ######
    def test_update_training_record_updates_record_and_writes_audit_log(self) -> None:
        """Перевіряє оновлення запису інструктажу та появу audit-події.
        Проверяет обновление записи инструктажа и появление audit-события.
        """

        with tempfile.TemporaryDirectory() as temporary_directory:
            application_paths = build_application_paths(Path(temporary_directory))
            context = initialize_application(application_paths)
            create_training_record(
                database_path=context.database_path,
                employee_personnel_number="0001",
                training_type="primary",
                event_date_text="2026-04-10",
                next_control_date_text="",
                work_risk_category="regular",
                conducted_by="Інспектор з ОП",
                note_text="Початковий запис",
            )

            created_record = next(
                training_record
                for training_record in load_training_registry(context.database_path)
                if training_record.employee_personnel_number == "0001" and training_record.note_text == "Початковий запис"
            )
            update_training_record(
                database_path=context.database_path,
                record_id=int(created_record.record_id),
                employee_personnel_number="0001",
                training_type="repeated",
                event_date_text="2026-04-12",
                next_control_date_text="",
                work_risk_category="high_risk",
                conducted_by="Головний інспектор",
                note_text="Оновлений запис",
            )

            updated_record = next(
                training_record
                for training_record in load_training_registry(context.database_path)
                if int(training_record.record_id) == int(created_record.record_id)
            )
            connection = sqlite3.connect(context.database_path)
            audit_events = connection.execute(
                "SELECT event_type FROM audit_log WHERE event_type = 'training.updated';"
            ).fetchall()
            connection.close()

            self.assertEqual(updated_record.conducted_by, "Головний інспектор")
            self.assertEqual(updated_record.note_text, "Оновлений запис")
            self.assertEqual(updated_record.next_control_date, "2026-07-12")
            self.assertEqual(len(audit_events), 1)
            shut_down_logging()


if __name__ == "__main__":
    unittest.main()

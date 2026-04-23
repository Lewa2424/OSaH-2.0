import sqlite3
import tempfile
import unittest
from pathlib import Path

from osah.application.services.create_medical_record import create_medical_record
from osah.application.services.initialize_application import initialize_application
from osah.application.services.load_medical_registry import load_medical_registry
from osah.application.services.update_medical_record import update_medical_record
from osah.domain.entities.medical_decision import MedicalDecision
from osah.infrastructure.config.application_paths import build_application_paths
from osah.infrastructure.logging.shutdown_logging import shut_down_logging


class UpdateMedicalRecordTests(unittest.TestCase):
    """Тести оновлення запису меддопуску.
    Tests for updating a medical admission record.
    """

    # ###### ПЕРЕВІРКА ОНОВЛЕННЯ ТА AUDIT МЕДИЦИНИ / UPDATE AND AUDIT CHECK ######
    def test_update_medical_record_updates_record_and_writes_audit_log(self) -> None:
        """Перевіряє оновлення медичного запису та появу audit-події.
        Checks that a medical record is updated and an audit event is written.
        """

        with tempfile.TemporaryDirectory() as temporary_directory:
            application_paths = build_application_paths(Path(temporary_directory))
            context = initialize_application(application_paths)
            create_medical_record(
                database_path=context.database_path,
                employee_personnel_number="0001",
                valid_from_text="2026-04-10",
                valid_until_text="2026-06-10",
                medical_decision=MedicalDecision.FIT.value,
                restriction_note="",
            )

            created_record = next(
                record
                for record in load_medical_registry(context.database_path)
                if record.employee_personnel_number == "0001" and record.valid_from == "2026-04-10"
            )
            update_medical_record(
                database_path=context.database_path,
                record_id=int(created_record.record_id),
                employee_personnel_number="0001",
                valid_from_text="2026-04-12",
                valid_until_text="2026-07-12",
                medical_decision=MedicalDecision.RESTRICTED.value,
                restriction_note="Не виконувати висотні роботи",
            )

            updated_record = next(
                record
                for record in load_medical_registry(context.database_path)
                if int(record.record_id) == int(created_record.record_id)
            )
            connection = sqlite3.connect(context.database_path)
            audit_events = connection.execute(
                "SELECT event_type FROM audit_log WHERE event_type = 'medical.updated';"
            ).fetchall()
            connection.close()

            self.assertEqual(updated_record.valid_until, "2026-07-12")
            self.assertEqual(updated_record.medical_decision, MedicalDecision.RESTRICTED)
            self.assertEqual(updated_record.restriction_note, "Не виконувати висотні роботи")
            self.assertEqual(len(audit_events), 1)
            shut_down_logging()


if __name__ == "__main__":
    unittest.main()

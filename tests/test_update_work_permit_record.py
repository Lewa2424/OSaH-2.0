import sqlite3
import tempfile
import unittest
from pathlib import Path

from osah.application.services.create_work_permit_record import create_work_permit_record
from osah.application.services.initialize_application import initialize_application
from osah.application.services.load_work_permit_registry import load_work_permit_registry
from osah.application.services.update_work_permit_record import update_work_permit_record
from osah.infrastructure.config.application_paths import build_application_paths
from osah.infrastructure.logging.shutdown_logging import shut_down_logging


class UpdateWorkPermitRecordTests(unittest.TestCase):
    """Тести оновлення наряду-допуску.
    Tests for updating a work permit.
    """

    # ###### ПЕРЕВІРКА ОНОВЛЕННЯ ТА AUDIT / UPDATE AND AUDIT CHECK ######
    def test_update_work_permit_record_updates_record_participant_and_audit_log(self) -> None:
        """Перевіряє оновлення наряду, учасника та появу audit-події.
        Checks work permit update, participant update and audit event.
        """

        with tempfile.TemporaryDirectory() as temporary_directory:
            application_paths = build_application_paths(Path(temporary_directory))
            context = initialize_application(application_paths)
            create_work_permit_record(
                context.database_path,
                "ND-UT-201",
                "Висотні роботи",
                "Дільниця А",
                "2099-04-10 08:00",
                "2099-04-10 12:00",
                "Майстер",
                "Інспектор",
                "0001",
                "executor",
                "Початковий наряд",
            )
            created_record = next(record for record in load_work_permit_registry(context.database_path) if record.permit_number == "ND-UT-201")

            update_work_permit_record(
                context.database_path,
                int(created_record.record_id),
                "ND-UT-201A",
                "Газонебезпечні роботи",
                "Дільниця Б",
                "2099-04-11 08:00",
                "2099-04-11 12:00",
                "Старший майстер",
                "Інженер з ОП",
                "0002",
                "team_member",
                "Оновлений наряд",
            )

            updated_record = next(record for record in load_work_permit_registry(context.database_path) if int(record.record_id) == int(created_record.record_id))
            connection = sqlite3.connect(context.database_path)
            audit_events = connection.execute("SELECT event_type FROM audit_log WHERE event_type = 'work_permit.updated';").fetchall()
            connection.close()

            self.assertEqual(updated_record.permit_number, "ND-UT-201A")
            self.assertEqual(updated_record.work_kind, "Газонебезпечні роботи")
            self.assertEqual(updated_record.participants[0].employee_personnel_number, "0002")
            self.assertEqual(len(audit_events), 1)
            shut_down_logging()


if __name__ == "__main__":
    unittest.main()

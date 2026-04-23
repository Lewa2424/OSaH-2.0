import sqlite3
import tempfile
import unittest
from pathlib import Path

from osah.application.services.cancel_work_permit_record import cancel_work_permit_record
from osah.application.services.create_work_permit_record import create_work_permit_record
from osah.application.services.initialize_application import initialize_application
from osah.application.services.load_work_permit_registry import load_work_permit_registry
from osah.domain.entities.work_permit_status import WorkPermitStatus
from osah.infrastructure.config.application_paths import build_application_paths
from osah.infrastructure.logging.shutdown_logging import shut_down_logging


class CancelWorkPermitRecordTests(unittest.TestCase):
    """Тести скасування наряду-допуску.
    Tests for canceling a work permit.
    """

    # ###### ПЕРЕВІРКА СКАСУВАННЯ ТА AUDIT / CANCEL AND AUDIT CHECK ######
    def test_cancel_work_permit_record_marks_record_and_writes_audit_log(self) -> None:
        """Перевіряє скасування наряду з причиною та audit-подією.
        Checks canceling a work permit with a reason and audit event.
        """

        with tempfile.TemporaryDirectory() as temporary_directory:
            application_paths = build_application_paths(Path(temporary_directory))
            context = initialize_application(application_paths)
            create_work_permit_record(
                context.database_path,
                "ND-UT-301",
                "Вогневі роботи",
                "Дільниця В",
                "2099-04-10 08:00",
                "2099-04-10 12:00",
                "Майстер",
                "Інспектор",
                "0001",
                "executor",
                "Потребує скасування",
            )
            created_record = next(record for record in load_work_permit_registry(context.database_path) if record.permit_number == "ND-UT-301")

            cancel_work_permit_record(context.database_path, int(created_record.record_id), "Роботи перенесено")

            canceled_record = next(record for record in load_work_permit_registry(context.database_path) if int(record.record_id) == int(created_record.record_id))
            connection = sqlite3.connect(context.database_path)
            audit_events = connection.execute("SELECT event_type FROM audit_log WHERE event_type = 'work_permit.canceled';").fetchall()
            connection.close()

            self.assertEqual(canceled_record.status, WorkPermitStatus.CANCELED)
            self.assertEqual(canceled_record.cancel_reason_text, "Роботи перенесено")
            self.assertEqual(len(audit_events), 1)
            shut_down_logging()


if __name__ == "__main__":
    unittest.main()

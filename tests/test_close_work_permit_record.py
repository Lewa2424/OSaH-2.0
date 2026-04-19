import sqlite3
import tempfile
import unittest
from pathlib import Path

from osah.application.services.close_work_permit_record import close_work_permit_record
from osah.application.services.create_work_permit_record import create_work_permit_record
from osah.application.services.initialize_application import initialize_application
from osah.application.services.load_work_permit_registry import load_work_permit_registry
from osah.infrastructure.config.application_paths import build_application_paths
from osah.infrastructure.logging.shutdown_logging import shut_down_logging


class CloseWorkPermitRecordTests(unittest.TestCase):
    """Тести ручного закриття наряду-допуску.
    Тесты ручного закрытия наряда-допуска.
    """

    # ###### ПЕРЕВІРКА РУЧНОГО ЗАКРИТТЯ НАРЯДУ / ПРОВЕРКА РУЧНОГО ЗАКРЫТИЯ НАРЯДА ######
    def test_close_work_permit_record_marks_record_as_closed_and_writes_audit_log(self) -> None:
        """Перевіряє ручне закриття наряду-допуску та появу audit-події.
        Проверяет ручное закрытие наряда-допуска и появление audit-события.
        """

        with tempfile.TemporaryDirectory() as temporary_directory:
            application_paths = build_application_paths(Path(temporary_directory))
            context = initialize_application(application_paths)
            create_work_permit_record(
                database_path=context.database_path,
                permit_number="НД-101",
                work_kind="Висотні роботи",
                work_location="Дільниця Б",
                starts_at_text="2099-04-10 08:00",
                ends_at_text="2099-04-10 10:00",
                responsible_person="Майстер зміни",
                issuer_person="Інспектор з ОП",
                employee_personnel_number="0001",
                participant_role="executor",
                note_text="Потрібне ручне закриття",
            )

            created_record = next(
                work_permit_record
                for work_permit_record in load_work_permit_registry(context.database_path)
                if work_permit_record.permit_number == "НД-101"
            )
            close_work_permit_record(context.database_path, int(created_record.record_id))

            updated_record = next(
                work_permit_record
                for work_permit_record in load_work_permit_registry(context.database_path)
                if int(work_permit_record.record_id) == int(created_record.record_id)
            )
            connection = sqlite3.connect(context.database_path)
            audit_events = connection.execute(
                "SELECT event_type FROM audit_log WHERE event_type = 'work_permit.closed';"
            ).fetchall()
            connection.close()

            self.assertIsNotNone(updated_record.closed_at)
            self.assertEqual(updated_record.status.value, "closed")
            self.assertEqual(len(audit_events), 1)
            shut_down_logging()


if __name__ == "__main__":
    unittest.main()

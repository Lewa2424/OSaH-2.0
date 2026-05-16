import tempfile
import unittest
from pathlib import Path

from osah.application.services.create_work_permit_record import create_work_permit_record
from osah.application.services.initialize_application import initialize_application
from osah.application.services.load_dashboard_snapshot_from_path import load_dashboard_snapshot_from_path
from osah.application.services.load_work_permit_registry import load_work_permit_registry
from osah.infrastructure.config.application_paths import build_application_paths
from osah.infrastructure.logging.shutdown_logging import shut_down_logging


class CreateWorkPermitRecordTests(unittest.TestCase):
    """Тести створення наряду-допуску.
    Tests for work permit creation.
    """

    def test_create_work_permit_record_persists_record_and_participant(self) -> None:
        """Зберігає наряд з учасником.
        Persists a permit with a participant.
        """

        with tempfile.TemporaryDirectory() as temporary_directory:
            application_paths = build_application_paths(Path(temporary_directory))
            context = initialize_application(application_paths)
            permit_total_before = len(load_work_permit_registry(context.database_path))

            create_work_permit_record(
                database_path=context.database_path,
                permit_number="НД-100",
                work_kind="Вогневі роботи",
                work_location="Дільниця А",
                starts_at_text="2099-04-10 08:00",
                ends_at_text="2099-04-10 10:00",
                responsible_person="Майстер зміни",
                issuer_person="Інспектор з ОП",
                employee_personnel_number="0001",
                participant_role="executor",
                note_text="Початковий наряд",
            )

            work_permit_records = load_work_permit_registry(context.database_path)
            snapshot = load_dashboard_snapshot_from_path(context.database_path)
            target_records = [record for record in work_permit_records if record.permit_number == "НД-100"]

            self.assertEqual(len(work_permit_records), permit_total_before + 1)
            self.assertEqual(len(target_records), 1)
            self.assertEqual(len(target_records[0].participants), 1)
            self.assertGreater(len(snapshot.active_notifications), 0)
            shut_down_logging()

    def test_create_work_permit_record_allows_lightweight_registry_entry(self) -> None:
        """Дозволяє легкий запис без допускаючого та складу бригади.
        Allows a lightweight registry entry without issuer and brigade.
        """

        with tempfile.TemporaryDirectory() as temporary_directory:
            application_paths = build_application_paths(Path(temporary_directory))
            context = initialize_application(application_paths)

            create_work_permit_record(
                database_path=context.database_path,
                permit_number="НД-101",
                work_kind="Ремонтні роботи",
                work_location="Цех 4",
                starts_at_text="2099-04-10 08:00",
                ends_at_text="2099-04-10 12:00",
                responsible_person="Старший майстер",
                issuer_person="",
                employee_personnel_number="",
                participant_role="",
                note_text="Лише контрольний запис",
            )

            created_record = next(
                record for record in load_work_permit_registry(context.database_path) if record.permit_number == "НД-101"
            )

            self.assertEqual(created_record.issuer_person, "")
            self.assertEqual(created_record.participants, ())
            shut_down_logging()

    def test_create_work_permit_record_rejects_term_longer_than_fifteen_days(self) -> None:
        """Забороняє первинний строк понад 15 днів.
        Rejects an initial term longer than 15 days.
        """

        with tempfile.TemporaryDirectory() as temporary_directory:
            application_paths = build_application_paths(Path(temporary_directory))
            context = initialize_application(application_paths)

            with self.assertRaisesRegex(ValueError, "15"):
                create_work_permit_record(
                    database_path=context.database_path,
                    permit_number="НД-102",
                    work_kind="Вогневі роботи",
                    work_location="Дільниця А",
                    starts_at_text="2099-04-10 08:00",
                    ends_at_text="2099-04-26 10:00",
                    responsible_person="Майстер зміни",
                    issuer_person="Інспектор з ОП",
                    employee_personnel_number="0001",
                    participant_role="executor",
                    note_text="Надто довгий наряд",
                )
            shut_down_logging()


if __name__ == "__main__":
    unittest.main()

import sqlite3
import tempfile
import unittest
from pathlib import Path

from osah.application.services.create_work_permit_record import create_work_permit_record
from osah.application.services.initialize_application import initialize_application
from osah.application.services.load_work_permit_registry import load_work_permit_registry
from osah.application.services.record_work_permit_daily_check import record_work_permit_daily_check
from osah.infrastructure.config.application_paths import build_application_paths
from osah.infrastructure.logging.shutdown_logging import shut_down_logging


class RecordWorkPermitDailyCheckTests(unittest.TestCase):
    """Тести фіксації щоденних перевірок для наряду-допуску.
    Tests for recording daily checks on work permits.
    """

    def test_record_work_permit_daily_check_adds_check_and_writes_audit_log(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            application_paths = build_application_paths(Path(temporary_directory))
            context = initialize_application(application_paths)
            create_work_permit_record(
                context.database_path,
                "ND-CHK-001",
                "Вогневі роботи",
                "Дільниця А",
                "2099-04-10 08:00",
                "2099-04-12 18:00",
                "Майстер",
                "Інспектор",
                "0001",
                "executor",
                "Багатоденний наряд",
            )
            created_record = next(record for record in load_work_permit_registry(context.database_path) if record.permit_number == "ND-CHK-001")

            record_work_permit_daily_check(
                context.database_path,
                int(created_record.record_id),
                "11.04.2099 09:30",
                "Старший майстер",
                "Місце робіт перевірено",
            )

            updated_record = next(
                record for record in load_work_permit_registry(context.database_path) if int(record.record_id) == int(created_record.record_id)
            )
            connection = sqlite3.connect(context.database_path)
            audit_events = connection.execute(
                "SELECT event_type FROM audit_log WHERE event_type = 'work_permit.daily_check_recorded';"
            ).fetchall()
            connection.close()

            self.assertEqual(len(updated_record.daily_checks), 1)
            self.assertEqual(updated_record.daily_checks[0].checked_by, "Старший майстер")
            self.assertEqual(len(audit_events), 1)
            shut_down_logging()

    def test_record_work_permit_daily_check_rejects_second_check_for_same_day(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            application_paths = build_application_paths(Path(temporary_directory))
            context = initialize_application(application_paths)
            create_work_permit_record(
                context.database_path,
                "ND-CHK-002",
                "Вогневі роботи",
                "Дільниця Б",
                "2099-04-10 08:00",
                "2099-04-12 18:00",
                "Майстер",
                "Інспектор",
                "0001",
                "executor",
                "Багатоденний наряд",
            )
            created_record = next(record for record in load_work_permit_registry(context.database_path) if record.permit_number == "ND-CHK-002")

            record_work_permit_daily_check(
                context.database_path,
                int(created_record.record_id),
                "2099-04-11 09:00",
                "Старший майстер",
            )

            with self.assertRaisesRegex(ValueError, "вже зафіксовано"):
                record_work_permit_daily_check(
                    context.database_path,
                    int(created_record.record_id),
                    "2099-04-11 15:00",
                    "Старший майстер",
                )
            shut_down_logging()

import sqlite3
import tempfile
import unittest
from pathlib import Path

from osah.application.services.create_work_permit_record import create_work_permit_record
from osah.application.services.initialize_application import initialize_application
from osah.application.services.load_work_permit_registry import load_work_permit_registry
from osah.infrastructure.config.application_paths import build_application_paths
from osah.infrastructure.logging.shutdown_logging import shut_down_logging


class WorkPermitTargetTrainingTests(unittest.TestCase):
    """Тести цільового інструктажу в нарядах-допусках.
    Tests for targeted training fields in work permits.
    """

    def test_future_active_permit_without_target_training_is_warning(self) -> None:
        """Дає warning до початку робіт, якщо інструктаж ще не проведено.
        Raises warning before work starts when targeted training is not done.
        """

        with tempfile.TemporaryDirectory() as temporary_directory:
            context = initialize_application(build_application_paths(Path(temporary_directory)))

            create_work_permit_record(
                context.database_path,
                "ND-WARN-1",
                "Висотні роботи",
                "Дільниця А",
                "2099-05-10 08:00",
                "2099-05-10 12:00",
                "Майстер",
                "Інженер з ОП",
                "0001",
                "executor",
                "Майбутній наряд",
                target_training_status="required_not_done",
                target_training_date_text="2099-05-09",
                target_training_conducted_by="Інструктор",
                target_training_note="Ще не завершено",
                basis_text="Наказ на роботи",
                basis_note="Очікує інструктаж",
            )

            connection = sqlite3.connect(context.database_path)
            row = connection.execute(
                """
                SELECT notification_level
                FROM notifications
                WHERE source_module = 'work_permits.registry' AND message_text LIKE '%ND-WARN-1%'
                ORDER BY id DESC
                LIMIT 1
                """
            ).fetchone()
            connection.close()

            self.assertIsNotNone(row)
            self.assertEqual(row[0], "warning")
            created_record = next(record for record in load_work_permit_registry(context.database_path) if record.permit_number == "ND-WARN-1")
            self.assertEqual(created_record.target_training_status.value, "required_not_done")
            self.assertEqual(created_record.target_training_date, "2099-05-09")
            self.assertEqual(created_record.target_training_conducted_by, "Інструктор")
            self.assertEqual(created_record.target_training_note, "Ще не завершено")
            self.assertEqual(created_record.basis_text, "Наказ на роботи")
            self.assertEqual(created_record.basis_note, "Очікує інструктаж")
            shut_down_logging()

    def test_started_active_permit_without_target_training_is_critical(self) -> None:
        """Дає critical після початку робіт, якщо цільовий інструктаж не відмічений.
        Raises critical after work starts when targeted training is missing.
        """

        with tempfile.TemporaryDirectory() as temporary_directory:
            context = initialize_application(build_application_paths(Path(temporary_directory)))

            create_work_permit_record(
                context.database_path,
                "ND-CRIT-1",
                "Газонебезпечні роботи",
                "Дільниця Б",
                "2000-05-10 08:00",
                "2099-05-10 12:00",
                "Майстер",
                "Інженер з ОП",
                "0001",
                "executor",
                "Початі роботи",
                target_training_status="required_not_done",
            )

            connection = sqlite3.connect(context.database_path)
            row = connection.execute(
                """
                SELECT notification_level
                FROM notifications
                WHERE source_module = 'work_permits.registry' AND message_text LIKE '%ND-CRIT-1%'
                ORDER BY id DESC
                LIMIT 1
                """
            ).fetchone()
            connection.close()

            self.assertIsNotNone(row)
            self.assertEqual(row[0], "critical")
            shut_down_logging()

    def test_done_target_training_does_not_create_training_warning(self) -> None:
        """Не створює попередження по цільовому інструктажу, якщо він проведений.
        Does not create targeted-training warning when it is completed.
        """

        with tempfile.TemporaryDirectory() as temporary_directory:
            context = initialize_application(build_application_paths(Path(temporary_directory)))

            create_work_permit_record(
                context.database_path,
                "ND-DONE-1",
                "Електророботи",
                "Дільниця В",
                "2099-05-10 08:00",
                "2099-05-10 12:00",
                "Майстер",
                "Інженер з ОП",
                "0001",
                "executor",
                "Інструктаж проведено",
                target_training_status="done",
            )

            connection = sqlite3.connect(context.database_path)
            rows = connection.execute(
                """
                SELECT COUNT(*)
                FROM notifications
                WHERE source_module = 'work_permits.registry'
                  AND title_text LIKE '%Не зафіксовано цільовий інструктаж%'
                  AND message_text LIKE '%ND-DONE-1%'
                """
            ).fetchone()
            connection.close()

            self.assertEqual(rows[0], 0)
            shut_down_logging()


if __name__ == "__main__":
    unittest.main()

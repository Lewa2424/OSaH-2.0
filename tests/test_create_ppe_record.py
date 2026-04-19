import tempfile
import unittest
from pathlib import Path

from osah.application.services.create_ppe_record import create_ppe_record
from osah.application.services.initialize_application import initialize_application
from osah.application.services.load_dashboard_snapshot_from_path import load_dashboard_snapshot_from_path
from osah.application.services.load_ppe_registry import load_ppe_registry
from osah.infrastructure.config.application_paths import build_application_paths
from osah.infrastructure.logging.shutdown_logging import shut_down_logging


class CreatePpeRecordTests(unittest.TestCase):
    """Тести створення запису ЗІЗ.
    Тесты создания записи СИЗ.
    """

    # ###### ПЕРЕВІРКА СТВОРЕННЯ ЗАПИСУ ЗІЗ / ПРОВЕРКА СОЗДАНИЯ ЗАПИСИ СИЗ ######
    def test_create_ppe_record_persists_record_and_updates_notifications(self) -> None:
        """Перевіряє збереження запису ЗІЗ та оновлення сигналів контролю.
        Проверяет сохранение записи СИЗ и обновление сигналов контроля.
        """

        with tempfile.TemporaryDirectory() as temporary_directory:
            application_paths = build_application_paths(Path(temporary_directory))
            context = initialize_application(application_paths)
            ppe_total_before = len(load_ppe_registry(context.database_path))

            create_ppe_record(
                database_path=context.database_path,
                employee_personnel_number="0001",
                ppe_name="Каска",
                is_required=True,
                is_issued=True,
                issue_date_text="2026-04-10",
                replacement_date_text="2026-05-10",
                quantity_text="1",
                note_text="Початкова видача",
            )

            ppe_records = load_ppe_registry(context.database_path)
            snapshot = load_dashboard_snapshot_from_path(context.database_path)

            self.assertEqual(len(ppe_records), ppe_total_before + 1)
            self.assertTrue(any(ppe_record.employee_personnel_number == "0001" and ppe_record.ppe_name == "Каска" for ppe_record in ppe_records))
            self.assertGreater(len(snapshot.active_notifications), 0)
            shut_down_logging()


if __name__ == "__main__":
    unittest.main()

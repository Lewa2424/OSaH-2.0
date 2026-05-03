import tempfile
import unittest
from pathlib import Path

from osah.application.services.create_training_record import create_training_record
from osah.application.services.initialize_application import initialize_application
from osah.application.services.load_dashboard_snapshot_from_path import load_dashboard_snapshot_from_path
from osah.application.services.load_training_registry import load_training_registry
from osah.infrastructure.config.application_paths import build_application_paths
from osah.infrastructure.logging.shutdown_logging import shut_down_logging


class CreateTrainingRecordTests(unittest.TestCase):
    """Тести створення запису інструктажу.
    Тесты создания записи инструктажа.
    """

    # ###### ПЕРЕВІРКА СТВОРЕННЯ ІНСТРУКТАЖУ / ПРОВЕРКА СОЗДАНИЯ ИНСТРУКТАЖА ######
    def test_create_training_record_persists_record_and_updates_dashboard(self) -> None:
        """Перевіряє збереження запису інструктажу та оновлення головного екрана.
        Проверяет сохранение записи инструктажа и обновление главного экрана.
        """

        with tempfile.TemporaryDirectory() as temporary_directory:
            application_paths = build_application_paths(Path(temporary_directory))
            context = initialize_application(application_paths)

            snapshot_before = load_dashboard_snapshot_from_path(context.database_path)
            training_total_before = len(load_training_registry(context.database_path))

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

            training_records = load_training_registry(context.database_path)
            snapshot_after = load_dashboard_snapshot_from_path(context.database_path)

            self.assertEqual(len(training_records), training_total_before + 1)
            self.assertTrue(
                any(
                    training_record.employee_personnel_number == "0001"
                    and training_record.next_control_date == "2026-10-10"
                    and training_record.note_text == "Початковий запис"
                    for training_record in training_records
                )
            )
            self.assertLess(snapshot_after.critical_items, snapshot_before.critical_items)
            shut_down_logging()


if __name__ == "__main__":
    unittest.main()

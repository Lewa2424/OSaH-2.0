import tempfile
import unittest
from pathlib import Path

from osah.application.services.create_training_records_batch import create_training_records_batch
from osah.application.services.initialize_application import initialize_application
from osah.application.services.load_training_registry import load_training_registry
from osah.infrastructure.config.application_paths import build_application_paths
from osah.infrastructure.logging.shutdown_logging import shut_down_logging


class CreateTrainingRecordsBatchTests(unittest.TestCase):
    """Тести масового створення записів інструктажів.
    Тесты массового создания записей инструктажей.
    """

    # ###### ПЕРЕВІРКА МАСОВОГО СТВОРЕННЯ ІНСТРУКТАЖІВ / ПРОВЕРКА МАССОВОГО СОЗДАНИЯ ИНСТРУКТАЖЕЙ ######
    def test_create_training_records_batch_creates_records_for_each_employee(self) -> None:
        """Перевіряє створення записів інструктажів для кількох працівників.
        Проверяет создание записей инструктажей для нескольких сотрудников.
        """

        with tempfile.TemporaryDirectory() as temporary_directory:
            application_paths = build_application_paths(Path(temporary_directory))
            context = initialize_application(application_paths)
            training_total_before = len(load_training_registry(context.database_path))

            create_training_records_batch(
                database_path=context.database_path,
                employee_personnel_numbers=("0001", "0002"),
                training_type="repeated",
                event_date_text="2026-04-10",
                next_control_date_text="",
                work_risk_category="high_risk",
                conducted_by="Інспектор з ОП",
                note_text="Масовий запис",
            )

            training_records = load_training_registry(context.database_path)

            self.assertEqual(len(training_records), training_total_before + 2)
            self.assertTrue(
                {"0001", "0002"}.issubset(
                    {
                        training_record.employee_personnel_number
                        for training_record in training_records
                        if training_record.note_text == "Масовий запис"
                    }
                )
            )
            shut_down_logging()


if __name__ == "__main__":
    unittest.main()

import tempfile
import unittest
from pathlib import Path

from osah.application.services.create_medical_record import create_medical_record
from osah.application.services.initialize_application import initialize_application
from osah.application.services.load_medical_registry import load_medical_registry
from osah.infrastructure.config.application_paths import build_application_paths
from osah.infrastructure.logging.shutdown_logging import shut_down_logging


class CreateMedicalRecordTests(unittest.TestCase):
    """Тести створення медичного запису.
    Тесты создания медицинской записи.
    """

    # ###### ПЕРЕВІРКА СТВОРЕННЯ МЕДИЧНОГО ЗАПИСУ / ПРОВЕРКА СОЗДАНИЯ МЕДИЦИНСКОЙ ЗАПИСИ ######
    def test_create_medical_record_persists_record_with_computed_status(self) -> None:
        """Перевіряє збереження медичного запису та обчислення його статусу.
        Проверяет сохранение медицинской записи и вычисление её статуса.
        """

        with tempfile.TemporaryDirectory() as temporary_directory:
            application_paths = build_application_paths(Path(temporary_directory))
            context = initialize_application(application_paths)
            medical_total_before = len(load_medical_registry(context.database_path))

            create_medical_record(
                database_path=context.database_path,
                employee_personnel_number="0001",
                valid_from_text="2026-04-10",
                valid_until_text="2099-04-10",
                medical_decision="fit",
                restriction_note="",
            )

            medical_records = load_medical_registry(context.database_path)
            target_records = [medical_record for medical_record in medical_records if medical_record.employee_personnel_number == "0001"]

            self.assertEqual(len(medical_records), medical_total_before + 1)
            self.assertTrue(target_records)
            self.assertEqual(target_records[-1].medical_decision.value, "fit")
            self.assertEqual(target_records[-1].status.value, "current")
            shut_down_logging()


if __name__ == "__main__":
    unittest.main()

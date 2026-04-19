import json
import tempfile
import unittest
from pathlib import Path

from osah.application.services.create_employee_import_batch_from_file import create_employee_import_batch_from_file
from osah.application.services.initialize_application import initialize_application
from osah.application.services.load_latest_employee_import_review import load_latest_employee_import_review
from osah.infrastructure.config.application_paths import build_application_paths
from osah.infrastructure.logging.shutdown_logging import shut_down_logging


class CreateEmployeeImportBatchFromFileTests(unittest.TestCase):
    """Тести створення чернеток імпорту працівників з файлу.
    Тесты создания черновиков импорта сотрудников из файла.
    """

    # ###### ПЕРЕВІРКА СТВОРЕННЯ ПАРТІЇ ІМПОРТУ З JSON / ПРОВЕРКА СОЗДАНИЯ ПАРТИИ ИМПОРТА ИЗ JSON ######
    def test_create_employee_import_batch_from_file_creates_review_drafts(self) -> None:
        """Перевіряє створення чернеток імпорту працівників з JSON-файлу.
        Проверяет создание черновиков импорта сотрудников из JSON-файла.
        """

        with tempfile.TemporaryDirectory() as temporary_directory:
            application_paths = build_application_paths(Path(temporary_directory))
            context = initialize_application(application_paths)
            source_path = Path(temporary_directory) / "employees-import.json"
            source_path.write_text(
                json.dumps(
                    [
                        {
                            "personnel_number": "0003",
                            "full_name": "Петренко Марія Ігорівна",
                            "position_name": "Майстер дільниці",
                            "department_name": "Виробнича дільниця N2",
                            "employment_status": "active",
                        }
                    ],
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            batch_id = create_employee_import_batch_from_file(context.database_path, source_path)
            latest_batch_summary, employee_import_drafts = load_latest_employee_import_review(context.database_path)

            self.assertEqual(batch_id, latest_batch_summary.batch_id)
            self.assertEqual(latest_batch_summary.valid_total, 1)
            self.assertEqual(len(employee_import_drafts), 1)
            self.assertEqual(employee_import_drafts[0].personnel_number, "0003")
            shut_down_logging()


if __name__ == "__main__":
    unittest.main()

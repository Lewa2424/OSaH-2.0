import json
import tempfile
import unittest
from pathlib import Path

from osah.application.services.apply_employee_import_batch import apply_employee_import_batch
from osah.application.services.create_employee_import_batch_from_file import create_employee_import_batch_from_file
from osah.application.services.initialize_application import initialize_application
from osah.application.services.load_employee_registry import load_employee_registry
from osah.application.services.load_latest_employee_import_review import load_latest_employee_import_review
from osah.infrastructure.config.application_paths import build_application_paths
from osah.infrastructure.logging.shutdown_logging import shut_down_logging


class ApplyEmployeeImportBatchTests(unittest.TestCase):
    """Тести застосування партії імпорту працівників.
    Тесты применения партии импорта сотрудников.
    """

    # ###### ПЕРЕВІРКА ЗАСТОСУВАННЯ ПАРТІЇ ІМПОРТУ / ПРОВЕРКА ПРИМЕНЕНИЯ ПАРТИИ ИМПОРТА ######
    def test_apply_employee_import_batch_persists_new_employee(self) -> None:
        """Перевіряє застосування валідної партії імпорту до реєстру працівників.
        Проверяет применение валидной партии импорта к реестру сотрудников.
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
            apply_employee_import_batch(context.database_path, batch_id)

            employees = load_employee_registry(context.database_path)
            latest_batch_summary, _ = load_latest_employee_import_review(context.database_path)

            self.assertTrue(any(employee.personnel_number == "0003" for employee in employees))
            self.assertIsNotNone(latest_batch_summary.applied_at)
            shut_down_logging()


if __name__ == "__main__":
    unittest.main()

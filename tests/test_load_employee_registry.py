import tempfile
import unittest
from pathlib import Path

from osah.application.services.initialize_application import initialize_application
from osah.application.services.load_employee_registry import load_employee_registry
from osah.infrastructure.config.application_paths import build_application_paths
from osah.infrastructure.logging.shutdown_logging import shut_down_logging


class LoadEmployeeRegistryTests(unittest.TestCase):
    """Тести читання реєстру працівників.
    Тесты чтения реестра сотрудников.
    """

    # ###### ПЕРЕВІРКА ЧИТАННЯ РЕЄСТРУ / ПРОВЕРКА ЧТЕНИЯ РЕЕСТРА ######
    def test_load_employee_registry_returns_seeded_employees(self) -> None:
        """Перевіряє, що стартовий реєстр містить типове наповнення підприємства.
        Проверяет, что стартовый реестр содержит типовое наполнение предприятия.
        """

        with tempfile.TemporaryDirectory() as temporary_directory:
            application_paths = build_application_paths(Path(temporary_directory))
            context = initialize_application(application_paths)
            employees = load_employee_registry(context.database_path)

            self.assertGreaterEqual(len(employees), 50)
            employee_names = {employee.full_name for employee in employees}
            department_names = {employee.department_name for employee in employees}
            self.assertIn("Коваль Олена Вікторівна", employee_names)
            self.assertIn("Служба охорони праці", department_names)
            self.assertIn("Механоскладальний цех", department_names)
            shut_down_logging()


if __name__ == "__main__":
    unittest.main()

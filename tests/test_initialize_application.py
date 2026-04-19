import sqlite3
import tempfile
import unittest
from pathlib import Path

from osah.application.services.initialize_application import initialize_application
from osah.infrastructure.config.application_paths import build_application_paths
from osah.infrastructure.logging.shutdown_logging import shut_down_logging


class InitializeApplicationTests(unittest.TestCase):
    """Тести ініціалізації застосунку.
    Тесты инициализации приложения.
    """

    # ###### ПЕРЕВІРКА СТВОРЕННЯ БАЗИ / ПРОВЕРКА СОЗДАНИЯ БАЗЫ ######
    def test_initialize_application_creates_database_and_log_files(self) -> None:
        """Перевіряє створення робочих файлів під час ініціалізації.
        Проверяет создание рабочих файлов при инициализации.
        """

        with tempfile.TemporaryDirectory() as temporary_directory:
            application_paths = build_application_paths(Path(temporary_directory))
            context = initialize_application(application_paths)

            self.assertTrue(context.database_path.exists())
            self.assertTrue(context.log_path.exists())

            connection = sqlite3.connect(context.database_path)
            tables = {
                row[0]
                for row in connection.execute(
                    "SELECT name FROM sqlite_master WHERE type = 'table';"
                ).fetchall()
            }
            employee_total = connection.execute("SELECT COUNT(*) FROM employees;").fetchone()[0]
            training_total = connection.execute("SELECT COUNT(*) FROM trainings;").fetchone()[0]
            ppe_total = connection.execute("SELECT COUNT(*) FROM ppe_records;").fetchone()[0]
            medical_total = connection.execute("SELECT COUNT(*) FROM medical_records;").fetchone()[0]
            work_permit_total = connection.execute("SELECT COUNT(*) FROM work_permits;").fetchone()[0]
            connection.close()
            self.assertIn("employees", tables)
            self.assertIn("audit_log", tables)
            shut_down_logging()

            self.assertGreaterEqual(employee_total, 50)
            self.assertGreater(training_total, 30)
            self.assertGreater(ppe_total, 100)
            self.assertGreater(medical_total, 30)
            self.assertGreater(work_permit_total, 5)


if __name__ == "__main__":
    unittest.main()

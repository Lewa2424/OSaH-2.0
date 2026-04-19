import tempfile
import unittest
from pathlib import Path

from osah.application.services.initialize_application import initialize_application
from osah.application.services.load_training_registry_rows import load_training_registry_rows
from osah.domain.entities.training_registry_filter import TrainingRegistryFilter
from osah.infrastructure.config.application_paths import build_application_paths
from osah.infrastructure.logging.shutdown_logging import shut_down_logging


class LoadTrainingRegistryRowsTests(unittest.TestCase):
    """Тести завантаження рядків реєстру інструктажів.
    Тесты загрузки строк реестра инструктажей.
    """

    # ###### ПЕРЕВІРКА ФІЛЬТРА ВІДСУТНІХ ЗАПИСІВ / ПРОВЕРКА ФИЛЬТРА ОТСУТСТВУЮЩИХ ЗАПИСЕЙ ######
    def test_load_training_registry_rows_returns_missing_rows_for_active_employees_without_records(self) -> None:
        """Перевіряє, що фільтр відсутніх записів показує активних працівників без інструктажів.
        Проверяет, что фильтр отсутствующих записей показывает активных сотрудников без инструктажей.
        """

        with tempfile.TemporaryDirectory() as temporary_directory:
            application_paths = build_application_paths(Path(temporary_directory))
            context = initialize_application(application_paths)

            rows = load_training_registry_rows(context.database_path, TrainingRegistryFilter.MISSING)

            self.assertGreaterEqual(len(rows), 5)
            self.assertTrue(all(row.status_label == "Відсутній" for row in rows))
            shut_down_logging()


if __name__ == "__main__":
    unittest.main()

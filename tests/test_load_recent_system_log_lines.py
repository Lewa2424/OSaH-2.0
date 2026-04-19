import tempfile
import unittest
from pathlib import Path

from osah.application.services.initialize_application import initialize_application
from osah.application.services.load_recent_system_log_lines import load_recent_system_log_lines
from osah.infrastructure.config.application_paths import build_application_paths
from osah.infrastructure.logging.shutdown_logging import shut_down_logging


class LoadRecentSystemLogLinesTests(unittest.TestCase):
    """Тести читання останніх рядків системного логу.
    Тесты чтения последних строк системного лога.
    """

    # ###### ПЕРЕВІРКА ЧИТАННЯ СИСТЕМНОГО ЛОГУ / ПРОВЕРКА ЧТЕНИЯ СИСТЕМНОГО ЛОГА ######
    def test_initialize_application_writes_bootstrap_lines_to_system_log(self) -> None:
        """Перевіряє, що bootstrap події потрапляють до файлового логу.
        Проверяет, что bootstrap события попадают в файловый лог.
        """

        with tempfile.TemporaryDirectory() as temporary_directory:
            application_paths = build_application_paths(Path(temporary_directory))
            context = initialize_application(application_paths)

            recent_system_log_lines = load_recent_system_log_lines(context.database_path, line_limit=10)

            self.assertTrue(recent_system_log_lines)
            self.assertTrue(any("Application bootstrap started." in log_line for log_line in recent_system_log_lines))
            self.assertTrue(any("Application bootstrap completed successfully." in log_line for log_line in recent_system_log_lines))
            shut_down_logging()


if __name__ == "__main__":
    unittest.main()

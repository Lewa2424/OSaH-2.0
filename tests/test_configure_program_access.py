import tempfile
import unittest
from pathlib import Path

from osah.application.services.initialize_application import initialize_application
from osah.application.services.security.configure_program_access import configure_program_access
from osah.application.services.security.load_security_profile import load_security_profile
from osah.infrastructure.config.application_paths import build_application_paths
from osah.infrastructure.logging.shutdown_logging import shut_down_logging


class ConfigureProgramAccessTests(unittest.TestCase):
    """Тести первинного налаштування доступу до програми.
    Тесты первичной настройки доступа к программе.
    """

    # ###### ПЕРЕВІРКА СТВОРЕННЯ RECOVERY-ФАЙЛУ / ПРОВЕРКА СОЗДАНИЯ RECOVERY-ФАЙЛА ######
    def test_configure_program_access_creates_recovery_file_and_profile(self) -> None:
        """Перевіряє налаштування паролів і створення recovery-файлу.
        Проверяет настройку паролей и создание recovery-файла.
        """

        with tempfile.TemporaryDirectory() as temporary_directory:
            application_paths = build_application_paths(Path(temporary_directory))
            context = initialize_application(application_paths)

            reset_result = configure_program_access(context.database_path, "inspector-123", "manager-456")
            security_profile = load_security_profile(context.database_path)

            self.assertTrue(security_profile.is_configured)
            self.assertTrue(reset_result.recovery_file_path.exists())
            self.assertIn("Recovery code", reset_result.recovery_file_path.read_text(encoding="utf-8"))
            shut_down_logging()


if __name__ == "__main__":
    unittest.main()

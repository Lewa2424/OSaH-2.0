import tempfile
import unittest
from pathlib import Path

from osah.application.services.initialize_application import initialize_application
from osah.application.services.security.authenticate_program_access import authenticate_program_access
from osah.application.services.security.configure_program_access import configure_program_access
from osah.application.services.security.reset_program_access_with_recovery_code import (
    reset_program_access_with_recovery_code,
)
from osah.domain.entities.access_role import AccessRole
from osah.infrastructure.config.application_paths import build_application_paths
from osah.infrastructure.logging.shutdown_logging import shut_down_logging


class ResetProgramAccessWithRecoveryCodeTests(unittest.TestCase):
    """Тести скидання доступу через recovery-код.
    Тесты сброса доступа через recovery-код.
    """

    # ###### ПЕРЕВІРКА СКИДАННЯ ЧЕРЕЗ RECOVERY-КОД / ПРОВЕРКА СБРОСА ЧЕРЕЗ RECOVERY-КОД ######
    def test_reset_program_access_with_recovery_code_replaces_passwords(self) -> None:
        """Перевіряє заміну паролів і перевипуск recovery-коду.
        Проверяет замену паролей и перевыпуск recovery-кода.
        """

        with tempfile.TemporaryDirectory() as temporary_directory:
            application_paths = build_application_paths(Path(temporary_directory))
            context = initialize_application(application_paths)
            initial_result = configure_program_access(context.database_path, "inspector-123", "manager-456")

            reset_result = reset_program_access_with_recovery_code(
                context.database_path,
                initial_result.recovery_code,
                "inspector-789",
                "manager-999",
            )
            authentication_result = authenticate_program_access(
                context.database_path,
                AccessRole.INSPECTOR,
                "inspector-789",
            )

            self.assertTrue(authentication_result.is_authenticated)
            self.assertNotEqual(initial_result.recovery_code, reset_result.recovery_code)
            shut_down_logging()


if __name__ == "__main__":
    unittest.main()

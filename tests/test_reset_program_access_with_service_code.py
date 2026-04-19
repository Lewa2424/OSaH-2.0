import tempfile
import unittest
from pathlib import Path

from osah.application.services.initialize_application import initialize_application
from osah.application.services.security.authenticate_program_access import authenticate_program_access
from osah.application.services.security.build_service_reset_request import build_service_reset_request
from osah.application.services.security.configure_program_access import configure_program_access
from osah.application.services.security.reset_program_access_with_service_code import (
    reset_program_access_with_service_code,
)
from osah.domain.entities.access_role import AccessRole
from osah.domain.services.security.build_service_reset_code import build_service_reset_code
from osah.infrastructure.config.application_paths import build_application_paths
from osah.infrastructure.logging.shutdown_logging import shut_down_logging


class ResetProgramAccessWithServiceCodeTests(unittest.TestCase):
    """Тести скидання доступу через сервісний код.
    Тесты сброса доступа через сервисный код.
    """

    # ###### ПЕРЕВІРКА СКИДАННЯ ЧЕРЕЗ СЕРВІСНИЙ КОД / ПРОВЕРКА СБРОСА ЧЕРЕЗ СЕРВИСНЫЙ КОД ######
    def test_reset_program_access_with_service_code_accepts_installation_bound_code(self) -> None:
        """Перевіряє скидання через installation-bound сервісний код.
        Проверяет сброс через installation-bound сервисный код.
        """

        with tempfile.TemporaryDirectory() as temporary_directory:
            application_paths = build_application_paths(Path(temporary_directory))
            context = initialize_application(application_paths)
            configure_program_access(context.database_path, "inspector-123", "manager-456")
            service_reset_request = build_service_reset_request(context.database_path)
            service_code = build_service_reset_code(
                service_reset_request.installation_id,
                service_reset_request.request_counter,
            )

            reset_program_access_with_service_code(
                context.database_path,
                service_code,
                "inspector-789",
                "manager-999",
            )
            authentication_result = authenticate_program_access(
                context.database_path,
                AccessRole.MANAGER,
                "manager-999",
            )

            self.assertTrue(authentication_result.is_authenticated)
            shut_down_logging()


if __name__ == "__main__":
    unittest.main()

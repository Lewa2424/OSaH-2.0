import tempfile
import unittest
from pathlib import Path

from osah.application.services.initialize_application import initialize_application
from osah.application.services.security.authenticate_program_access import authenticate_program_access
from osah.application.services.security.configure_program_access import configure_program_access
from osah.domain.entities.access_role import AccessRole
from osah.infrastructure.config.application_paths import build_application_paths
from osah.infrastructure.logging.shutdown_logging import shut_down_logging


class AuthenticateProgramAccessTests(unittest.TestCase):
    """Тести автентифікації доступу до програми.
    Тесты аутентификации доступа к программе.
    """

    # ###### ПЕРЕВІРКА УСПІШНОГО ВХОДУ ІНСПЕКТОРА / ПРОВЕРКА УСПЕШНОГО ВХОДА ИНСПЕКТОРА ######
    def test_authenticate_program_access_accepts_valid_inspector_password(self) -> None:
        """Перевіряє успішний вхід інспектора з правильним паролем.
        Проверяет успешный вход инспектора с правильным паролем.
        """

        with tempfile.TemporaryDirectory() as temporary_directory:
            application_paths = build_application_paths(Path(temporary_directory))
            context = initialize_application(application_paths)
            configure_program_access(context.database_path, "inspector-123", "manager-456")

            authentication_result = authenticate_program_access(
                context.database_path,
                AccessRole.INSPECTOR,
                "inspector-123",
            )

            self.assertTrue(authentication_result.is_authenticated)
            self.assertEqual(authentication_result.access_role, AccessRole.INSPECTOR)
            shut_down_logging()

    # ###### ПЕРЕВІРКА ТИМЧАСОВОГО БЛОКУВАННЯ ПІСЛЯ ПОМИЛОК / ПРОВЕРКА ВРЕМЕННОЙ БЛОКИРОВКИ ПОСЛЕ ОШИБОК ######
    def test_authenticate_program_access_locks_after_five_failures(self) -> None:
        """Перевіряє тимчасове блокування після п'яти невдалих спроб входу.
        Проверяет временную блокировку после пяти неудачных попыток входа.
        """

        with tempfile.TemporaryDirectory() as temporary_directory:
            application_paths = build_application_paths(Path(temporary_directory))
            context = initialize_application(application_paths)
            configure_program_access(context.database_path, "inspector-123", "manager-456")

            last_result = None
            for _ in range(5):
                last_result = authenticate_program_access(
                    context.database_path,
                    AccessRole.MANAGER,
                    "wrong-password",
                )

            self.assertIsNotNone(last_result)
            self.assertFalse(last_result.is_authenticated)
            self.assertIn("заблоковано", last_result.message_text)
            shut_down_logging()


if __name__ == "__main__":
    unittest.main()

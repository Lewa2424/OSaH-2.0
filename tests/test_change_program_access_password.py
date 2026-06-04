import tempfile
import unittest
from pathlib import Path

from osah.application.services.initialize_application import initialize_application
from osah.application.services.security.authenticate_program_access import authenticate_program_access
from osah.application.services.security.change_program_access_password import change_program_access_password
from osah.application.services.security.configure_program_access import configure_program_access
from osah.domain.entities.access_role import AccessRole
from osah.infrastructure.config.application_paths import build_application_paths
from osah.infrastructure.logging.shutdown_logging import shut_down_logging


class ChangeProgramAccessPasswordTests(unittest.TestCase):
    """Тести зміни пароля ролі в налаштуваннях."""

    def test_inspector_can_change_own_password(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            context = initialize_application(build_application_paths(Path(temporary_directory)))
            configure_program_access(context.database_path, "inspector-123456", "manager-654321")
            change_program_access_password(
                context.database_path,
                AccessRole.INSPECTOR,
                "inspector-123456",
                "inspector-newpass",
            )
            result = authenticate_program_access(
                context.database_path,
                AccessRole.INSPECTOR,
                "inspector-newpass",
            )
            self.assertTrue(result.is_authenticated)
            shut_down_logging()

    def test_manager_cannot_reuse_inspector_password(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            context = initialize_application(build_application_paths(Path(temporary_directory)))
            configure_program_access(context.database_path, "inspector-123456", "manager-654321")
            with self.assertRaises(ValueError):
                change_program_access_password(
                    context.database_path,
                    AccessRole.MANAGER,
                    "manager-654321",
                    "inspector-123456",
                )
            shut_down_logging()


if __name__ == "__main__":
    unittest.main()

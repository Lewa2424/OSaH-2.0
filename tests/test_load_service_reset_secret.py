import tempfile
import unittest
from pathlib import Path

from osah.application.services.initialize_application import initialize_application
from osah.application.services.security.configure_program_access import configure_program_access
from osah.application.services.security.security_setting_keys import SERVICE_RESET_SECRET
from osah.infrastructure.config.application_paths import build_application_paths
from osah.infrastructure.database.create_database_connection import create_database_connection
from osah.infrastructure.database.queries.list_app_settings import list_app_settings
from osah.infrastructure.logging.shutdown_logging import shut_down_logging


def load_service_reset_secret(database_path: Path) -> str:
    connection = create_database_connection(database_path)
    try:
        return list_app_settings(connection).get(SERVICE_RESET_SECRET, "")
    finally:
        connection.close()


class LoadServiceResetSecretTests(unittest.TestCase):
    """Перевіряє наявність сервісного секрету після налаштування доступу."""

    def test_configure_program_access_persists_service_reset_secret(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            context = initialize_application(build_application_paths(Path(temporary_directory)))
            configure_program_access(context.database_path, "inspector-123456", "manager-654321")
            secret = load_service_reset_secret(context.database_path)
            self.assertTrue(len(secret) >= 32)
            shut_down_logging()


if __name__ == "__main__":
    unittest.main()

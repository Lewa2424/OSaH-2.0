import json
import tempfile
import unittest
from pathlib import Path

from osah.application.services.export_full_system_state import export_full_system_state
from osah.application.services.initialize_application import initialize_application
from osah.infrastructure.config.application_paths import build_application_paths
from osah.infrastructure.logging.shutdown_logging import shut_down_logging
from osah.domain.entities.access_role import AccessRole


class ExportFullSystemStateTests(unittest.TestCase):
    """Тести повного експорту стану системи.
    Тесты полного экспорта состояния системы.
    """

    # ###### ПЕРЕВІРКА ПОВНОГО ЕКСПОРТУ СИСТЕМИ / ПРОВЕРКА ПОЛНОГО ЭКСПОРТА СИСТЕМЫ ######
    def test_export_full_system_state_creates_json_file_with_tables(self) -> None:
        """Перевіряє створення JSON-файлу з повним станом системи.
        Проверяет создание JSON-файла с полным состоянием системы.
        """

        with tempfile.TemporaryDirectory() as temporary_directory:
            application_paths = build_application_paths(Path(temporary_directory))
            context = initialize_application(application_paths)

            export_file_path = export_full_system_state(context.database_path, access_role=AccessRole.INSPECTOR)
            export_payload = json.loads(export_file_path.read_text(encoding="utf-8"))

            self.assertTrue(export_file_path.exists())
            self.assertIn("tables", export_payload)
            self.assertIn("employees", export_payload["tables"])
            self.assertNotIn("app_settings", export_payload["tables"])
            self.assertTrue(export_payload.get("secrets_redacted"))
            export_text = export_file_path.read_text(encoding="utf-8")
            self.assertNotIn("inspector_password_hash", export_text)
            self.assertNotIn("mail.smtp_password", export_text)
            shut_down_logging()


if __name__ == "__main__":
    unittest.main()
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

from osah.application.services.ensure_startup_auto_backup import ensure_startup_auto_backup
from osah.application.services.initialize_application import initialize_application
from osah.application.services.load_backup_registry import load_backup_registry
from osah.domain.entities.backup_kind import BackupKind
from osah.infrastructure.config.application_paths import build_application_paths
from osah.infrastructure.logging.shutdown_logging import shut_down_logging


class EnsureStartupAutoBackupTests(unittest.TestCase):
    """Тести автоматичної резервної копії при запуску.
    Тесты автоматической резервной копии при запуске.
    """

    # ###### ПЕРЕВІРКА ОДНІЄЇ АВТОКОПІЇ НА ДОБУ / ПРОВЕРКА ОДНОЙ АВТОКОПИИ В СУТКИ ######
    def test_ensure_startup_auto_backup_creates_only_one_backup_per_day(self) -> None:
        """Перевіряє, що за одну дату не створюється більше однієї автокопії.
        Проверяет, что за одну дату не создаётся больше одной автокопии.
        """

        with tempfile.TemporaryDirectory() as temporary_directory:
            application_paths = build_application_paths(Path(temporary_directory))
            context = initialize_application(application_paths)

            second_backup_path = ensure_startup_auto_backup(
                context.database_path,
                current_moment=datetime.now(),
            )
            backup_snapshots = load_backup_registry(context.database_path)
            auto_snapshots = [
                backup_snapshot
                for backup_snapshot in backup_snapshots
                if backup_snapshot.backup_kind == BackupKind.AUTO
            ]

            self.assertIsNone(second_backup_path)
            self.assertEqual(len(auto_snapshots), 1)
            shut_down_logging()


if __name__ == "__main__":
    unittest.main()

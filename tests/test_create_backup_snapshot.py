import tempfile
import unittest
from pathlib import Path

from osah.application.services.create_backup_snapshot import create_backup_snapshot
from osah.application.services.initialize_application import initialize_application
from osah.application.services.load_backup_registry import load_backup_registry
from osah.domain.entities.backup_kind import BackupKind
from osah.infrastructure.config.application_paths import build_application_paths
from osah.infrastructure.logging.shutdown_logging import shut_down_logging


class CreateBackupSnapshotTests(unittest.TestCase):
    """Тести створення резервної копії локальної БД.
    Тесты создания резервной копии локальной БД.
    """

    # ###### ПЕРЕВІРКА СТВОРЕННЯ РУЧНОЇ РЕЗЕРВНОЇ КОПІЇ / ПРОВЕРКА СОЗДАНИЯ РУЧНОЙ РЕЗЕРВНОЙ КОПИИ ######
    def test_create_backup_snapshot_creates_manual_backup_file(self) -> None:
        """Перевіряє створення ручної резервної копії та її появу в реєстрі.
        Проверяет создание ручной резервной копии и её появление в реестре.
        """

        with tempfile.TemporaryDirectory() as temporary_directory:
            application_paths = build_application_paths(Path(temporary_directory))
            context = initialize_application(application_paths)

            backup_file_path = create_backup_snapshot(context.database_path, BackupKind.MANUAL)
            backup_snapshots = load_backup_registry(context.database_path)

            self.assertTrue(backup_file_path.exists())
            self.assertTrue(any(backup_snapshot.file_name == backup_file_path.name for backup_snapshot in backup_snapshots))
            shut_down_logging()


if __name__ == "__main__":
    unittest.main()

import sqlite3
import tempfile
import unittest
from pathlib import Path

from osah.application.services.create_backup_snapshot import create_backup_snapshot
from osah.application.services.initialize_application import initialize_application
from osah.application.services.restore_backup_snapshot import restore_backup_snapshot
from osah.domain.entities.access_role import AccessRole
from osah.domain.entities.backup_kind import BackupKind
from osah.infrastructure.config.application_paths import build_application_paths
from osah.infrastructure.logging.shutdown_logging import shut_down_logging


class RestoreBackupValidationTests(unittest.TestCase):
    """Тести перевірки файлу резервної копії перед відновленням."""

    def test_restore_backup_snapshot_rejects_backup_without_employees_table(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            context = initialize_application(build_application_paths(Path(temporary_directory)))
            backup_file_path = create_backup_snapshot(
                context.database_path,
                BackupKind.MANUAL,
                access_role=AccessRole.INSPECTOR,
            )
            invalid_backup_path = Path(temporary_directory) / "invalid-backup.db"
            connection = sqlite3.connect(invalid_backup_path)
            try:
                connection.execute("CREATE TABLE audit_log (id INTEGER PRIMARY KEY)")
                connection.commit()
            finally:
                connection.close()
            with self.assertRaises(ValueError):
                restore_backup_snapshot(
                    context.database_path,
                    invalid_backup_path,
                    access_role=AccessRole.INSPECTOR,
                )
            shut_down_logging()


if __name__ == "__main__":
    unittest.main()

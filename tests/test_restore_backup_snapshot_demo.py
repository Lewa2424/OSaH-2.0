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


class RestoreBackupSnapshotDemoTests(unittest.TestCase):
    """Тести заборони restore у demo-only дистрибуції."""

    def test_restore_backup_snapshot_is_blocked_in_timed_demo(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            project_root = Path(temporary_directory)
            (project_root / "ClearWork.demo").write_text("demo", encoding="utf-8")
            (project_root / "ClearWork.demo_timed").write_text("timed", encoding="utf-8")
            application_paths = build_application_paths(project_root)
            context = initialize_application(application_paths)
            backup_file_path = create_backup_snapshot(
                context.database_path,
                BackupKind.MANUAL,
                access_role=AccessRole.INSPECTOR,
            )
            shut_down_logging()

            with self.assertRaises(ValueError) as error:
                restore_backup_snapshot(
                    context.database_path,
                    backup_file_path,
                    access_role=AccessRole.INSPECTOR,
                )
            self.assertIn("демонстраційній версії", str(error.exception))


if __name__ == "__main__":
    unittest.main()

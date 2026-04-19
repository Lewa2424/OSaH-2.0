import json
import tempfile
import unittest
from pathlib import Path

from osah.application.services.apply_employee_import_batch import apply_employee_import_batch
from osah.application.services.create_backup_snapshot import create_backup_snapshot
from osah.application.services.create_employee_import_batch_from_file import create_employee_import_batch_from_file
from osah.application.services.initialize_application import initialize_application
from osah.application.services.load_backup_registry import load_backup_registry
from osah.application.services.load_employee_registry import load_employee_registry
from osah.application.services.restore_backup_snapshot import restore_backup_snapshot
from osah.domain.entities.backup_kind import BackupKind
from osah.infrastructure.config.application_paths import build_application_paths
from osah.infrastructure.logging.shutdown_logging import shut_down_logging


class RestoreBackupSnapshotTests(unittest.TestCase):
    """Тести відновлення локальної БД з резервної копії.
    Тесты восстановления локальной БД из резервной копии.
    """

    # ###### ПЕРЕВІРКА ВІДНОВЛЕННЯ РЕЗЕРВНОЇ КОПІЇ / ПРОВЕРКА ВОССТАНОВЛЕНИЯ РЕЗЕРВНОЙ КОПИИ ######
    def test_restore_backup_snapshot_restores_previous_state_and_creates_safety_copy(self) -> None:
        """Перевіряє відновлення попереднього стану та створення страховочної копії.
        Проверяет восстановление предыдущего состояния и создание страховочной копии.
        """

        with tempfile.TemporaryDirectory() as temporary_directory:
            application_paths = build_application_paths(Path(temporary_directory))
            context = initialize_application(application_paths)
            backup_file_path = create_backup_snapshot(context.database_path, BackupKind.MANUAL)

            source_path = Path(temporary_directory) / "employees-import.json"
            source_path.write_text(
                json.dumps(
                    [
                        {
                            "personnel_number": "9003",
                            "full_name": "Петренко Марія Ігорівна",
                            "position_name": "Майстер дільниці",
                            "department_name": "Виробнича дільниця N2",
                            "employment_status": "active",
                        }
                    ],
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            batch_id = create_employee_import_batch_from_file(context.database_path, source_path)
            apply_employee_import_batch(context.database_path, batch_id)

            employees_before_restore = load_employee_registry(context.database_path)
            safety_backup_path = restore_backup_snapshot(context.database_path, backup_file_path)
            employees_after_restore = load_employee_registry(context.database_path)
            backup_snapshots = load_backup_registry(context.database_path)

            self.assertTrue(any(employee.personnel_number == "9003" for employee in employees_before_restore))
            self.assertFalse(any(employee.personnel_number == "9003" for employee in employees_after_restore))
            self.assertTrue(safety_backup_path.exists())
            self.assertTrue(any(backup_snapshot.file_name == safety_backup_path.name for backup_snapshot in backup_snapshots))
            shut_down_logging()


if __name__ == "__main__":
    unittest.main()

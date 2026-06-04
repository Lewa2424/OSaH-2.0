import json
import tempfile
import unittest
from pathlib import Path

from osah.application.services.archive_employee import archive_employee
from osah.application.services.build_and_save_manual_daily_report import build_and_save_manual_daily_report
from osah.application.services.cancel_work_permit_record import cancel_work_permit_record
from osah.application.services.close_work_permit_record import close_work_permit_record
from osah.application.services.create_backup_snapshot import create_backup_snapshot
from osah.application.services.create_employee import create_employee
from osah.application.services.create_employee_import_batch_from_file import create_employee_import_batch_from_file
from osah.application.services.create_medical_record import create_medical_record
from osah.application.services.create_ppe_record import create_ppe_record
from osah.application.services.create_training_record import create_training_record
from osah.application.services.create_training_records_batch import create_training_records_batch
from osah.application.services.refresh_news_sources import refresh_news_sources
from osah.application.services.send_daily_report_email import send_daily_report_email
from osah.application.services.create_work_permit_record import create_work_permit_record
from osah.application.services.initialize_application import initialize_application
from osah.application.services.load_medical_registry import load_medical_registry
from osah.application.services.load_ppe_registry import load_ppe_registry
from osah.application.services.load_work_permit_workspace import load_work_permit_workspace
from osah.application.services.restore_backup_snapshot import restore_backup_snapshot
from osah.application.services.update_employee import update_employee
from osah.application.services.update_medical_record import update_medical_record
from osah.application.services.update_ppe_record import update_ppe_record
from osah.domain.entities.access_role import AccessRole
from osah.domain.entities.backup_kind import BackupKind
from osah.domain.errors.access_denied_error import AccessDeniedError
from osah.infrastructure.config.application_paths import build_application_paths
from osah.infrastructure.logging.shutdown_logging import shut_down_logging


class ManagerReadOnlyServicesTests(unittest.TestCase):
    """Checks that manager role is denied by mutating application services."""

    def test_manager_cannot_create_employee(self) -> None:
        with self._application_context() as context:
            with self.assertRaises(AccessDeniedError):
                create_employee(
                    context.database_path,
                    "9001",
                    "Тестовий Керівник",
                    "Цех",
                    "Майстер",
                    "active",
                    access_role=AccessRole.MANAGER,
                )

    def test_manager_cannot_update_employee(self) -> None:
        with self._application_context() as context:
            with self.assertRaises(AccessDeniedError):
                update_employee(
                    context.database_path,
                    "0001",
                    "Оновлене Ім'я",
                    "Цех",
                    "Слюсар",
                    "active",
                    None,
                    False,
                    access_role=AccessRole.MANAGER,
                )

    def test_manager_cannot_archive_employee(self) -> None:
        with self._application_context() as context:
            with self.assertRaises(AccessDeniedError):
                archive_employee(context.database_path, "0001", access_role=AccessRole.MANAGER)

    def test_manager_cannot_create_training_record(self) -> None:
        with self._application_context() as context:
            with self.assertRaises(AccessDeniedError):
                create_training_record(
                    context.database_path,
                    "0001",
                    "introductory",
                    "2026-05-01",
                    "",
                    "Інспектор",
                    "",
                    access_role=AccessRole.MANAGER,
                )

    def test_manager_cannot_create_or_update_ppe_record(self) -> None:
        with self._application_context() as context:
            with self.assertRaises(AccessDeniedError):
                create_ppe_record(
                    context.database_path,
                    "0001",
                    "Каска",
                    True,
                    True,
                    "2026-05-01",
                    "2026-06-01",
                    "1",
                    "",
                    access_role=AccessRole.MANAGER,
                )

            create_ppe_record(
                context.database_path,
                "0001",
                "Каска",
                True,
                True,
                "2026-05-01",
                "2026-06-01",
                "1",
                "",
                access_role=AccessRole.INSPECTOR,
            )
            record_id = int(load_ppe_registry(context.database_path)[0].record_id or 0)
            with self.assertRaises(AccessDeniedError):
                update_ppe_record(
                    context.database_path,
                    record_id,
                    "0001",
                    "Каска",
                    True,
                    True,
                    "2026-05-01",
                    "2026-07-01",
                    "1",
                    "",
                    "issued",
                    "checked",
                    "",
                    "",
                    access_role=AccessRole.MANAGER,
                )

    def test_manager_cannot_create_or_update_medical_record(self) -> None:
        with self._application_context() as context:
            with self.assertRaises(AccessDeniedError):
                create_medical_record(
                    context.database_path,
                    "0001",
                    "2026-05-01",
                    "2026-06-01",
                    "fit",
                    "",
                    access_role=AccessRole.MANAGER,
                )

            create_medical_record(
                context.database_path,
                "0001",
                "2026-05-01",
                "2026-06-01",
                "fit",
                "",
                access_role=AccessRole.INSPECTOR,
            )
            record_id = int(load_medical_registry(context.database_path)[0].record_id or 0)
            with self.assertRaises(AccessDeniedError):
                update_medical_record(
                    context.database_path,
                    record_id,
                    "0001",
                    "2026-05-01",
                    "2026-07-01",
                    "fit",
                    "",
                    "legacy_not_tracked",
                    "",
                    "",
                    access_role=AccessRole.MANAGER,
                )

    def test_manager_cannot_create_close_or_cancel_work_permit(self) -> None:
        with self._application_context() as context:
            with self.assertRaises(AccessDeniedError):
                create_work_permit_record(
                    context.database_path,
                    "ND-RO-001",
                    "Вогневі роботи",
                    "Дільниця",
                    "19.05.2026 08:00",
                    "19.05.2026 16:00",
                    "Керівник",
                    "Допускаючий",
                    "0001",
                    "executor",
                    "",
                    access_role=AccessRole.MANAGER,
                )

            create_work_permit_record(
                context.database_path,
                "ND-RO-002",
                "Вогневі роботи",
                "Дільниця",
                "19.05.2026 08:00",
                "19.05.2026 16:00",
                "Керівник",
                "Допускаючий",
                "0001",
                "executor",
                "",
                access_role=AccessRole.INSPECTOR,
            )
            record_id = int(load_work_permit_workspace(context.database_path).rows[0].record_id or 0)
            with self.assertRaises(AccessDeniedError):
                close_work_permit_record(context.database_path, record_id, access_role=AccessRole.MANAGER)
            with self.assertRaises(AccessDeniedError):
                cancel_work_permit_record(
                    context.database_path,
                    record_id,
                    "Скасовано",
                    access_role=AccessRole.MANAGER,
                )

    def test_manager_cannot_restore_backup(self) -> None:
        with self._application_context() as context:
            backup_file_path = create_backup_snapshot(
                context.database_path,
                BackupKind.MANUAL,
                access_role=AccessRole.INSPECTOR,
            )
            with self.assertRaises(AccessDeniedError):
                restore_backup_snapshot(
                    context.database_path,
                    backup_file_path,
                    access_role=AccessRole.MANAGER,
                )

    def test_manager_cannot_start_import(self) -> None:
        with self._application_context() as context:
            source_path = Path(context.database_path.parent) / "manager-import.json"
            source_path.write_text(
                json.dumps(
                    [
                        {
                            "personnel_number": "9901",
                            "full_name": "Імпортований Працівник",
                            "position_name": "Майстер",
                            "department_name": "Цех",
                            "employment_status": "active",
                        }
                    ],
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            with self.assertRaises(AccessDeniedError):
                create_employee_import_batch_from_file(
                    context.database_path,
                    source_path,
                    access_role=AccessRole.MANAGER,
                )

    def test_manager_cannot_send_daily_report_email(self) -> None:
        with self._application_context() as context:
            with self.assertRaises(AccessDeniedError):
                send_daily_report_email(context.database_path, access_role=AccessRole.MANAGER)

    def test_manager_cannot_refresh_news_sources(self) -> None:
        with self._application_context() as context:
            with self.assertRaises(AccessDeniedError):
                refresh_news_sources(context.database_path, lambda _url: (), access_role=AccessRole.MANAGER)

    def test_manager_cannot_create_training_records_batch(self) -> None:
        with self._application_context() as context:
            with self.assertRaises(AccessDeniedError):
                create_training_records_batch(
                    database_path=context.database_path,
                    employee_personnel_numbers=("0001",),
                    training_type="introductory",
                    event_date_text="2026-05-01",
                    next_control_date_text="",
                    work_risk_category="high_risk",
                    conducted_by="Інспектор",
                    note_text="",
                    access_role=AccessRole.MANAGER,
                )

    def test_manager_cannot_build_manual_report_file(self) -> None:
        with self._application_context() as context:
            target_path = Path(context.database_path.parent) / "manager-report.txt"
            with self.assertRaises(AccessDeniedError):
                build_and_save_manual_daily_report(
                    context.database_path,
                    target_path,
                    access_role=AccessRole.MANAGER,
                )

    def _application_context(self):
        return _TemporaryApplicationContext()


class _TemporaryApplicationContext:
    """Creates a temporary initialized application context for service tests."""

    def __enter__(self):
        self._temporary_directory = tempfile.TemporaryDirectory()
        self._paths = build_application_paths(Path(self._temporary_directory.name))
        self.context = initialize_application(self._paths)
        return self.context

    def __exit__(self, exc_type, exc, tb) -> None:
        shut_down_logging()
        self._temporary_directory.cleanup()


if __name__ == "__main__":
    unittest.main()

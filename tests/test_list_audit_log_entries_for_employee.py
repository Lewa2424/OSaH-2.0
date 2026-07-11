import sqlite3
import tempfile
import unittest
from pathlib import Path

from osah.application.services.initialize_application import initialize_application
from osah.application.services.load_employee_audit_history import load_employee_audit_history
from osah.domain.entities.employee import Employee
from osah.domain.entities.employee_status_level import EmployeeStatusLevel
from osah.domain.entities.employee_workspace_row import EmployeeWorkspaceRow
from osah.domain.entities.training_record import TrainingRecord
from osah.domain.entities.training_status import TrainingStatus
from osah.domain.entities.training_type import TrainingType
from osah.domain.services.build_employee_audit_entity_keys import build_employee_audit_entity_keys
from osah.infrastructure.config.application_paths import build_application_paths
from osah.infrastructure.database.commands.insert_audit_log import insert_audit_log
from osah.infrastructure.database.create_database_connection import create_database_connection
from osah.infrastructure.database.queries.list_audit_log_entries_for_employee import (
    list_audit_log_entries_for_employee,
)
from osah.infrastructure.logging.shutdown_logging import shut_down_logging


class ListAuditLogEntriesForEmployeeTests(unittest.TestCase):
    """Інтеграційні тести фільтрації audit-журналу по працівнику.
    Integration tests for employee audit log filtering.
    """

    def test_filters_related_audit_entries_only(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            context = initialize_application(build_application_paths(Path(temporary_directory)))
            connection = create_database_connection(context.database_path)
            try:
                insert_audit_log(
                    connection,
                    event_type="employee.updated",
                    module_name="employees",
                    event_level="info",
                    actor_name="inspector",
                    entity_name="employee:0001",
                    result_status="success",
                    description_text="employee card updated",
                )
                insert_audit_log(
                    connection,
                    event_type="training.updated",
                    module_name="trainings",
                    event_level="info",
                    actor_name="inspector",
                    entity_name="training:15",
                    result_status="success",
                    description_text="training updated",
                )
                insert_audit_log(
                    connection,
                    event_type="training.updated_from_work_permit",
                    module_name="trainings",
                    event_level="info",
                    actor_name="inspector",
                    entity_name="training:0001:work_permit:НД-1",
                    result_status="success",
                    description_text="linked training",
                )
                insert_audit_log(
                    connection,
                    event_type="employee.reactivated",
                    module_name="archive",
                    event_level="warning",
                    actor_name="inspector",
                    entity_name="0001",
                    result_status="success",
                    description_text="reactivated",
                )
                insert_audit_log(
                    connection,
                    event_type="employee.updated",
                    module_name="employees",
                    event_level="info",
                    actor_name="inspector",
                    entity_name="employee:0002",
                    result_status="success",
                    description_text="other employee",
                )
                connection.commit()

                entity_keys = build_employee_audit_entity_keys(
                    personnel_number="0001",
                    training_records=(
                        TrainingRecord(
                            record_id=15,
                            employee_personnel_number="0001",
                            employee_full_name="Працівник",
                            training_type=TrainingType.PRIMARY,
                            event_date="2026-01-01",
                            next_control_date="2026-07-01",
                            conducted_by="Інспектор",
                            note_text="",
                            status=TrainingStatus.CURRENT,
                        ),
                    ),
                    ppe_records=(),
                    medical_records=(),
                    work_permit_records=(),
                )
                entries = list_audit_log_entries_for_employee(connection, entity_keys, limit=20)
            finally:
                connection.close()

            event_types = {entry.event_type for entry in entries}
            self.assertEqual(
                event_types,
                {
                    "employee.updated",
                    "training.updated",
                    "training.updated_from_work_permit",
                    "employee.reactivated",
                },
            )
            shut_down_logging()

    def test_load_employee_audit_history_uses_workspace_row(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            context = initialize_application(build_application_paths(Path(temporary_directory)))
            try:
                connection = create_database_connection(context.database_path)
                try:
                    insert_audit_log(
                        connection,
                        event_type="ppe.created",
                        module_name="ppe",
                        event_level="info",
                        actor_name="inspector",
                        entity_name="ppe:0003",
                        result_status="success",
                        description_text="ppe created",
                    )
                    connection.commit()
                finally:
                    connection.close()

                employee_row = EmployeeWorkspaceRow(
                    employee=Employee(
                        personnel_number="0003",
                        full_name="Працівник",
                        position_name="Слюсар",
                        department_name="Цех",
                        employment_status="active",
                    ),
                    status_level=EmployeeStatusLevel.NORMAL,
                    status_label="Актуально",
                    status_reason="",
                    department_name="Цех",
                    site_name="",
                    position_name="Слюсар",
                    photo_path=None,
                    training_records=(),
                    ppe_records=(),
                    medical_records=(),
                    work_permit_records=(),
                    module_summaries=(),
                    problems=(),
                )
                entries = load_employee_audit_history(context.database_path, employee_row)
                self.assertEqual(len(entries), 1)
                self.assertEqual(entries[0].event_type, "ppe.created")
            finally:
                shut_down_logging()


if __name__ == "__main__":
    unittest.main()

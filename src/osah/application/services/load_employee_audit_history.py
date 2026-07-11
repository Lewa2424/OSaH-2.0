from pathlib import Path

from osah.domain.entities.audit_log_entry import AuditLogEntry
from osah.domain.entities.employee_workspace_row import EmployeeWorkspaceRow
from osah.domain.services.build_employee_audit_entity_keys import build_employee_audit_entity_keys
from osah.infrastructure.database.create_database_connection import create_database_connection
from osah.infrastructure.database.queries.list_audit_log_entries_for_employee import (
    list_audit_log_entries_for_employee,
)


# ###### ЗАВАНТАЖЕННЯ ІСТОРІЇ ПРАЦІВНИКА / LOAD EMPLOYEE AUDIT HISTORY ######
def load_employee_audit_history(
    database_path: Path,
    employee_row: EmployeeWorkspaceRow,
    *,
    limit: int = 100,
) -> tuple[AuditLogEntry, ...]:
    """Повертає audit-історію вибраного працівника для вкладки «Історія».
    Returns the selected employee audit history for the History tab.
    """

    entity_keys = build_employee_audit_entity_keys(
        personnel_number=employee_row.employee.personnel_number,
        training_records=employee_row.training_records,
        ppe_records=employee_row.ppe_records,
        medical_records=employee_row.medical_records,
        work_permit_records=employee_row.work_permit_records,
    )

    connection = create_database_connection(database_path)
    try:
        return list_audit_log_entries_for_employee(connection, entity_keys, limit=limit)
    finally:
        connection.close()

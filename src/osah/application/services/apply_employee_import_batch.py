from datetime import datetime
from pathlib import Path

from osah.application.services.sync_control_notifications import sync_control_notifications
from osah.domain.entities.employee import Employee
from osah.domain.entities.employee_import_draft_status import EmployeeImportDraftStatus
from osah.infrastructure.database.commands.insert_audit_log import insert_audit_log
from osah.infrastructure.database.commands.mark_import_batch_as_applied import mark_import_batch_as_applied
from osah.infrastructure.database.commands.upsert_employee_row import upsert_employee_row
from osah.infrastructure.database.create_database_connection import create_database_connection
from osah.infrastructure.database.queries.list_employee_import_drafts_by_batch import list_employee_import_drafts_by_batch
from osah.infrastructure.logging.log_system_event import log_system_event


# ###### ЗАСТОСУВАННЯ ПАРТІЇ ІМПОРТУ ПРАЦІВНИКІВ / ПРИМЕНЕНИЕ ПАРТИИ ИМПОРТА СОТРУДНИКОВ ######
def apply_employee_import_batch(database_path: Path, batch_id: int) -> None:
    """Застосовує валідні чернетки партії імпорту працівників до бойових сутностей.
    Применяет валидные черновики партии импорта сотрудников к боевым сущностям.
    """

    connection = create_database_connection(database_path)
    try:
        employee_import_drafts = list_employee_import_drafts_by_batch(connection, batch_id)
        if not employee_import_drafts:
            raise ValueError("Чернетки для обраної партії імпорту не знайдено.")

        applied_count = 0
        for employee_import_draft in employee_import_drafts:
            if employee_import_draft.resolution_status in (
                EmployeeImportDraftStatus.INVALID,
                EmployeeImportDraftStatus.UNCHANGED,
            ):
                continue

            upsert_employee_row(
                connection,
                Employee(
                    personnel_number=employee_import_draft.personnel_number,
                    full_name=employee_import_draft.full_name,
                    position_name=employee_import_draft.position_name,
                    department_name=employee_import_draft.department_name,
                    employment_status=employee_import_draft.employment_status,
                ),
            )
            applied_count += 1

        applied_at = datetime.now().isoformat(sep=" ", timespec="minutes")
        mark_import_batch_as_applied(connection, batch_id, applied_at)
        insert_audit_log(
            connection,
            event_type="import.applied",
            module_name="import_export",
            event_level="info",
            actor_name="system",
            entity_name=f"batch:{batch_id}",
            result_status="success",
            description_text=f"applied_count={applied_count};applied_at={applied_at}",
        )
        sync_control_notifications(connection)
        connection.commit()
        log_system_event("import_export", f"Employee import batch applied: batch_id={batch_id};applied_count={applied_count}")
    finally:
        connection.close()

from pathlib import Path

from osah.application.services.create_ppe_record import _parse_quantity, _resolve_provision_status
from osah.application.services.security.ensure_write_access import ensure_write_access
from osah.application.services.sync_control_notifications import sync_control_notifications
from osah.domain.entities.access_role import AccessRole
from osah.domain.entities.ppe_compliance_check_state import PpeComplianceCheckState
from osah.domain.entities.ppe_provision_status import PpeProvisionStatus
from osah.domain.entities.ppe_record import PpeRecord
from osah.domain.entities.ppe_status import PpeStatus
from osah.domain.services.parse_ui_date_text import parse_ui_date_text
from osah.domain.services.serialize_ppe_record_for_audit import serialize_ppe_record_for_audit
from osah.infrastructure.database.commands.insert_audit_log import insert_audit_log
from osah.infrastructure.database.commands.update_ppe_record_row import update_ppe_record_row
from osah.infrastructure.database.create_database_connection import create_database_connection
from osah.infrastructure.database.queries.get_ppe_record_by_id import get_ppe_record_by_id


# ###### ОБНОВЛЕНИЕ ЗАПИСИ СИЗ / UPDATE PPE RECORD ######
def update_ppe_record(
    database_path: Path,
    record_id: int,
    employee_personnel_number: str,
    ppe_name: str,
    is_required: bool,
    is_issued: bool,
    issue_date_text: str,
    replacement_date_text: str,
    quantity_text: str,
    note_text: str,
    provision_status: str = "",
    compliance_check_state: str = "legacy_not_tracked",
    basis_text: str = "",
    basis_note: str = "",
    *,
    access_role: AccessRole,
) -> None:
    """Обновляет запись СИЗ, синхронизирует уведомления и пишет audit.
    Updates a PPE record, synchronizes notifications and writes audit.
    """

    ensure_write_access(access_role, "update_ppe_record")
    normalized_personnel_number = employee_personnel_number.strip()
    normalized_ppe_name = ppe_name.strip()
    normalized_note = note_text.strip()
    if not normalized_personnel_number:
        raise ValueError("Потрібно вибрати працівника.")
    if not normalized_ppe_name:
        raise ValueError("Потрібно вказати назву ЗІЗ.")
    quantity = _parse_quantity(quantity_text.strip())
    issue_date = parse_ui_date_text(issue_date_text)
    replacement_date = parse_ui_date_text(replacement_date_text)
    if replacement_date < issue_date:
        raise ValueError("Дата заміни не може бути раніше дати видачі.")

    connection = create_database_connection(database_path)
    try:
        previous_record = get_ppe_record_by_id(connection, record_id)
        if previous_record is None:
            raise ValueError("Запис ЗІЗ не знайдено.")

        updated_record = PpeRecord(
            record_id=record_id,
            employee_personnel_number=normalized_personnel_number,
            employee_full_name=previous_record.employee_full_name,
            ppe_name=normalized_ppe_name,
            is_required=is_required,
            is_issued=is_issued,
            issue_date=issue_date.isoformat(),
            replacement_date=replacement_date.isoformat(),
            quantity=quantity,
            note_text=normalized_note,
            status=PpeStatus.CURRENT,
            provision_status=PpeProvisionStatus(provision_status.strip() or _resolve_provision_status(is_required, is_issued)),
            compliance_check_state=PpeComplianceCheckState(compliance_check_state.strip() or "legacy_not_tracked"),
            basis_text=basis_text.strip(),
            basis_note=basis_note.strip(),
        )
        update_ppe_record_row(connection, updated_record)
        insert_audit_log(
            connection,
            event_type="ppe.updated",
            module_name="ppe",
            event_level="info",
            actor_name="system",
            entity_name=f"ppe:{record_id}",
            result_status="success",
            description_text=(
                f"old=({serialize_ppe_record_for_audit(previous_record)}) "
                f"new=({serialize_ppe_record_for_audit(updated_record)})"
            ),
        )
        sync_control_notifications(connection)
        connection.commit()
    finally:
        connection.close()

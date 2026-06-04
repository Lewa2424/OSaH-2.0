from pathlib import Path

from osah.application.services.security.ensure_write_access import ensure_write_access
from osah.application.services.sync_control_notifications import sync_control_notifications
from osah.domain.entities.access_role import AccessRole
from osah.domain.entities.ppe_compliance_check_state import PpeComplianceCheckState
from osah.domain.entities.ppe_provision_status import PpeProvisionStatus
from osah.domain.entities.ppe_record import PpeRecord
from osah.domain.entities.ppe_status import PpeStatus
from osah.domain.services.parse_service_date_text import parse_service_date_text
from osah.domain.services.serialize_ppe_record_for_audit import serialize_ppe_record_for_audit
from osah.infrastructure.database.commands.insert_audit_log import insert_audit_log
from osah.infrastructure.database.commands.insert_ppe_record import insert_ppe_record
from osah.infrastructure.database.create_database_connection import create_database_connection


# ###### СОЗДАНИЕ ЗАПИСИ СИЗ / CREATE PPE RECORD ######
def create_ppe_record(
    database_path: Path,
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
    """Создаёт новую запись СИЗ и синхронизирует контрольные уведомления.
    Creates a new PPE record and synchronizes control notifications.
    """

    ensure_write_access(access_role, "create_ppe_record")
    normalized_personnel_number = employee_personnel_number.strip()
    normalized_ppe_name = ppe_name.strip()
    normalized_quantity_text = quantity_text.strip()
    normalized_note = note_text.strip()
    if not normalized_personnel_number:
        raise ValueError("Потрібно вибрати працівника.")
    if not normalized_ppe_name:
        raise ValueError("Потрібно вказати назву ЗІЗ.")
    if not normalized_quantity_text:
        raise ValueError("Потрібно вказати кількість.")

    quantity = _parse_quantity(normalized_quantity_text)
    issue_date = parse_service_date_text(issue_date_text)
    replacement_date = parse_service_date_text(replacement_date_text)
    if replacement_date < issue_date:
        raise ValueError("Дата заміни не може бути раніше дати видачі.")

    resolved_provision_status = provision_status.strip() or _resolve_provision_status(is_required, is_issued)
    connection = create_database_connection(database_path)
    try:
        record = PpeRecord(
            record_id=None,
            employee_personnel_number=normalized_personnel_number,
            employee_full_name="",
            ppe_name=normalized_ppe_name,
            is_required=is_required,
            is_issued=is_issued,
            issue_date=issue_date.isoformat(),
            replacement_date=replacement_date.isoformat(),
            quantity=quantity,
            note_text=normalized_note,
            status=PpeStatus.CURRENT,
            provision_status=PpeProvisionStatus(resolved_provision_status),
            compliance_check_state=PpeComplianceCheckState(compliance_check_state.strip() or "legacy_not_tracked"),
            basis_text=basis_text.strip(),
            basis_note=basis_note.strip(),
        )
        insert_ppe_record(connection, record)
        insert_audit_log(
            connection,
            event_type="ppe.created",
            module_name="ppe",
            event_level="info",
            actor_name="system",
            entity_name=f"ppe:{normalized_personnel_number}",
            result_status="success",
            description_text=f"created=({serialize_ppe_record_for_audit(record)})",
        )
        sync_control_notifications(connection)
        connection.commit()
    finally:
        connection.close()


def _parse_quantity(quantity_text: str) -> int:
    try:
        quantity = int(quantity_text)
    except ValueError as error:
        raise ValueError("Кількість має бути цілим числом.") from error
    if quantity <= 0:
        raise ValueError("Кількість має бути більшою за нуль.")
    return quantity


def _resolve_provision_status(is_required: bool, is_issued: bool) -> str:
    if is_required and not is_issued:
        return PpeProvisionStatus.REQUIRED_NOT_ISSUED.value
    if not is_required:
        return PpeProvisionStatus.NOT_REQUIRED.value
    return PpeProvisionStatus.ISSUED.value

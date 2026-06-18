from pathlib import Path

from osah.application.services.ai.resolve_ppe_catalog_item import resolve_ppe_catalog_item
from osah.application.services.ai.find_ppe_record_for_issuance import find_ppe_record_for_issuance
from osah.application.services.security.ensure_write_access import ensure_write_access
from osah.application.services.sync_control_notifications import sync_control_notifications
from osah.application.services.update_ppe_record import update_ppe_record
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


def create_ppe_records_batch(
    database_path: Path,
    employee_personnel_numbers: tuple[str, ...],
    ppe_name: str,
    quantity_text: str,
    issue_date_text: str,
    replacement_date_text: str,
    note_text: str,
    *,
    access_role: AccessRole,
) -> int:
    """Створює записи ЗІЗ для кількох працівників в одній транзакції.
    Creates PPE records for multiple employees in one transaction.
    """

    ensure_write_access(access_role, "create_ppe_records_batch")
    normalized_numbers = tuple(number.strip() for number in employee_personnel_numbers if number.strip())
    normalized_ppe_name = ppe_name.strip()
    normalized_quantity_text = quantity_text.strip()
    normalized_note = note_text.strip()
    if not normalized_numbers:
        raise ValueError("Потрібно вибрати хоча б одного працівника.")
    if not normalized_ppe_name:
        raise ValueError("Потрібно вказати назву ЗІЗ.")
    if not normalized_quantity_text:
        raise ValueError("Потрібно вказати кількість.")

    quantity = int(normalized_quantity_text)
    if quantity <= 0:
        raise ValueError("Кількість має бути більшою за нуль.")
    issue_date = parse_service_date_text(issue_date_text)
    replacement_date = parse_service_date_text(replacement_date_text)
    if replacement_date < issue_date:
        raise ValueError("Дата заміни не може бути раніше дати видачі.")

    resolved_ppe_name = resolve_ppe_catalog_item(database_path, normalized_ppe_name) or normalized_ppe_name
    numbers_to_insert: list[str] = []
    processed_total = 0

    for personnel_number in normalized_numbers:
        existing_record = find_ppe_record_for_issuance(
            database_path,
            personnel_number,
            normalized_ppe_name,
        )
        if existing_record is not None and existing_record.record_id is not None:
            update_ppe_record(
                database_path,
                record_id=int(existing_record.record_id),
                employee_personnel_number=personnel_number,
                ppe_name=resolved_ppe_name,
                is_required=True,
                is_issued=True,
                issue_date_text=issue_date_text,
                replacement_date_text=replacement_date_text,
                quantity_text=normalized_quantity_text,
                note_text=normalized_note,
                provision_status=PpeProvisionStatus.ISSUED.value,
                compliance_check_state=existing_record.compliance_check_state.value,
                basis_text=existing_record.basis_text,
                basis_note=existing_record.basis_note,
                access_role=access_role,
            )
            processed_total += 1
            continue
        numbers_to_insert.append(personnel_number)

    if not numbers_to_insert:
        return processed_total

    connection = create_database_connection(database_path)
    try:
        for personnel_number in numbers_to_insert:
            record = PpeRecord(
                record_id=None,
                employee_personnel_number=personnel_number,
                employee_full_name="",
                ppe_name=resolved_ppe_name,
                is_required=True,
                is_issued=True,
                issue_date=issue_date.isoformat(),
                replacement_date=replacement_date.isoformat(),
                quantity=quantity,
                note_text=normalized_note,
                status=PpeStatus.CURRENT,
                provision_status=PpeProvisionStatus.ISSUED,
                compliance_check_state=PpeComplianceCheckState.LEGACY_NOT_TRACKED,
            )
            insert_ppe_record(connection, record)
            insert_audit_log(
                connection,
                event_type="ppe.created",
                module_name="ppe",
                event_level="info",
                actor_name="system",
                entity_name=f"ppe:{personnel_number}",
                result_status="success",
                description_text=f"created=({serialize_ppe_record_for_audit(record)})",
            )
            processed_total += 1

        insert_audit_log(
            connection,
            event_type="ppe.bulk_created",
            module_name="ppe",
            event_level="info",
            actor_name="system",
            entity_name="ppe:bulk",
            result_status="success",
            description_text=f"count={len(numbers_to_insert)};ppe={resolved_ppe_name}",
        )
        sync_control_notifications(connection)
        connection.commit()
    finally:
        connection.close()
    return processed_total

import json
from pathlib import Path
from uuid import uuid4

from osah.application.services.load_contractor_workspace import load_contractor_workspace
from osah.domain.entities.contractor_record import ContractorRecord
from osah.infrastructure.database.commands.insert_audit_log import insert_audit_log
from osah.infrastructure.database.commands.upsert_app_setting import upsert_app_setting
from osah.infrastructure.database.create_database_connection import create_database_connection

_CONTRACTOR_REGISTRY_SETTING_KEY = "contractors.registry_v1"


# ###### ЗБЕРЕЖЕННЯ ЗАПИСУ ПІДРЯДНИКА / SAVE CONTRACTOR RECORD ######
def save_contractor_record(database_path: Path, record: ContractorRecord) -> ContractorRecord:
    """Creates or updates contractor record in staged contractors registry."""

    workspace = load_contractor_workspace(database_path)
    normalized_record = _normalize_record(record)
    records_by_id = {entry.contractor_id: entry for entry in workspace.records}
    records_by_id[normalized_record.contractor_id] = normalized_record
    payload = _serialize_records(tuple(records_by_id.values()))

    connection = create_database_connection(database_path)
    try:
        upsert_app_setting(connection, _CONTRACTOR_REGISTRY_SETTING_KEY, payload)
        insert_audit_log(
            connection,
            event_type="contractor.saved",
            module_name="contractors",
            event_level="info",
            actor_name="inspector",
            entity_name=normalized_record.contractor_id,
            result_status="success",
            description_text=f"Contractor record saved for {normalized_record.company_name}.",
        )
        connection.commit()
    finally:
        connection.close()
    return normalized_record


# ###### НОРМАЛІЗАЦІЯ ЗАПИСУ ПІДРЯДНИКА / NORMALIZE CONTRACTOR RECORD ######
def _normalize_record(record: ContractorRecord) -> ContractorRecord:
    """Normalizes contractor record before persistence."""

    contractor_id = record.contractor_id.strip() or uuid4().hex[:12]
    company_name = record.company_name.strip()
    if not company_name:
        raise ValueError("Потрібно вказати назву організації підрядника.")

    return ContractorRecord(
        contractor_id=contractor_id,
        company_name=company_name,
        contact_person=record.contact_person.strip(),
        contact_phone=record.contact_phone.strip(),
        contact_email=record.contact_email.strip(),
        activity_status=(record.activity_status.strip() or "active"),
        note_text=record.note_text.strip(),
    )


# ###### СЕРІАЛІЗАЦІЯ ЗАПИСІВ ПІДРЯДНИКІВ / SERIALIZE CONTRACTOR RECORDS ######
def _serialize_records(records: tuple[ContractorRecord, ...]) -> str:
    """Serializes contractors registry for app settings storage."""

    return json.dumps(
        [
            {
                "contractor_id": record.contractor_id,
                "company_name": record.company_name,
                "contact_person": record.contact_person,
                "contact_phone": record.contact_phone,
                "contact_email": record.contact_email,
                "activity_status": record.activity_status,
                "note_text": record.note_text,
            }
            for record in sorted(records, key=lambda value: (value.company_name.lower(), value.contractor_id))
        ],
        ensure_ascii=False,
    )

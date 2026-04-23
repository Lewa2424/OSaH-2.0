import json
from pathlib import Path

from osah.domain.entities.contractor_record import ContractorRecord
from osah.domain.entities.contractor_workspace import ContractorWorkspace
from osah.infrastructure.database.create_database_connection import create_database_connection
from osah.infrastructure.database.queries.list_app_settings import list_app_settings

_CONTRACTOR_REGISTRY_SETTING_KEY = "contractors.registry_v1"


# ###### ЗАВАНТАЖЕННЯ РЕЄСТРУ ПІДРЯДНИКІВ / LOAD CONTRACTOR WORKSPACE ######
def load_contractor_workspace(database_path: Path) -> ContractorWorkspace:
    """Loads staged contractor registry from app settings storage."""

    connection = create_database_connection(database_path)
    try:
        app_settings = list_app_settings(connection)
    finally:
        connection.close()

    records = tuple(_deserialize_contractor_records(app_settings.get(_CONTRACTOR_REGISTRY_SETTING_KEY, "[]")))
    return ContractorWorkspace(records=records)


# ###### ДЕСЕРІАЛІЗАЦІЯ ЗАПИСІВ ПІДРЯДНИКІВ / DESERIALIZE CONTRACTOR RECORDS ######
def _deserialize_contractor_records(raw_value: str) -> tuple[ContractorRecord, ...]:
    """Safely deserializes contractor records JSON payload."""

    try:
        payload = json.loads(raw_value)
    except json.JSONDecodeError:
        payload = []
    if not isinstance(payload, list):
        payload = []

    records: list[ContractorRecord] = []
    for item in payload:
        if not isinstance(item, dict):
            continue
        contractor_id = str(item.get("contractor_id", "")).strip()
        company_name = str(item.get("company_name", "")).strip()
        if not contractor_id or not company_name:
            continue
        records.append(
            ContractorRecord(
                contractor_id=contractor_id,
                company_name=company_name,
                contact_person=str(item.get("contact_person", "")).strip(),
                contact_phone=str(item.get("contact_phone", "")).strip(),
                contact_email=str(item.get("contact_email", "")).strip(),
                activity_status=str(item.get("activity_status", "active")).strip() or "active",
                note_text=str(item.get("note_text", "")).strip(),
            )
        )
    return tuple(records)

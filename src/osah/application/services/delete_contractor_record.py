from pathlib import Path

from osah.application.services.security.ensure_write_access import ensure_write_access
from osah.application.services.load_contractor_workspace import load_contractor_workspace
from osah.application.services.serialize_contractor_records import serialize_contractor_records
from osah.domain.entities.access_role import AccessRole
from osah.infrastructure.database.commands.insert_audit_log import insert_audit_log
from osah.infrastructure.database.commands.upsert_app_setting import upsert_app_setting
from osah.infrastructure.database.create_database_connection import create_database_connection

_CONTRACTOR_REGISTRY_SETTING_KEY = "contractors.registry_v1"


def delete_contractor_record(
    database_path: Path,
    contractor_id: str,
    *,
    access_role: AccessRole,
) -> None:
    """Видаляє запис підрядника зі staged-реєстру.
    Deletes contractor record from staged registry.
    """

    ensure_write_access(access_role, "delete_contractor_record")
    normalized_id = contractor_id.strip()
    if not normalized_id:
        raise ValueError("Не вибрано підрядника для видалення.")

    workspace = load_contractor_workspace(database_path)
    remaining_records = tuple(record for record in workspace.records if record.contractor_id != normalized_id)
    if len(remaining_records) == len(workspace.records):
        raise ValueError("Запис підрядника не знайдено.")

    connection = create_database_connection(database_path)
    try:
        upsert_app_setting(connection, _CONTRACTOR_REGISTRY_SETTING_KEY, serialize_contractor_records(remaining_records))
        insert_audit_log(
            connection,
            event_type="contractor.deleted",
            module_name="contractors",
            event_level="info",
            actor_name="inspector",
            entity_name=normalized_id,
            result_status="success",
            description_text=f"Contractor record deleted: contractor_id={normalized_id}.",
        )
        connection.commit()
    finally:
        connection.close()

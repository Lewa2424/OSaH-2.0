from pathlib import Path

from osah.application.services.ensure_port_passport_allows_changes import ensure_port_passport_allows_changes
from osah.application.services.security.ensure_write_access import ensure_write_access
from osah.domain.entities.access_role import AccessRole
from osah.domain.entities.port_passport_status import PortPassportStatus
from osah.infrastructure.database.commands.insert_audit_log import insert_audit_log
from osah.infrastructure.database.create_database_connection import create_database_connection


def archive_port_site_passport(
    database_path: Path,
    passport_id: int,
    *,
    access_role: AccessRole,
) -> None:
    """Архівує паспорт ділянки ПОРТ-Р.
    Archives a PORT-R site passport.
    """

    ensure_write_access(access_role, "archive_port_site_passport")
    connection = create_database_connection(database_path)
    try:
        ensure_port_passport_allows_changes(connection, passport_id)
        connection.execute(
            """
            UPDATE port_site_passports
            SET
                status = ?,
                archived_at = CURRENT_TIMESTAMP,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?;
            """,
            (PortPassportStatus.ARCHIVED.value, passport_id),
        )
        insert_audit_log(
            connection,
            event_type="port_r.passport.archived",
            module_name="port_r",
            event_level="info",
            actor_name="system",
            entity_name=f"port_site_passport:{passport_id}",
            result_status="success",
            description_text=f"status={PortPassportStatus.ARCHIVED.value}",
        )
        connection.commit()
    finally:
        connection.close()

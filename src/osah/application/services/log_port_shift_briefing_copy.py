from pathlib import Path

from osah.application.services.security.ensure_write_access import ensure_write_access
from osah.domain.entities.access_role import AccessRole
from osah.infrastructure.database.commands.insert_audit_log import insert_audit_log
from osah.infrastructure.database.create_database_connection import create_database_connection


# ###### АУДИТ КОПІЇ ОПЕРАТИВНОГО ЛИСТА / SHIFT BRIEFING COPY AUDIT ######
def log_port_shift_briefing_copy(
    database_path: Path,
    passport_id: int,
    source_path: Path,
    destination_path: Path,
    *,
    actor_name: str,
    access_role: AccessRole,
) -> None:
    """Записує аудит-подію копіювання .docx оперативного листа в обране користувачем місце.
    Logs an audit event for copying the shift briefing .docx to a user-chosen location.
    """

    ensure_write_access(access_role, "log_port_shift_briefing_copy")
    connection = create_database_connection(database_path)
    try:
        insert_audit_log(
            connection,
            event_type="port_r.shift_briefing.copied",
            module_name="port_r",
            event_level="info",
            actor_name=actor_name,
            entity_name=f"port_site_passport:{passport_id}",
            result_status="success",
            description_text=f"source={source_path};destination={destination_path}",
        )
        connection.commit()
    finally:
        connection.close()

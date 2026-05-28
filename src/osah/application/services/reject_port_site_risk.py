from pathlib import Path

from osah.application.services.ensure_port_passport_allows_changes import ensure_risk_passport_allows_changes
from osah.application.services.security.ensure_write_access import ensure_write_access
from osah.domain.entities.access_role import AccessRole
from osah.domain.entities.port_passport_risk_status import PortPassportRiskStatus
from osah.infrastructure.database.commands.insert_audit_log import insert_audit_log
from osah.infrastructure.database.create_database_connection import create_database_connection


# ###### ВІДХИЛЕННЯ РИЗИКУ ПАСПОРТА ПОРТ-Р / REJECT PORT-R PASSPORT RISK ######
def reject_port_site_risk(
    database_path: Path,
    risk_id: int,
    *,
    inspector_comment: str = "",
    access_role: AccessRole,
) -> None:
    """Встановлює статус «відхилений» для запису ризику.
    Sets status to rejected for a risk record.
    """

    ensure_write_access(access_role, "reject_port_site_risk")
    connection = create_database_connection(database_path)
    try:
        passport_id = ensure_risk_passport_allows_changes(connection, risk_id)
        connection.execute(
            """
            UPDATE port_site_risks
            SET
                status = ?,
                risk_level = '',
                inspector_comment = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?;
            """,
            (
                PortPassportRiskStatus.REJECTED.value,
                inspector_comment.strip(),
                risk_id,
            ),
        )
        insert_audit_log(
            connection,
            event_type="port_r.risk.rejected",
            module_name="port_r",
            event_level="info",
            actor_name="system",
            entity_name=f"port_site_risk:{risk_id}",
            result_status="success",
            description_text=f"passport_id={passport_id}",
        )
        connection.commit()
    finally:
        connection.close()

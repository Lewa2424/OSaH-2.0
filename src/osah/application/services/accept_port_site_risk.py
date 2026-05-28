from pathlib import Path

from osah.application.services.ensure_port_passport_allows_changes import ensure_risk_passport_allows_changes
from osah.application.services.security.ensure_write_access import ensure_write_access
from osah.domain.entities.access_role import AccessRole
from osah.domain.entities.port_passport_risk_status import PortPassportRiskStatus
from osah.domain.entities.port_risk_level import PortRiskLevel
from osah.infrastructure.database.commands.insert_audit_log import insert_audit_log
from osah.infrastructure.database.create_database_connection import create_database_connection


# ###### ПРИЙНЯТТЯ РИЗИКУ ПАСПОРТА ПОРТ-Р / ACCEPT PORT-R PASSPORT RISK ######
def accept_port_site_risk(
    database_path: Path,
    risk_id: int,
    risk_level: PortRiskLevel,
    *,
    assessment_reason: str = "",
    inspector_comment: str = "",
    access_role: AccessRole,
) -> None:
    """Встановлює статус «прийнятий» і рівень ризику для запису.
    Sets status to accepted and assigns the risk level to the record.
    """

    ensure_write_access(access_role, "accept_port_site_risk")
    connection = create_database_connection(database_path)
    try:
        passport_id = ensure_risk_passport_allows_changes(connection, risk_id)
        connection.execute(
            """
            UPDATE port_site_risks
            SET
                status = ?,
                risk_level = ?,
                assessment_reason = ?,
                inspector_comment = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?;
            """,
            (
                PortPassportRiskStatus.ACCEPTED.value,
                risk_level.value,
                assessment_reason.strip(),
                inspector_comment.strip(),
                risk_id,
            ),
        )
        insert_audit_log(
            connection,
            event_type="port_r.risk.accepted",
            module_name="port_r",
            event_level="info",
            actor_name="system",
            entity_name=f"port_site_risk:{risk_id}",
            result_status="success",
            description_text=f"passport_id={passport_id};risk_level={risk_level.value}",
        )
        connection.commit()
    finally:
        connection.close()

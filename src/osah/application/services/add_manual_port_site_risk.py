from pathlib import Path

from osah.application.services.ensure_port_passport_allows_changes import ensure_port_passport_allows_changes
from osah.application.services.security.ensure_write_access import ensure_write_access
from osah.domain.entities.access_role import AccessRole
from osah.domain.entities.port_passport_risk_status import PortPassportRiskStatus
from osah.infrastructure.database.commands.insert_audit_log import insert_audit_log
from osah.infrastructure.database.create_database_connection import create_database_connection


# ###### РУЧНЕ ДОДАВАННЯ РИЗИКУ В ПАСПОРТ ПОРТ-Р / ADD MANUAL PORT-R RISK ######
def add_manual_port_site_risk(
    database_path: Path,
    passport_id: int,
    *,
    risk_situation: str,
    hazard_source: str = "",
    occurrence_conditions: str = "",
    consequences: str = "",
    inspector_comment: str = "",
    access_role: AccessRole,
) -> int:
    """Додає ризик вручну без прив'язки до реєстру.
    Adds a risk manually without a registry link.
    """

    ensure_write_access(access_role, "add_manual_port_site_risk")
    if not risk_situation.strip():
        raise ValueError("Ризикова ситуація не може бути порожньою.")

    connection = create_database_connection(database_path)
    try:
        ensure_port_passport_allows_changes(connection, passport_id)
        next_sort_order = int(
            connection.execute(
                "SELECT COALESCE(MAX(sort_order), 0) + 1 FROM port_site_risks WHERE passport_id = ?;",
                (passport_id,),
            ).fetchone()[0]
        )
        cursor = connection.execute(
            """
            INSERT INTO port_site_risks (
                passport_id,
                registry_risk_id,
                risk_situation,
                hazard_source,
                occurrence_conditions,
                consequences,
                inspector_comment,
                status,
                addition_source,
                sort_order
            )
            VALUES (?, NULL, ?, ?, ?, ?, ?, ?, 'manual', ?);
            """,
            (
                passport_id,
                risk_situation.strip(),
                hazard_source.strip(),
                occurrence_conditions.strip(),
                consequences.strip(),
                inspector_comment.strip(),
                PortPassportRiskStatus.MANUAL.value,
                next_sort_order,
            ),
        )
        inserted_id = int(cursor.lastrowid)
        insert_audit_log(
            connection,
            event_type="port_r.risk.manual_added",
            module_name="port_r",
            event_level="info",
            actor_name="system",
            entity_name=f"port_site_passport:{passport_id}",
            result_status="success",
            description_text=f"port_site_risk_id={inserted_id}",
        )
        connection.commit()
        return inserted_id
    finally:
        connection.close()

from pathlib import Path

from osah.application.services.ensure_port_passport_allows_changes import ensure_port_passport_allows_changes
from osah.application.services.security.ensure_write_access import ensure_write_access
from osah.domain.entities.access_role import AccessRole
from osah.domain.entities.port_passport_risk_status import PortPassportRiskStatus
from osah.infrastructure.database.commands.insert_audit_log import insert_audit_log
from osah.infrastructure.database.create_database_connection import create_database_connection


# ###### ДОДАВАННЯ РЕКОМЕНДОВАНОГО РИЗИКУ В ПАСПОРТ / ADD SUGGESTED RISK TO PASSPORT ######
def add_port_risk_suggestion_to_passport(
    database_path: Path,
    passport_id: int,
    registry_risk_id: int,
    *,
    suggestion_reason: str,
    access_role: AccessRole,
) -> int:
    """Додає реєстровий ризик у паспорт зі статусом suggested.
    Adds a registry risk to passport with suggested status.
    """

    ensure_write_access(access_role, "add_port_risk_suggestion_to_passport")
    connection = create_database_connection(database_path)
    try:
        ensure_port_passport_allows_changes(connection, passport_id)
        existing_row = connection.execute(
            """
            SELECT id
            FROM port_site_risks
            WHERE passport_id = ? AND registry_risk_id = ?
            LIMIT 1;
            """,
            (passport_id, registry_risk_id),
        ).fetchone()
        if existing_row is not None:
            return int(existing_row["id"])

        registry_row = connection.execute(
            """
            SELECT risk_situation, hazard_source, occurrence_conditions, consequences
            FROM port_risk_registry
            WHERE id = ?;
            """,
            (registry_risk_id,),
        ).fetchone()
        if registry_row is None:
            raise ValueError("Реєстровий ризик не знайдено.")

        next_sort_order = int(
            connection.execute(
                """
                SELECT COALESCE(MAX(sort_order), 0) + 1
                FROM port_site_risks
                WHERE passport_id = ?;
                """,
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
                suggestion_reason,
                status,
                addition_source,
                sort_order
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """,
            (
                passport_id,
                registry_risk_id,
                str(registry_row["risk_situation"] or ""),
                str(registry_row["hazard_source"] or ""),
                str(registry_row["occurrence_conditions"] or ""),
                str(registry_row["consequences"] or ""),
                suggestion_reason.strip(),
                PortPassportRiskStatus.SUGGESTED.value,
                "registry",
                next_sort_order,
            ),
        )
        inserted_id = int(cursor.lastrowid)
        insert_audit_log(
            connection,
            event_type="port_r.risk_suggestion.added",
            module_name="port_r",
            event_level="info",
            actor_name="system",
            entity_name=f"port_site_passport:{passport_id}",
            result_status="success",
            description_text=f"registry_risk_id={registry_risk_id};port_site_risk_id={inserted_id}",
        )
        connection.commit()
        return inserted_id
    finally:
        connection.close()

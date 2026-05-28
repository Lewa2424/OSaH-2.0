from pathlib import Path

from osah.application.services.ensure_port_passport_allows_changes import ensure_port_passport_allows_changes
from osah.application.services.security.ensure_write_access import ensure_write_access
from osah.domain.entities.access_role import AccessRole
from osah.domain.entities.port_passport_status import PortPassportStatus
from osah.domain.entities.port_risk_profile import PortRiskProfile
from osah.infrastructure.database.commands.insert_audit_log import insert_audit_log
from osah.infrastructure.database.create_database_connection import create_database_connection


# ###### ЗАТВЕРДЖЕННЯ ПАСПОРТА ПОРТ-Р / APPROVE PORT-R PASSPORT ######
def approve_port_passport(
    database_path: Path,
    passport_id: int,
    *,
    actor_name: str,
    access_role: AccessRole,
) -> None:
    """Затверджує паспорт ділянки, переводячи його в статус «Діючий».
    Approves the site passport, changing its status to Active.
    """

    ensure_write_access(access_role, "approve_port_passport")
    connection = create_database_connection(database_path)
    try:
        ensure_port_passport_allows_changes(connection, passport_id)
        row = connection.execute(
            "SELECT calculated_profile FROM port_site_passports WHERE id = ?;",
            (passport_id,),
        ).fetchone()
        if row is None:
            raise ValueError("Паспорт не знайдено.")

        profile = str(row["calculated_profile"] or PortRiskProfile.NOT_CALCULATED.value)
        if profile == PortRiskProfile.NOT_CALCULATED.value:
            raise ValueError("Неможливо затвердити паспорт без розрахованого профілю ризику.")

        connection.execute(
            """
            UPDATE port_site_passports
            SET
                status = ?,
                approved_by = ?,
                approved_at = CURRENT_TIMESTAMP,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?;
            """,
            (PortPassportStatus.ACTIVE.value, actor_name, passport_id),
        )
        insert_audit_log(
            connection,
            event_type="port_r.passport.approved",
            module_name="port_r",
            event_level="info",
            actor_name=actor_name,
            entity_name=f"port_site_passport:{passport_id}",
            result_status="success",
            description_text=f"profile={profile};status={PortPassportStatus.ACTIVE.value}",
        )
        connection.commit()
    finally:
        connection.close()

from pathlib import Path

from osah.application.services.ensure_port_passport_allows_changes import ensure_port_passport_allows_changes
from osah.application.services.security.ensure_write_access import ensure_write_access
from osah.domain.entities.access_role import AccessRole
from osah.domain.entities.port_passport_risk_status import PortPassportRiskStatus
from osah.domain.entities.port_passport_status import PortPassportStatus
from osah.domain.entities.port_risk_level import PortRiskLevel
from osah.domain.entities.port_risk_profile import PortRiskProfile
from osah.infrastructure.database.commands.insert_audit_log import insert_audit_log
from osah.infrastructure.database.create_database_connection import create_database_connection

_LEVEL_PRIORITY: dict[str, int] = {
    PortRiskLevel.LOW.value: 1,
    PortRiskLevel.MEDIUM.value: 2,
    PortRiskLevel.HIGH.value: 3,
    PortRiskLevel.CRITICAL.value: 4,
}


# ###### РОЗРАХУНОК ПРОФІЛЮ РИЗИКУ ПАСПОРТА ПОРТ-Р / CALCULATE PORT-R PASSPORT RISK PROFILE ######
def calculate_port_passport_profile(
    database_path: Path,
    passport_id: int,
    *,
    actor_name: str,
    access_role: AccessRole,
) -> PortRiskProfile:
    """Розраховує профіль ризику паспорта на основі прийнятих ризиків.
    Calculates the passport risk profile based on accepted risks.
    """

    ensure_write_access(access_role, "calculate_port_passport_profile")
    connection = create_database_connection(database_path)
    try:
        ensure_port_passport_allows_changes(connection, passport_id)
        rows = connection.execute(
            """
            SELECT risk_level
            FROM port_site_risks
            WHERE passport_id = ?
              AND status IN (?, ?)
              AND risk_level != '';
            """,
            (
                passport_id,
                PortPassportRiskStatus.ACCEPTED.value,
                PortPassportRiskStatus.MANUAL.value,
            ),
        ).fetchall()

        profile = _derive_profile(rows)
        new_status = _derive_status(profile)

        connection.execute(
            """
            UPDATE port_site_passports
            SET
                calculated_profile = ?,
                final_profile = ?,
                status = ?,
                calculated_by = ?,
                calculated_at = CURRENT_TIMESTAMP,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?;
            """,
            (
                profile.value,
                profile.value,
                new_status.value,
                actor_name,
                passport_id,
            ),
        )
        insert_audit_log(
            connection,
            event_type="port_r.passport.profile_calculated",
            module_name="port_r",
            event_level="info",
            actor_name=actor_name,
            entity_name=f"port_site_passport:{passport_id}",
            result_status="success",
            description_text=f"profile={profile.value};status={new_status.value}",
        )
        connection.commit()
        return profile
    finally:
        connection.close()


def _derive_profile(rows: list) -> PortRiskProfile:
    max_priority = 0
    for row in rows:
        priority = _LEVEL_PRIORITY.get(str(row["risk_level"] or ""), 0)
        if priority > max_priority:
            max_priority = priority
    mapping = {
        1: PortRiskProfile.LOW,
        2: PortRiskProfile.MEDIUM,
        3: PortRiskProfile.HIGH,
        4: PortRiskProfile.CRITICAL,
    }
    return mapping.get(max_priority, PortRiskProfile.NOT_CALCULATED)


def _derive_status(profile: PortRiskProfile) -> PortPassportStatus:
    if profile in {PortRiskProfile.HIGH, PortRiskProfile.CRITICAL}:
        return PortPassportStatus.NEEDS_ACTIONS
    if profile == PortRiskProfile.NOT_CALCULATED:
        return PortPassportStatus.NEEDS_RISK_ASSESSMENT
    return PortPassportStatus.NEEDS_RISK_ASSESSMENT

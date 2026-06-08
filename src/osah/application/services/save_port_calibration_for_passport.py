from pathlib import Path

from osah.application.services.security.ensure_write_access import ensure_write_access
from osah.domain.entities.access_role import AccessRole
from osah.domain.entities.port_passport_calibration import PortPassportCalibration
from osah.infrastructure.database.commands.insert_audit_log import insert_audit_log
from osah.infrastructure.database.commands.save_port_calibration import save_port_calibration
from osah.infrastructure.database.create_database_connection import create_database_connection


# ###### ЗБЕРЕЖЕННЯ КАЛІБРУВАННЯ ПАСПОРТА ПОРТ-Р / SAVE PORT-R PASSPORT CALIBRATION ######
def save_port_calibration_for_passport(
    database_path: Path,
    calibration: PortPassportCalibration,
    *,
    actor_name: str,
    access_role: AccessRole,
) -> None:
    """Зберігає калібрування динамічного контуру паспорта ПОРТ-Р (пороги і бар'єри).
    Saves the PORT-R passport dynamic-circuit calibration (thresholds and barriers).
    """

    ensure_write_access(access_role, "save_port_calibration_for_passport")
    connection = create_database_connection(database_path)
    try:
        save_port_calibration(connection, calibration)
        insert_audit_log(
            connection,
            event_type="port_r.passport.calibration_saved",
            module_name="port_r",
            event_level="info",
            actor_name=actor_name,
            entity_name=f"port_site_passport:{calibration.passport_id}",
            result_status="success",
            description_text=(
                f"thresholds={len(calibration.thresholds)};"
                f"barriers={len(calibration.compensating_barriers)};"
                f"r_base={calibration.r_base}"
            ),
        )
        connection.commit()
    finally:
        connection.close()

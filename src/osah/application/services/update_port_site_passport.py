from pathlib import Path
from sqlite3 import IntegrityError

from osah.application.services.create_port_site_passport import (
    _normalize_passport_input,
    _validate_passport_input,
)
from osah.application.services.security.ensure_write_access import ensure_write_access
from osah.application.services.sync_port_passport_tags import sync_port_passport_tags
from osah.domain.entities.access_role import AccessRole
from osah.domain.entities.port_passport_status import PortPassportStatus
from osah.domain.entities.port_site_passport_input import PortSitePassportInput
from osah.infrastructure.database.commands.insert_audit_log import insert_audit_log
from osah.infrastructure.database.create_database_connection import create_database_connection


def update_port_site_passport(
    database_path: Path,
    passport_id: int,
    passport_input: PortSitePassportInput,
    *,
    access_role: AccessRole,
) -> None:
    """Оновлює паспорт ділянки та перераховує його теги.
    Updates a site passport and recalculates its tags.
    """

    ensure_write_access(access_role, "update_port_site_passport")
    normalized_input = _normalize_passport_input(passport_input)
    _validate_passport_input(normalized_input)

    connection = create_database_connection(database_path)
    try:
        status_row = connection.execute(
            "SELECT status FROM port_site_passports WHERE id = ?;",
            (passport_id,),
        ).fetchone()
        if status_row is None:
            raise ValueError("Паспорт не знайдено.")
        if str(status_row["status"] or "") == PortPassportStatus.ARCHIVED.value:
            raise ValueError("Архівний паспорт не можна редагувати.")

        try:
            connection.execute(
                """
                UPDATE port_site_passports
                SET
                    passport_code = ?,
                    site_name = ?,
                    site_type = ?,
                    site_location = ?,
                    site_description = ?,
                    work_kind = ?,
                    typical_operations = ?,
                    work_mode = ?,
                    typical_cargo = ?,
                    cargo_features = ?,
                    main_equipment = ?,
                    lifting_devices = ?,
                    has_railway_zone = ?,
                    has_auto_zone = ?,
                    has_crane_zone = ?,
                    crew_composition = ?,
                    responsible_person = ?,
                    has_contractors = ?,
                    contractors_note = ?,
                    zone_kind = ?,
                    has_night_works = ?,
                    weather_features = ?,
                    has_limited_visibility = ?,
                    has_height_work = ?,
                    has_water_edge_work = ?,
                    has_stack_edge_work = ?,
                    has_communication_barrier = ?,
                    communication_barrier = ?,
                    has_fencing_barrier = ?,
                    fencing_barrier = ?,
                    has_signalman = ?,
                    has_lighting_barrier = ?,
                    lighting_barrier = ?,
                    ppe_text = ?,
                    additional_barriers = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?;
                """,
                (
                    normalized_input.passport_code,
                    normalized_input.site_name,
                    normalized_input.site_type,
                    normalized_input.site_location,
                    normalized_input.site_description,
                    normalized_input.work_kind,
                    normalized_input.typical_operations,
                    normalized_input.work_mode,
                    normalized_input.typical_cargo,
                    normalized_input.cargo_features,
                    normalized_input.main_equipment,
                    normalized_input.lifting_devices,
                    int(normalized_input.has_railway_zone),
                    int(normalized_input.has_auto_zone),
                    int(normalized_input.has_crane_zone),
                    normalized_input.crew_composition,
                    normalized_input.responsible_person,
                    int(normalized_input.has_contractors),
                    normalized_input.contractors_note,
                    normalized_input.zone_kind,
                    int(normalized_input.has_night_works),
                    normalized_input.weather_features,
                    int(normalized_input.has_limited_visibility),
                    int(normalized_input.has_height_work),
                    int(normalized_input.has_water_edge_work),
                    int(normalized_input.has_stack_edge_work),
                    int(normalized_input.has_communication_barrier),
                    normalized_input.communication_barrier,
                    int(normalized_input.has_fencing_barrier),
                    normalized_input.fencing_barrier,
                    int(normalized_input.has_signalman),
                    int(normalized_input.has_lighting_barrier),
                    normalized_input.lighting_barrier,
                    normalized_input.ppe_text,
                    normalized_input.additional_barriers,
                    passport_id,
                ),
            )
        except IntegrityError as error:
            if "passport_code" in str(error).lower() or "unique" in str(error).lower():
                raise ValueError("Паспорт з таким кодом уже існує.") from error
            raise

        sync_port_passport_tags(connection, passport_id)
        insert_audit_log(
            connection,
            event_type="port_r.passport.updated",
            module_name="port_r",
            event_level="info",
            actor_name="system",
            entity_name=f"port_site_passport:{passport_id}",
            result_status="success",
            description_text=(
                f"passport_code={normalized_input.passport_code};"
                f"site_name={normalized_input.site_name};"
                f"site_type={normalized_input.site_type}"
            ),
        )
        connection.commit()
    finally:
        connection.close()

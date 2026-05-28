from pathlib import Path
from sqlite3 import IntegrityError

from osah.application.services.security.ensure_write_access import ensure_write_access
from osah.application.services.sync_port_passport_tags import sync_port_passport_tags
from osah.domain.entities.access_role import AccessRole
from osah.domain.entities.port_site_passport_input import PortSitePassportInput
from osah.infrastructure.database.commands.insert_audit_log import insert_audit_log
from osah.infrastructure.database.commands.insert_port_site_passport import insert_port_site_passport
from osah.infrastructure.database.create_database_connection import create_database_connection


# ###### СТВОРЕННЯ ПАСПОРТА ДІЛЯНКИ / CREATE PORT SITE PASSPORT ######
def create_port_site_passport(
    database_path: Path,
    passport_input: PortSitePassportInput,
    *,
    access_role: AccessRole,
) -> int:
    """Створює паспорт ділянки ПОРТ-Р зі статусом «Потребує оцінки».
    Creates a PORT-R site passport with the "needs assessment" status.
    """

    ensure_write_access(access_role, "create_port_site_passport")
    normalized_input = _normalize_passport_input(passport_input)
    _validate_passport_input(normalized_input)

    connection = create_database_connection(database_path)
    try:
        try:
            passport_id = insert_port_site_passport(connection, normalized_input)
        except IntegrityError as error:
            if "passport_code" in str(error).lower() or "unique" in str(error).lower():
                raise ValueError("Паспорт з таким кодом уже існує.") from error
            raise
        sync_port_passport_tags(connection, passport_id)
        insert_audit_log(
            connection,
            event_type="port_r.passport.created",
            module_name="port_r",
            event_level="info",
            actor_name="system",
            entity_name=f"port_site_passport:{normalized_input.passport_code}",
            result_status="success",
            description_text=(
                f"site_name={normalized_input.site_name};"
                f"site_type={normalized_input.site_type};"
                "status=needs_risk_assessment"
            ),
        )
        connection.commit()
        return passport_id
    finally:
        connection.close()


def _normalize_passport_input(passport_input: PortSitePassportInput) -> PortSitePassportInput:
    return PortSitePassportInput(
        passport_code=passport_input.passport_code.strip(),
        site_name=passport_input.site_name.strip(),
        site_type=passport_input.site_type.strip(),
        site_location=passport_input.site_location.strip(),
        site_description=passport_input.site_description.strip(),
        work_kind=passport_input.work_kind.strip(),
        typical_operations=passport_input.typical_operations.strip(),
        work_mode=passport_input.work_mode.strip(),
        typical_cargo=passport_input.typical_cargo.strip(),
        cargo_features=passport_input.cargo_features.strip(),
        main_equipment=passport_input.main_equipment.strip(),
        lifting_devices=passport_input.lifting_devices.strip(),
        has_railway_zone=passport_input.has_railway_zone,
        has_auto_zone=passport_input.has_auto_zone,
        has_crane_zone=passport_input.has_crane_zone,
        crew_composition=passport_input.crew_composition.strip(),
        responsible_person=passport_input.responsible_person.strip(),
        has_contractors=passport_input.has_contractors,
        contractors_note=passport_input.contractors_note.strip(),
        zone_kind=passport_input.zone_kind.strip(),
        has_night_works=passport_input.has_night_works,
        weather_features=passport_input.weather_features.strip(),
        has_limited_visibility=passport_input.has_limited_visibility,
        has_height_work=passport_input.has_height_work,
        has_water_edge_work=passport_input.has_water_edge_work,
        has_stack_edge_work=passport_input.has_stack_edge_work,
        has_communication_barrier=passport_input.has_communication_barrier,
        communication_barrier=passport_input.communication_barrier.strip(),
        has_fencing_barrier=passport_input.has_fencing_barrier,
        fencing_barrier=passport_input.fencing_barrier.strip(),
        has_signalman=passport_input.has_signalman,
        has_lighting_barrier=passport_input.has_lighting_barrier,
        lighting_barrier=passport_input.lighting_barrier.strip(),
        ppe_text=passport_input.ppe_text.strip(),
        additional_barriers=passport_input.additional_barriers.strip(),
    )


def _validate_passport_input(passport_input: PortSitePassportInput) -> None:
    if not passport_input.passport_code:
        raise ValueError("Потрібно вказати код / номер паспорта.")
    if not passport_input.site_name:
        raise ValueError("Потрібно вказати назву ділянки.")

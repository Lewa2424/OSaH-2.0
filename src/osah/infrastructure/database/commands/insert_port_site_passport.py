from sqlite3 import Connection

from osah.domain.entities.port_passport_status import PortPassportStatus
from osah.domain.entities.port_risk_profile import PortRiskProfile
from osah.domain.entities.port_site_passport_input import PortSitePassportInput


# ###### СТВОРЕННЯ ПАСПОРТА ПОРТ-Р / INSERT PORT-R PASSPORT ######
def insert_port_site_passport(
    connection: Connection,
    passport_input: PortSitePassportInput,
) -> int:
    """Зберігає новий паспорт виробничої ділянки ПОРТ-Р.
    Persists a new PORT-R production site passport.
    """

    cursor = connection.execute(
        """
        INSERT INTO port_site_passports (
            passport_code,
            site_name,
            site_type,
            site_location,
            site_description,
            work_kind,
            typical_operations,
            work_mode,
            typical_cargo,
            cargo_features,
            main_equipment,
            lifting_devices,
            has_railway_zone,
            has_auto_zone,
            has_crane_zone,
            crew_composition,
            responsible_person,
            has_contractors,
            contractors_note,
            zone_kind,
            has_night_works,
            weather_features,
            has_limited_visibility,
            has_height_work,
            has_water_edge_work,
            has_stack_edge_work,
            has_communication_barrier,
            communication_barrier,
            has_fencing_barrier,
            fencing_barrier,
            has_signalman,
            has_lighting_barrier,
            lighting_barrier,
            ppe_text,
            additional_barriers,
            status,
            calculated_profile,
            final_profile
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """,
        (
            passport_input.passport_code,
            passport_input.site_name,
            passport_input.site_type,
            passport_input.site_location,
            passport_input.site_description,
            passport_input.work_kind,
            passport_input.typical_operations,
            passport_input.work_mode,
            passport_input.typical_cargo,
            passport_input.cargo_features,
            passport_input.main_equipment,
            passport_input.lifting_devices,
            int(passport_input.has_railway_zone),
            int(passport_input.has_auto_zone),
            int(passport_input.has_crane_zone),
            passport_input.crew_composition,
            passport_input.responsible_person,
            int(passport_input.has_contractors),
            passport_input.contractors_note,
            passport_input.zone_kind,
            int(passport_input.has_night_works),
            passport_input.weather_features,
            int(passport_input.has_limited_visibility),
            int(passport_input.has_height_work),
            int(passport_input.has_water_edge_work),
            int(passport_input.has_stack_edge_work),
            int(passport_input.has_communication_barrier),
            passport_input.communication_barrier,
            int(passport_input.has_fencing_barrier),
            passport_input.fencing_barrier,
            int(passport_input.has_signalman),
            int(passport_input.has_lighting_barrier),
            passport_input.lighting_barrier,
            passport_input.ppe_text,
            passport_input.additional_barriers,
            PortPassportStatus.NEEDS_RISK_ASSESSMENT.value,
            PortRiskProfile.NOT_CALCULATED.value,
            PortRiskProfile.NOT_CALCULATED.value,
        ),
    )
    return int(cursor.lastrowid)

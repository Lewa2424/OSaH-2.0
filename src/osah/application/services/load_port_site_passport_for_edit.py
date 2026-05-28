from pathlib import Path

from osah.domain.entities.port_site_passport_input import PortSitePassportInput
from osah.infrastructure.database.create_database_connection import create_database_connection


def load_port_site_passport_for_edit(
    database_path: Path,
    passport_id: int,
) -> PortSitePassportInput:
    """Завантажує повні дані паспорта для редагування.
    Loads complete passport data for editing.
    """

    connection = create_database_connection(database_path)
    try:
        row = connection.execute(
            """
            SELECT
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
                additional_barriers
            FROM port_site_passports
            WHERE id = ?;
            """,
            (passport_id,),
        ).fetchone()
        if row is None:
            raise ValueError("Паспорт не знайдено.")

        return PortSitePassportInput(
            passport_code=str(row["passport_code"] or ""),
            site_name=str(row["site_name"] or ""),
            site_type=str(row["site_type"] or ""),
            site_location=str(row["site_location"] or ""),
            site_description=str(row["site_description"] or ""),
            work_kind=str(row["work_kind"] or ""),
            typical_operations=str(row["typical_operations"] or ""),
            work_mode=str(row["work_mode"] or ""),
            typical_cargo=str(row["typical_cargo"] or ""),
            cargo_features=str(row["cargo_features"] or ""),
            main_equipment=str(row["main_equipment"] or ""),
            lifting_devices=str(row["lifting_devices"] or ""),
            has_railway_zone=bool(row["has_railway_zone"]),
            has_auto_zone=bool(row["has_auto_zone"]),
            has_crane_zone=bool(row["has_crane_zone"]),
            crew_composition=str(row["crew_composition"] or ""),
            responsible_person=str(row["responsible_person"] or ""),
            has_contractors=bool(row["has_contractors"]),
            contractors_note=str(row["contractors_note"] or ""),
            zone_kind=str(row["zone_kind"] or ""),
            has_night_works=bool(row["has_night_works"]),
            weather_features=str(row["weather_features"] or ""),
            has_limited_visibility=bool(row["has_limited_visibility"]),
            has_height_work=bool(row["has_height_work"]),
            has_water_edge_work=bool(row["has_water_edge_work"]),
            has_stack_edge_work=bool(row["has_stack_edge_work"]),
            has_communication_barrier=bool(row["has_communication_barrier"]),
            communication_barrier=str(row["communication_barrier"] or ""),
            has_fencing_barrier=bool(row["has_fencing_barrier"]),
            fencing_barrier=str(row["fencing_barrier"] or ""),
            has_signalman=bool(row["has_signalman"]),
            has_lighting_barrier=bool(row["has_lighting_barrier"]),
            lighting_barrier=str(row["lighting_barrier"] or ""),
            ppe_text=str(row["ppe_text"] or ""),
            additional_barriers=str(row["additional_barriers"] or ""),
        )
    finally:
        connection.close()

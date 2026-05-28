from sqlite3 import Connection

from osah.domain.services.extract_port_risk_tags_from_text import extract_port_risk_tags_from_text


# ###### СИНХРОНІЗАЦІЯ ТЕГІВ ПАСПОРТА ПОРТ-Р / SYNC PORT-R PASSPORT TAGS ######
def sync_port_passport_tags(connection: Connection, passport_id: int) -> int:
    """Перераховує та зберігає теги паспорта ділянки.
    Recalculates and persists site passport tags.

    Повертає кількість збережених тегів.
    Returns count of persisted tags.
    """

    row = connection.execute(
        """
        SELECT
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
            crew_composition,
            responsible_person,
            contractors_note,
            zone_kind,
            weather_features,
            communication_barrier,
            fencing_barrier,
            lighting_barrier,
            ppe_text,
            additional_barriers,
            has_railway_zone,
            has_auto_zone,
            has_crane_zone,
            has_night_works,
            has_limited_visibility,
            has_height_work,
            has_water_edge_work,
            has_stack_edge_work,
            has_communication_barrier,
            has_fencing_barrier,
            has_signalman,
            has_lighting_barrier
        FROM port_site_passports
        WHERE id = ?;
        """,
        (passport_id,),
    ).fetchone()
    if row is None:
        return 0

    text_parts = [
        str(row["site_name"] or ""),
        str(row["site_type"] or ""),
        str(row["site_location"] or ""),
        str(row["site_description"] or ""),
        str(row["work_kind"] or ""),
        str(row["typical_operations"] or ""),
        str(row["work_mode"] or ""),
        str(row["typical_cargo"] or ""),
        str(row["cargo_features"] or ""),
        str(row["main_equipment"] or ""),
        str(row["lifting_devices"] or ""),
        str(row["crew_composition"] or ""),
        str(row["responsible_person"] or ""),
        str(row["contractors_note"] or ""),
        str(row["zone_kind"] or ""),
        str(row["weather_features"] or ""),
        str(row["communication_barrier"] or ""),
        str(row["fencing_barrier"] or ""),
        str(row["lighting_barrier"] or ""),
        str(row["ppe_text"] or ""),
        str(row["additional_barriers"] or ""),
    ]
    text_parts.extend(_build_boolean_phrases(row))
    extracted_tags = extract_port_risk_tags_from_text(*text_parts)
    tag_codes = tuple(extracted_tags.keys())

    connection.execute("DELETE FROM port_passport_tags WHERE passport_id = ?;", (passport_id,))
    if not tag_codes:
        return 0

    placeholders = ", ".join("?" for _ in tag_codes)
    tag_rows = connection.execute(
        f"SELECT id FROM port_risk_tags WHERE tag_code IN ({placeholders});",
        tag_codes,
    ).fetchall()
    if not tag_rows:
        return 0

    links = [(passport_id, int(tag_row["id"])) for tag_row in tag_rows]
    connection.executemany(
        """
        INSERT OR IGNORE INTO port_passport_tags (passport_id, tag_id)
        VALUES (?, ?);
        """,
        links,
    )
    return len(links)


def _build_boolean_phrases(row: object) -> list[str]:
    phrases: list[str] = []
    if int(row["has_railway_zone"] or 0):
        phrases.append("залізнична зона")
    if int(row["has_auto_zone"] or 0):
        phrases.append("зона автотранспорту")
    if int(row["has_crane_zone"] or 0):
        phrases.append("кранова зона")
    if int(row["has_night_works"] or 0):
        phrases.append("нічні роботи")
    if int(row["has_limited_visibility"] or 0):
        phrases.append("обмежена видимість")
    if int(row["has_height_work"] or 0):
        phrases.append("роботи на висоті")
    if int(row["has_water_edge_work"] or 0):
        phrases.append("роботи біля води")
    if int(row["has_stack_edge_work"] or 0):
        phrases.append("роботи біля краю штабеля")
    if int(row["has_communication_barrier"] or 0):
        phrases.append("бар'єр комунікації")
    if int(row["has_fencing_barrier"] or 0):
        phrases.append("бар'єр огородження")
    if int(row["has_signalman"] or 0):
        phrases.append("наявний сигнальник")
    if int(row["has_lighting_barrier"] or 0):
        phrases.append("бар'єр освітлення")
    return phrases

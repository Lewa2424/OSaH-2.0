from sqlite3 import Connection

from osah.domain.services.extract_port_risk_tags_from_text import extract_port_risk_tags_from_text


# ###### ЗАСІВ ТЕГІВ РЕЄСТРУ РИЗИКІВ / SEED PORT-R RISK REGISTRY TAGS ######
def seed_port_risk_registry_tags(connection: Connection, *, force: bool = False) -> int:
    """Автоматично створює теги для кожного ризику реєстру (один раз).
    Automatically creates tags for each registry risk (once only).

    Повертає кількість зв'язок ризик-тег.
    Returns the number of risk-tag links created.
    """

    if not force and _tags_are_populated(connection):
        return 0

    risk_rows = connection.execute(
        """
        SELECT
            id,
            level_2,
            level_3,
            risk_situation,
            hazard_source,
            occurrence_conditions
        FROM port_risk_registry
        ORDER BY id ASC;
        """
    ).fetchall()
    if not risk_rows:
        return 0

    if force:
        connection.execute("DELETE FROM port_risk_registry_tags;")
        connection.execute(
            """
            DELETE FROM port_risk_tags
            WHERE id NOT IN (SELECT tag_id FROM port_passport_tags);
            """
        )

    tag_id_by_code: dict[str, int] = _load_existing_tag_ids(connection)
    links: list[tuple[int, int]] = []

    for row in risk_rows:
        risk_id = int(row["id"])
        tags = extract_port_risk_tags_from_text(
            str(row["level_2"] or ""),
            str(row["level_3"] or ""),
            str(row["risk_situation"] or ""),
            str(row["hazard_source"] or ""),
            str(row["occurrence_conditions"] or ""),
        )
        for stem, label in tags.items():
            tag_id = _get_or_create_tag(connection, stem, label, tag_id_by_code)
            links.append((risk_id, tag_id))

    connection.executemany(
        """
        INSERT OR IGNORE INTO port_risk_registry_tags (registry_risk_id, tag_id)
        VALUES (?, ?);
        """,
        links,
    )
    return len(links)


def _tags_are_populated(connection: Connection) -> bool:
    row = connection.execute("SELECT 1 FROM port_risk_registry_tags LIMIT 1;").fetchone()
    return row is not None


def _load_existing_tag_ids(connection: Connection) -> dict[str, int]:
    rows = connection.execute("SELECT id, tag_code FROM port_risk_tags;").fetchall()
    return {str(row["tag_code"]): int(row["id"]) for row in rows}


def _get_or_create_tag(
    connection: Connection,
    tag_code: str,
    label_uk: str,
    tag_id_by_code: dict[str, int],
) -> int:
    existing_id = tag_id_by_code.get(tag_code)
    if existing_id is not None:
        return existing_id

    connection.execute(
        """
        INSERT OR IGNORE INTO port_risk_tags (tag_code, label_uk)
        VALUES (?, ?);
        """,
        (tag_code, label_uk),
    )
    row = connection.execute(
        "SELECT id FROM port_risk_tags WHERE tag_code = ?;",
        (tag_code,),
    ).fetchone()
    if row is None:
        raise RuntimeError(f"Не вдалося створити тег: {tag_code}")

    tag_id = int(row["id"])
    tag_id_by_code[tag_code] = tag_id
    return tag_id

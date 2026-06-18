from sqlite3 import Connection


def list_ai_pattern_memory_entries(connection: Connection) -> tuple[tuple[str, str, str], ...]:
    """Повертає всі записи AI-пам'яті синонімів.
    Returns all AI pattern memory synonym entries.
    """

    rows = connection.execute(
        """
        SELECT source_phrase, mapping_type, target_value
        FROM ai_pattern_memory
        ORDER BY hit_count DESC, source_phrase ASC;
        """
    ).fetchall()
    return tuple((str(row["source_phrase"]), str(row["mapping_type"]), str(row["target_value"])) for row in rows)

from sqlite3 import Connection


def upsert_ai_pattern_memory_entry(
    connection: Connection,
    *,
    source_phrase: str,
    mapping_type: str,
    target_value: str,
) -> None:
    """Зберігає або оновлює синонім AI-пам'яті.
    Saves or updates an AI pattern memory synonym.
    """

    connection.execute(
        """
        INSERT INTO ai_pattern_memory (
            source_phrase,
            mapping_type,
            target_value,
            hit_count,
            last_confirmed_at
        )
        VALUES (?, ?, ?, 1, CURRENT_TIMESTAMP)
        ON CONFLICT(source_phrase, mapping_type)
        DO UPDATE SET
            target_value = excluded.target_value,
            hit_count = ai_pattern_memory.hit_count + 1,
            last_confirmed_at = CURRENT_TIMESTAMP;
        """,
        (source_phrase.strip().lower(), mapping_type.strip(), target_value.strip()),
    )

from pathlib import Path

from osah.infrastructure.database.commands.upsert_ai_pattern_memory_entry import upsert_ai_pattern_memory_entry
from osah.infrastructure.database.create_database_connection import create_database_connection


def save_ai_pattern_memory_entry(
    database_path: Path,
    *,
    source_phrase: str,
    mapping_type: str,
    target_value: str,
) -> None:
    """Зберігає підтверджений синонім AI-пам'яті.
    Saves a confirmed AI pattern memory synonym.
    """

    connection = create_database_connection(database_path)
    try:
        upsert_ai_pattern_memory_entry(
            connection,
            source_phrase=source_phrase,
            mapping_type=mapping_type,
            target_value=target_value,
        )
        connection.commit()
    finally:
        connection.close()

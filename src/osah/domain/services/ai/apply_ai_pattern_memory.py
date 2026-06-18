from pathlib import Path

from osah.infrastructure.database.create_database_connection import create_database_connection
from osah.infrastructure.database.queries.list_ai_pattern_memory_entries import list_ai_pattern_memory_entries


def apply_ai_pattern_memory(database_path: Path, command_text: str) -> str:
    """Підставляє підтверджені синоніми перед LLM-розбором.
    Applies confirmed synonym patterns before LLM parsing.
    """

    normalized_command = command_text.strip()
    if not normalized_command:
        return normalized_command

    connection = create_database_connection(database_path)
    try:
        entries = list_ai_pattern_memory_entries(connection)
    finally:
        connection.close()

    resolved_command = normalized_command
    for source_phrase, _mapping_type, target_value in entries:
        if not source_phrase:
            continue
        resolved_command = _replace_case_insensitive(resolved_command, source_phrase, target_value)
    return resolved_command


def _replace_case_insensitive(text: str, source_phrase: str, target_value: str) -> str:
    lower_text = text.lower()
    lower_source = source_phrase.lower()
    start_index = lower_text.find(lower_source)
    if start_index < 0:
        return text
    end_index = start_index + len(source_phrase)
    return f"{text[:start_index]}{target_value}{text[end_index:]}"

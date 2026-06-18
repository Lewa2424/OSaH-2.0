import json
from pathlib import Path

from osah.infrastructure.database.commands.insert_ai_action_journal_entry import insert_ai_action_journal_entry
from osah.infrastructure.database.create_database_connection import create_database_connection


def log_ai_action(
    database_path: Path,
    *,
    raw_command: str,
    intent: str,
    draft_payload: dict[str, object] | None,
    was_confirmed: bool,
    result_status: str,
    result_message: str,
    actor_role: str,
) -> None:
    """Записує AI-дію в журнал.
    Writes an AI action entry into the journal.
    """

    draft_json = json.dumps(draft_payload or {}, ensure_ascii=False)
    connection = create_database_connection(database_path)
    try:
        insert_ai_action_journal_entry(
            connection,
            raw_command=raw_command,
            intent=intent,
            draft_json=draft_json,
            was_confirmed=was_confirmed,
            result_status=result_status,
            result_message=result_message,
            actor_role=actor_role,
        )
        connection.commit()
    finally:
        connection.close()

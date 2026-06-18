from sqlite3 import Connection


def insert_ai_action_journal_entry(
    connection: Connection,
    *,
    raw_command: str,
    intent: str,
    draft_json: str,
    was_confirmed: bool,
    result_status: str,
    result_message: str,
    actor_role: str,
) -> None:
    """Зберігає запис AI-журналу.
    Persists an AI action journal entry.
    """

    connection.execute(
        """
        INSERT INTO ai_action_journal (
            raw_command,
            intent,
            draft_json,
            was_confirmed,
            result_status,
            result_message,
            actor_role
        )
        VALUES (?, ?, ?, ?, ?, ?, ?);
        """,
        (
            raw_command,
            intent,
            draft_json,
            1 if was_confirmed else 0,
            result_status,
            result_message,
            actor_role,
        ),
    )

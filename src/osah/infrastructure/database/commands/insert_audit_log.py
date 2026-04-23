from sqlite3 import Connection

from osah.infrastructure.logging.sanitize_log_message import sanitize_log_message


# ###### ДОДАВАННЯ AUDIT-ЗАПИСУ / AUDIT RECORD INSERT ######
def insert_audit_log(
    connection: Connection,
    event_type: str,
    module_name: str,
    event_level: str,
    actor_name: str,
    entity_name: str,
    result_status: str,
    description_text: str,
) -> None:
    """Зберігає audit-подію в локальній базі даних після маскування чутливого опису.
    Saves an audit event into the local database after redacting sensitive description text.
    """

    connection.execute(
        """
        INSERT INTO audit_log (
            event_type,
            module_name,
            event_level,
            actor_name,
            entity_name,
            result_status,
            description_text
        )
        VALUES (?, ?, ?, ?, ?, ?, ?);
        """,
        (
            event_type,
            module_name,
            event_level,
            actor_name,
            entity_name,
            result_status,
            sanitize_log_message(description_text),
        ),
    )

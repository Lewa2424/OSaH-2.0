from sqlite3 import Connection


# ###### ДОДАВАННЯ AUDIT-ЗАПИСУ / ДОБАВЛЕНИЕ AUDIT-ЗАПИСИ ######
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
    """Зберігає audit-подію в локальній базі даних.
    Сохраняет audit-событие в локальной базе данных.
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
            description_text,
        ),
    )

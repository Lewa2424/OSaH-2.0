from sqlite3 import Connection


# ###### ЗАКРИТТЯ НАРЯДУ-ДОПУСКУ / ЗАКРЫТИЕ НАРЯДА-ДОПУСКА ######
def close_work_permit_record_row(connection: Connection, record_id: int, closed_at: str) -> None:
    """Позначає наряд-допуск як закритий вручну.
    Помечает наряд-допуск как закрытый вручную.
    """

    connection.execute(
        """
        UPDATE work_permits
        SET closed_at = ?
        WHERE id = ?;
        """,
        (closed_at, record_id),
    )

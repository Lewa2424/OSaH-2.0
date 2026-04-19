from sqlite3 import Connection


# ###### ПОЗНАЧЕННЯ ПАРТІЇ ІМПОРТУ ЯК ЗАСТОСОВАНОЇ / ПОМЕТКА ПАРТИИ ИМПОРТА КАК ПРИМЕНЁННОЙ ######
def mark_import_batch_as_applied(connection: Connection, batch_id: int, applied_at: str) -> None:
    """Позначає партію імпорту як застосовану.
    Помечает партию импорта как применённую.
    """

    connection.execute(
        """
        UPDATE import_batches
        SET applied_at = ?
        WHERE id = ?;
        """,
        (applied_at, batch_id),
    )

from sqlite3 import Connection


# ###### ВИДАЛЕННЯ ДЖЕРЕЛА НОВИН / УДАЛЕНИЕ ИСТОЧНИКА НОВОСТЕЙ ######
def delete_news_source_row(connection: Connection, source_id: int) -> None:
    """Видаляє запис довіреного джерела новин з локальної бази.
    Удаляет запись доверенного источника новостей из локальной базы.
    """

    connection.execute("DELETE FROM news_sources WHERE id = ?;", (source_id,))

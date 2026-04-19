from sqlite3 import Connection


# ###### ПІДРАХУНОК НЕПРОЧИТАНИХ НОВИННИХ МАТЕРІАЛІВ / ПОДСЧЁТ НЕПРОЧИТАННЫХ НОВОСТНЫХ МАТЕРИАЛОВ ######
def count_unread_news_items(connection: Connection) -> int:
    """Повертає кількість непрочитаних кешованих матеріалів.
    Возвращает количество непрочитанных кэшированных материалов.
    """

    row = connection.execute(
        """
        SELECT COUNT(*) AS unread_total
        FROM news_items
        WHERE read_state = 'new';
        """
    ).fetchone()
    return int(row["unread_total"])

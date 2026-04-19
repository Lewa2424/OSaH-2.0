from sqlite3 import Connection


# ###### ПОЗНАЧЕННЯ НОВИННОГО МАТЕРІАЛУ ЯК ПРОЧИТАНОГО / ПОМЕТКА НОВОСТНОГО МАТЕРИАЛА КАК ПРОЧИТАННОГО ######
def mark_news_item_as_read_row(connection: Connection, item_id: int) -> None:
    """Оновлює стан новинного матеріалу до прочитаного.
    Обновляет состояние новостного материала до прочитанного.
    """

    connection.execute(
        """
        UPDATE news_items
        SET read_state = 'read'
        WHERE id = ?;
        """,
        (item_id,),
    )

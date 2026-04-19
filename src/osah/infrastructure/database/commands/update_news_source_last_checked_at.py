from sqlite3 import Connection


# ###### ОНОВЛЕННЯ ЧАСУ ОСТАННЬОЇ ПЕРЕВІРКИ ДЖЕРЕЛА / ОБНОВЛЕНИЕ ВРЕМЕНИ ПОСЛЕДНЕЙ ПРОВЕРКИ ИСТОЧНИКА ######
def update_news_source_last_checked_at(connection: Connection, source_id: int, checked_at_text: str) -> None:
    """Фіксує час останнього refresh для джерела.
    Фиксирует время последнего refresh для источника.
    """

    connection.execute(
        """
        UPDATE news_sources
        SET last_checked_at = ?
        WHERE id = ?;
        """,
        (checked_at_text, source_id),
    )

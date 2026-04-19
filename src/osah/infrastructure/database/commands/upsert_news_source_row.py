from sqlite3 import Connection


# ###### ДОДАВАННЯ АБО ОНОВЛЕННЯ ДЖЕРЕЛА НОВИН / ДОБАВЛЕНИЕ ИЛИ ОБНОВЛЕНИЕ ИСТОЧНИКА НОВОСТЕЙ ######
def upsert_news_source_row(
    connection: Connection,
    source_name: str,
    source_url: str,
    source_kind: str,
    is_active: bool,
    is_trusted: bool,
) -> int:
    """Зберігає джерело новин або НПА за URL і повертає його ідентифікатор.
    Сохраняет источник новостей или НПА по URL и возвращает его идентификатор.
    """

    connection.execute(
        """
        INSERT INTO news_sources (
            source_name,
            source_url,
            source_kind,
            is_active,
            is_trusted
        )
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(source_url)
        DO UPDATE SET
            source_name = excluded.source_name,
            source_kind = excluded.source_kind,
            is_active = excluded.is_active,
            is_trusted = excluded.is_trusted;
        """,
        (
            source_name,
            source_url,
            source_kind,
            1 if is_active else 0,
            1 if is_trusted else 0,
        ),
    )
    row = connection.execute(
        """
        SELECT id
        FROM news_sources
        WHERE source_url = ?;
        """,
        (source_url,),
    ).fetchone()
    return int(row["id"])

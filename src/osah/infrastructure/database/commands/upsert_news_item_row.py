from sqlite3 import Connection


# ###### ДОДАВАННЯ АБО ОНОВЛЕННЯ НОВИННОГО МАТЕРІАЛУ / ДОБАВЛЕНИЕ ИЛИ ОБНОВЛЕНИЕ НОВОСТНОГО МАТЕРИАЛА ######
def upsert_news_item_row(
    connection: Connection,
    source_id: int,
    title_text: str,
    link_url: str,
    published_at_text: str,
    source_kind: str,
    fingerprint_value: str,
) -> None:
    """Зберігає кешований матеріал і не скидає стан прочитання при повторному refresh.
    Сохраняет кэшированный материал и не сбрасывает состояние прочтения при повторном refresh.
    """

    connection.execute(
        """
        INSERT INTO news_items (
            source_id,
            title_text,
            link_url,
            published_at_text,
            source_kind,
            fingerprint_value,
            read_state
        )
        VALUES (?, ?, ?, ?, ?, ?, 'new')
        ON CONFLICT(source_id, fingerprint_value)
        DO UPDATE SET
            title_text = excluded.title_text,
            link_url = excluded.link_url,
            published_at_text = excluded.published_at_text,
            source_kind = excluded.source_kind;
        """,
        (
            source_id,
            title_text,
            link_url,
            published_at_text,
            source_kind,
            fingerprint_value,
        ),
    )

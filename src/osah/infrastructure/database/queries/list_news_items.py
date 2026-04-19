from sqlite3 import Connection

from osah.domain.entities.news_item import NewsItem
from osah.domain.entities.news_item_read_state import NewsItemReadState
from osah.domain.entities.news_source_kind import NewsSourceKind


# ###### ЧИТАННЯ СПИСКУ НОВИННИХ МАТЕРІАЛІВ / ЧТЕНИЕ СПИСКА НОВОСТНЫХ МАТЕРИАЛОВ ######
def list_news_items(connection: Connection, unread_only: bool = False) -> tuple[NewsItem, ...]:
    """Повертає кешовані матеріали зі стабільним сортуванням від нових до старих.
    Возвращает кэшированные материалы со стабильной сортировкой от новых к старым.
    """

    unread_filter_sql = "WHERE news_items.read_state = 'new'" if unread_only else ""
    rows = connection.execute(
        f"""
        SELECT
            news_items.id,
            news_items.source_id,
            news_sources.source_name,
            news_items.source_kind,
            news_items.title_text,
            news_items.link_url,
            news_items.published_at_text,
            news_items.read_state
        FROM news_items
        INNER JOIN news_sources
            ON news_sources.id = news_items.source_id
        {unread_filter_sql}
        ORDER BY news_items.published_at_text DESC, news_items.id DESC;
        """
    ).fetchall()
    return tuple(
        NewsItem(
            item_id=int(row["id"]),
            source_id=int(row["source_id"]),
            source_name=row["source_name"],
            source_kind=NewsSourceKind(row["source_kind"]),
            title_text=row["title_text"],
            link_url=row["link_url"],
            published_at_text=row["published_at_text"],
            read_state=NewsItemReadState(row["read_state"]),
        )
        for row in rows
    )

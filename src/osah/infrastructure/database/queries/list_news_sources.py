from sqlite3 import Connection

from osah.domain.entities.news_source import NewsSource
from osah.domain.entities.news_source_kind import NewsSourceKind


# ###### ЧИТАННЯ СПИСКУ ДЖЕРЕЛ НОВИН / ЧТЕНИЕ СПИСКА ИСТОЧНИКОВ НОВОСТЕЙ ######
def list_news_sources(connection: Connection) -> tuple[NewsSource, ...]:
    """Повертає довірені джерела новин і НПА для налаштувань та refresh.
    Возвращает доверенные источники новостей и НПА для настроек и refresh.
    """

    rows = connection.execute(
        """
        SELECT
            id,
            source_name,
            source_url,
            source_kind,
            is_active,
            is_trusted,
            COALESCE(last_checked_at, '') AS last_checked_at
        FROM news_sources
        ORDER BY source_name ASC;
        """
    ).fetchall()
    return tuple(
        NewsSource(
            source_id=int(row["id"]),
            source_name=row["source_name"],
            source_url=row["source_url"],
            source_kind=NewsSourceKind(row["source_kind"]),
            is_active=bool(row["is_active"]),
            is_trusted=bool(row["is_trusted"]),
            last_checked_at_text=row["last_checked_at"],
        )
        for row in rows
    )

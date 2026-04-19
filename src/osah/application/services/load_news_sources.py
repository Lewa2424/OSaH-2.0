from pathlib import Path

from osah.domain.entities.news_source import NewsSource
from osah.infrastructure.database.create_database_connection import create_database_connection
from osah.infrastructure.database.queries.list_news_sources import list_news_sources


# ###### ЗАВАНТАЖЕННЯ ДЖЕРЕЛ НОВИН / ЗАГРУЗКА ИСТОЧНИКОВ НОВОСТЕЙ ######
def load_news_sources(database_path: Path) -> tuple[NewsSource, ...]:
    """Повертає список довірених джерел зовнішнього контуру.
    Возвращает список доверенных источников внешнего контура.
    """

    connection = create_database_connection(database_path)
    try:
        return list_news_sources(connection)
    finally:
        connection.close()

from pathlib import Path

from osah.domain.entities.news_item import NewsItem
from osah.infrastructure.database.create_database_connection import create_database_connection
from osah.infrastructure.database.queries.list_news_items import list_news_items


# ###### ЗАВАНТАЖЕННЯ НОВИННИХ МАТЕРІАЛІВ / ЗАГРУЗКА НОВОСТНЫХ МАТЕРИАЛОВ ######
def load_news_items(database_path: Path, unread_only: bool = False) -> tuple[NewsItem, ...]:
    """Повертає кешовані новини і правові матеріали з локального контуру.
    Возвращает кэшированные новости и правовые материалы из локального контура.
    """

    connection = create_database_connection(database_path)
    try:
        return list_news_items(connection, unread_only=unread_only)
    finally:
        connection.close()

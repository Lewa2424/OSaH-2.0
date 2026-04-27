from pathlib import Path

from osah.infrastructure.database.commands.delete_news_source_row import delete_news_source_row
from osah.infrastructure.database.commands.insert_audit_log import insert_audit_log
from osah.infrastructure.database.create_database_connection import create_database_connection


# ###### ВИДАЛЕННЯ ДЖЕРЕЛА НОВИН / УДАЛЕНИЕ ИСТОЧНИКА НОВОСТЕЙ ######
def delete_news_source(database_path: Path, source_id: int) -> None:
    """Видаляє довірене джерело новин або НПА з локальної бази.
    Удаляет доверенный источник новостей или НПА из локальной базы.
    """

    connection = create_database_connection(database_path)
    try:
        delete_news_source_row(connection, source_id)
        insert_audit_log(
            connection,
            event_type="news.source_deleted",
            module_name="news_npa",
            event_level="info",
            actor_name="inspector",
            entity_name=str(source_id),
            result_status="success",
            description_text=f"Trusted source source_id={source_id} deleted.",
        )
        connection.commit()
    finally:
        connection.close()

from pathlib import Path

from osah.application.services.security.ensure_write_access import ensure_write_access
from osah.domain.entities.access_role import AccessRole
from osah.infrastructure.database.commands.insert_audit_log import insert_audit_log
from osah.infrastructure.database.commands.mark_news_item_as_read_row import mark_news_item_as_read_row
from osah.infrastructure.database.create_database_connection import create_database_connection


# ###### ПОЗНАЧЕННЯ НОВИННОГО МАТЕРІАЛУ ЯК ПРОЧИТАНОГО / ПОМЕТКА НОВОСТНОГО МАТЕРИАЛА КАК ПРОЧИТАННОГО ######
def mark_news_item_as_read(database_path: Path, item_id: int, *, access_role: AccessRole) -> None:
    """Позначає кешований матеріал як прочитаний у локальному контурі.
    Помечает кэшированный материал как прочитанный в локальном контуре.
    """

    ensure_write_access(access_role, "mark_news_item_as_read")
    connection = create_database_connection(database_path)
    try:
        mark_news_item_as_read_row(connection, item_id)
        insert_audit_log(
            connection,
            event_type="news.item_marked_read",
            module_name="news_npa",
            event_level="info",
            actor_name="inspector",
            entity_name=str(item_id),
            result_status="success",
            description_text="Cached news item marked as read.",
        )
        connection.commit()
    finally:
        connection.close()

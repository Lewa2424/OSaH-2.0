from pathlib import Path

from osah.domain.entities.news_source_kind import NewsSourceKind
from osah.infrastructure.database.commands.insert_audit_log import insert_audit_log
from osah.infrastructure.database.commands.upsert_news_source_row import upsert_news_source_row
from osah.infrastructure.database.create_database_connection import create_database_connection


# ###### СТВОРЕННЯ ДЖЕРЕЛА НОВИН АБО НПА / СОЗДАНИЕ ИСТОЧНИКА НОВОСТЕЙ ИЛИ НПА ######
def create_news_source(
    database_path: Path,
    source_name: str,
    source_url: str,
    source_kind: NewsSourceKind,
) -> int:
    """Зберігає довірене джерело новин або НПА для подальшого refresh.
    Сохраняет доверенный источник новостей или НПА для дальнейшего refresh.
    """

    normalized_source_name = source_name.strip()
    normalized_source_url = source_url.strip()
    if not normalized_source_name:
        raise ValueError("Потрібно вказати назву джерела.")
    if not normalized_source_url.startswith(("http://", "https://")):
        raise ValueError("URL джерела має починатися з http:// або https://.")

    connection = create_database_connection(database_path)
    try:
        source_id = upsert_news_source_row(
            connection,
            source_name=normalized_source_name,
            source_url=normalized_source_url,
            source_kind=source_kind.value,
            is_active=True,
            is_trusted=True,
        )
        insert_audit_log(
            connection,
            event_type="news.source_saved",
            module_name="news_npa",
            event_level="info",
            actor_name="inspector",
            entity_name=normalized_source_url,
            result_status="success",
            description_text="Trusted external source saved.",
        )
        connection.commit()
        return source_id
    finally:
        connection.close()

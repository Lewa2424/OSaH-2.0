from pathlib import Path

from osah.infrastructure.database.commands.insert_audit_log import insert_audit_log
from osah.infrastructure.database.commands.upsert_news_source_row import upsert_news_source_row
from osah.infrastructure.database.create_database_connection import create_database_connection


# ###### ПЕРЕМИКАННЯ АКТИВНОСТІ ДЖЕРЕЛА НОВИН / TOGGLE NEWS SOURCE ACTIVITY ######
def toggle_news_source_activity(database_path: Path, source_id: int, is_active: bool) -> None:
    """Updates source active flag while preserving source identity fields."""

    connection = create_database_connection(database_path)
    try:
        row = connection.execute(
            """
            SELECT id, source_name, source_url, source_kind, is_trusted
            FROM news_sources
            WHERE id = ?;
            """,
            (source_id,),
        ).fetchone()
        if row is None:
            raise ValueError("Джерело не знайдено.")

        upsert_news_source_row(
            connection,
            source_name=str(row["source_name"]),
            source_url=str(row["source_url"]),
            source_kind=str(row["source_kind"]),
            is_active=is_active,
            is_trusted=bool(int(row["is_trusted"])),
        )
        insert_audit_log(
            connection,
            event_type="news.source_activity_changed",
            module_name="news_npa",
            event_level="info",
            actor_name="inspector",
            entity_name=str(row["source_url"]),
            result_status="success",
            description_text=f"Trusted source active={is_active}.",
        )
        connection.commit()
    finally:
        connection.close()

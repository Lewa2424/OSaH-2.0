from datetime import datetime
from pathlib import Path
from typing import Callable

from osah.domain.entities.rss_feed_entry import RssFeedEntry
from osah.domain.services.build_news_item_fingerprint import build_news_item_fingerprint
from osah.infrastructure.database.commands.insert_audit_log import insert_audit_log
from osah.infrastructure.database.commands.update_news_source_last_checked_at import update_news_source_last_checked_at
from osah.infrastructure.database.commands.upsert_news_item_row import upsert_news_item_row
from osah.infrastructure.database.create_database_connection import create_database_connection
from osah.infrastructure.database.queries.list_news_sources import list_news_sources
from osah.infrastructure.logging.log_alert_event import log_alert_event
from osah.infrastructure.logging.log_system_event import log_system_event
from osah.infrastructure.news.fetch_feed_entries_from_url import fetch_feed_entries_from_url


# ###### ОНОВЛЕННЯ ЗОВНІШНІХ ДЖЕРЕЛ НОВИН / ОБНОВЛЕНИЕ ВНЕШНИХ ИСТОЧНИКОВ НОВОСТЕЙ ######
def refresh_news_sources(
    database_path: Path,
    feed_fetcher: Callable[[str], tuple[RssFeedEntry, ...]] = fetch_feed_entries_from_url,
) -> int:
    """Оновлює активні зовнішні джерела і кешує нові матеріали локально.
    Обновляет активные внешние источники и кэширует новые материалы локально.
    """

    connection = create_database_connection(database_path)
    try:
        news_sources = tuple(news_source for news_source in list_news_sources(connection) if news_source.is_active)
        cached_item_total = 0
        failed_source_total = 0
        for news_source in news_sources:
            try:
                feed_entries = feed_fetcher(news_source.source_url)
            except Exception as error:  # noqa: BLE001
                failed_source_total += 1
                log_alert_event(
                    "news_npa",
                    f"Source refresh failed: source={news_source.source_url};error={type(error).__name__}",
                )
                continue

            for feed_entry in feed_entries:
                upsert_news_item_row(
                    connection,
                    source_id=news_source.source_id,
                    title_text=feed_entry.title_text,
                    link_url=feed_entry.link_url,
                    published_at_text=feed_entry.published_at_text,
                    source_kind=news_source.source_kind.value,
                    fingerprint_value=build_news_item_fingerprint(feed_entry.title_text, feed_entry.link_url),
                )
                cached_item_total += 1

            update_news_source_last_checked_at(
                connection,
                news_source.source_id,
                datetime.now().isoformat(timespec="seconds"),
            )

        insert_audit_log(
            connection,
            event_type="news.refresh_completed",
            module_name="news_npa",
            event_level="warning" if failed_source_total else "info",
            actor_name="inspector",
            entity_name="news.sources",
            result_status="partial" if failed_source_total else "success",
            description_text=(
                f"External news refresh completed for {len(news_sources)} sources; "
                f"failed_sources={failed_source_total}."
            ),
        )
        connection.commit()
        log_system_event(
            "news_npa",
            f"External news refresh completed: sources={len(news_sources)};items={cached_item_total};failed={failed_source_total}",
        )
        return cached_item_total
    finally:
        connection.close()

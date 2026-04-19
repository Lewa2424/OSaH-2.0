import tempfile
import unittest
from pathlib import Path

from osah.application.services.create_news_source import create_news_source
from osah.application.services.initialize_application import initialize_application
from osah.application.services.load_news_items import load_news_items
from osah.application.services.mark_news_item_as_read import mark_news_item_as_read
from osah.application.services.refresh_news_sources import refresh_news_sources
from osah.domain.entities.news_item_read_state import NewsItemReadState
from osah.domain.entities.news_source_kind import NewsSourceKind
from osah.domain.entities.rss_feed_entry import RssFeedEntry
from osah.infrastructure.config.application_paths import build_application_paths
from osah.infrastructure.logging.shutdown_logging import shut_down_logging


class MarkNewsItemAsReadTests(unittest.TestCase):
    """Тести позначення новинних матеріалів як прочитаних.
    Тесты пометки новостных материалов как прочитанных.
    """

    # ###### ПЕРЕВІРКА READ-STATE НОВИННОГО МАТЕРІАЛУ / ПРОВЕРКА READ-STATE НОВОСТНОГО МАТЕРИАЛА ######
    def test_mark_news_item_as_read_updates_item_state(self) -> None:
        """Перевіряє оновлення стану прочитання кешованого матеріалу.
        Проверяет обновление состояния прочтения кэшированного материала.
        """

        with tempfile.TemporaryDirectory() as temporary_directory:
            application_paths = build_application_paths(Path(temporary_directory))
            context = initialize_application(application_paths)
            create_news_source(
                context.database_path,
                "НПА",
                "https://example.com/npa.xml",
                NewsSourceKind.NPA,
            )

            refresh_news_sources(
                context.database_path,
                lambda _: (
                    RssFeedEntry(
                        title_text="Зміни до нормативного акту",
                        link_url="https://example.com/npa-1",
                        published_at_text="2026-04-10T13:00:00",
                    ),
                ),
            )
            news_item = load_news_items(context.database_path)[0]

            mark_news_item_as_read(context.database_path, news_item.item_id)

            updated_news_item = load_news_items(context.database_path)[0]
            self.assertEqual(updated_news_item.read_state, NewsItemReadState.READ)
            shut_down_logging()


if __name__ == "__main__":
    unittest.main()

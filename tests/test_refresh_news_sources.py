import tempfile
import unittest
from pathlib import Path

from osah.application.services.create_news_source import create_news_source
from osah.application.services.initialize_application import initialize_application
from osah.application.services.load_news_items import load_news_items
from osah.application.services.refresh_news_sources import refresh_news_sources
from osah.domain.entities.news_source_kind import NewsSourceKind
from osah.domain.entities.rss_feed_entry import RssFeedEntry
from osah.infrastructure.config.application_paths import build_application_paths
from osah.infrastructure.logging.shutdown_logging import shut_down_logging


class RefreshNewsSourcesTests(unittest.TestCase):
    """Тести refresh зовнішніх джерел новин.
    Тесты refresh внешних источников новостей.
    """

    # ###### ПЕРЕВІРКА КЕШУВАННЯ І ДЕДУПЛІКАЦІЇ МАТЕРІАЛІВ / ПРОВЕРКА КЭШИРОВАНИЯ И ДЕДУПЛИКАЦИИ МАТЕРИАЛОВ ######
    def test_refresh_news_sources_caches_materials_without_duplicates(self) -> None:
        """Перевіряє кешування матеріалів і захист від дублювання при повторному refresh.
        Проверяет кэширование материалов и защиту от дублирования при повторном refresh.
        """

        with tempfile.TemporaryDirectory() as temporary_directory:
            application_paths = build_application_paths(Path(temporary_directory))
            context = initialize_application(application_paths)
            create_news_source(
                context.database_path,
                "Новини ОП",
                "https://example.com/news.xml",
                NewsSourceKind.NEWS,
            )

            def fake_feed_fetcher(_: str) -> tuple[RssFeedEntry, ...]:
                return (
                    RssFeedEntry(
                        title_text="Оновлення правил охорони праці",
                        link_url="https://example.com/item-1",
                        published_at_text="2026-04-10T10:00:00",
                    ),
                    RssFeedEntry(
                        title_text="Нове роз'яснення Держпраці",
                        link_url="https://example.com/item-2",
                        published_at_text="2026-04-10T12:00:00",
                    ),
                )

            refresh_news_sources(context.database_path, fake_feed_fetcher)
            refresh_news_sources(context.database_path, fake_feed_fetcher)

            news_items = load_news_items(context.database_path)
            self.assertEqual(len(news_items), 2)
            self.assertEqual(news_items[0].title_text, "Нове роз'яснення Держпраці")
            shut_down_logging()


if __name__ == "__main__":
    unittest.main()

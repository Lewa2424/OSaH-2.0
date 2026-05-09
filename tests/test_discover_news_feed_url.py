import unittest

from osah.application.services.discover_news_feed_url import discover_news_feed_url


class DiscoverNewsFeedUrlTests(unittest.TestCase):
    """Тести пошуку RSS/Atom-стрічки для звичайного сайту.
    Тесты поиска RSS/Atom-ленты для обычного сайта.
    """

    def test_returns_same_url_when_input_is_feed(self) -> None:
        """Перевіряє, що прямий feed URL повертається без змін.
        Проверяет, что прямой feed URL возвращается без изменений.
        """

        def fake_reader(source_url: str) -> tuple[str, str]:
            return "application/rss+xml", "<rss><channel><title>Feed</title></channel></rss>"

        self.assertEqual(discover_news_feed_url("https://example.com/rss.xml", fake_reader), "https://example.com/rss.xml")

    def test_discovers_alternate_feed_from_html(self) -> None:
        """Перевіряє пошук feed через rel=alternate у HTML.
        Проверяет поиск feed через rel=alternate в HTML.
        """

        def fake_reader(source_url: str) -> tuple[str, str]:
            if source_url == "https://example.com/news":
                return (
                    "text/html",
                    '<html><head><link rel="alternate" type="application/rss+xml" href="/feed.xml"></head></html>',
                )
            if source_url == "https://example.com/feed.xml":
                return "application/rss+xml", "<rss><channel><title>Feed</title></channel></rss>"
            raise AssertionError(source_url)

        self.assertEqual(discover_news_feed_url("https://example.com/news", fake_reader), "https://example.com/feed.xml")

    def test_raises_when_feed_not_found(self) -> None:
        """Перевіряє зрозумілу помилку, якщо feed не знайдено.
        Проверяет понятную ошибку, если feed не найден.
        """

        def fake_reader(source_url: str) -> tuple[str, str]:
            return "text/html", "<html><head><title>No feed</title></head><body></body></html>"

        with self.assertRaises(ValueError):
            discover_news_feed_url("https://example.com", fake_reader)


if __name__ == "__main__":
    unittest.main()

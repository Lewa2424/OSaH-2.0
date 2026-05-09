import unittest

from osah.infrastructure.news.parse_feed_xml_content import parse_feed_xml_content


class ParseFeedXmlContentTests(unittest.TestCase):
    """Тести розбору RSS/Atom XML-контенту.
    Тесты разбора RSS/Atom XML-контента.
    """

    def test_parses_rss_with_leading_whitespace_and_description(self) -> None:
        """Перевіряє стійкий розбір feed з відступом перед XML та description.
        Проверяет устойчивый разбор feed с отступом перед XML и description.
        """

        xml_content_text = """
        <?xml version="1.0" encoding="UTF-8"?>
        <rss version="2.0">
            <channel>
                <item>
                    <title>Оновлення правил охорони праці</title>
                    <link>https://example.com/item-1</link>
                    <description>Короткий опис про безпеку праці.</description>
                    <pubDate>Fri, 09 May 2026 10:00:00 GMT</pubDate>
                </item>
            </channel>
        </rss>
        """

        entries = parse_feed_xml_content(xml_content_text)

        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0].summary_text, "Короткий опис про безпеку праці.")


if __name__ == "__main__":
    unittest.main()

import unittest

from osah.domain.entities.rss_feed_entry import RssFeedEntry
from osah.domain.services.is_occupational_safety_related_feed_entry import (
    is_occupational_safety_related_feed_entry,
)


class IsOccupationalSafetyRelatedFeedEntryTests(unittest.TestCase):
    """Тести тематичної фільтрації новин по охороні праці.
    Тесты тематической фильтрации новостей по охране труда.
    """

    def test_returns_true_for_ukrainian_occupational_safety_phrase(self) -> None:
        """Перевіряє пропуск матеріалу з прямою українською згадкою охорони праці.
        Проверяет пропуск материала с прямым украинским упоминанием охраны труда.
        """

        entry = RssFeedEntry(
            title_text="Оновлення правил охорони праці для підприємств",
            link_url="https://example.com/item-1",
            published_at_text="2026-05-01T10:00:00",
        )

        self.assertTrue(is_occupational_safety_related_feed_entry(entry))

    def test_returns_true_for_russian_summary_match(self) -> None:
        """Перевіряє пошук по summary для російськомовного матеріалу.
        Проверяет поиск по summary для русскоязычного материала.
        """

        entry = RssFeedEntry(
            title_text="Обновление",
            link_url="https://example.com/item-2",
            published_at_text="2026-05-01T11:00:00",
            summary_text="Новые разъяснения по охране труда и средствам индивидуальной защиты.",
        )

        self.assertTrue(is_occupational_safety_related_feed_entry(entry))

    def test_returns_false_for_irrelevant_general_news(self) -> None:
        """Перевіряє відсікання загальної новини без теми охорони праці.
        Проверяет отсечение общей новости без темы охраны труда.
        """

        entry = RssFeedEntry(
            title_text="Курс валют на сьогодні та ситуація на ринку",
            link_url="https://example.com/item-3",
            published_at_text="2026-05-01T12:00:00",
            summary_text="Огляд економічних показників та банківського сектору.",
        )

        self.assertFalse(is_occupational_safety_related_feed_entry(entry))


if __name__ == "__main__":
    unittest.main()

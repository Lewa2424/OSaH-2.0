import tempfile
import unittest
from pathlib import Path

from osah.application.services.create_news_source import create_news_source
from osah.application.services.initialize_application import initialize_application
from osah.application.services.load_news_sources import load_news_sources
from osah.domain.entities.news_source_kind import NewsSourceKind
from osah.infrastructure.config.application_paths import build_application_paths
from osah.infrastructure.logging.shutdown_logging import shut_down_logging


class CreateNewsSourceTests(unittest.TestCase):
    """Тести створення джерел новин і НПА.
    Тесты создания источников новостей и НПА.
    """

    # ###### ПЕРЕВІРКА ЗБЕРЕЖЕННЯ ДЖЕРЕЛА НОВИН / ПРОВЕРКА СОХРАНЕНИЯ ИСТОЧНИКА НОВОСТЕЙ ######
    def test_create_news_source_persists_trusted_source(self) -> None:
        """Перевіряє збереження джерела у локальному зовнішньому контурі.
        Проверяет сохранение источника в локальном внешнем контуре.
        """

        with tempfile.TemporaryDirectory() as temporary_directory:
            application_paths = build_application_paths(Path(temporary_directory))
            context = initialize_application(application_paths)

            create_news_source(
                context.database_path,
                "Держпраці",
                "https://example.com/rss.xml",
                NewsSourceKind.NPA,
            )

            news_sources = load_news_sources(context.database_path)
            self.assertEqual(len(news_sources), 1)
            self.assertEqual(news_sources[0].source_kind, NewsSourceKind.NPA)
            shut_down_logging()


if __name__ == "__main__":
    unittest.main()

import tempfile
import unittest
from pathlib import Path

from PySide6.QtWidgets import QApplication

from osah.application.services.create_news_source import create_news_source
from osah.application.services.initialize_application import initialize_application
from osah.application.services.load_news_items import load_news_items
from osah.application.services.refresh_news_sources import refresh_news_sources
from osah.domain.entities.access_role import AccessRole
from osah.domain.entities.news_item_read_state import NewsItemReadState
from osah.domain.entities.news_source_kind import NewsSourceKind
from osah.domain.entities.rss_feed_entry import RssFeedEntry
from osah.infrastructure.config.application_paths import build_application_paths
from osah.infrastructure.logging.shutdown_logging import shut_down_logging
from osah.ui.qt.screens.news.news_screen import NewsScreen


class ManagerNewsReadOnlyTests(unittest.TestCase):
    """Checks that manager news viewing does not mutate read-state."""

    @classmethod
    def setUpClass(cls) -> None:
        cls._app = QApplication.instance() or QApplication([])

    def test_manager_view_does_not_mark_news_as_read(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            try:
                application_paths = build_application_paths(Path(temporary_directory))
                context = initialize_application(application_paths)
                create_news_source(
                    context.database_path,
                    "НПА",
                    "https://example.com/npa.xml",
                    NewsSourceKind.NPA,
                    access_role=AccessRole.INSPECTOR,
                )
                refresh_news_sources(
                    context.database_path,
                    lambda _: (
                        RssFeedEntry(
                            title_text="Зміни до нормативного акту з охорони праці",
                            link_url="https://example.com/npa-1",
                            published_at_text="2026-05-19T10:00:00",
                        ),
                    ),
                )

                initial_items = load_news_items(context.database_path)
                self.assertEqual(len(initial_items), 1)

                screen = NewsScreen(context.database_path, AccessRole.MANAGER)
                screen.items_table.selectRow(0)
                self._app.processEvents()

                reloaded_item = load_news_items(context.database_path)[0]
                self.assertEqual(reloaded_item.read_state, NewsItemReadState.NEW)
                screen.deleteLater()
            finally:
                shut_down_logging()


if __name__ == "__main__":
    unittest.main()

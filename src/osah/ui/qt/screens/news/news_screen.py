from pathlib import Path

from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QCheckBox, QPushButton, QSplitter, QVBoxLayout, QWidget

from osah.application.services.load_news_items import load_news_items
from osah.application.services.load_news_sources import load_news_sources
from osah.application.services.mark_news_item_as_read import mark_news_item_as_read
from osah.ui.qt.components.form_feedback_label import FormFeedbackLabel
from osah.ui.qt.components.scrollable_table_frame import ScrollableTableFrame
from osah.ui.qt.components.section_header import SectionHeader
from osah.ui.qt.design.tokens import SPACING
from osah.ui.qt.screens.news.news_items_table import NewsItemsTable
from osah.ui.qt.screens.news.news_sources_panel import NewsSourcesPanel


class NewsScreen(QWidget):
    """Screen for trusted sources, NPA/news cache and read-state flow."""

    def __init__(self, database_path: Path) -> None:
        super().__init__()
        self._database_path = database_path

        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACING["xl"], SPACING["lg"], SPACING["xl"], SPACING["lg"])
        layout.setSpacing(SPACING["lg"])

        layout.addWidget(
            SectionHeader(
                "Новини / НПА",
                "Інформаційний inbox зовнішнього контуру: довірені джерела, кеш, дедуплікація, нове/прочитано.",
            )
        )

        self.feedback = FormFeedbackLabel()
        layout.addWidget(self.feedback)

        splitter = QSplitter()
        splitter.setChildrenCollapsible(False)

        self.sources_panel = NewsSourcesPanel()
        splitter.addWidget(self.sources_panel)

        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(0, 0, 0, 0)
        self.unread_only = QCheckBox("Показувати тільки нові")
        self.unread_only.stateChanged.connect(lambda _: self._reload_state())
        right_layout.addWidget(self.unread_only)
        self.items_table = NewsItemsTable()
        right_layout.addWidget(ScrollableTableFrame(self.items_table), stretch=1)
        mark_read_button = QPushButton("Позначити прочитаним")
        mark_read_button.clicked.connect(self._mark_selected_read)
        right_layout.addWidget(mark_read_button)
        open_link_button = QPushButton("Відкрити посилання")
        open_link_button.clicked.connect(self._open_selected_link)
        right_layout.addWidget(open_link_button)
        splitter.addWidget(right)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)

        layout.addWidget(splitter, stretch=1)
        self._reload_state()

    # ###### ПОЗНАЧЕННЯ ПРОЧИТАНИМ / MARK AS READ ######
    def _mark_selected_read(self) -> None:
        """Marks selected informational item as read."""

        current_item = self.items_table.current_news_item()
        if current_item is None:
            self.feedback.show_error("Оберіть матеріал у списку.")
            return
        mark_news_item_as_read(self._database_path, current_item.item_id)
        self.feedback.show_success("Матеріал позначено як прочитаний.")
        self._reload_state()

    # ###### ВІДКРИТТЯ ПОСИЛАННЯ / OPEN LINK ######
    def _open_selected_link(self) -> None:
        """Opens selected item link in browser."""

        current_item = self.items_table.current_news_item()
        if current_item is None:
            self.feedback.show_error("Оберіть матеріал у списку.")
            return
        QDesktopServices.openUrl(QUrl(current_item.link_url))

    # ###### ОНОВЛЕННЯ ЕКРАНУ / RELOAD SCREEN ######
    def _reload_state(self) -> None:
        """Reloads trusted sources and cached materials."""

        self.sources_panel.set_sources(load_news_sources(self._database_path))
        self.items_table.set_items(load_news_items(self._database_path, unread_only=self.unread_only.isChecked()))

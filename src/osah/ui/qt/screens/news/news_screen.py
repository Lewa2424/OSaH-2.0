from pathlib import Path

from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QCheckBox, QLabel, QPushButton, QSplitter, QVBoxLayout, QWidget

from osah.application.services.create_news_source import create_news_source
from osah.application.services.load_news_items import load_news_items
from osah.application.services.load_news_sources import load_news_sources
from osah.application.services.mark_news_item_as_read import mark_news_item_as_read
from osah.application.services.refresh_news_sources import refresh_news_sources
from osah.domain.entities.news_source_kind import NewsSourceKind
from osah.ui.qt.components.form_feedback_label import FormFeedbackLabel
from osah.ui.qt.design.tokens import COLOR, SPACING
from osah.ui.qt.screens.news.news_items_table import NewsItemsTable
from osah.ui.qt.screens.news.news_sources_panel import NewsSourcesPanel


class NewsScreen(QWidget):
    """Екран НПА, новин, довірених джерел і статусу прочитання.
    Screen for NPA/news, trusted sources, and read state.
    """

    def __init__(self, database_path: Path) -> None:
        super().__init__()
        self._database_path = database_path

        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACING["xl"], SPACING["lg"], SPACING["xl"], SPACING["lg"])
        layout.setSpacing(SPACING["lg"])

        title = QLabel("Новини / НПА")
        title.setStyleSheet("font-size: 22px; font-weight: 900;")
        layout.addWidget(title)

        subtitle = QLabel(
            "Інформаційний inbox зовнішнього контуру: довірені джерела, кеш, дедуплікація, нове/прочитано."
        )
        subtitle.setStyleSheet(f"color: {COLOR['text_secondary']};")
        layout.addWidget(subtitle)

        self.feedback = FormFeedbackLabel()
        layout.addWidget(self.feedback)

        splitter = QSplitter()
        splitter.setChildrenCollapsible(False)

        self.sources_panel = NewsSourcesPanel()
        self.sources_panel.create_source_requested.connect(self._create_source)
        self.sources_panel.refresh_requested.connect(self._refresh_sources)
        splitter.addWidget(self.sources_panel)

        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(0, 0, 0, 0)
        self.unread_only = QCheckBox("Показувати тільки нові")
        self.unread_only.stateChanged.connect(lambda _: self._reload_state())
        right_layout.addWidget(self.unread_only)
        self.items_table = NewsItemsTable()
        right_layout.addWidget(self.items_table, stretch=1)
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

    # ###### СТВОРЕННЯ ДЖЕРЕЛА / CREATE SOURCE ######
    def _create_source(self, source_name: str, source_url: str, source_kind_value: str) -> None:
        """Створює довірене джерело через application-service, без запису у внутрішній ОТ-контур.
        Creates a trusted source through an application service without changing internal OT data.
        """

        try:
            create_news_source(self._database_path, source_name, source_url, NewsSourceKind(source_kind_value))
            self.feedback.show_success("Довірене джерело збережено.")
        except Exception as error:  # noqa: BLE001
            self.feedback.show_error(f"Джерело не збережено: {error}")
        self._reload_state()

    # ###### ОНОВЛЕННЯ ДЖЕРЕЛ / REFRESH SOURCES ######
    def _refresh_sources(self) -> None:
        """Перевіряє активні довірені джерела і оновлює локальний кеш матеріалів.
        Checks active trusted sources and updates the local material cache.
        """

        cached_total = refresh_news_sources(self._database_path)
        self.feedback.show_success(f"Перевірку завершено. Оброблено матеріалів: {cached_total}.")
        self._reload_state()

    # ###### ПОЗНАЧЕННЯ ПРОЧИТАНИМ / MARK READ ######
    def _mark_selected_read(self) -> None:
        """Позначає вибраний інформаційний матеріал як прочитаний.
        Marks the selected informational material as read.
        """

        current_item = self.items_table.current_news_item()
        if current_item is None:
            self.feedback.show_error("Оберіть матеріал у списку.")
            return
        mark_news_item_as_read(self._database_path, current_item.item_id)
        self.feedback.show_success("Матеріал позначено як прочитаний.")
        self._reload_state()

    # ###### ВІДКРИТТЯ ПОСИЛАННЯ / OPEN LINK ######
    def _open_selected_link(self) -> None:
        """Відкриває посилання вибраного матеріалу у браузері користувача.
        Opens the selected material link in the user's browser.
        """

        current_item = self.items_table.current_news_item()
        if current_item is None:
            self.feedback.show_error("Оберіть матеріал у списку.")
            return
        QDesktopServices.openUrl(QUrl(current_item.link_url))

    # ###### ОНОВЛЕННЯ ЕКРАНУ / RELOAD SCREEN ######
    def _reload_state(self) -> None:
        """Оновлює список джерел та кешованих матеріалів без зміни основної БД ОТ.
        Reloads sources and cached materials without changing the internal OT database contour.
        """

        self.sources_panel.set_sources(load_news_sources(self._database_path))
        self.items_table.set_items(load_news_items(self._database_path, unread_only=self.unread_only.isChecked()))

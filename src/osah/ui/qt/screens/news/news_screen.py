from pathlib import Path

from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QCheckBox, QPushButton, QSplitter, QVBoxLayout, QWidget

from osah.application.services.create_news_source import create_news_source
from osah.application.services.load_news_items import load_news_items
from osah.application.services.load_news_sources import load_news_sources
from osah.application.services.mark_news_item_as_read import mark_news_item_as_read
from osah.domain.entities.news_source_kind import NewsSourceKind
from osah.ui.qt.components.form_feedback_label import FormFeedbackLabel
from osah.ui.qt.components.scrollable_table_frame import ScrollableTableFrame
from osah.ui.qt.components.section_header import SectionHeader
from osah.ui.qt.components.task_progress_widget import TaskProgressWidget
from osah.ui.qt.design.tokens import SPACING
from osah.ui.qt.screens.news.news_items_table import NewsItemsTable
from osah.ui.qt.screens.news.news_sources_panel import NewsSourcesPanel
from osah.ui.qt.workers.news_refresh_worker import NewsRefreshWorker
from osah.ui.qt.workers.worker_task_controller import WorkerTaskController


class NewsScreen(QWidget):
    """Screen for trusted sources, NPA/news cache and read-state flow."""

    def __init__(self, database_path: Path) -> None:
        super().__init__()
        self._database_path = database_path

        self._task_controller = WorkerTaskController()
        self._task_controller.started.connect(self._on_task_started)
        self._task_controller.progress.connect(self._on_task_progress)
        self._task_controller.success.connect(self._on_task_success)
        self._task_controller.error.connect(self._on_task_error)
        self._task_controller.finished.connect(self._on_task_finished)

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

        self._task_progress = TaskProgressWidget()
        layout.addWidget(self._task_progress)

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

    # ###### СТВОРЕННЯ ДЖЕРЕЛА / CREATE SOURCE ######
    def _create_source(self, source_name: str, source_url: str, source_kind_value: str) -> None:
        """Creates trusted source through application service."""

        try:
            create_news_source(self._database_path, source_name, source_url, NewsSourceKind(source_kind_value))
            self.feedback.show_success("Довірене джерело збережено.")
        except Exception as error:  # noqa: BLE001
            self.feedback.show_error(f"Джерело не збережено: {error}")
        self._reload_state()

    # ###### ОНОВЛЕННЯ ДЖЕРЕЛ У ФОНІ / REFRESH SOURCES IN BACKGROUND ######
    def _refresh_sources(self) -> None:
        """Starts background refresh of trusted sources."""

        if not self._task_controller.start_worker(NewsRefreshWorker(self._database_path)):
            self.feedback.show_error("Оновлення вже виконується. Дочекайтеся завершення.")

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

    # ###### СТАРТ ФОНОВОЇ ЗАДАЧІ / BACKGROUND TASK START ######
    def _on_task_started(self) -> None:
        """Applies busy-state while refresh is active."""

        self._task_progress.show_indeterminate("Оновлення джерел виконується у фоні...")
        self.sources_panel.setEnabled(False)
        self.items_table.setEnabled(False)
        self.unread_only.setEnabled(False)

    # ###### ПРОГРЕС ФОНОВОЇ ЗАДАЧІ / BACKGROUND TASK PROGRESS ######
    def _on_task_progress(self, progress_value: int, message_text: str) -> None:
        """Updates progress status."""

        self._task_progress.show_progress(message_text, progress_value)

    # ###### УСПІХ ФОНОВОЇ ЗАДАЧІ / BACKGROUND TASK SUCCESS ######
    def _on_task_success(self, payload: object) -> None:
        """Handles successful refresh result."""

        cached_total = int(payload) if isinstance(payload, int) else 0
        self.feedback.show_success(f"Перевірку завершено. Оброблено матеріалів: {cached_total}.")
        self._reload_state()

    # ###### ПОМИЛКА ФОНОВОЇ ЗАДАЧІ / BACKGROUND TASK ERROR ######
    def _on_task_error(self, message_text: str) -> None:
        """Shows refresh failure message."""

        self.feedback.show_error(message_text)

    # ###### ФІНАЛ ФОНОВОЇ ЗАДАЧІ / BACKGROUND TASK FINISH ######
    def _on_task_finished(self) -> None:
        """Resets busy-state after refresh completion."""

        self._task_progress.hide_state()
        self.sources_panel.setEnabled(True)
        self.items_table.setEnabled(True)
        self.unread_only.setEnabled(True)

    # ###### ОНОВЛЕННЯ ЕКРАНУ / RELOAD SCREEN ######
    def _reload_state(self) -> None:
        """Reloads trusted sources and cached materials."""

        self.sources_panel.set_sources(load_news_sources(self._database_path))
        self.items_table.set_items(load_news_items(self._database_path, unread_only=self.unread_only.isChecked()))

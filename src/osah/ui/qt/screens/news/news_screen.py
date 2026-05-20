from pathlib import Path

from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QCheckBox, QHBoxLayout, QPushButton, QVBoxLayout, QWidget

from osah.application.services.load_news_items import load_news_items
from osah.application.services.mark_news_item_as_read import mark_news_item_as_read
from osah.domain.entities.access_role import AccessRole
from osah.domain.entities.news_item_read_state import NewsItemReadState
from osah.ui.qt.components.form_feedback_label import FormFeedbackLabel
from osah.ui.qt.components.section_header import SectionHeader
from osah.ui.qt.design.tokens import SPACING
from osah.ui.qt.screens.news.news_item_detail_panel import NewsItemDetailPanel
from osah.ui.qt.screens.news.news_items_table import NewsItemsTable


class NewsScreen(QWidget):
    """Screen for trusted sources, NPA/news cache and read-state flow."""

    def __init__(self, database_path: Path, access_role: AccessRole) -> None:
        super().__init__()
        self._database_path = database_path
        self._access_role = access_role
        self._read_only = access_role != AccessRole.INSPECTOR

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

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(SPACING["md"])

        filters_row = QHBoxLayout()
        filters_row.setContentsMargins(0, 0, 0, 0)
        filters_row.setSpacing(SPACING["md"])

        self.unread_only = QCheckBox("Показувати тільки нові")
        self.unread_only.stateChanged.connect(lambda _: self._reload_state())
        filters_row.addWidget(self.unread_only)
        filters_row.addStretch()
        content_layout.addLayout(filters_row)

        self.items_table = NewsItemsTable()
        self.items_table.item_selected.connect(self._sync_detail_panel)
        content_layout.addWidget(self.items_table, stretch=1)

        self.detail_panel = NewsItemDetailPanel()
        content_layout.addWidget(self.detail_panel)

        actions_row = QHBoxLayout()
        actions_row.setContentsMargins(0, 0, 0, 0)
        actions_row.setSpacing(SPACING["sm"])
        self.mark_read_button = QPushButton("Позначити прочитаним")
        self.mark_read_button.setProperty("variant", "accent")
        self.mark_read_button.clicked.connect(self._mark_selected_read)
        self.mark_read_button.setVisible(not self._read_only)
        self.mark_read_button.setEnabled(not self._read_only)
        actions_row.addWidget(self.mark_read_button)
        self.open_link_button = QPushButton("Відкрити оригінал")
        self.open_link_button.setProperty("variant", "accent")
        self.open_link_button.clicked.connect(self._open_selected_link)
        actions_row.addWidget(self.open_link_button)
        actions_row.addStretch()
        content_layout.addLayout(actions_row)

        layout.addWidget(content, stretch=1)
        self._reload_state()

    # ###### ПОЗНАЧЕННЯ ПРОЧИТАНИМ / MARK AS READ ######
    def _mark_selected_read(self) -> None:
        """Marks selected informational item as read."""

        if self._read_only:
            self.feedback.show_error("Режим read-only: зміна статусу новини недоступна.")
            return
        current_item = self.items_table.current_news_item()
        if current_item is None:
            self.feedback.show_error("Оберіть матеріал у списку.")
            return
        self._mark_item_as_read(current_item.item_id, show_feedback=True)
        self._sync_detail_panel(current_item.item_id)

    def _mark_item_as_read(self, item_id: int, show_feedback: bool = False) -> None:
        """Позначає матеріал як прочитаний з урахуванням поточного фільтра екрана.
        Marks the material as read while respecting the current screen filter.
        """

        mark_news_item_as_read(self._database_path, item_id, access_role=self._access_role)
        if self.unread_only.isChecked():
            self._reload_state()
        else:
            self.items_table.mark_item_as_read(item_id)
        if show_feedback:
            self.feedback.show_success("Матеріал позначено як прочитаний.")

    # ###### ВІДКРИТТЯ ПОСИЛАННЯ / OPEN LINK ######
    def _open_selected_link(self) -> None:
        """Opens selected item link in browser."""

        current_item = self.items_table.current_news_item()
        if current_item is None:
            self.feedback.show_error("Оберіть матеріал у списку.")
            return
        QDesktopServices.openUrl(QUrl(current_item.link_url))

    def _sync_detail_panel(self, _item_id: int) -> None:
        """Синхронізує detail-панель і доступність action-кнопок з поточним вибором.
        Syncs detail panel and action buttons with the current selection.
        """

        current_item = self.items_table.current_news_item()
        has_selection = current_item is not None
        self.mark_read_button.setEnabled(has_selection and not self._read_only)
        self.open_link_button.setEnabled(has_selection)
        if current_item is None:
            self.detail_panel.show_placeholder()
            return
        if not self._read_only and current_item.read_state == NewsItemReadState.NEW:
            selected_item_id = current_item.item_id
            self._mark_item_as_read(selected_item_id)
            current_item = self.items_table.current_news_item()
            if current_item is None:
                self.detail_panel.show_placeholder()
                self.mark_read_button.setEnabled(False)
                self.open_link_button.setEnabled(False)
                return
        self.detail_panel.set_item(current_item)

    # ###### ОНОВЛЕННЯ ЕКРАНУ / RELOAD SCREEN ######
    def _reload_state(self) -> None:
        """Reloads trusted sources and cached materials."""

        self.items_table.set_items(load_news_items(self._database_path, unread_only=self.unread_only.isChecked()))
        self._sync_detail_panel(-1)

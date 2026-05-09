from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from osah.domain.entities.news_source import NewsSource
from osah.ui.qt.design.tokens import COLOR, RADIUS, SPACING


class NewsSourcesPanel(QWidget):
    """Панель перегляду довірених джерел НПА та новин (тільки перегляд).
    Read-only panel displaying trusted NPA/news sources list.
    """

    source_filter_changed = Signal(object)

    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING["sm"])
        self._sources: tuple[NewsSource, ...] = ()

        hint = QLabel("Керування джерелами — у розділі «Налаштування».")
        hint.setProperty("role", "hint_label")
        layout.addWidget(hint)

        self._summary_label = QLabel()
        self._summary_label.setWordWrap(True)
        self._summary_label.setStyleSheet(
            f"background: {COLOR['accent_soft']}; color: {COLOR['text_secondary']}; "
            f"border: 1px solid {COLOR['border_soft']}; border-radius: {RADIUS['md']}px; "
            f"padding: {SPACING['sm']}px {SPACING['md']}px; font-weight: 600;"
        )
        layout.addWidget(self._summary_label)

        action_row = QHBoxLayout()
        action_row.setContentsMargins(0, 0, 0, 0)
        action_row.setSpacing(SPACING["sm"])
        action_row.addStretch()
        self._clear_filter_button = QPushButton("Усі джерела")
        self._clear_filter_button.setProperty("variant", "secondary")
        self._clear_filter_button.clicked.connect(self._clear_selection)
        action_row.addWidget(self._clear_filter_button)
        layout.addLayout(action_row)

        self.sources_table = QTableWidget(0, 3)
        self.sources_table.setHorizontalHeaderLabels(("Джерело", "Стан", "Остання перевірка"))
        self.sources_table.verticalHeader().setVisible(False)
        self.sources_table.horizontalHeader().setStretchLastSection(False)
        self.sources_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.sources_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.sources_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.sources_table.setWordWrap(False)
        self.sources_table.setShowGrid(False)
        self.sources_table.setAlternatingRowColors(True)
        self.sources_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.sources_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.sources_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.sources_table.itemSelectionChanged.connect(self._emit_filter_selection)
        layout.addWidget(self.sources_table)

    # ###### ВСТАНОВЛЕННЯ ДЖЕРЕЛ / SET SOURCES ######
    def set_sources(self, news_sources: tuple[NewsSource, ...], selected_source_id: int | None = None) -> None:
        """Показує список довірених джерел і дату останньої перевірки.
        Shows trusted sources and last check time.
        """

        self._sources = news_sources
        active_total = sum(1 for source in news_sources if source.is_active)
        self._summary_label.setText(
            f"Усього джерел: {len(news_sources)}. Активних: {active_total}. "
            "Оберіть рядок, щоб звузити список новин, або залиште без вибору для всіх джерел."
        )

        self.sources_table.blockSignals(True)
        self.sources_table.clearSelection()
        self.sources_table.setRowCount(len(news_sources))
        for row_index, source in enumerate(news_sources):
            values = (
                source.source_name,
                _build_source_status_label(source),
                source.last_checked_at_text or "ще не перевірялось",
            )
            for column_index, value in enumerate(values):
                item = QTableWidgetItem(value)
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                item.setToolTip(value)
                if not source.is_active:
                    item.setForeground(Qt.GlobalColor.gray)
                self.sources_table.setItem(row_index, column_index, item)
            self.sources_table.setRowHeight(row_index, 34)
            if selected_source_id is not None and source.source_id == selected_source_id:
                self.sources_table.selectRow(row_index)
        self.sources_table.blockSignals(False)
        self._clear_filter_button.setEnabled(selected_source_id is not None)

    def selected_source_id(self) -> int | None:
        """Повертає id вибраного джерела або None, якщо фільтр не встановлено.
        Returns selected source id or None when no filter is active.
        """

        selected_rows = self.sources_table.selectionModel().selectedRows()
        if not selected_rows:
            return None
        row_index = selected_rows[0].row()
        if row_index < 0 or row_index >= len(self._sources):
            return None
        return self._sources[row_index].source_id

    def _emit_filter_selection(self) -> None:
        """Повідомляє екран про зміну джерела-фільтра.
        Notifies the screen when the source filter changes.
        """

        selected_source_id = self.selected_source_id()
        self._clear_filter_button.setEnabled(selected_source_id is not None)
        self.source_filter_changed.emit(selected_source_id)

    def _clear_selection(self) -> None:
        """Скидає вибране джерело й повертає список новин до загального виду.
        Clears selected source and returns the news list to the global view.
        """

        self.sources_table.clearSelection()
        self._clear_filter_button.setEnabled(False)
        self.source_filter_changed.emit(None)


def _build_source_status_label(source: NewsSource) -> str:
    """Повертає короткий статус джерела для лівої панелі.
    Returns a short source status for the left panel.
    """

    kind_label = "НПА" if source.source_kind.value == "npa" else "Новини"
    activity_label = "активне" if source.is_active else "вимкнене"
    return f"{kind_label} • {activity_label}"

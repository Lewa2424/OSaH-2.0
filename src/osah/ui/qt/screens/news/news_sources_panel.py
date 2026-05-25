from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QTableWidget,
    QVBoxLayout,
    QWidget,
)

from osah.domain.entities.news_source import NewsSource
from osah.ui.qt.components.sortable_table_widget_item import ROW_KEY_ROLE, SortableTableWidgetItem
from osah.ui.qt.design.tokens import COLOR, RADIUS, SPACING


class NewsSourcesPanel(QWidget):
    """Read-only panel displaying trusted NPA/news sources list."""

    source_filter_changed = Signal(object)

    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING["sm"])
        self._sources_by_key: dict[str, NewsSource] = {}
        self._default_sort_column = 0

        hint = QLabel('Керування джерелами — у розділі "Налаштування".')
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
        self.sources_table.setSortingEnabled(True)
        self.sources_table.horizontalHeader().setSortIndicatorShown(True)
        self.sources_table.horizontalHeader().setSortIndicator(self._default_sort_column, Qt.SortOrder.AscendingOrder)
        self.sources_table.itemSelectionChanged.connect(self._emit_filter_selection)
        layout.addWidget(self.sources_table)

    def set_sources(self, news_sources: tuple[NewsSource, ...], selected_source_id: int | None = None) -> None:
        """Shows trusted sources and last check time."""

        self._sources_by_key = {str(source.source_id): source for source in news_sources}
        active_total = sum(1 for source in news_sources if source.is_active)
        self._summary_label.setText(
            f"Усього джерел: {len(news_sources)}. Активних: {active_total}. "
            "Оберіть рядок, щоб звузити список новин, або залиште без вибору для всіх джерел."
        )

        sort_column = self.sources_table.horizontalHeader().sortIndicatorSection()
        sort_order = self.sources_table.horizontalHeader().sortIndicatorOrder()
        self.sources_table.blockSignals(True)
        self.sources_table.setSortingEnabled(False)
        self.sources_table.clearSelection()
        self.sources_table.setRowCount(len(news_sources))
        target_row_key = str(selected_source_id) if selected_source_id is not None else None

        for row_index, source in enumerate(news_sources):
            values = (
                (source.source_name, source.source_name),
                (_build_source_status_label(source), _build_source_status_label(source)),
                (source.last_checked_at_text or "ще не перевірялось", source.last_checked_at_text or ""),
            )
            for column_index, (value, sort_value) in enumerate(values):
                item = SortableTableWidgetItem(value, row_key=str(source.source_id), sort_value=sort_value)
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                item.setToolTip(value)
                if not source.is_active:
                    item.setForeground(Qt.GlobalColor.gray)
                self.sources_table.setItem(row_index, column_index, item)
            self.sources_table.setRowHeight(row_index, 34)

        self.sources_table.setSortingEnabled(True)
        self.sources_table.sortItems(sort_column if sort_column >= 0 else self._default_sort_column, sort_order)
        if target_row_key is not None:
            self._select_source_by_key(target_row_key)
        self.sources_table.blockSignals(False)
        self._clear_filter_button.setEnabled(selected_source_id is not None)

    def selected_source_id(self) -> int | None:
        """Returns selected source id or None when no filter is active."""

        selected_rows = self.sources_table.selectionModel().selectedRows()
        if not selected_rows:
            return None
        item = self.sources_table.item(selected_rows[0].row(), 0)
        if item is None:
            return None
        row_key = item.data(ROW_KEY_ROLE)
        return int(row_key) if row_key is not None else None

    def _emit_filter_selection(self) -> None:
        """Notifies the screen when the source filter changes."""

        selected_source_id = self.selected_source_id()
        self._clear_filter_button.setEnabled(selected_source_id is not None)
        self.source_filter_changed.emit(selected_source_id)

    def _clear_selection(self) -> None:
        """Clears selected source and returns the news list to the global view."""

        self.sources_table.clearSelection()
        self._clear_filter_button.setEnabled(False)
        self.source_filter_changed.emit(None)

    def _select_source_by_key(self, row_key: str) -> None:
        for row_index in range(self.sources_table.rowCount()):
            item = self.sources_table.item(row_index, 0)
            if item is not None and item.data(ROW_KEY_ROLE) == row_key:
                self.sources_table.selectRow(row_index)
                return


def _build_source_status_label(source: NewsSource) -> str:
    kind_label = "НПА" if source.source_kind.value == "npa" else "Новини"
    activity_label = "активне" if source.is_active else "вимкнене"
    return f"{kind_label} • {activity_label}"

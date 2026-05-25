from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QAbstractItemView, QTableWidget

from osah.domain.entities.archive_entry import ArchiveEntry
from osah.ui.qt.components.ensure_table_column_width import ensure_table_column_width
from osah.ui.qt.components.sortable_table_widget_item import ROW_KEY_ROLE, SortableTableWidgetItem


_TYPE_MAP = {
    "employee": "Працівник",
    "work_permit": "Наряд-допуск",
}

_STATUS_MAP = {
    "archived": "В архіві",
    "inactive": "Неактивний",
    "dismissed": "Звільнено",
    "closed": "Закрито",
    "canceled": "Скасовано",
}


class ArchiveRegistryTable(QTableWidget):
    """Archive registry table with interactive column sorting."""

    row_selected = Signal(object)

    def __init__(self) -> None:
        super().__init__(0, 5)
        self._rows_by_key: dict[str, ArchiveEntry] = {}
        self._default_sort_column = 1
        self.setHorizontalHeaderLabels(["Тип", "Назва", "Підзаголовок", "Статус", "Причина"])
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setAlternatingRowColors(True)
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setStretchLastSection(False)
        self.setSortingEnabled(True)
        self.horizontalHeader().setSortIndicatorShown(True)
        self.horizontalHeader().setSortIndicator(self._default_sort_column, Qt.SortOrder.AscendingOrder)
        self.itemSelectionChanged.connect(self._emit_selected_row)

    def set_rows(self, rows: tuple[ArchiveEntry, ...]) -> None:
        """Populates table with archive rows."""

        self._rows_by_key = {row.entry_key: row for row in rows}
        sort_column = self.horizontalHeader().sortIndicatorSection()
        sort_order = self.horizontalHeader().sortIndicatorOrder()
        self.setSortingEnabled(False)
        self.setRowCount(0)

        for row_index, row in enumerate(rows):
            self.insertRow(row_index)
            type_label = _TYPE_MAP.get(row.entry_type.value, row.entry_type.value)
            status_label = _STATUS_MAP.get(row.status_label.lower(), row.status_label)
            cell_specs = (
                (type_label, type_label),
                (row.title, row.title),
                (row.subtitle, row.subtitle),
                (status_label, status_label),
                (row.reason_text, row.reason_text),
            )
            for column_index, (text, sort_value) in enumerate(cell_specs):
                item = SortableTableWidgetItem(text, row_key=row.entry_key, sort_value=sort_value)
                item.setToolTip(text)
                self.setItem(row_index, column_index, item)

        self.resizeColumnsToContents()
        ensure_table_column_width(self, 4, max_width=500)
        self.setSortingEnabled(True)
        self.sortItems(sort_column if sort_column >= 0 else self._default_sort_column, sort_order)

    def select_first(self) -> None:
        """Selects first row if available."""

        if self.rowCount():
            self.selectRow(0)

    def _emit_selected_row(self) -> None:
        """Emits selected archive entry."""

        selected = self.selectedItems()
        if not selected:
            return
        row_key = str(selected[0].data(ROW_KEY_ROLE))
        row = self._rows_by_key.get(row_key)
        if row is not None:
            self.row_selected.emit(row)

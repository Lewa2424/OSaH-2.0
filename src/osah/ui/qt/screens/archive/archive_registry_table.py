from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QAbstractItemView, QTableWidget, QTableWidgetItem

from osah.domain.entities.archive_entry import ArchiveEntry
from osah.ui.qt.components.ensure_table_column_width import ensure_table_column_width


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
    """Archive registry table."""

    row_selected = Signal(object)

    def __init__(self) -> None:
        super().__init__(0, 5)
        self._rows: tuple[ArchiveEntry, ...] = ()
        self.setHorizontalHeaderLabels(["Тип", "Назва", "Підзаголовок", "Статус", "Причина"])
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setAlternatingRowColors(True)
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setStretchLastSection(False)
        self.itemSelectionChanged.connect(self._emit_selected_row)

    # ###### ЗАПОВНЕННЯ ТАБЛИЦІ АРХІВУ / SET ARCHIVE ROWS ######
    def set_rows(self, rows: tuple[ArchiveEntry, ...]) -> None:
        """Populates table with archive rows."""

        self._rows = rows
        self.setRowCount(0)
        for row_index, row in enumerate(rows):
            self.insertRow(row_index)
            
            type_label = _TYPE_MAP.get(row.entry_type.value, row.entry_type.value)
            status_label = _STATUS_MAP.get(row.status_label.lower(), row.status_label)
            
            for column_index, text in enumerate((type_label, row.title, row.subtitle, status_label, row.reason_text)):
                item = QTableWidgetItem(text)
                item.setData(Qt.ItemDataRole.UserRole, row_index)
                item.setToolTip(text)
                self.setItem(row_index, column_index, item)
        self.resizeColumnsToContents()
        ensure_table_column_width(self, 4, max_width=500)

    # ###### ВИДІЛЕННЯ ПЕРШОГО РЯДКА / SELECT FIRST ROW ######
    def select_first(self) -> None:
        """Selects first row if available."""

        if self.rowCount():
            self.selectRow(0)

    # ###### ПЕРЕДАЧА ОБРАНОГО РЯДКА / EMIT SELECTED ROW ######
    def _emit_selected_row(self) -> None:
        """Emits selected archive entry."""

        selected = self.selectedItems()
        if not selected:
            return
        row_index = selected[0].row()
        if 0 <= row_index < len(self._rows):
            self.row_selected.emit(self._rows[row_index])

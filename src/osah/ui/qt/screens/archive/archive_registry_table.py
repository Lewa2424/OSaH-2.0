from PySide6.QtCore import Signal
from PySide6.QtWidgets import QAbstractItemView, QTableWidget, QTableWidgetItem

from osah.domain.entities.archive_entry import ArchiveEntry


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
        self.horizontalHeader().setStretchLastSection(True)
        self.itemSelectionChanged.connect(self._emit_selected_row)

    # ###### ЗАПОВНЕННЯ ТАБЛИЦІ АРХІВУ / SET ARCHIVE ROWS ######
    def set_rows(self, rows: tuple[ArchiveEntry, ...]) -> None:
        """Populates table with archive rows."""

        self._rows = rows
        self.setRowCount(0)
        for row_index, row in enumerate(rows):
            self.insertRow(row_index)
            self.setItem(row_index, 0, QTableWidgetItem(row.entry_type.value))
            self.setItem(row_index, 1, QTableWidgetItem(row.title))
            self.setItem(row_index, 2, QTableWidgetItem(row.subtitle))
            self.setItem(row_index, 3, QTableWidgetItem(row.status_label))
            self.setItem(row_index, 4, QTableWidgetItem(row.reason_text))
        self.resizeColumnsToContents()

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

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QAbstractItemView, QTableWidget, QTableWidgetItem

from osah.domain.entities.contractor_record import ContractorRecord


class ContractorsRegistryTable(QTableWidget):
    """Contractors registry table."""

    row_selected = Signal(object)

    def __init__(self) -> None:
        super().__init__(0, 5)
        self._rows: tuple[ContractorRecord, ...] = ()
        self.setHorizontalHeaderLabels(["Організація", "Контакт", "Телефон", "Email", "Статус"])
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setAlternatingRowColors(True)
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setStretchLastSection(True)
        self.itemSelectionChanged.connect(self._emit_selected_row)

    # ###### ЗАПОВНЕННЯ РЕЄСТРУ ПІДРЯДНИКІВ / SET CONTRACTOR ROWS ######
    def set_rows(self, rows: tuple[ContractorRecord, ...]) -> None:
        """Populates contractors table."""

        self._rows = rows
        self.setRowCount(0)
        for row_index, row in enumerate(rows):
            self.insertRow(row_index)
            self.setItem(row_index, 0, QTableWidgetItem(row.company_name))
            self.setItem(row_index, 1, QTableWidgetItem(row.contact_person))
            self.setItem(row_index, 2, QTableWidgetItem(row.contact_phone))
            self.setItem(row_index, 3, QTableWidgetItem(row.contact_email))
            self.setItem(row_index, 4, QTableWidgetItem(row.activity_status))
        self.resizeColumnsToContents()

    # ###### ВИБІР ПЕРШОГО РЯДКА / SELECT FIRST ROW ######
    def select_first(self) -> None:
        """Selects first row if available."""

        if self.rowCount():
            self.selectRow(0)

    # ###### ПЕРЕДАЧА ОБРАНОГО ЗАПИСУ / EMIT SELECTED RECORD ######
    def _emit_selected_row(self) -> None:
        """Emits selected contractor record."""

        selected = self.selectedItems()
        if not selected:
            return
        row_index = selected[0].row()
        if 0 <= row_index < len(self._rows):
            self.row_selected.emit(self._rows[row_index])

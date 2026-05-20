from PySide6.QtCore import Signal
from PySide6.QtWidgets import QAbstractItemView, QTableWidget, QTableWidgetItem

from osah.domain.entities.contractor_workspace_row import ContractorWorkspaceRow


class ContractorsRegistryTable(QTableWidget):
    """Таблиця реєстру підрядників із коротким статусом готовності.
    Contractors registry table with compact readiness state.
    """

    row_selected = Signal(object)

    def __init__(self) -> None:
        super().__init__(0, 6)
        self._rows: tuple[ContractorWorkspaceRow, ...] = ()
        self.setHorizontalHeaderLabels(["Організація", "Контакт", "Працівн.", "Готові", "Проблемні", "Статус"])
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setAlternatingRowColors(True)
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setStretchLastSection(True)
        self.itemSelectionChanged.connect(self._emit_selected_row)

    def set_rows(self, rows: tuple[ContractorWorkspaceRow, ...]) -> None:
        """Заповнює таблицю підготовленими рядками підрядників.
        Populates the table with prepared contractor rows.
        """

        self._rows = rows
        self.setRowCount(0)
        for row_index, row in enumerate(rows):
            self.insertRow(row_index)
            self.setItem(row_index, 0, QTableWidgetItem(row.record.company_name))
            self.setItem(row_index, 1, QTableWidgetItem(row.record.contact_person))
            self.setItem(row_index, 2, QTableWidgetItem(str(row.readiness.total_workers)))
            self.setItem(row_index, 3, QTableWidgetItem(str(row.readiness.ready_workers)))
            self.setItem(row_index, 4, QTableWidgetItem(str(row.readiness.problem_workers)))
            self.setItem(row_index, 5, QTableWidgetItem(row.readiness.status_label))
        self.resizeColumnsToContents()

    def select_first(self) -> None:
        """Вибирає перший рядок таблиці, якщо він існує.
        Selects first table row when available.
        """

        if self.rowCount():
            self.selectRow(0)

    def _emit_selected_row(self) -> None:
        """Передає вибраний рядок підрядника назовні.
        Emits selected contractor row.
        """

        selected = self.selectedItems()
        if not selected:
            return
        row_index = selected[0].row()
        if 0 <= row_index < len(self._rows):
            self.row_selected.emit(self._rows[row_index])

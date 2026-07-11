from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QAbstractItemView, QTableWidget

from osah.domain.entities.contractor_workspace_row import ContractorWorkspaceRow
from osah.ui.qt.components.sortable_table_widget_item import ROW_KEY_ROLE, SortableTableWidgetItem


class ContractorsRegistryTable(QTableWidget):
    """Contractors registry table with interactive column sorting."""

    row_selected = Signal(object)

    def __init__(self) -> None:
        super().__init__(0, 6)
        self._rows_by_key: dict[str, ContractorWorkspaceRow] = {}
        self._default_sort_column = 0
        self.setHorizontalHeaderLabels(["Організація", "Контакт", "Працівн.", "Готові", "Проблемні", "Статус"])
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setAlternatingRowColors(True)
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setStretchLastSection(True)
        self.setStyleSheet(
            """
            QTableWidget {
                background: rgba(255, 255, 255, 0.9);
                border: 1px solid #D6E1EC;
                border-radius: 18px;
                gridline-color: #E2EAF2;
                font-size: 14px;
                selection-background-color: rgba(76, 121, 173, 0.16);
                selection-color: #102846;
            }
            QHeaderView::section {
                background: #EAF1F7;
                color: #17365D;
                padding: 11px 8px;
                border: none;
                font-size: 13px;
                font-weight: 800;
            }
            """
        )
        self.setSortingEnabled(True)
        self.horizontalHeader().setSortIndicatorShown(True)
        self.horizontalHeader().setSortIndicator(self._default_sort_column, Qt.SortOrder.AscendingOrder)
        self.itemSelectionChanged.connect(self._emit_selected_row)

    def set_rows(self, rows: tuple[ContractorWorkspaceRow, ...]) -> None:
        """Populates the table with prepared contractor rows."""

        self._rows_by_key = {row.record.contractor_id: row for row in rows}
        sort_column = self.horizontalHeader().sortIndicatorSection()
        sort_order = self.horizontalHeader().sortIndicatorOrder()
        self.setSortingEnabled(False)
        self.setRowCount(0)

        for row_index, row in enumerate(rows):
            self.insertRow(row_index)
            cell_specs = (
                (row.record.company_name, row.record.company_name),
                (row.record.contact_person, row.record.contact_person),
                (str(row.readiness.total_workers), row.readiness.total_workers),
                (str(row.readiness.ready_workers), row.readiness.ready_workers),
                (str(row.readiness.problem_workers), row.readiness.problem_workers),
                (row.readiness.status_label, row.readiness.status_label),
            )
            for column_index, (text, sort_value) in enumerate(cell_specs):
                item = SortableTableWidgetItem(text, row_key=row.record.contractor_id, sort_value=sort_value)
                self.setItem(row_index, column_index, item)
            self.setRowHeight(row_index, 44)

        self.resizeColumnsToContents()
        self.setSortingEnabled(True)
        self.sortItems(sort_column if sort_column >= 0 else self._default_sort_column, sort_order)

    def select_first(self) -> None:
        """Selects first table row when available."""

        if self.rowCount():
            self.selectRow(0)

    def _emit_selected_row(self) -> None:
        """Emits selected contractor row."""

        selected = self.selectedItems()
        if not selected:
            return
        row_key = str(selected[0].data(ROW_KEY_ROLE))
        row = self._rows_by_key.get(row_key)
        if row is not None:
            self.row_selected.emit(row)

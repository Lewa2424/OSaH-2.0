from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QAbstractItemView, QTableWidget

from osah.domain.entities.training_registry_filter import TrainingRegistryFilter
from osah.domain.entities.training_workspace_row import TrainingWorkspaceRow
from osah.domain.services.format_ui_date import format_ui_date
from osah.ui.qt.components.ensure_table_column_width import ensure_table_column_width
from osah.ui.qt.components.sortable_table_widget_item import MATCH_VALUE_ROLE, ROW_KEY_ROLE, SortableTableWidgetItem
from osah.ui.qt.design.tokens import COLOR
from osah.ui.qt.screens.trainings.training_status_badge import TrainingStatusBadge


class TrainingsRegistryTable(QTableWidget):
    """Central trainings registry with interactive column sorting."""

    row_selected = Signal(object)

    def __init__(self) -> None:
        super().__init__(0, 8)
        self._rows_by_key: dict[str, TrainingWorkspaceRow] = {}
        self._default_sort_column = 0
        self.setHorizontalHeaderLabels(
            ["ПІБ", "Підрозділ", "Тип", "Проведено", "Наст. строк", "Статус", "Проводив", "Причина"]
        )
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setAlternatingRowColors(True)
        self.setWordWrap(True)
        self.setTextElideMode(Qt.TextElideMode.ElideNone)
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setStretchLastSection(False)
        self.setSortingEnabled(True)
        self.horizontalHeader().setSortIndicatorShown(True)
        self.horizontalHeader().setSortIndicator(self._default_sort_column, Qt.SortOrder.AscendingOrder)
        self.itemSelectionChanged.connect(self._emit_selected_row)

    def set_rows(self, rows: tuple[TrainingWorkspaceRow, ...]) -> None:
        """Redraws the table with prepared rows."""

        self._rows_by_key = {self._row_key(row): row for row in rows}
        sort_column = self.horizontalHeader().sortIndicatorSection()
        sort_order = self.horizontalHeader().sortIndicatorOrder()
        self.setSortingEnabled(False)
        self.setRowCount(0)

        for row_index, row in enumerate(rows):
            self.insertRow(row_index)
            cell_specs = (
                (0, row.employee_full_name, row.employee_full_name, row.employee_personnel_number),
                (1, row.department_name, row.department_name, row.employee_personnel_number),
                (2, row.training_type_label, row.training_type_label, row.employee_personnel_number),
                (3, format_ui_date(row.event_date), row.event_date, row.employee_personnel_number),
                (4, format_ui_date(row.next_control_date), row.next_control_date, row.employee_personnel_number),
                (5, row.status_label, row.status_label, row.employee_personnel_number),
                (6, row.conducted_by, row.conducted_by, row.employee_personnel_number),
                (7, row.status_reason, row.status_reason, row.employee_personnel_number),
            )
            for column_index, text, sort_value, match_value in cell_specs:
                self._set_item(
                    row_index,
                    column_index,
                    text,
                    row,
                    sort_value=sort_value,
                    match_value=match_value,
                )
            self.setCellWidget(row_index, 5, TrainingStatusBadge(row.status_filter, row.status_label))

        self.resizeColumnsToContents()
        ensure_table_column_width(self, 5)
        ensure_table_column_width(self, 7, max_width=420)
        self.resizeRowsToContents()
        for row_index in range(self.rowCount()):
            self.setRowHeight(row_index, max(38, self.rowHeight(row_index)))

        self.setSortingEnabled(True)
        self.sortItems(sort_column if sort_column >= 0 else self._default_sort_column, sort_order)

    def select_first(self) -> None:
        """Selects the first row when the table is not empty."""

        if self.rowCount():
            self.selectRow(0)

    def select_record(self, record_id: int) -> bool:
        """Restores selection by training record id."""

        record_key = str(record_id)
        for row_index in range(self.rowCount()):
            item = self.item(row_index, 0)
            if item is not None and item.data(ROW_KEY_ROLE) == record_key:
                self.selectRow(row_index)
                return True
        return False

    def select_employee(self, personnel_number: str) -> bool:
        """Restores selection by employee personnel number."""

        for row_index in range(self.rowCount()):
            item = self.item(row_index, 0)
            if item is not None and item.data(MATCH_VALUE_ROLE) == personnel_number:
                self.selectRow(row_index)
                return True
        return False

    def _set_item(
        self,
        row_index: int,
        column_index: int,
        text: str,
        row: TrainingWorkspaceRow,
        *,
        sort_value: object,
        match_value: object,
    ) -> None:
        item = SortableTableWidgetItem(
            text,
            row_key=self._row_key(row),
            sort_value=sort_value,
            match_value=match_value,
        )
        item.setToolTip(text)
        if column_index == 7:
            item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        if row.status_filter in {
            TrainingRegistryFilter.OVERDUE,
            TrainingRegistryFilter.MISSING,
            TrainingRegistryFilter.INVALID,
        }:
            item.setForeground(QColor(COLOR["critical"]))
        elif row.status_filter == TrainingRegistryFilter.WARNING:
            item.setForeground(QColor(COLOR["warning"]))
        self.setItem(row_index, column_index, item)

    def _emit_selected_row(self) -> None:
        """Emits the selected row to the detail pane."""

        selected = self.selectedItems()
        if not selected:
            return
        row_key = str(selected[0].data(ROW_KEY_ROLE))
        row = self._rows_by_key.get(row_key)
        if row is not None:
            self.row_selected.emit(row)

    def _row_key(self, row: TrainingWorkspaceRow) -> str:
        return str(row.record_id)

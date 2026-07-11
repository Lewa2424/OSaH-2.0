from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QAbstractItemView, QTableWidget

from osah.domain.entities.work_permit_status import WorkPermitStatus
from osah.domain.entities.work_permit_workspace_row import WorkPermitWorkspaceRow
from osah.domain.services.format_ui_datetime import format_ui_datetime
from osah.ui.qt.components.ensure_table_column_width import ensure_table_column_width
from osah.ui.qt.components.sortable_table_widget_item import MATCH_VALUE_ROLE, ROW_KEY_ROLE, SortableTableWidgetItem
from osah.ui.qt.design.tokens import COLOR
from osah.ui.qt.screens.work_permits.work_permit_status_badge import WorkPermitStatusBadge


class WorkPermitsRegistryTable(QTableWidget):
    """Central work permits registry with interactive column sorting."""

    row_selected = Signal(object)

    def __init__(self) -> None:
        super().__init__(0, 9)
        self._rows_by_key: dict[str, WorkPermitWorkspaceRow] = {}
        self._default_sort_column = 0
        self.setHorizontalHeaderLabels(
            ["№", "Вид робіт", "Місце", "Початок", "Завершення", "Статус", "Відповідальний", "Учасн.", "Причина"]
        )
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
        self.setStyleSheet(
            f"""
            QTableWidget {{
                background: rgba(255, 255, 255, 0.97);
                border: 1px solid #D9E2EC;
                border-radius: 22px;
                gridline-color: #E5ECF2;
                font-size: 13px;
                color: {COLOR['text_primary']};
            }}
            QHeaderView::section {{
                background: #EEF4F9;
                color: {COLOR['text_secondary']};
                border: none;
                border-bottom: 1px solid #D9E2EC;
                padding: 10px 12px;
                font-size: 12px;
                font-weight: 900;
            }}
            QTableWidget::item:selected {{
                background: #E7F0F8;
                color: {COLOR['text_primary']};
            }}
            """
        )

    def set_rows(self, rows: tuple[WorkPermitWorkspaceRow, ...]) -> None:
        """Redraws the table with prepared rows."""

        self._rows_by_key = {self._row_key(row): row for row in rows}
        sort_column = self.horizontalHeader().sortIndicatorSection()
        sort_order = self.horizontalHeader().sortIndicatorOrder()
        self.setSortingEnabled(False)
        self.setRowCount(0)

        for row_index, row in enumerate(rows):
            self.insertRow(row_index)
            cell_specs = (
                (0, row.permit_number, row.permit_number, row.employee_numbers[0] if row.employee_numbers else ""),
                (1, row.work_kind, row.work_kind, row.employee_numbers[0] if row.employee_numbers else ""),
                (2, row.work_location, row.work_location, row.employee_numbers[0] if row.employee_numbers else ""),
                (3, format_ui_datetime(row.starts_at), row.starts_at, row.employee_numbers[0] if row.employee_numbers else ""),
                (4, format_ui_datetime(row.ends_at), row.ends_at, row.employee_numbers[0] if row.employee_numbers else ""),
                (5, row.status_label, row.status_label, row.employee_numbers[0] if row.employee_numbers else ""),
                (6, row.responsible_person, row.responsible_person, row.employee_numbers[0] if row.employee_numbers else ""),
                (7, str(row.participant_count), row.participant_count, row.employee_numbers[0] if row.employee_numbers else ""),
                (8, _build_reason_text(row), _build_reason_text(row), row.employee_numbers[0] if row.employee_numbers else ""),
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
            self.setCellWidget(row_index, 5, WorkPermitStatusBadge(row.status, row.status_label))
            self.setRowHeight(row_index, 44)

        self.resizeColumnsToContents()
        ensure_table_column_width(self, 5)
        ensure_table_column_width(self, 8, max_width=520)
        self.setSortingEnabled(True)
        self.sortItems(sort_column if sort_column >= 0 else self._default_sort_column, sort_order)

    def select_first(self) -> None:
        """Selects the first row when the table is not empty."""

        if self.rowCount():
            self.selectRow(0)

    def select_record(self, record_id: int) -> bool:
        """Restores selection by work permit record id."""

        record_key = str(record_id)
        for row_index in range(self.rowCount()):
            item = self.item(row_index, 0)
            if item is not None and item.data(ROW_KEY_ROLE) == record_key:
                self.selectRow(row_index)
                return True
        return False

    def select_employee(self, personnel_number: str) -> bool:
        """Restores selection by participant personnel number."""

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
        row: WorkPermitWorkspaceRow,
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
        if row.status in {WorkPermitStatus.EXPIRED, WorkPermitStatus.INVALID} or row.has_conflicts:
            item.setForeground(QColor(COLOR["critical"]))
        elif row.status == WorkPermitStatus.WARNING:
            item.setForeground(QColor(COLOR["warning"]))
        elif row.status in {WorkPermitStatus.CLOSED, WorkPermitStatus.REISSUED}:
            item.setForeground(QColor(COLOR["text_muted"]))
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

    def _row_key(self, row: WorkPermitWorkspaceRow) -> str:
        return str(row.record_id)


def _build_reason_text(row: WorkPermitWorkspaceRow) -> str:
    """Returns status reason together with participant conflicts."""

    if row.conflict_reasons:
        return f"{row.status_reason}; конфлікти: {len(row.conflict_reasons)}"
    return row.status_reason

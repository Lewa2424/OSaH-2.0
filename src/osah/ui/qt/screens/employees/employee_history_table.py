from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QAbstractItemView, QHeaderView, QTableWidget

from osah.domain.entities.audit_log_entry import AuditLogEntry
from osah.domain.services.format_employee_audit_event_label import format_employee_audit_event_label
from osah.domain.services.format_employee_audit_module_label import format_employee_audit_module_label
from osah.ui.qt.components.sortable_table_widget_item import ROW_KEY_ROLE, SortableTableWidgetItem


class EmployeeHistoryTable(QTableWidget):
    """Таблиця audit-історії працівника з сортуванням.
    Employee audit history table with sorting.
    """

    entry_selected = Signal(int)

    def __init__(self) -> None:
        super().__init__(0, 4)
        self._rows_by_key: dict[str, AuditLogEntry] = {}
        self._default_sort_column = 0
        self.setHorizontalHeaderLabels(("Час", "Модуль", "Подія", "Результат"))
        self.verticalHeader().setVisible(False)
        self.setAlternatingRowColors(True)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        header = self.horizontalHeader()
        header.setStretchLastSection(False)
        header.setMinimumSectionSize(72)
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.setSortingEnabled(True)
        self.horizontalHeader().setSortIndicatorShown(True)
        self.horizontalHeader().setSortIndicator(self._default_sort_column, Qt.SortOrder.DescendingOrder)
        self.itemSelectionChanged.connect(self._emit_selected_entry)

    def set_entries(self, audit_entries: tuple[AuditLogEntry, ...]) -> None:
        """Заповнює таблицю audit-записами працівника.
        Fills the table with employee audit entries.
        """

        self._rows_by_key = {str(entry.entry_id): entry for entry in audit_entries}
        sort_column = self.horizontalHeader().sortIndicatorSection()
        sort_order = self.horizontalHeader().sortIndicatorOrder()
        self.setSortingEnabled(False)
        self.clearSelection()
        self.setRowCount(len(audit_entries))
        for row_index, entry in enumerate(audit_entries):
            cell_specs = (
                (entry.created_at_text, entry.created_at_text),
                (
                    format_employee_audit_module_label(entry.module_name),
                    format_employee_audit_module_label(entry.module_name),
                ),
                (
                    format_employee_audit_event_label(entry.event_type),
                    format_employee_audit_event_label(entry.event_type),
                ),
                (_build_result_label(entry.result_status), _build_result_label(entry.result_status)),
            )
            for column_index, (text, sort_value) in enumerate(cell_specs):
                item = SortableTableWidgetItem(text, row_key=str(entry.entry_id), sort_value=sort_value)
                self.setItem(row_index, column_index, item)
        self.resizeColumnsToContents()
        self.setColumnWidth(2, max(180, self.columnWidth(2)))
        self.setSortingEnabled(True)
        self.sortItems(sort_column if sort_column >= 0 else self._default_sort_column, sort_order)
        if self.rowCount():
            self.selectRow(0)

    def current_entry(self) -> AuditLogEntry | None:
        """Повертає вибраний audit-запис або None.
        Returns the selected audit entry or None.
        """

        selected_rows = self.selectionModel().selectedRows()
        if not selected_rows:
            return None
        item = self.item(selected_rows[0].row(), 0)
        if item is None:
            return None
        return self._rows_by_key.get(str(item.data(ROW_KEY_ROLE)))

    def _emit_selected_entry(self) -> None:
        current_entry = self.current_entry()
        if current_entry is not None:
            self.entry_selected.emit(current_entry.entry_id)


def _build_result_label(result_status: str) -> str:
    normalized_status = result_status.strip().lower()
    if normalized_status == "success":
        return "успішно"
    if normalized_status == "failed":
        return "помилка"
    return result_status or "невідомо"

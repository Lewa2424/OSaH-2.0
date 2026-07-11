from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QAbstractItemView, QHeaderView, QTableWidget

from osah.domain.entities.audit_log_entry import AuditLogEntry
from osah.ui.qt.components.sortable_table_widget_item import ROW_KEY_ROLE, SortableTableWidgetItem


class ReportHistoryTable(QTableWidget):
    """Table showing the history of generated daily reports with sorting."""

    entry_selected = Signal(int)

    def __init__(self) -> None:
        super().__init__(0, 4)
        self._rows_by_key: dict[str, AuditLogEntry] = {}
        self._default_sort_column = 0
        self.setHorizontalHeaderLabels(("Час", "Результат", "Файл", "Опис"))
        self.verticalHeader().setVisible(False)
        self.setAlternatingRowColors(True)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.setStyleSheet(
            """
            QTableWidget {
                background: rgba(255, 255, 255, 0.9);
                border: 1px solid #D6E1EC;
                border-radius: 18px;
                gridline-color: #E2EAF2;
                font-size: 14px;
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
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.setSortingEnabled(True)
        self.horizontalHeader().setSortIndicatorShown(True)
        self.horizontalHeader().setSortIndicator(self._default_sort_column, Qt.SortOrder.DescendingOrder)
        self.itemSelectionChanged.connect(self._emit_selected_entry)

    def set_entries(self, audit_entries: tuple[AuditLogEntry, ...]) -> None:
        """Fills the table with the history of generated report files."""

        rows = tuple(
            entry
            for entry in audit_entries
            if entry.module_name == "reports" and entry.event_type == "report.file_created"
        )
        self._rows_by_key = {str(entry.entry_id): entry for entry in rows}
        sort_column = self.horizontalHeader().sortIndicatorSection()
        sort_order = self.horizontalHeader().sortIndicatorOrder()
        self.setSortingEnabled(False)
        self.clearSelection()
        self.setRowCount(len(rows))
        for row_index, entry in enumerate(rows):
            cell_specs = (
                (entry.created_at_text, entry.created_at_text),
                (_build_result_label(entry.result_status), _build_result_label(entry.result_status)),
                (_extract_file_name(entry.description_text), _extract_file_name(entry.description_text)),
                (entry.description_text, entry.description_text),
            )
            for column_index, (text, sort_value) in enumerate(cell_specs):
                item = SortableTableWidgetItem(text, row_key=str(entry.entry_id), sort_value=sort_value)
                self.setItem(row_index, column_index, item)
            self.setRowHeight(row_index, 44)
        self.setSortingEnabled(True)
        self.sortItems(sort_column if sort_column >= 0 else self._default_sort_column, sort_order)
        if self.rowCount():
            self.selectRow(0)

    def current_entry(self) -> AuditLogEntry | None:
        """Returns the selected history entry or None."""

        selected_rows = self.selectionModel().selectedRows()
        if not selected_rows:
            return None
        item = self.item(selected_rows[0].row(), 0)
        if item is None:
            return None
        return self._rows_by_key.get(str(item.data(ROW_KEY_ROLE)))

    def _emit_selected_entry(self) -> None:
        """Emits selected entry id for the detail panel."""

        current_entry = self.current_entry()
        if current_entry is not None:
            self.entry_selected.emit(current_entry.entry_id)


def _extract_file_name(description_text: str) -> str:
    key_token = "saved_path="
    if key_token not in description_text:
        return "-"
    raw_path = description_text.split(key_token, maxsplit=1)[1].split(";", maxsplit=1)[0].strip()
    if not raw_path:
        return "-"
    return raw_path.replace("\\", "/").split("/")[-1] or raw_path


def _build_result_label(result_status: str) -> str:
    normalized_status = result_status.strip().lower()
    if normalized_status == "success":
        return "успішно"
    if normalized_status == "failed":
        return "помилка"
    return result_status or "-"

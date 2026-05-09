from PySide6.QtCore import Signal
from PySide6.QtWidgets import QAbstractItemView, QHeaderView, QTableWidget, QTableWidgetItem

from osah.domain.entities.audit_log_entry import AuditLogEntry


class ReportHistoryTable(QTableWidget):
    """Таблиця історії сформованих щоденних звітів.
    Table showing the history of generated daily reports.
    """

    entry_selected = Signal(int)

    def __init__(self) -> None:
        super().__init__(0, 4)
        self._rows: tuple[AuditLogEntry, ...] = ()
        self.setHorizontalHeaderLabels(("Час", "Результат", "Файл", "Опис"))
        self.verticalHeader().setVisible(False)
        self.setAlternatingRowColors(True)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.itemSelectionChanged.connect(self._emit_selected_entry)

    def set_entries(self, audit_entries: tuple[AuditLogEntry, ...]) -> None:
        """Заповнює таблицю історією сформованих звітів.
        Fills the table with the history of generated report files.
        """

        self._rows = tuple(
            entry
            for entry in audit_entries
            if entry.module_name == "reports" and entry.event_type == "report.file_created"
        )
        self.clearSelection()
        self.setRowCount(len(self._rows))
        for row_index, entry in enumerate(self._rows):
            values = (
                entry.created_at_text,
                _build_result_label(entry.result_status),
                _extract_file_name(entry.description_text),
                entry.description_text,
            )
            for column_index, value in enumerate(values):
                self.setItem(row_index, column_index, QTableWidgetItem(value))
        if self._rows:
            self.selectRow(0)

    def current_entry(self) -> AuditLogEntry | None:
        """Повертає вибраний запис історії або None.
        Returns the selected history entry or None.
        """

        selected_rows = self.selectionModel().selectedRows()
        if not selected_rows:
            return None
        row_index = selected_rows[0].row()
        if row_index < 0 or row_index >= len(self._rows):
            return None
        return self._rows[row_index]

    def _emit_selected_entry(self) -> None:
        """Передає ідентифікатор вибраного запису для detail-панелі.
        Emits selected entry id for the detail panel.
        """

        current_entry = self.current_entry()
        if current_entry is not None:
            self.entry_selected.emit(current_entry.entry_id)


def _extract_file_name(description_text: str) -> str:
    """Витягує назву файлу з audit-опису для компактного рядка.
    Extracts a file name from the audit description for compact display.
    """

    key_token = "saved_path="
    if key_token not in description_text:
        return "-"
    raw_path = description_text.split(key_token, maxsplit=1)[1].split(";", maxsplit=1)[0].strip()
    if not raw_path:
        return "-"
    return raw_path.replace("\\", "/").split("/")[-1] or raw_path


def _build_result_label(result_status: str) -> str:
    """Повертає зрозумілий підпис результату для таблиці історії.
    Returns a readable result label for the history table.
    """

    normalized_status = result_status.strip().lower()
    if normalized_status == "success":
        return "успішно"
    if normalized_status == "failed":
        return "помилка"
    return result_status or "-"

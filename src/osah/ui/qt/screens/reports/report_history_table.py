from PySide6.QtCore import Signal
from PySide6.QtWidgets import QAbstractItemView, QHeaderView, QTableWidget, QTableWidgetItem

from osah.domain.entities.audit_log_entry import AuditLogEntry


class ReportHistoryTable(QTableWidget):
    """Таблиця останніх службових подій пошти та щоденного звіту.
    Table of recent service events for mail and daily reports.
    """

    entry_selected = Signal(int)

    def __init__(self) -> None:
        super().__init__(0, 5)
        self._rows: tuple[AuditLogEntry, ...] = ()
        self.setHorizontalHeaderLabels(("Час", "Подія", "Рівень", "Результат", "Опис"))
        self.verticalHeader().setVisible(False)
        self.setAlternatingRowColors(True)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.itemSelectionChanged.connect(self._emit_selected_entry)

    # ###### ВСТАНОВЛЕННЯ ІСТОРІЇ / SET HISTORY ######
    def set_entries(self, audit_entries: tuple[AuditLogEntry, ...]) -> None:
        """Заповнює таблицю останніми подіями зовнішнього поштового контуру.
        Fills the table with recent external mail events.
        """

        self._rows = tuple(entry for entry in audit_entries if entry.module_name == "reports_mail")
        self.clearSelection()
        self.setRowCount(len(self._rows))
        for row_index, entry in enumerate(self._rows):
            values = (
                entry.created_at_text,
                entry.event_type,
                entry.event_level,
                entry.result_status,
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

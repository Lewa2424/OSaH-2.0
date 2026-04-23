from PySide6.QtWidgets import QHeaderView, QTableWidget, QTableWidgetItem

from osah.domain.entities.audit_log_entry import AuditLogEntry


class ReportHistoryTable(QTableWidget):
    """Таблиця останніх службових подій пошти та щоденного звіту.
    Table of recent service events for mail and daily reports.
    """

    def __init__(self) -> None:
        super().__init__(0, 5)
        self.setHorizontalHeaderLabels(("Час", "Подія", "Рівень", "Результат", "Опис"))
        self.verticalHeader().setVisible(False)
        self.setAlternatingRowColors(True)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)

    # ###### ВСТАНОВЛЕННЯ ІСТОРІЇ / SET HISTORY ######
    def set_entries(self, audit_entries: tuple[AuditLogEntry, ...]) -> None:
        """Заповнює таблицю останніми подіями зовнішнього поштового контуру.
        Fills the table with recent external mail events.
        """

        rows = tuple(entry for entry in audit_entries if entry.module_name == "reports_mail")
        self.setRowCount(len(rows))
        for row_index, entry in enumerate(rows):
            values = (
                entry.created_at_text,
                entry.event_type,
                entry.event_level,
                entry.result_status,
                entry.description_text,
            )
            for column_index, value in enumerate(values):
                self.setItem(row_index, column_index, QTableWidgetItem(value))

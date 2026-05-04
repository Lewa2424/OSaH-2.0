from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QAbstractItemView, QLabel, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget

from osah.domain.entities.medical_record import MedicalRecord
from osah.domain.services.build_medical_status_reason import build_medical_status_reason
from osah.domain.services.format_medical_decision_label import format_medical_decision_label
from osah.domain.services.format_medical_status_label import format_medical_status_label
from osah.domain.services.format_ui_date import format_ui_date
from osah.ui.qt.components.ensure_table_column_width import ensure_table_column_width
from osah.ui.qt.components.scrollable_table_frame import ScrollableTableFrame
from osah.ui.qt.design.tokens import COLOR, SPACING


class EmployeeMedicalTab(QWidget):
    """Реальна вкладка медицини у картці працівника.
    Real medical admission tab inside an employee card.
    """

    record_requested = Signal(str, int)

    def __init__(self, records: tuple[MedicalRecord, ...]) -> None:
        super().__init__()
        self._records = records
        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACING["lg"], SPACING["lg"], SPACING["lg"], SPACING["lg"])
        layout.setSpacing(SPACING["md"])
        title = QLabel("Меддопуск працівника")
        title.setStyleSheet("font-size: 14px; font-weight: 900;")
        layout.addWidget(title)

        if not records:
            empty = QLabel("Медичних записів немає. Потрібно перевірити актуальний допуск до робіт.")
            empty.setWordWrap(True)
            empty.setStyleSheet(f"color: {COLOR['warning']}; font-weight: 700;")
            layout.addWidget(empty)
            layout.addStretch()
            return

        table = QTableWidget(0, 6)
        table.itemClicked.connect(self._emit_record_request)
        table.setHorizontalHeaderLabels(["Початок", "Закінчення", "Рішення", "Обмеження", "Статус", "Причина"])
        table.verticalHeader().setVisible(False)
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        table.setAlternatingRowColors(True)

        for record in records:
            row_index = table.rowCount()
            table.insertRow(row_index)
            values = (
                format_ui_date(record.valid_from),
                format_ui_date(record.valid_until),
                format_medical_decision_label(record.medical_decision),
                record.restriction_note or "-",
                format_medical_status_label(record.status),
                build_medical_status_reason(record),
            )
            for column, value in enumerate(values):
                item = QTableWidgetItem(value)
                item.setData(Qt.ItemDataRole.UserRole, row_index)
                table.setItem(row_index, column, item)

        table.resizeColumnsToContents()
        ensure_table_column_width(table, 4)
        layout.addWidget(ScrollableTableFrame(table))

    def _emit_record_request(self, item: QTableWidgetItem) -> None:
        """Переходить до конкретного медичного запису з картки працівника.
        Navigates to a concrete medical record from the employee card.
        """

        row_index_data = item.data(Qt.ItemDataRole.UserRole)
        row_index = int(row_index_data) if row_index_data is not None else -1
        if 0 <= row_index < len(self._records):
            record = self._records[row_index]
            if record.record_id is not None:
                self.record_requested.emit(record.employee_personnel_number, record.record_id)


def build_medical_history_hint(records: tuple[MedicalRecord, ...]) -> str:
    """Повертає коротку підказку про історію медичних записів.
    Returns a short hint about medical record history.
    """

    return f"Записів у медичній історії: {len(records)}"

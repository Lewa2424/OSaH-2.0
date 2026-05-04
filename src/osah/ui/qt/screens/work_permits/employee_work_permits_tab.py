from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QAbstractItemView, QLabel, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget

from osah.domain.entities.work_permit_record import WorkPermitRecord
from osah.domain.services.build_work_permit_status_reason import build_work_permit_status_reason
from osah.domain.services.format_ui_datetime import format_ui_datetime
from osah.domain.services.format_work_permit_status_label import format_work_permit_status_label
from osah.ui.qt.components.ensure_table_column_width import ensure_table_column_width
from osah.ui.qt.components.scrollable_table_frame import ScrollableTableFrame
from osah.ui.qt.design.tokens import COLOR, SPACING


class EmployeeWorkPermitsTab(QWidget):
    """Реальна вкладка нарядів-допусків у картці працівника.
    Real work permits tab inside an employee card.
    """

    record_requested = Signal(str, int)

    def __init__(self, employee_personnel_number: str, records: tuple[WorkPermitRecord, ...]) -> None:
        super().__init__()
        self._employee_personnel_number = employee_personnel_number
        self._records = records
        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACING["lg"], SPACING["lg"], SPACING["lg"], SPACING["lg"])
        layout.setSpacing(SPACING["md"])
        title = QLabel("Наряди-допуски працівника")
        title.setStyleSheet("font-size: 14px; font-weight: 900;")
        layout.addWidget(title)
        if not records:
            empty = QLabel("Активних або історичних нарядів-допусків для працівника не знайдено.")
            empty.setWordWrap(True)
            empty.setStyleSheet(f"color: {COLOR['text_secondary']}; font-weight: 700;")
            layout.addWidget(empty)
            layout.addStretch()
            return

        table = QTableWidget(0, 6)
        table.itemClicked.connect(self._emit_record_request)
        table.setHorizontalHeaderLabels(["№", "Вид робіт", "Місце", "Завершення", "Статус", "Причина"])
        table.verticalHeader().setVisible(False)
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        for record in records:
            row_index = table.rowCount()
            table.insertRow(row_index)
            values = (
                record.permit_number,
                record.work_kind,
                record.work_location,
                format_ui_datetime(record.ends_at),
                format_work_permit_status_label(record.status),
                build_work_permit_status_reason(record),
            )
            for column, value in enumerate(values):
                item = QTableWidgetItem(value)
                item.setData(Qt.ItemDataRole.UserRole, row_index)
                table.setItem(row_index, column, item)
        table.resizeColumnsToContents()
        ensure_table_column_width(table, 4)
        layout.addWidget(ScrollableTableFrame(table))

    def _emit_record_request(self, item: QTableWidgetItem) -> None:
        """Переходить до конкретного наряду-допуску з картки працівника.
        Navigates to a concrete work permit from the employee card.
        """

        row_index_data = item.data(Qt.ItemDataRole.UserRole)
        row_index = int(row_index_data) if row_index_data is not None else -1
        if 0 <= row_index < len(self._records):
            record = self._records[row_index]
            if record.record_id is not None:
                self.record_requested.emit(self._employee_personnel_number, record.record_id)

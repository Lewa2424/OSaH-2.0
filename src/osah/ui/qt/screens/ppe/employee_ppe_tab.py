from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QAbstractItemView, QLabel, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget

from osah.domain.entities.ppe_record import PpeRecord
from osah.domain.services.build_ppe_status_reason import build_ppe_status_reason
from osah.domain.services.format_ppe_status_label import format_ppe_status_label
from osah.domain.services.format_ui_date import format_ui_date
from osah.ui.qt.components.ensure_table_column_width import ensure_table_column_width
from osah.ui.qt.components.scrollable_table_frame import ScrollableTableFrame
from osah.ui.qt.design.tokens import COLOR, SPACING


class EmployeePpeTab(QWidget):
    """Реальна вкладка ЗІЗ у картці працівника.
    Real PPE tab inside an employee card.
    """

    record_requested = Signal(str, int)

    def __init__(self, records: tuple[PpeRecord, ...]) -> None:
        super().__init__()
        self._records = records
        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACING["lg"], SPACING["lg"], SPACING["lg"], SPACING["lg"])
        layout.setSpacing(SPACING["md"])
        title = QLabel("ЗІЗ працівника")
        title.setStyleSheet("font-size: 14px; font-weight: 900;")
        layout.addWidget(title)
        if not records:
            empty = QLabel("Записів ЗІЗ немає. Потрібно перевірити забезпечення за нормами.")
            empty.setWordWrap(True)
            empty.setStyleSheet(f"color: {COLOR['warning']}; font-weight: 700;")
            layout.addWidget(empty)
            layout.addStretch()
            return

        table = QTableWidget(0, 6)
        self._table = table
        table.setHorizontalHeaderLabels(["ЗІЗ", "Положено", "Видано", "К-сть", "Заміна", "Статус"])
        table.verticalHeader().setVisible(False)
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        table.itemClicked.connect(self._emit_record_request)
        for record in records:
            row_index = table.rowCount()
            table.insertRow(row_index)
            values = (
                record.ppe_name,
                "Так" if record.is_required else "Ні",
                "Так" if record.is_issued else "Ні",
                str(record.quantity),
                format_ui_date(record.replacement_date),
                f"{format_ppe_status_label(record.status)} - {build_ppe_status_reason(record)}",
            )
            for column, value in enumerate(values):
                item = QTableWidgetItem(value)
                item.setData(Qt.ItemDataRole.UserRole, row_index)
                table.setItem(row_index, column, item)
        table.resizeColumnsToContents()
        ensure_table_column_width(table, 5)
        layout.addWidget(ScrollableTableFrame(table))

    def _emit_record_request(self, item: QTableWidgetItem) -> None:
        """Переходить до конкретного запису ЗІЗ за кліком у картці працівника.
        Navigates to a concrete PPE record on click from the employee card.
        """

        row_index_data = item.data(Qt.ItemDataRole.UserRole)
        row_index = int(row_index_data) if row_index_data is not None else -1
        if 0 <= row_index < len(self._records):
            record = self._records[row_index]
            if record.record_id is not None:
                self.record_requested.emit(record.employee_personnel_number, record.record_id)

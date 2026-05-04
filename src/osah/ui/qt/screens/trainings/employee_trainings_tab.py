from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QAbstractItemView, QLabel, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget

from osah.domain.entities.employee import Employee
from osah.domain.entities.training_record import TrainingRecord
from osah.domain.services.build_training_workspace_rows import build_training_workspace_rows
from osah.domain.services.format_ui_date import format_ui_date
from osah.ui.qt.components.ensure_table_column_width import ensure_table_column_width
from osah.ui.qt.components.scrollable_table_frame import ScrollableTableFrame
from osah.ui.qt.design.tokens import COLOR, SPACING


class EmployeeTrainingsTab(QWidget):
    """Реальна вкладка інструктажів у картці працівника.
    Real trainings tab inside an employee card.
    """

    record_requested = Signal(str, object)

    def __init__(self, employee: Employee, records: tuple[TrainingRecord, ...]) -> None:
        super().__init__()
        self._employee = employee
        self._rows = rows = build_training_workspace_rows((employee,), records)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACING["lg"], SPACING["lg"], SPACING["lg"], SPACING["lg"])
        layout.setSpacing(SPACING["md"])

        title = QLabel("Інструктажі працівника")
        title.setStyleSheet("font-size: 14px; font-weight: 900;")
        layout.addWidget(title)

        if not rows:
            empty = QLabel("Записів інструктажів немає. Потрібно створити первинний запис.")
            empty.setWordWrap(True)
            empty.setStyleSheet(f"color: {COLOR['critical']}; font-weight: 700;")
            layout.addWidget(empty)
            layout.addStretch()
            return

        table = QTableWidget(0, 5)
        table.itemClicked.connect(self._emit_record_request)
        table.setHorizontalHeaderLabels(["Тип", "Проведено", "Наст. строк", "Статус", "Проводив"])
        table.verticalHeader().setVisible(False)
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        for row in rows:
            row_index = table.rowCount()
            table.insertRow(row_index)
            values = (
                row.training_type_label,
                format_ui_date(row.event_date),
                format_ui_date(row.next_control_date),
                f"{row.status_label} - {row.status_reason.replace(chr(10), ' ')}",
                row.conducted_by,
            )
            for column, value in enumerate(values):
                item = QTableWidgetItem(value)
                item.setData(Qt.ItemDataRole.UserRole, row_index)
                table.setItem(row_index, column, item)
        table.resizeColumnsToContents()
        ensure_table_column_width(table, 3)
        layout.addWidget(ScrollableTableFrame(table))

    def _emit_record_request(self, item: QTableWidgetItem) -> None:
        """Переходить до конкретного запису інструктажу або до фільтра працівника.
        Navigates to a concrete training record or falls back to employee-filtered view.
        """

        row_index_data = item.data(Qt.ItemDataRole.UserRole)
        row_index = int(row_index_data) if row_index_data is not None else -1
        if 0 <= row_index < len(self._rows):
            row = self._rows[row_index]
            self.record_requested.emit(self._employee.personnel_number, row.record_id)

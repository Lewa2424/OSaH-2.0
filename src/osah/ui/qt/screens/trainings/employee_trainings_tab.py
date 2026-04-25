from PySide6.QtWidgets import QAbstractItemView, QLabel, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget

from osah.domain.entities.training_record import TrainingRecord
from osah.domain.services.build_training_status_reason import build_training_status_reason
from osah.domain.services.format_training_status_label import format_training_status_label
from osah.domain.services.format_training_type_label import format_training_type_label
from osah.domain.services.format_ui_date import format_ui_date
from osah.ui.qt.components.ensure_table_column_width import ensure_table_column_width
from osah.ui.qt.components.scrollable_table_frame import ScrollableTableFrame
from osah.ui.qt.design.tokens import COLOR, SPACING


class EmployeeTrainingsTab(QWidget):
    """Реальна вкладка інструктажів у картці працівника.
    Real trainings tab inside an employee card.
    """

    def __init__(self, records: tuple[TrainingRecord, ...]) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACING["lg"], SPACING["lg"], SPACING["lg"], SPACING["lg"])
        layout.setSpacing(SPACING["md"])

        title = QLabel("Інструктажі працівника")
        title.setStyleSheet("font-size: 14px; font-weight: 900;")
        layout.addWidget(title)

        if not records:
            empty = QLabel("Записів інструктажів немає. Потрібно створити первинний запис.")
            empty.setWordWrap(True)
            empty.setStyleSheet(f"color: {COLOR['critical']}; font-weight: 700;")
            layout.addWidget(empty)
            layout.addStretch()
            return

        table = QTableWidget(0, 5)
        table.setHorizontalHeaderLabels(["Тип", "Проведено", "Наст. строк", "Статус", "Проводив"])
        table.verticalHeader().setVisible(False)
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        for record in records:
            row_index = table.rowCount()
            table.insertRow(row_index)
            values = (
                format_training_type_label(record.training_type),
                format_ui_date(record.event_date),
                format_ui_date(record.next_control_date),
                f"{format_training_status_label(record.status)} - {build_training_status_reason(record.status, record.training_type, record.next_control_date)}",
                record.conducted_by,
            )
            for column, value in enumerate(values):
                table.setItem(row_index, column, QTableWidgetItem(value))
        table.resizeColumnsToContents()
        ensure_table_column_width(table, 3)
        layout.addWidget(ScrollableTableFrame(table))

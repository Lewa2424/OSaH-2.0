from PySide6.QtWidgets import QAbstractItemView, QLabel, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget

from osah.domain.entities.work_permit_record import WorkPermitRecord
from osah.domain.services.build_work_permit_status_reason import build_work_permit_status_reason
from osah.domain.services.format_work_permit_status_label import format_work_permit_status_label
from osah.ui.qt.design.tokens import COLOR, SPACING


class EmployeeWorkPermitsTab(QWidget):
    """Реальна вкладка нарядів-допусків у картці працівника.
    Real work permits tab inside an employee card.
    """

    def __init__(self, records: tuple[WorkPermitRecord, ...]) -> None:
        super().__init__()
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
                record.ends_at,
                format_work_permit_status_label(record.status),
                build_work_permit_status_reason(record),
            )
            for column, value in enumerate(values):
                table.setItem(row_index, column, QTableWidgetItem(value))
        table.resizeColumnsToContents()
        layout.addWidget(table)

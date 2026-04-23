from PySide6.QtWidgets import QAbstractItemView, QLabel, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget

from osah.domain.entities.medical_record import MedicalRecord
from osah.domain.services.build_medical_status_reason import build_medical_status_reason
from osah.domain.services.format_medical_decision_label import format_medical_decision_label
from osah.domain.services.format_medical_status_label import format_medical_status_label
from osah.ui.qt.design.tokens import COLOR, SPACING


class EmployeeMedicalTab(QWidget):
    """Реальна вкладка медицини у картці працівника.
    Real medical admission tab inside an employee card.
    """

    def __init__(self, records: tuple[MedicalRecord, ...]) -> None:
        super().__init__()
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
        table.setHorizontalHeaderLabels(["Початок", "Закінчення", "Рішення", "Обмеження", "Статус", "Причина"])
        table.verticalHeader().setVisible(False)
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        table.setAlternatingRowColors(True)

        for record in records:
            row_index = table.rowCount()
            table.insertRow(row_index)
            values = (
                record.valid_from,
                record.valid_until,
                format_medical_decision_label(record.medical_decision),
                record.restriction_note or "-",
                format_medical_status_label(record.status),
                build_medical_status_reason(record),
            )
            for column, value in enumerate(values):
                table.setItem(row_index, column, QTableWidgetItem(value))

        table.resizeColumnsToContents()
        layout.addWidget(table)


# ###### ФОРМАТУВАННЯ ІСТОРІЇ / HISTORY FORMAT ######
def build_medical_history_hint(records: tuple[MedicalRecord, ...]) -> str:
    """Повертає коротку підказку про історію медичних записів.
    Returns a short hint about medical record history.
    """

    return f"Записів у медичній історії: {len(records)}"

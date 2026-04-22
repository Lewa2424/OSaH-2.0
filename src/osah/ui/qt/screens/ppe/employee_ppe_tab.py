from PySide6.QtWidgets import QAbstractItemView, QLabel, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget

from osah.domain.entities.ppe_record import PpeRecord
from osah.domain.services.build_ppe_status_reason import build_ppe_status_reason
from osah.domain.services.format_ppe_status_label import format_ppe_status_label
from osah.ui.qt.design.tokens import COLOR, SPACING


class EmployeePpeTab(QWidget):
    """Реальна вкладка ЗІЗ у картці працівника.
    Real PPE tab inside an employee card.
    """

    def __init__(self, records: tuple[PpeRecord, ...]) -> None:
        super().__init__()
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
        table.setHorizontalHeaderLabels(["ЗІЗ", "Положено", "Видано", "К-сть", "Заміна", "Статус"])
        table.verticalHeader().setVisible(False)
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        for record in records:
            row_index = table.rowCount()
            table.insertRow(row_index)
            values = (
                record.ppe_name,
                "Так" if record.is_required else "Ні",
                "Так" if record.is_issued else "Ні",
                str(record.quantity),
                record.replacement_date,
                f"{format_ppe_status_label(record.status)} - {build_ppe_status_reason(record)}",
            )
            for column, value in enumerate(values):
                table.setItem(row_index, column, QTableWidgetItem(value))
        table.resizeColumnsToContents()
        layout.addWidget(table)

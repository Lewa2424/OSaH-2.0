from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QAbstractItemView, QTableWidget, QTableWidgetItem

from osah.domain.entities.medical_status import MedicalStatus
from osah.domain.entities.medical_workspace_row import MedicalWorkspaceRow
from osah.ui.qt.design.tokens import COLOR
from osah.ui.qt.screens.medical.medical_status_badge import MedicalStatusBadge


class MedicalRegistryTable(QTableWidget):
    """Central medical admission registry."""

    row_selected = Signal(object)

    def __init__(self) -> None:
        super().__init__(0, 8)
        self._rows: tuple[MedicalWorkspaceRow, ...] = ()
        self.setHorizontalHeaderLabels(["ПІБ", "Підрозділ", "Посада", "Рішення", "До", "Обмеження", "Статус", "Причина"])
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setAlternatingRowColors(True)
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setStretchLastSection(True)
        self.itemSelectionChanged.connect(self._emit_selected_row)

    def set_rows(self, rows: tuple[MedicalWorkspaceRow, ...]) -> None:
        """###### ЗАПОВНЕННЯ РЕЄСТРУ / POPULATE REGISTRY ######"""

        self._rows = rows
        self.setRowCount(0)
        for row_index, row in enumerate(rows):
            self.insertRow(row_index)
            for column, text in enumerate(
                (
                    row.employee_full_name,
                    row.department_name,
                    row.position_name,
                    row.decision_label,
                    row.valid_until,
                    "Так" if row.has_restriction else "Ні",
                )
            ):
                self._set_item(row_index, column, text, row)
            self.setCellWidget(row_index, 6, MedicalStatusBadge(row.status, row.status_label))
            self._set_item(row_index, 7, row.status_reason, row)
            self.setRowHeight(row_index, 38)
        self.resizeColumnsToContents()

    def select_first(self) -> None:
        """###### ВИБІР ПЕРШОГО РЯДКА / SELECT FIRST ROW ######"""

        if self.rowCount():
            self.selectRow(0)

    def _set_item(self, row_index: int, column_index: int, text: str, row: MedicalWorkspaceRow) -> None:
        """###### КОМІРКА РЕЄСТРУ / REGISTRY CELL ######"""

        item = QTableWidgetItem(text)
        item.setData(Qt.ItemDataRole.UserRole, row_index)
        if row.status in {MedicalStatus.EXPIRED, MedicalStatus.NOT_FIT}:
            item.setForeground(QColor(COLOR["critical"]))
        elif row.status == MedicalStatus.WARNING:
            item.setForeground(QColor(COLOR["warning"]))
        elif row.status == MedicalStatus.RESTRICTED:
            item.setForeground(QColor(COLOR["restricted"]))
        self.setItem(row_index, column_index, item)

    def _emit_selected_row(self) -> None:
        """###### СИГНАЛ ВИБОРУ / SELECTION SIGNAL ######"""

        selected = self.selectedItems()
        if selected:
            row_index = selected[0].row()
            if 0 <= row_index < len(self._rows):
                self.row_selected.emit(self._rows[row_index])

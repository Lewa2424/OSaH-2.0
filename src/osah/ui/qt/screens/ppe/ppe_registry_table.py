from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QAbstractItemView, QTableWidget, QTableWidgetItem

from osah.domain.entities.ppe_status import PpeStatus
from osah.domain.entities.ppe_workspace_row import PpeWorkspaceRow
from osah.domain.services.format_ui_date import format_ui_date
from osah.ui.qt.components.ensure_table_column_width import ensure_table_column_width
from osah.ui.qt.design.tokens import COLOR
from osah.ui.qt.screens.ppe.ppe_status_badge import PpeStatusBadge


class PpeRegistryTable(QTableWidget):
    """Центральний реєстр позицій ЗІЗ.
    Central PPE item registry.
    """

    row_selected = Signal(object)

    def __init__(self) -> None:
        super().__init__(0, 8)
        self._rows: tuple[PpeWorkspaceRow, ...] = ()
        self.setHorizontalHeaderLabels(["ПІБ", "Підрозділ", "ЗІЗ", "К-сть", "Видано", "Заміна", "Статус", "Причина"])
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setAlternatingRowColors(True)
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setStretchLastSection(False)
        self.itemSelectionChanged.connect(self._emit_selected_row)

    def set_rows(self, rows: tuple[PpeWorkspaceRow, ...]) -> None:
        """Перемальовує таблицю за підготовленими рядками.
        Redraws the table with prepared rows.
        """

        self._rows = rows
        self.setRowCount(0)
        for row_index, row in enumerate(rows):
            self.insertRow(row_index)
            for column, text in enumerate(
                (
                    row.employee_full_name,
                    row.department_name,
                    row.ppe_name,
                    str(row.quantity),
                    "Так" if row.is_issued else "Ні",
                    format_ui_date(row.replacement_date),
                )
            ):
                self._set_item(row_index, column, text, row)
            self.setCellWidget(row_index, 6, PpeStatusBadge(row.status, row.status_label))
            self._set_item(row_index, 7, row.status_reason, row)
            self.setRowHeight(row_index, 38)
        self.resizeColumnsToContents()
        ensure_table_column_width(self, 6)
        ensure_table_column_width(self, 7, max_width=500)

    def select_first(self) -> None:
        """Виділяє перший рядок, якщо таблиця не порожня.
        Selects the first row when the table is not empty.
        """

        if self.rowCount():
            self.selectRow(0)

    def _set_item(self, row_index: int, column_index: int, text: str, row: PpeWorkspaceRow) -> None:
        """Додає текстову комірку з візуальним акцентом статусу.
        Adds a text cell with status visual accent.
        """

        item = QTableWidgetItem(text)
        item.setData(Qt.ItemDataRole.UserRole, row_index)
        item.setToolTip(text)
        if row.status in {PpeStatus.EXPIRED, PpeStatus.NOT_ISSUED}:
            item.setForeground(QColor(COLOR["critical"]))
        elif row.status == PpeStatus.WARNING:
            item.setForeground(QColor(COLOR["warning"]))
        self.setItem(row_index, column_index, item)

    def _emit_selected_row(self) -> None:
        """Передає вибраний рядок у detail-pane.
        Emits the selected row to the detail pane.
        """

        selected = self.selectedItems()
        if selected:
            row_index = selected[0].row()
            if 0 <= row_index < len(self._rows):
                self.row_selected.emit(self._rows[row_index])

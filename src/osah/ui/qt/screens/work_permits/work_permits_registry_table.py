from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QAbstractItemView, QTableWidget, QTableWidgetItem

from osah.domain.entities.work_permit_status import WorkPermitStatus
from osah.domain.entities.work_permit_workspace_row import WorkPermitWorkspaceRow
from osah.ui.qt.design.tokens import COLOR
from osah.ui.qt.screens.work_permits.work_permit_status_badge import WorkPermitStatusBadge


class WorkPermitsRegistryTable(QTableWidget):
    """Центральний реєстр нарядів-допусків.
    Central work permits registry table.
    """

    row_selected = Signal(object)

    def __init__(self) -> None:
        super().__init__(0, 9)
        self._rows: tuple[WorkPermitWorkspaceRow, ...] = ()
        self.setHorizontalHeaderLabels(["№", "Вид робіт", "Місце", "Початок", "Завершення", "Статус", "Відповідальний", "Учасн.", "Причина"])
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setAlternatingRowColors(True)
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setStretchLastSection(True)
        self.itemSelectionChanged.connect(self._emit_selected_row)

    # ###### ЗАПОВНЕННЯ ТАБЛИЦІ / SET ROWS ######
    def set_rows(self, rows: tuple[WorkPermitWorkspaceRow, ...]) -> None:
        """Перемальовує таблицю за підготовленими рядками.
        Redraws the table with prepared rows.
        """

        self._rows = rows
        self.setRowCount(0)
        for row_index, row in enumerate(rows):
            self.insertRow(row_index)
            for column, text in enumerate(
                (
                    row.permit_number,
                    row.work_kind,
                    row.work_location,
                    row.starts_at,
                    row.ends_at,
                )
            ):
                self._set_item(row_index, column, text, row)
            self.setCellWidget(row_index, 5, WorkPermitStatusBadge(row.status, row.status_label))
            for column, text in enumerate(
                (
                    row.responsible_person,
                    str(row.participant_count),
                    _build_reason_text(row),
                ),
                start=6,
            ):
                self._set_item(row_index, column, text, row)
            self.setRowHeight(row_index, 38)
        self.resizeColumnsToContents()

    # ###### ВИБІР ПЕРШОГО РЯДКА / SELECT FIRST ######
    def select_first(self) -> None:
        """Виділяє перший рядок, якщо таблиця не порожня.
        Selects the first row when the table is not empty.
        """

        if self.rowCount():
            self.selectRow(0)

    # ###### КОМІРКА / CELL ######
    def _set_item(self, row_index: int, column_index: int, text: str, row: WorkPermitWorkspaceRow) -> None:
        """Додає текстову комірку з візуальним акцентом статусу.
        Adds a text cell with status visual accent.
        """

        item = QTableWidgetItem(text)
        item.setData(Qt.ItemDataRole.UserRole, row_index)
        if row.status in {WorkPermitStatus.EXPIRED, WorkPermitStatus.INVALID} or row.has_conflicts:
            item.setForeground(QColor(COLOR["critical"]))
        elif row.status == WorkPermitStatus.WARNING:
            item.setForeground(QColor(COLOR["warning"]))
        elif row.status == WorkPermitStatus.CLOSED:
            item.setForeground(QColor(COLOR["text_muted"]))
        self.setItem(row_index, column_index, item)

    # ###### ПЕРЕДАЧА ВИБОРУ / EMIT SELECTION ######
    def _emit_selected_row(self) -> None:
        """Передає вибраний рядок у detail-pane.
        Emits the selected row to the detail pane.
        """

        selected = self.selectedItems()
        if selected:
            row_index = selected[0].row()
            if 0 <= row_index < len(self._rows):
                self.row_selected.emit(self._rows[row_index])


# ###### ТЕКСТ ПРИЧИНИ / REASON TEXT ######
def _build_reason_text(row: WorkPermitWorkspaceRow) -> str:
    """Повертає причину статусу разом із конфліктами учасників.
    Returns status reason together with participant conflicts.
    """

    if row.conflict_reasons:
        return f"{row.status_reason}; конфлікти: {len(row.conflict_reasons)}"
    return row.status_reason

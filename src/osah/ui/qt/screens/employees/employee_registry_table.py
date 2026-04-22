from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QAbstractItemView, QTableWidget, QTableWidgetItem

from osah.domain.entities.employee_status_level import EmployeeStatusLevel
from osah.domain.entities.employee_workspace_row import EmployeeWorkspaceRow
from osah.ui.qt.design.tokens import COLOR
from osah.ui.qt.screens.employees.employee_row_state_badge import EmployeeRowStateBadge


class EmployeeRegistryTable(QTableWidget):
    """Центральний компактний реєстр працівників.
    Central compact employee registry.
    """

    employee_selected = Signal(str)

    def __init__(self) -> None:
        super().__init__(0, 9)
        self._rows_by_personnel_number: dict[str, EmployeeWorkspaceRow] = {}
        self.setHorizontalHeaderLabels(
            ["ПІБ", "Таб. №", "Підрозділ", "Посада", "Статус", "Інструктажі", "ЗІЗ", "Медицина", "НД"]
        )
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setAlternatingRowColors(True)
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setStretchLastSection(True)
        self.itemSelectionChanged.connect(self._emit_selected_employee)

    # ###### ЗАПОВНЕННЯ РЕЄСТРУ / POPULATE REGISTRY ######
    def set_rows(self, rows: tuple[EmployeeWorkspaceRow, ...]) -> None:
        """Перемальовує таблицю за переданими рядками робочої моделі.
        Redraws the table from provided workspace rows.
        """

        self.setRowCount(0)
        self._rows_by_personnel_number = {row.employee.personnel_number: row for row in rows}

        for row_index, row in enumerate(rows):
            self.insertRow(row_index)
            self._set_text_item(row_index, 0, row.employee.full_name, row)
            self._set_text_item(row_index, 1, row.employee.personnel_number, row)
            self._set_text_item(row_index, 2, row.department_name, row)
            self._set_text_item(row_index, 3, row.position_name, row)
            self.setCellWidget(row_index, 4, EmployeeRowStateBadge(row.status_level, row.status_label))

            for module_index, summary in enumerate(row.module_summaries):
                self._set_text_item(row_index, 5 + module_index, f"{summary.label}: {summary.reason}", row)

            self.setRowHeight(row_index, 38)

        self.resizeColumnsToContents()

    # ###### ВИБІР ПРАЦІВНИКА / SELECT EMPLOYEE ######
    def select_employee(self, personnel_number: str) -> None:
        """Виділяє працівника за табельним номером, якщо він є у поточному реєстрі.
        Selects an employee by personnel number when present in the current registry.
        """

        for row_index in range(self.rowCount()):
            item = self.item(row_index, 1)
            if item and item.text() == personnel_number:
                self.selectRow(row_index)
                self.scrollToItem(item)
                return

    # ###### ПОТОЧНИЙ РЯДОК / CURRENT ROW MODEL ######
    def current_employee_row(self) -> EmployeeWorkspaceRow | None:
        """Повертає модель вибраного працівника або None.
        Returns selected employee model or None.
        """

        selected = self.selectedItems()
        if not selected:
            return None
        personnel_number = self.item(selected[0].row(), 1).text()
        return self._rows_by_personnel_number.get(personnel_number)

    def _set_text_item(self, row_index: int, column_index: int, text: str, row: EmployeeWorkspaceRow) -> None:
        """Додає текстову комірку таблиці з прив'язкою до працівника.
        Adds a text table cell bound to an employee row.
        """

        item = QTableWidgetItem(text)
        item.setData(Qt.ItemDataRole.UserRole, row.employee.personnel_number)
        if row.status_level == EmployeeStatusLevel.CRITICAL:
            item.setForeground(QColor(COLOR["critical"]))
        elif row.status_level == EmployeeStatusLevel.WARNING:
            item.setForeground(QColor(COLOR["warning"]))
        elif row.status_level == EmployeeStatusLevel.RESTRICTED:
            item.setForeground(QColor("#4338CA"))
        self.setItem(row_index, column_index, item)

    def _emit_selected_employee(self) -> None:
        """Передає табельний номер вибраного працівника назовні.
        Emits the selected employee personnel number.
        """

        selected_row = self.current_employee_row()
        if selected_row:
            self.employee_selected.emit(selected_row.employee.personnel_number)

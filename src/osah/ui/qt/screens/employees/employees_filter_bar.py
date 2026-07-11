from PySide6.QtCore import Signal
from PySide6.QtWidgets import QCheckBox, QComboBox, QHBoxLayout, QLineEdit, QPushButton, QWidget

from osah.domain.entities.employee_status_level import EmployeeStatusLevel
from osah.domain.entities.employee_workspace import EmployeeWorkspace
from osah.ui.qt.design.tokens import COLOR, RADIUS, SPACING


class EmployeesFilterBar(QWidget):
    """Top search and filter bar for the employees module. / Верхняя панель поиска и фильтров модуля работников."""

    filters_changed = Signal()

    def __init__(self, workspace: EmployeeWorkspace) -> None:
        super().__init__()
        self.setObjectName("employeesFilterBar")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(SPACING["md"], SPACING["md"], SPACING["md"], SPACING["md"])
        layout.setSpacing(SPACING["sm"])

        self.setStyleSheet(
            f"""
            QWidget#employeesFilterBar {{
                background: {COLOR['bg_card']};
                border: 1px solid {COLOR['border_soft']};
                border-radius: {RADIUS['xl']}px;
            }}
            QWidget#employeesFilterBar QLineEdit,
            QWidget#employeesFilterBar QComboBox {{
                min-height: 40px;
                padding: 0 14px;
                border-radius: 14px;
            }}
            QWidget#employeesFilterBar QCheckBox {{
                font-size: 13px;
                font-weight: 700;
                color: {COLOR['text_secondary']};
                spacing: 8px;
            }}
            QWidget#employeesFilterBar QCheckBox::indicator {{
                width: 16px;
                height: 16px;
                border-radius: 5px;
                border: 1px solid {COLOR['input_border']};
                background: {COLOR['bg_card']};
            }}
            QWidget#employeesFilterBar QCheckBox::indicator:checked {{
                background: {COLOR['accent']};
                border: 1px solid {COLOR['accent']};
            }}
            QWidget#employeesFilterBar QPushButton {{
                min-height: 40px;
                border-radius: 14px;
            }}
            """
        )

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Пошук: ПІБ, табельний, посада, підрозділ, участок")
        self.search_input.textChanged.connect(lambda _text: self.filters_changed.emit())
        layout.addWidget(self.search_input, stretch=3)

        self.department_filter = QComboBox()
        self.department_filter.addItem("Усі підрозділи", "")
        for department in sorted({row.department_name for row in workspace.rows}):
            self.department_filter.addItem(department, department)
        self.department_filter.currentIndexChanged.connect(lambda _index: self.filters_changed.emit())
        layout.addWidget(self.department_filter, stretch=1)

        self.position_filter = QComboBox()
        self.position_filter.addItem("Усі посади", "")
        for position in sorted({row.position_name for row in workspace.rows}):
            self.position_filter.addItem(position, position)
        self.position_filter.currentIndexChanged.connect(lambda _index: self.filters_changed.emit())
        layout.addWidget(self.position_filter, stretch=1)

        self.status_filter = QComboBox()
        self.status_filter.addItem("Усі статуси", "")
        for level, label in (
            (EmployeeStatusLevel.NORMAL, "Норма"),
            (EmployeeStatusLevel.WARNING, "Увага"),
            (EmployeeStatusLevel.CRITICAL, "Критично"),
            (EmployeeStatusLevel.RESTRICTED, "Обмежено"),
            (EmployeeStatusLevel.ARCHIVED, "Архів"),
        ):
            self.status_filter.addItem(label, level.value)
        self.status_filter.currentIndexChanged.connect(lambda _index: self.filters_changed.emit())
        layout.addWidget(self.status_filter)

        self.critical_only = QCheckBox("Критика")
        self.critical_only.stateChanged.connect(lambda _state: self.filters_changed.emit())
        layout.addWidget(self.critical_only)

        self.warning_only = QCheckBox("Увага")
        self.warning_only.stateChanged.connect(lambda _state: self.filters_changed.emit())
        layout.addWidget(self.warning_only)

        self._reset_button = QPushButton("Скинути")
        self._reset_button.setProperty("variant", "secondary")
        self._reset_button.clicked.connect(self.reset_filters)
        layout.addWidget(self._reset_button)

    def set_workspace(self, workspace: EmployeeWorkspace) -> None:
        """Updates department and position filter choices from a new workspace. / Обновляет списки подразделений и должностей."""

        current_search = self.search_input.text()
        current_department = self.department_filter.currentData() or ""
        current_position = self.position_filter.currentData() or ""

        self.department_filter.blockSignals(True)
        self.position_filter.blockSignals(True)
        self.department_filter.clear()
        self.position_filter.clear()

        self.department_filter.addItem("Усі підрозділи", "")
        for department_name in sorted({row.department_name for row in workspace.rows}):
            self.department_filter.addItem(department_name, department_name)

        self.position_filter.addItem("Усі посади", "")
        for position_name in sorted({row.position_name for row in workspace.rows}):
            self.position_filter.addItem(position_name, position_name)

        department_index = self.department_filter.findData(current_department)
        self.department_filter.setCurrentIndex(department_index if department_index >= 0 else 0)

        position_index = self.position_filter.findData(current_position)
        self.position_filter.setCurrentIndex(position_index if position_index >= 0 else 0)

        self.department_filter.blockSignals(False)
        self.position_filter.blockSignals(False)
        self.search_input.setText(current_search)

    def reset_filters(self) -> None:
        """Returns all filters to the initial state. / Сбрасывает все фильтры в исходное состояние."""

        self.search_input.clear()
        self.department_filter.setCurrentIndex(0)
        self.position_filter.setCurrentIndex(0)
        self.status_filter.setCurrentIndex(0)
        self.critical_only.setChecked(False)
        self.warning_only.setChecked(False)
        self.filters_changed.emit()

    def set_department_filter(self, department_name: str) -> None:
        """Activates the department filter from the structure tree. / Активирует фильтр подразделения из дерева."""

        index = self.department_filter.findData(department_name)
        if index >= 0:
            self.department_filter.setCurrentIndex(index)

    def set_position_filter(self, position_name: str) -> None:
        """Activates the position filter from the structure tree. / Активирует фильтр должности из дерева."""

        index = self.position_filter.findData(position_name)
        if index >= 0:
            self.position_filter.setCurrentIndex(index)

    def values(self) -> dict[str, object]:
        """Returns current filter state as a dictionary. / Возвращает текущее состояние фильтров."""

        return {
            "search": self.search_input.text().strip().lower(),
            "department": self.department_filter.currentData() or "",
            "position": self.position_filter.currentData() or "",
            "status": self.status_filter.currentData() or "",
            "critical_only": self.critical_only.isChecked(),
            "warning_only": self.warning_only.isChecked(),
        }

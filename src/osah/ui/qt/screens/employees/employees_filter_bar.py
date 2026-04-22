from PySide6.QtCore import Signal
from PySide6.QtWidgets import QCheckBox, QComboBox, QHBoxLayout, QLineEdit, QPushButton, QWidget

from osah.domain.entities.employee_status_level import EmployeeStatusLevel
from osah.domain.entities.employee_workspace import EmployeeWorkspace
from osah.ui.qt.design.tokens import SPACING


class EmployeesFilterBar(QWidget):
    """Верхня панель пошуку і фільтрів модуля працівників.
    Top search and filter bar for the employees module.
    """

    filters_changed = Signal()

    def __init__(self, workspace: EmployeeWorkspace) -> None:
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING["sm"])

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Пошук: ПІБ, табельний, посада, підрозділ, участок")
        self.search_input.textChanged.connect(self.filters_changed.emit)
        layout.addWidget(self.search_input, stretch=3)

        self.department_filter = QComboBox()
        self.department_filter.addItem("Усі підрозділи", "")
        for department in sorted({row.department_name for row in workspace.rows}):
            self.department_filter.addItem(department, department)
        self.department_filter.currentIndexChanged.connect(self.filters_changed.emit)
        layout.addWidget(self.department_filter, stretch=1)

        self.position_filter = QComboBox()
        self.position_filter.addItem("Усі посади", "")
        for position in sorted({row.position_name for row in workspace.rows}):
            self.position_filter.addItem(position, position)
        self.position_filter.currentIndexChanged.connect(self.filters_changed.emit)
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
        self.status_filter.currentIndexChanged.connect(self.filters_changed.emit)
        layout.addWidget(self.status_filter)

        self.critical_only = QCheckBox("Критика")
        self.critical_only.stateChanged.connect(self.filters_changed.emit)
        layout.addWidget(self.critical_only)

        self.warning_only = QCheckBox("Увага")
        self.warning_only.stateChanged.connect(self.filters_changed.emit)
        layout.addWidget(self.warning_only)

        reset_button = QPushButton("Скинути")
        reset_button.setProperty("variant", "secondary")
        reset_button.clicked.connect(self.reset_filters)
        layout.addWidget(reset_button)

    # ###### СКИДАННЯ ФІЛЬТРІВ / RESET FILTERS ######
    def reset_filters(self) -> None:
        """Повертає всі фільтри до початкового стану.
        Returns all filters to the initial state.
        """

        self.search_input.clear()
        self.department_filter.setCurrentIndex(0)
        self.position_filter.setCurrentIndex(0)
        self.status_filter.setCurrentIndex(0)
        self.critical_only.setChecked(False)
        self.warning_only.setChecked(False)
        self.filters_changed.emit()

    # ###### ВСТАНОВЛЕННЯ ПІДРОЗДІЛУ / SET DEPARTMENT ######
    def set_department_filter(self, department_name: str) -> None:
        """Активує фільтр підрозділу з дерева структури.
        Activates the department filter from the structure tree.
        """

        index = self.department_filter.findData(department_name)
        if index >= 0:
            self.department_filter.setCurrentIndex(index)

    # ###### ВСТАНОВЛЕННЯ ПОСАДИ / SET POSITION ######
    def set_position_filter(self, position_name: str) -> None:
        """Активує фільтр посади з дерева структури.
        Activates the position filter from the structure tree.
        """

        index = self.position_filter.findData(position_name)
        if index >= 0:
            self.position_filter.setCurrentIndex(index)

    # ###### ЗНАЧЕННЯ ФІЛЬТРІВ / FILTER VALUES ######
    def values(self) -> dict[str, object]:
        """Повертає поточний стан фільтрів як простий словник.
        Returns current filter state as a simple dictionary.
        """

        return {
            "search": self.search_input.text().strip().lower(),
            "department": self.department_filter.currentData() or "",
            "position": self.position_filter.currentData() or "",
            "status": self.status_filter.currentData() or "",
            "critical_only": self.critical_only.isChecked(),
            "warning_only": self.warning_only.isChecked(),
        }

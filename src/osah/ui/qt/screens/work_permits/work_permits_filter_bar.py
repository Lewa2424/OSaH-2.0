from PySide6.QtCore import Signal
from PySide6.QtWidgets import QCheckBox, QComboBox, QHBoxLayout, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget

from osah.domain.entities.work_permit_status import WorkPermitStatus
from osah.domain.entities.work_permit_workspace import WorkPermitWorkspace
from osah.domain.entities.work_permit_workspace_mode import WorkPermitWorkspaceMode
from osah.domain.services.format_work_permit_status_label import format_work_permit_status_label
from osah.ui.qt.design.tokens import SPACING


class WorkPermitsFilterBar(QWidget):
    """Панель пошуку, фільтрів і режимів перегляду нарядів.
    Search, filters and view modes bar for work permits.
    """

    filters_changed = Signal()

    def __init__(self, workspace: WorkPermitWorkspace) -> None:
        super().__init__()
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(SPACING["xs"])

        row = QHBoxLayout()
        outer.addLayout(row)
        self.mode_filter = QComboBox()
        self.mode_filter.addItem("По нарядах", WorkPermitWorkspaceMode.BY_PERMITS.value)
        self.mode_filter.addItem("По працівниках", WorkPermitWorkspaceMode.BY_EMPLOYEES.value)
        self.mode_filter.addItem("Активні роботи", WorkPermitWorkspaceMode.ACTIVE_WORKS.value)
        self.mode_filter.currentIndexChanged.connect(lambda _index: self.filters_changed.emit())
        row.addWidget(self.mode_filter)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Пошук: номер, вид робіт, місце, відповідальний, учасник")
        self.search_input.textChanged.connect(lambda _text: self.filters_changed.emit())
        row.addWidget(self.search_input, stretch=3)

        self.status_filter = QComboBox()
        self.status_filter.addItem("Усі статуси", "")
        for status in WorkPermitStatus:
            self.status_filter.addItem(format_work_permit_status_label(status), status.value)
        self.status_filter.currentIndexChanged.connect(lambda _index: self.filters_changed.emit())
        row.addWidget(self.status_filter)

        self.work_kind_filter = QComboBox()
        self.work_kind_filter.addItem("Усі види робіт", "")
        for work_kind in sorted({row.work_kind for row in workspace.rows}):
            self.work_kind_filter.addItem(work_kind, work_kind)
        self.work_kind_filter.currentIndexChanged.connect(lambda _index: self.filters_changed.emit())
        row.addWidget(self.work_kind_filter)

        reset_button = QPushButton("Скинути")
        reset_button.setProperty("variant", "secondary")
        reset_button.clicked.connect(self.reset_filters)
        row.addWidget(reset_button)

        second = QHBoxLayout()
        outer.addLayout(second)
        self.department_filter = QComboBox()
        self.department_filter.addItem("Усі підрозділи", "")
        for department in sorted({row.department_name for row in workspace.rows}):
            self.department_filter.addItem(department, department)
        self.department_filter.currentIndexChanged.connect(lambda _index: self.filters_changed.emit())
        second.addWidget(self.department_filter)

        self.employee_filter = QComboBox()
        self.employee_filter.addItem("Усі працівники", "")
        for employee in workspace.employees:
            self.employee_filter.addItem(f"{employee.full_name} ({employee.personnel_number})", employee.personnel_number)
        self.employee_filter.currentIndexChanged.connect(lambda _index: self.filters_changed.emit())
        second.addWidget(self.employee_filter, stretch=2)

        self.problem_only = QCheckBox("Тільки проблемні")
        self.problem_only.stateChanged.connect(lambda _state: self.filters_changed.emit())
        second.addWidget(self.problem_only)
        self.active_only = QCheckBox("Тільки активні")
        self.active_only.stateChanged.connect(lambda _state: self.filters_changed.emit())
        second.addWidget(self.active_only)
        self.active_filters_label = QLabel("Фільтри не активні")
        second.addWidget(self.active_filters_label)

    # ###### СКИДАННЯ ФІЛЬТРІВ / RESET FILTERS ######
    def reset_filters(self) -> None:
        """Скидає всі фільтри модуля нарядів.
        Resets all work permit module filters.
        """

        self.search_input.clear()
        for combo in (self.mode_filter, self.status_filter, self.work_kind_filter, self.department_filter, self.employee_filter):
            combo.setCurrentIndex(0)
        self.problem_only.setChecked(False)
        self.active_only.setChecked(False)
        self._update_active_filters_label()
        self.filters_changed.emit()

    # ###### СТАРТОВИЙ СТАТУС / INITIAL STATUS ######
    def set_status_filter(self, status: WorkPermitStatus) -> None:
        """Активує фільтр статусу з navigation intent.
        Activates status filter from navigation intent.
        """

        index = self.status_filter.findData(status.value)
        if index >= 0:
            self.status_filter.setCurrentIndex(index)

    # ###### ЗНАЧЕННЯ ФІЛЬТРІВ / FILTER VALUES ######
    def values(self) -> dict[str, str | bool]:
        """Повертає поточний стан фільтрів.
        Returns the current filter state.
        """

        values: dict[str, str | bool] = {
            "mode": self.mode_filter.currentData() or WorkPermitWorkspaceMode.BY_PERMITS.value,
            "search": self.search_input.text().strip().lower(),
            "status": self.status_filter.currentData() or "",
            "work_kind": self.work_kind_filter.currentData() or "",
            "department": self.department_filter.currentData() or "",
            "employee": self.employee_filter.currentData() or "",
            "problem_only": self.problem_only.isChecked(),
            "active_only": self.active_only.isChecked(),
        }
        self._update_active_filters_label()
        return values

    # ###### ІНДИКАТОР ФІЛЬТРІВ / FILTER INDICATOR ######
    def _update_active_filters_label(self) -> None:
        """Оновлює текстовий індикатор активних фільтрів.
        Updates textual indicator of active filters.
        """

        active_count = sum(
            1
            for value in (
                self.search_input.text().strip(),
                self.status_filter.currentData() or "",
                self.work_kind_filter.currentData() or "",
                self.department_filter.currentData() or "",
                self.employee_filter.currentData() or "",
                self.problem_only.isChecked(),
                self.active_only.isChecked(),
            )
            if value
        )
        self.active_filters_label.setText("Фільтри не активні" if active_count == 0 else f"Активних фільтрів: {active_count}")

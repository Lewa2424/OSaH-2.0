from PySide6.QtCore import Signal
from PySide6.QtWidgets import QCheckBox, QComboBox, QHBoxLayout, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget

from osah.domain.entities.medical_status import MedicalStatus
from osah.domain.entities.medical_workspace import MedicalWorkspace
from osah.domain.entities.medical_workspace_mode import MedicalWorkspaceMode
from osah.domain.services.format_medical_status_label import format_medical_status_label
from osah.ui.qt.design.tokens import SPACING


class MedicalFilterBar(QWidget):
    """Панель пошуку, фільтрів і режимів перегляду медицини.
    Search, filter and view-mode bar for medical records.
    """

    filters_changed = Signal()

    def __init__(self, workspace: MedicalWorkspace) -> None:
        super().__init__()
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(SPACING["xs"])
        row = QHBoxLayout()
        outer.addLayout(row)

        self.mode_filter = QComboBox()
        self.mode_filter.addItem("По записах", MedicalWorkspaceMode.BY_RECORDS.value)
        self.mode_filter.addItem("По працівниках", MedicalWorkspaceMode.BY_EMPLOYEES.value)
        self.mode_filter.currentIndexChanged.connect(lambda _index: self.filters_changed.emit())
        row.addWidget(self.mode_filter)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Пошук: ПІБ, табельний, підрозділ, посада, обмеження")
        self.search_input.textChanged.connect(lambda _text: self.filters_changed.emit())
        row.addWidget(self.search_input, stretch=3)

        self.department_filter = QComboBox()
        self.department_filter.addItem("Усі підрозділи", "")
        for department in sorted({item.department_name for item in workspace.rows}):
            self.department_filter.addItem(department, department)
        self.department_filter.currentIndexChanged.connect(lambda _index: self.filters_changed.emit())
        row.addWidget(self.department_filter)

        self.status_filter = QComboBox()
        self.status_filter.addItem("Усі статуси", "")
        for status in MedicalStatus:
            self.status_filter.addItem(format_medical_status_label(status), status.value)
        self.status_filter.currentIndexChanged.connect(lambda _index: self.filters_changed.emit())
        row.addWidget(self.status_filter)

        reset_button = QPushButton("Скинути")
        reset_button.setProperty("variant", "secondary")
        reset_button.clicked.connect(self.reset_filters)
        row.addWidget(reset_button)

        second = QHBoxLayout()
        outer.addLayout(second)
        self.site_filter = QComboBox()
        self.site_filter.addItem("Усі участки", "")
        for site in sorted({item.site_name for item in workspace.rows}):
            self.site_filter.addItem(site, site)
        self.site_filter.currentIndexChanged.connect(lambda _index: self.filters_changed.emit())
        second.addWidget(self.site_filter)

        self.position_filter = QComboBox()
        self.position_filter.addItem("Усі посади", "")
        for position in sorted({item.position_name for item in workspace.rows}):
            self.position_filter.addItem(position, position)
        self.position_filter.currentIndexChanged.connect(lambda _index: self.filters_changed.emit())
        second.addWidget(self.position_filter)

        self.employee_filter = QComboBox()
        self.employee_filter.addItem("Усі працівники", "")
        for employee in workspace.employees:
            self.employee_filter.addItem(f"{employee.full_name} ({employee.personnel_number})", employee.personnel_number)
        self.employee_filter.currentIndexChanged.connect(lambda _index: self.filters_changed.emit())
        second.addWidget(self.employee_filter, stretch=2)

        self.restricted_only = QCheckBox("Є обмеження")
        self.restricted_only.stateChanged.connect(lambda _state: self.filters_changed.emit())
        second.addWidget(self.restricted_only)
        self.active_filters_label = QLabel("Фільтри не активні")
        second.addWidget(self.active_filters_label)

    def reset_filters(self) -> None:
        """Скидає всі фільтри модуля медицини.
        Resets all medical module filters.
        """

        self.search_input.clear()
        for combo in (self.mode_filter, self.department_filter, self.status_filter, self.site_filter, self.position_filter, self.employee_filter):
            combo.setCurrentIndex(0)
        self.restricted_only.setChecked(False)
        self._update_active_filters_label()
        self.filters_changed.emit()

    def set_status_filter(self, status: MedicalStatus) -> None:
        """Активує фільтр статусу з navigation intent.
        Activates status filter from navigation intent.
        """

        index = self.status_filter.findData(status.value)
        if index >= 0:
            self.status_filter.setCurrentIndex(index)

    def set_employee_filter(self, personnel_number: str) -> None:
        """Активує фільтр працівника з navigation intent.
        Activates employee filter from navigation intent.
        """

        index = self.employee_filter.findData(personnel_number)
        if index >= 0:
            self.employee_filter.setCurrentIndex(index)

    def values(self) -> dict[str, str | bool]:
        """Повертає поточний стан фільтрів.
        Returns the current filter state.
        """

        values: dict[str, str | bool] = {
            "mode": self.mode_filter.currentData() or MedicalWorkspaceMode.BY_RECORDS.value,
            "search": self.search_input.text().strip().lower(),
            "department": self.department_filter.currentData() or "",
            "status": self.status_filter.currentData() or "",
            "site": self.site_filter.currentData() or "",
            "position": self.position_filter.currentData() or "",
            "employee": self.employee_filter.currentData() or "",
            "restricted_only": self.restricted_only.isChecked(),
        }
        self._update_active_filters_label()
        return values

    def _update_active_filters_label(self) -> None:
        """Оновлює текстовий індикатор активних фільтрів.
        Updates textual indicator of active filters.
        """

        active_count = sum(
            1
            for value in (
                self.search_input.text().strip(),
                self.department_filter.currentData() or "",
                self.status_filter.currentData() or "",
                self.site_filter.currentData() or "",
                self.position_filter.currentData() or "",
                self.employee_filter.currentData() or "",
                self.restricted_only.isChecked(),
            )
            if value
        )
        self.active_filters_label.setText("Фільтри не активні" if active_count == 0 else f"Активних фільтрів: {active_count}")

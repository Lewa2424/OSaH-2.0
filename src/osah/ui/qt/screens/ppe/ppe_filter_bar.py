from PySide6.QtCore import Signal
from PySide6.QtWidgets import QComboBox, QHBoxLayout, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget

from osah.domain.entities.ppe_status import PpeStatus
from osah.domain.entities.ppe_workspace import PpeWorkspace
from osah.domain.entities.ppe_workspace_mode import PpeWorkspaceMode
from osah.domain.services.format_ppe_status_label import format_ppe_status_label
from osah.ui.qt.design.tokens import SPACING


class PpeFilterBar(QWidget):
    """Панель пошуку, фільтрів і режимів перегляду ЗІЗ.
    Search, filter and view-mode bar for PPE.
    """

    filters_changed = Signal()

    def __init__(self, workspace: PpeWorkspace) -> None:
        super().__init__()
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(SPACING["xs"])
        row = QHBoxLayout()
        outer.addLayout(row)

        self.mode_filter = QComboBox()
        self.mode_filter.addItem("По позиціях ЗІЗ", PpeWorkspaceMode.BY_RECORDS.value)
        self.mode_filter.addItem("По працівниках", PpeWorkspaceMode.BY_EMPLOYEES.value)
        self.mode_filter.currentIndexChanged.connect(lambda _index: self.filters_changed.emit())
        row.addWidget(self.mode_filter)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Пошук: ПІБ, табельний, ЗІЗ, підрозділ, посада")
        self.search_input.textChanged.connect(lambda _text: self.filters_changed.emit())
        row.addWidget(self.search_input, stretch=3)

        self.ppe_filter = QComboBox()
        self.ppe_filter.addItem("Усі типи ЗІЗ", "")
        for ppe_name in sorted({item.ppe_name for item in workspace.rows}):
            self.ppe_filter.addItem(ppe_name, ppe_name)
        self.ppe_filter.currentIndexChanged.connect(lambda _index: self.filters_changed.emit())
        row.addWidget(self.ppe_filter)

        self.department_filter = QComboBox()
        self.department_filter.addItem("Усі підрозділи", "")
        for department in sorted({item.department_name for item in workspace.rows}):
            self.department_filter.addItem(department, department)
        self.department_filter.currentIndexChanged.connect(lambda _index: self.filters_changed.emit())
        row.addWidget(self.department_filter)

        self.status_filter = QComboBox()
        self.status_filter.addItem("Усі статуси", "")
        for status in PpeStatus:
            self.status_filter.addItem(format_ppe_status_label(status), status.value)
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

        self.active_filters_label = QLabel("Фільтри не активні")
        second.addWidget(self.active_filters_label)

    def reset_filters(self) -> None:
        """Скидає всі фільтри модуля ЗІЗ.
        Resets all PPE module filters.
        """

        self.search_input.clear()
        for combo in (
            self.mode_filter,
            self.ppe_filter,
            self.department_filter,
            self.status_filter,
            self.site_filter,
            self.position_filter,
            self.employee_filter,
        ):
            combo.setCurrentIndex(0)
        self._update_active_filters_label()
        self.filters_changed.emit()

    def set_status_filter(self, status: PpeStatus) -> None:
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

    def values(self) -> dict[str, str]:
        """Повертає поточний стан фільтрів.
        Returns the current filter state.
        """

        values = {
            "mode": self.mode_filter.currentData() or PpeWorkspaceMode.BY_RECORDS.value,
            "search": self.search_input.text().strip().lower(),
            "ppe": self.ppe_filter.currentData() or "",
            "department": self.department_filter.currentData() or "",
            "status": self.status_filter.currentData() or "",
            "site": self.site_filter.currentData() or "",
            "position": self.position_filter.currentData() or "",
            "employee": self.employee_filter.currentData() or "",
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
                self.ppe_filter.currentData() or "",
                self.department_filter.currentData() or "",
                self.status_filter.currentData() or "",
                self.site_filter.currentData() or "",
                self.position_filter.currentData() or "",
                self.employee_filter.currentData() or "",
            )
            if value
        )
        self.active_filters_label.setText("Фільтри не активні" if active_count == 0 else f"Активних фільтрів: {active_count}")

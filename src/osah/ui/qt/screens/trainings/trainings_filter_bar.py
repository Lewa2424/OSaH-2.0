from PySide6.QtCore import Signal
from PySide6.QtWidgets import QComboBox, QHBoxLayout, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget

from osah.domain.entities.training_registry_filter import TrainingRegistryFilter
from osah.domain.entities.training_type import TrainingType
from osah.domain.entities.training_workspace import TrainingWorkspace
from osah.domain.entities.training_workspace_mode import TrainingWorkspaceMode
from osah.domain.services.format_training_type_label import format_training_type_label
from osah.domain.services.parse_ui_date_text import parse_ui_date_text
from osah.ui.qt.design.tokens import SPACING


class TrainingsFilterBar(QWidget):
    """Панель пошуку, фільтрів і режимів перегляду інструктажів.
    Search, filter and view-mode bar for trainings.
    """

    filters_changed = Signal()

    def __init__(self, workspace: TrainingWorkspace) -> None:
        super().__init__()
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(SPACING["xs"])

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING["sm"])
        outer.addLayout(layout)

        self.mode_filter = QComboBox()
        self.mode_filter.addItem("По записах", TrainingWorkspaceMode.BY_RECORDS.value)
        self.mode_filter.addItem("По працівниках", TrainingWorkspaceMode.BY_EMPLOYEES.value)
        self.mode_filter.currentIndexChanged.connect(lambda _index: self.filters_changed.emit())
        layout.addWidget(self.mode_filter)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Пошук: ПІБ, табельний, підрозділ, посада, відповідальний")
        self.search_input.textChanged.connect(lambda _text: self.filters_changed.emit())
        layout.addWidget(self.search_input, stretch=3)

        self.type_filter = QComboBox()
        self.type_filter.addItem("Усі типи", "")
        for training_type in TrainingType:
            self.type_filter.addItem(format_training_type_label(training_type), training_type.value)
        self.type_filter.currentIndexChanged.connect(lambda _index: self.filters_changed.emit())
        layout.addWidget(self.type_filter)

        self.department_filter = QComboBox()
        self.department_filter.addItem("Усі підрозділи", "")
        for department in sorted({row.department_name for row in workspace.rows}):
            self.department_filter.addItem(department, department)
        self.department_filter.currentIndexChanged.connect(lambda _index: self.filters_changed.emit())
        layout.addWidget(self.department_filter)

        self.site_filter = QComboBox()
        self.site_filter.addItem("Усі участки", "")
        for site in sorted({row.site_name for row in workspace.rows}):
            self.site_filter.addItem(site, site)
        self.site_filter.currentIndexChanged.connect(lambda _index: self.filters_changed.emit())
        layout.addWidget(self.site_filter)

        self.position_filter = QComboBox()
        self.position_filter.addItem("Усі посади", "")
        for position in sorted({row.position_name for row in workspace.rows}):
            self.position_filter.addItem(position, position)
        self.position_filter.currentIndexChanged.connect(lambda _index: self.filters_changed.emit())
        layout.addWidget(self.position_filter)

        self.status_filter = QComboBox()
        self.status_filter.addItem("Усі статуси", "")
        self.status_filter.addItem("Актуально", TrainingRegistryFilter.CURRENT.value)
        self.status_filter.addItem("Увага", TrainingRegistryFilter.WARNING.value)
        self.status_filter.addItem("Критично", TrainingRegistryFilter.OVERDUE.value)
        self.status_filter.addItem("Відсутній", TrainingRegistryFilter.MISSING.value)
        self.status_filter.currentIndexChanged.connect(lambda _index: self.filters_changed.emit())
        layout.addWidget(self.status_filter)

        self.conducted_by_filter = QComboBox()
        self.conducted_by_filter.addItem("Усі відповідальні", "")
        for conducted_by in sorted({row.conducted_by for row in workspace.rows if row.conducted_by != "-"}):
            self.conducted_by_filter.addItem(conducted_by, conducted_by)
        self.conducted_by_filter.currentIndexChanged.connect(lambda _index: self.filters_changed.emit())
        layout.addWidget(self.conducted_by_filter)

        reset_button = QPushButton("Скинути")
        reset_button.setProperty("variant", "secondary")
        reset_button.clicked.connect(self.reset_filters)
        layout.addWidget(reset_button)

        second_row = QHBoxLayout()
        second_row.setContentsMargins(0, 0, 0, 0)
        second_row.setSpacing(SPACING["sm"])
        outer.addLayout(second_row)

        self.employee_filter = QComboBox()
        self.employee_filter.addItem("Усі працівники", "")
        for employee in workspace.employees:
            self.employee_filter.addItem(f"{employee.full_name} ({employee.personnel_number})", employee.personnel_number)
        self.employee_filter.currentIndexChanged.connect(lambda _index: self.filters_changed.emit())
        second_row.addWidget(self.employee_filter, stretch=2)

        self.date_from_input = QLineEdit()
        self.date_from_input.setPlaceholderText("Період з: ДД.ММ.ГГГГ")
        self.date_from_input.textChanged.connect(lambda _text: self.filters_changed.emit())
        second_row.addWidget(self.date_from_input)

        self.date_to_input = QLineEdit()
        self.date_to_input.setPlaceholderText("Період до: ДД.ММ.ГГГГ")
        self.date_to_input.textChanged.connect(lambda _text: self.filters_changed.emit())
        second_row.addWidget(self.date_to_input)

        self.active_filters_label = QLabel("Фільтри не активні")
        second_row.addWidget(self.active_filters_label)

    def reset_filters(self) -> None:
        """Скидає всі фільтри модуля інструктажів.
        Resets all trainings module filters.
        """

        self.search_input.clear()
        for combo in (
            self.mode_filter,
            self.type_filter,
            self.department_filter,
            self.site_filter,
            self.position_filter,
            self.status_filter,
            self.conducted_by_filter,
            self.employee_filter,
        ):
            combo.setCurrentIndex(0)
        self.date_from_input.clear()
        self.date_to_input.clear()
        self._update_active_filters_label()
        self.filters_changed.emit()

    def set_status_filter(self, status_filter: TrainingRegistryFilter) -> None:
        """Активує фільтр статусу з navigation intent.
        Activates status filter from navigation intent.
        """

        index = self.status_filter.findData(status_filter.value)
        if index >= 0:
            self.status_filter.setCurrentIndex(index)

    def values(self) -> dict[str, str]:
        """Повертає поточний стан фільтрів.
        Returns the current filter state.
        """

        values = {
            "mode": self.mode_filter.currentData() or TrainingWorkspaceMode.BY_RECORDS.value,
            "search": self.search_input.text().strip().lower(),
            "type": self.type_filter.currentData() or "",
            "department": self.department_filter.currentData() or "",
            "site": self.site_filter.currentData() or "",
            "position": self.position_filter.currentData() or "",
            "status": self.status_filter.currentData() or "",
            "conducted_by": self.conducted_by_filter.currentData() or "",
            "employee": self.employee_filter.currentData() or "",
            "date_from": _normalize_filter_date(self.date_from_input.text()),
            "date_to": _normalize_filter_date(self.date_to_input.text()),
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
                self.type_filter.currentData() or "",
                self.department_filter.currentData() or "",
                self.site_filter.currentData() or "",
                self.position_filter.currentData() or "",
                self.status_filter.currentData() or "",
                self.conducted_by_filter.currentData() or "",
                self.employee_filter.currentData() or "",
                self.date_from_input.text().strip(),
                self.date_to_input.text().strip(),
            )
            if value
        )
        self.active_filters_label.setText("Фільтри не активні" if active_count == 0 else f"Активних фільтрів: {active_count}")


# ###### НОРМАЛІЗАЦІЯ ДАТИ ФІЛЬТРА / NORMALIZE FILTER DATE ######
def _normalize_filter_date(date_text: str) -> str:
    """Нормалізує дату фільтра до ISO для внутрішнього порівняння.
    Normalizes filter date to ISO for internal comparison.
    """

    normalized_date_text = date_text.strip()
    if not normalized_date_text:
        return ""
    try:
        return parse_ui_date_text(normalized_date_text).isoformat()
    except ValueError:
        return normalized_date_text

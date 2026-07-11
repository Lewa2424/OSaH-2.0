from PySide6.QtCore import Signal
from PySide6.QtWidgets import QComboBox, QHBoxLayout, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget

from osah.domain.entities.training_registry_filter import TrainingRegistryFilter
from osah.domain.entities.training_type import TrainingType
from osah.domain.entities.training_workspace import TrainingWorkspace
from osah.domain.entities.training_workspace_mode import TrainingWorkspaceMode
from osah.domain.services.format_training_type_label import format_training_type_label
from osah.domain.services.parse_ui_date_text import parse_ui_date_text
from osah.ui.qt.components.date_line_edit import DateLineEdit
from osah.ui.qt.design.tokens import COLOR, RADIUS, SPACING


class TrainingsFilterBar(QWidget):
    """Search, filter and view-mode bar for trainings. / Панель пошуку, фільтрів і режимів інструктажів."""

    filters_changed = Signal()

    def __init__(self, workspace: TrainingWorkspace) -> None:
        super().__init__()
        self._validation_error_text = ""
        self.setObjectName("trainingsFilterBar")
        self.setStyleSheet(
            f"""
            QWidget#trainingsFilterBar {{
                background: rgba(255, 255, 255, 0.96);
                border: 1px solid #D9E2EC;
                border-radius: {RADIUS['xxl']}px;
            }}
            QWidget#trainingsFilterBar QComboBox,
            QWidget#trainingsFilterBar QLineEdit {{
                min-height: 40px;
                background: #FFFFFF;
                color: {COLOR['text_primary']};
                border: 1px solid #CBD6E2;
                border-radius: {RADIUS['lg']}px;
                padding: 0 14px;
                font-size: 14px;
                font-weight: 600;
            }}
            QWidget#trainingsFilterBar QComboBox:focus,
            QWidget#trainingsFilterBar QLineEdit:focus {{
                border: 1px solid {COLOR['accent']};
                background: #FCFEFF;
            }}
            QWidget#trainingsFilterBar QComboBox::drop-down {{
                width: 32px;
                border: none;
                background: transparent;
            }}
            QWidget#trainingsFilterBar QComboBox QAbstractItemView {{
                background: #FFFFFF;
                color: {COLOR['text_primary']};
                border: 1px solid #D9E2EC;
                border-radius: {RADIUS['md']}px;
                selection-background-color: #EAF1F8;
                selection-color: {COLOR['text_primary']};
                outline: none;
            }}
            QWidget#trainingsFilterBar QPushButton {{
                min-height: 40px;
                padding: 0 18px;
                border-radius: {RADIUS['lg']}px;
                font-size: 14px;
                font-weight: 800;
            }}
            QWidget#trainingsFilterBar QLabel#filterCaption {{
                color: {COLOR['text_secondary']};
                font-size: 13px;
                font-weight: 700;
            }}
            QWidget#trainingsFilterBar QLabel#filterState {{
                color: {COLOR['text_muted']};
                font-size: 13px;
                font-weight: 700;
            }}
            """
        )

        outer = QVBoxLayout(self)
        outer.setContentsMargins(SPACING["lg"], SPACING["lg"], SPACING["lg"], SPACING["lg"])
        outer.setSpacing(SPACING["sm"])

        first_row = QHBoxLayout()
        first_row.setContentsMargins(0, 0, 0, 0)
        first_row.setSpacing(SPACING["sm"])
        outer.addLayout(first_row)

        self.mode_filter = QComboBox()
        self.mode_filter.addItem("По записах", TrainingWorkspaceMode.BY_RECORDS.value)
        self.mode_filter.addItem("По працівниках", TrainingWorkspaceMode.BY_EMPLOYEES.value)
        self.mode_filter.currentIndexChanged.connect(lambda _index: self.filters_changed.emit())
        first_row.addWidget(self.mode_filter)
        self.mode_filter.setCurrentIndex(max(0, self.mode_filter.findData(TrainingWorkspaceMode.BY_EMPLOYEES.value)))

        self.employee_filter = QComboBox()
        self.employee_filter.addItem("Усі працівники", "")
        for employee in workspace.employees:
            self.employee_filter.addItem(f"{employee.full_name} ({employee.personnel_number})", employee.personnel_number)
        self.employee_filter.currentIndexChanged.connect(lambda _index: self.filters_changed.emit())
        first_row.addWidget(self.employee_filter, stretch=2)

        self.type_filter = QComboBox()
        self.type_filter.addItem("Усі типи", "")
        for training_type in TrainingType:
            self.type_filter.addItem(format_training_type_label(training_type), training_type.value)
        self.type_filter.currentIndexChanged.connect(lambda _index: self.filters_changed.emit())
        first_row.addWidget(self.type_filter)

        self.department_filter = QComboBox()
        self.department_filter.addItem("Усі підрозділи", "")
        for department in sorted({row.department_name for row in workspace.rows}):
            self.department_filter.addItem(department, department)
        self.department_filter.currentIndexChanged.connect(lambda _index: self.filters_changed.emit())
        first_row.addWidget(self.department_filter)

        self.site_filter = QComboBox()
        self.site_filter.addItem("Усі участки", "")
        for site in sorted({row.site_name for row in workspace.rows}):
            self.site_filter.addItem(site, site)
        self.site_filter.currentIndexChanged.connect(lambda _index: self.filters_changed.emit())
        first_row.addWidget(self.site_filter)

        second_row = QHBoxLayout()
        second_row.setContentsMargins(0, 0, 0, 0)
        second_row.setSpacing(SPACING["sm"])
        outer.addLayout(second_row)

        self.position_filter = QComboBox()
        self.position_filter.addItem("Усі посади", "")
        for position in sorted({row.position_name for row in workspace.rows}):
            self.position_filter.addItem(position, position)
        self.position_filter.currentIndexChanged.connect(lambda _index: self.filters_changed.emit())
        second_row.addWidget(self.position_filter)

        self.status_filter = QComboBox()
        self.status_filter.addItem("Усі статуси", "")
        self.status_filter.addItem("Актуально", TrainingRegistryFilter.CURRENT.value)
        self.status_filter.addItem("Увага", TrainingRegistryFilter.WARNING.value)
        self.status_filter.addItem("Критично", TrainingRegistryFilter.OVERDUE.value)
        self.status_filter.addItem("Відсутній", TrainingRegistryFilter.MISSING.value)
        self.status_filter.addItem("Конфлікт", TrainingRegistryFilter.INVALID.value)
        self.status_filter.currentIndexChanged.connect(lambda _index: self.filters_changed.emit())
        second_row.addWidget(self.status_filter)

        self.conducted_by_filter = QComboBox()
        self.conducted_by_filter.addItem("Усі відповідальні", "")
        for conducted_by in sorted({row.conducted_by for row in workspace.rows if row.conducted_by != "-"}):
            self.conducted_by_filter.addItem(conducted_by, conducted_by)
        self.conducted_by_filter.currentIndexChanged.connect(lambda _index: self.filters_changed.emit())
        second_row.addWidget(self.conducted_by_filter)

        reset_button = QPushButton("Скинути")
        reset_button.setProperty("variant", "secondary")
        reset_button.clicked.connect(self.reset_filters)
        second_row.addWidget(reset_button)

        self.active_filters_label = QLabel("Фільтри не активні")
        self.active_filters_label.setObjectName("filterState")
        second_row.addWidget(self.active_filters_label)
        second_row.addStretch(1)

        third_row = QHBoxLayout()
        third_row.setContentsMargins(0, 0, 0, 0)
        third_row.setSpacing(SPACING["sm"])
        outer.addLayout(third_row)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Пошук: ПІБ, табельний, підрозділ, посада, відповідальний")
        self.search_input.textChanged.connect(lambda _text: self.filters_changed.emit())
        third_row.addWidget(self.search_input, stretch=3)

        self.date_from_input = DateLineEdit()
        self.date_from_input.setPlaceholderText("Період з")
        self.date_from_input.textChanged.connect(lambda _text: self.filters_changed.emit())
        third_row.addWidget(self.date_from_input)

        self.date_to_input = DateLineEdit()
        self.date_to_input.setPlaceholderText("Період до")
        self.date_to_input.textChanged.connect(lambda _text: self.filters_changed.emit())
        third_row.addWidget(self.date_to_input)

    def reset_filters(self) -> None:
        self.search_input.clear()
        for combo in (
            self.type_filter,
            self.department_filter,
            self.site_filter,
            self.position_filter,
            self.status_filter,
            self.conducted_by_filter,
            self.employee_filter,
        ):
            combo.setCurrentIndex(0)
        self.mode_filter.setCurrentIndex(max(0, self.mode_filter.findData(TrainingWorkspaceMode.BY_EMPLOYEES.value)))
        self.date_from_input.clear()
        self.date_to_input.clear()
        self._update_active_filters_label()
        self.filters_changed.emit()

    def set_status_filter(self, status_filter: TrainingRegistryFilter) -> None:
        index = self.status_filter.findData(status_filter.value)
        if index >= 0:
            self.status_filter.setCurrentIndex(index)

    def set_employee_filter(self, personnel_number: str) -> None:
        index = self.employee_filter.findData(personnel_number)
        if index >= 0:
            self.employee_filter.setCurrentIndex(index)

    def values(self) -> dict[str, str]:
        date_from, date_from_error = _normalize_filter_date(self.date_from_input.text())
        date_to, date_to_error = _normalize_filter_date(self.date_to_input.text())
        self._validation_error_text = date_from_error or date_to_error
        values = {
            "mode": self.mode_filter.currentData() or TrainingWorkspaceMode.BY_EMPLOYEES.value,
            "search": self.search_input.text().strip().lower(),
            "type": self.type_filter.currentData() or "",
            "department": self.department_filter.currentData() or "",
            "site": self.site_filter.currentData() or "",
            "position": self.position_filter.currentData() or "",
            "status": self.status_filter.currentData() or "",
            "conducted_by": self.conducted_by_filter.currentData() or "",
            "employee": self.employee_filter.currentData() or "",
            "date_from": date_from,
            "date_to": date_to,
            "validation_error": self._validation_error_text,
        }
        self._update_active_filters_label()
        return values

    def _update_active_filters_label(self) -> None:
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


def _normalize_filter_date(date_text: str) -> tuple[str, str]:
    normalized_date_text = date_text.strip()
    if not normalized_date_text:
        return "", ""
    try:
        return parse_ui_date_text(normalized_date_text).isoformat(), ""
    except ValueError as error:
        return "", str(error)

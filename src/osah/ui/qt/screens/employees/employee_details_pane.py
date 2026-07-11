from pathlib import Path

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QScrollArea, QTabWidget, QVBoxLayout, QWidget

from osah.domain.entities.app_section import AppSection
from osah.domain.entities.employee_workspace_row import EmployeeWorkspaceRow
from osah.ui.qt.design.tokens import COLOR, RADIUS, SPACING
from osah.ui.qt.screens.employees.employee_header_card import EmployeeHeaderCard
from osah.ui.qt.screens.employees.employee_history_tab import EmployeeHistoryTab
from osah.ui.qt.screens.employees.employee_overview_tab import EmployeeOverviewTab
from osah.ui.qt.screens.medical.employee_medical_tab import EmployeeMedicalTab
from osah.ui.qt.screens.ppe.employee_ppe_tab import EmployeePpeTab
from osah.ui.qt.screens.trainings.employee_trainings_tab import EmployeeTrainingsTab
from osah.ui.qt.screens.work_permits.employee_work_permits_tab import EmployeeWorkPermitsTab


class EmployeeDetailsPane(QScrollArea):
    """Right detail pane for an employee card. / Правая панель карточки работника."""

    edit_requested = Signal(EmployeeWorkspaceRow)
    archive_requested = Signal(EmployeeWorkspaceRow)
    module_navigation_requested = Signal(AppSection, str)
    module_record_navigation_requested = Signal(AppSection, str, int)

    def __init__(self, database_path: Path, read_only: bool) -> None:
        super().__init__()
        self._database_path = database_path
        self._read_only = read_only
        self.setWidgetResizable(True)
        self.setMinimumWidth(560)
        self.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        self.show_empty_state()

    def show_empty_state(self) -> None:
        """Shows empty hint state. / Показывает подсказку до выбора работника."""

        label = QLabel("Оберіть працівника у реєстрі, щоб відкрити картку.")
        label.setWordWrap(True)
        label.setStyleSheet(f"color: {COLOR['text_muted']}; padding: 28px; font-size: 15px; font-weight: 700;")
        self.setWidget(label)

    def show_employee(self, row: EmployeeWorkspaceRow) -> None:
        """Displays selected employee card. / Показывает карточку выбранного работника."""

        container = QWidget()
        container.setObjectName("employeeDetailsContainer")
        container.setStyleSheet(
            f"""
            QWidget#employeeDetailsContainer {{
                background: transparent;
            }}
            QTabWidget::pane {{
                border: 1px solid {COLOR['border_soft']};
                background: {COLOR['bg_card']};
                border-radius: {RADIUS['xl']}px;
                top: -1px;
            }}
            QTabBar::tab {{
                background: #EEF3F8;
                color: {COLOR['text_secondary']};
                border: 1px solid {COLOR['border_soft']};
                border-bottom: none;
                padding: 10px 18px;
                margin-right: 6px;
                border-top-left-radius: 14px;
                border-top-right-radius: 14px;
                font-size: 13px;
                font-weight: 800;
            }}
            QTabBar::tab:selected {{
                background: {COLOR['bg_card']};
                color: {COLOR['text_primary']};
            }}
            QTabBar::tab:hover {{
                color: {COLOR['text_primary']};
            }}
            """
        )
        layout = QVBoxLayout(container)
        layout.setContentsMargins(SPACING["lg"], SPACING["lg"], SPACING["lg"], SPACING["lg"])
        layout.setSpacing(SPACING["lg"])

        layout.addWidget(EmployeeHeaderCard(row))

        tabs = QTabWidget()

        overview_tab = EmployeeOverviewTab(row)
        overview_tab.module_clicked.connect(
            lambda target_section: self.module_navigation_requested.emit(target_section, row.employee.personnel_number)
        )
        tabs.addTab(overview_tab, "Огляд")

        trainings_tab = EmployeeTrainingsTab(row.employee, row.training_records)
        trainings_tab.record_requested.connect(
            lambda personnel_number, record_id: self.module_record_navigation_requested.emit(
                AppSection.TRAININGS,
                personnel_number,
                int(record_id) if record_id is not None else 0,
            )
        )
        tabs.addTab(trainings_tab, "Інструктажі")

        ppe_tab = EmployeePpeTab(row.ppe_records)
        ppe_tab.record_requested.connect(
            lambda personnel_number, record_id: self.module_record_navigation_requested.emit(
                AppSection.PPE,
                personnel_number,
                record_id,
            )
        )
        tabs.addTab(ppe_tab, "ЗІЗ")

        medical_tab = EmployeeMedicalTab(row.medical_records)
        medical_tab.record_requested.connect(
            lambda personnel_number, record_id: self.module_record_navigation_requested.emit(
                AppSection.MEDICAL,
                personnel_number,
                record_id,
            )
        )
        tabs.addTab(medical_tab, "Медицина")

        permits_tab = EmployeeWorkPermitsTab(row.employee.personnel_number, row.work_permit_records)
        permits_tab.record_requested.connect(
            lambda personnel_number, record_id: self.module_record_navigation_requested.emit(
                AppSection.WORK_PERMITS,
                personnel_number,
                record_id,
            )
        )
        tabs.addTab(permits_tab, "Наряди-допуски")
        tabs.addTab(EmployeeHistoryTab(self._database_path, row), "Історія")
        layout.addWidget(tabs)

        actions_layout = QHBoxLayout()

        edit_button = QPushButton("Редагувати картку")
        edit_button.setProperty("variant", "accent")
        edit_button.setStyleSheet("padding: 10px 24px; font-size: 14px; font-weight: 800; border-radius: 14px;")
        edit_button.clicked.connect(lambda: self.edit_requested.emit(row))
        edit_button.setVisible(not self._read_only)
        edit_button.setEnabled(not self._read_only)
        actions_layout.addWidget(edit_button)

        actions_layout.addStretch()

        archive_button = QPushButton("Перемістити в архів")
        archive_button.setStyleSheet(
            f"background: {COLOR['critical_subtle']}; border: 1px solid {COLOR['critical']}; color: {COLOR['critical']}; "
            "padding: 10px 24px; font-size: 14px; font-weight: 800; border-radius: 14px;"
        )
        archive_button.clicked.connect(lambda: self.archive_requested.emit(row))
        archive_button.setVisible(not self._read_only)
        archive_button.setEnabled(not self._read_only)
        actions_layout.addWidget(archive_button)

        layout.addLayout(actions_layout)
        self.setWidget(container)

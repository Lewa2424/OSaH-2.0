from PySide6.QtCore import Signal
from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QScrollArea, QTabWidget, QVBoxLayout, QWidget

from osah.domain.entities.app_section import AppSection
from osah.domain.entities.employee_workspace_row import EmployeeWorkspaceRow
from osah.ui.qt.design.tokens import COLOR, SPACING
from osah.ui.qt.screens.employees.employee_header_card import EmployeeHeaderCard
from osah.ui.qt.screens.employees.employee_overview_tab import EmployeeOverviewTab
from osah.ui.qt.screens.medical.employee_medical_tab import EmployeeMedicalTab
from osah.ui.qt.screens.ppe.employee_ppe_tab import EmployeePpeTab
from osah.ui.qt.screens.trainings.employee_trainings_tab import EmployeeTrainingsTab
from osah.ui.qt.screens.work_permits.employee_work_permits_tab import EmployeeWorkPermitsTab


class EmployeeDetailsPane(QScrollArea):
    """Права панель картки працівника.
    Right detail pane for an employee card.
    """

    edit_requested = Signal(EmployeeWorkspaceRow)
    archive_requested = Signal(EmployeeWorkspaceRow)
    module_navigation_requested = Signal(AppSection, str)

    def __init__(self) -> None:
        super().__init__()
        self.setWidgetResizable(True)
        self.setMinimumWidth(560)
        self.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        self.show_empty_state()

    # ###### ПОКАЗ ПОРОЖНЬОГО СТАНУ / SHOW EMPTY STATE ######
    def show_empty_state(self) -> None:
        """Показує підказку, коли працівника ще не вибрано.
        Shows a hint when no employee is selected yet.
        """

        label = QLabel("Оберіть працівника в реєстрі, щоб відкрити картку.")
        label.setWordWrap(True)
        label.setStyleSheet(f"color: {COLOR['text_muted']}; padding: 24px;")
        self.setWidget(label)

    # ###### ПОКАЗ КАРТКИ / SHOW EMPLOYEE CARD ######
    def show_employee(self, row: EmployeeWorkspaceRow) -> None:
        """Відображає картку вибраного працівника з вкладкою огляду.
        Displays the selected employee card with the overview tab.
        """

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(SPACING["lg"], SPACING["lg"], SPACING["lg"], SPACING["lg"])
        layout.setSpacing(SPACING["lg"])

        layout.addWidget(EmployeeHeaderCard(row))

        tabs = QTabWidget()
        
        overview_tab = EmployeeOverviewTab(row)
        overview_tab.module_clicked.connect(
            lambda target_section: self.module_navigation_requested.emit(
                target_section, row.employee.personnel_number
            )
        )
        tabs.addTab(overview_tab, "Огляд")
        
        tabs.addTab(EmployeeTrainingsTab(row.training_records), "Інструктажі")
        tabs.addTab(EmployeePpeTab(row.ppe_records), "ЗІЗ")
        tabs.addTab(EmployeeMedicalTab(row.medical_records), "Медицина")
        tabs.addTab(EmployeeWorkPermitsTab(row.work_permit_records), "Наряди-допуски")
        tabs.addTab(_stub_tab("Історія", "Історія буде прив'язана до audit-журналу."), "Історія")
        layout.addWidget(tabs)

        actions_layout = QHBoxLayout()
        
        edit_button = QPushButton("Редагувати картку")
        edit_button.setProperty("variant", "accent")
        edit_button.setStyleSheet("padding: 10px 24px; font-size: 14px; font-weight: bold;")
        edit_button.clicked.connect(lambda: self.edit_requested.emit(row))
        actions_layout.addWidget(edit_button)

        actions_layout.addStretch()

        archive_button = QPushButton("Перемістити в архів")
        archive_button.setStyleSheet("background: #fff0f0; border: 1px solid #ffcdd2; color: #d32f2f; padding: 10px 24px; font-size: 14px; font-weight: bold; border-radius: 6px;")
        archive_button.clicked.connect(lambda: self.archive_requested.emit(row))
        actions_layout.addWidget(archive_button)

        layout.addLayout(actions_layout)

        self.setWidget(container)


# ###### ЗАГЛУШКА ВКЛАДКИ / TAB STUB ######
def _stub_tab(title: str, message: str) -> QWidget:
    """Створює легку read-only заглушку вкладки нового формату.
    Creates a lightweight read-only stub for a future tab.
    """

    widget = QWidget()
    layout = QVBoxLayout(widget)
    layout.setContentsMargins(SPACING["lg"], SPACING["lg"], SPACING["lg"], SPACING["lg"])
    label = QLabel(f"{title}\n{message}")
    label.setWordWrap(True)
    label.setStyleSheet(f"color: {COLOR['text_secondary']};")
    layout.addWidget(label)
    layout.addStretch()
    return widget

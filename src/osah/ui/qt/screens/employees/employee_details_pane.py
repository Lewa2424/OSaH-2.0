from PySide6.QtWidgets import QLabel, QScrollArea, QTabWidget, QVBoxLayout, QWidget

from osah.domain.entities.employee_workspace_row import EmployeeWorkspaceRow
from osah.ui.qt.design.tokens import COLOR, SPACING
from osah.ui.qt.screens.employees.employee_header_card import EmployeeHeaderCard
from osah.ui.qt.screens.employees.employee_overview_tab import EmployeeOverviewTab


class EmployeeDetailsPane(QScrollArea):
    """Права панель картки працівника.
    Right detail pane for an employee card.
    """

    def __init__(self) -> None:
        super().__init__()
        self.setWidgetResizable(True)
        self.setMinimumWidth(390)
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
        tabs.addTab(EmployeeOverviewTab(row), "Огляд")
        tabs.addTab(_stub_tab("Інструктажі", "Повна вкладка буде підключена на наступному етапі."), "Інструктажі")
        tabs.addTab(_stub_tab("ЗІЗ", "Read-only зведення вже враховано в огляді."), "ЗІЗ")
        tabs.addTab(_stub_tab("Медицина", "Read-only зведення вже враховано в огляді."), "Медицина")
        tabs.addTab(_stub_tab("Наряди-допуски", "Read-only зведення вже враховано в огляді."), "Наряди-допуски")
        tabs.addTab(_stub_tab("Історія", "Історія буде прив'язана до audit-журналу."), "Історія")
        layout.addWidget(tabs)
        layout.addStretch()
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

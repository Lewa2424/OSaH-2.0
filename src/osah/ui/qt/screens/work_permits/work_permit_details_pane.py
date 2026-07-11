from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QScrollArea, QSizePolicy, QVBoxLayout, QWidget

from osah.domain.entities.access_role import AccessRole
from osah.domain.entities.app_section import AppSection
from osah.domain.entities.employee import Employee
from osah.domain.entities.work_permit_workspace_row import WorkPermitWorkspaceRow
from osah.ui.qt.design.tokens import COLOR, RADIUS, SPACING
from osah.ui.qt.screens.work_permits.permit_participants_panel import PermitParticipantsPanel
from osah.ui.qt.screens.work_permits.work_permit_editor import WorkPermitEditor


class WorkPermitDetailsPane(QScrollArea):
    """Right details and editor pane for work permits. / Права панель деталей наряду-допуску."""

    employee_requested = Signal(str)
    module_navigation_requested = Signal(AppSection, str)

    def __init__(self, database_path: Path, employees: tuple[Employee, ...], access_role: AccessRole) -> None:
        super().__init__()
        self.setWidgetResizable(True)
        self.setMinimumWidth(440)
        self.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        self._read_only = access_role != AccessRole.INSPECTOR
        self._current_employee_number: str | None = None
        self.participants_panel = PermitParticipantsPanel()
        self.editor = WorkPermitEditor(database_path, employees, access_role)
        self.editor.module_navigation_requested.connect(self.module_navigation_requested.emit)
        self.new_permit_button = QPushButton("Новий наряд")
        self.new_permit_button.setProperty("variant", "accent")
        self.new_permit_button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.new_permit_button.clicked.connect(self.editor.clear_form)
        self.new_permit_button.setVisible(not self._read_only)
        self.new_permit_button.setEnabled(not self._read_only)
        self.open_employee_button = QPushButton("Відкрити картку учасника")
        self.open_employee_button.setProperty("variant", "secondary")
        self.open_employee_button.clicked.connect(self._emit_employee_request)
        self.show_empty_state()

    def show_empty_state(self) -> None:
        container = QWidget()
        container.setObjectName("workPermitDetailsContainer")
        container.setStyleSheet(
            f"""
            QWidget#workPermitDetailsContainer {{
                background: rgba(255, 255, 255, 0.95);
                border: 1px solid #D9E2EC;
                border-radius: {RADIUS['xxl']}px;
            }}
            QLabel#detailsTitle {{
                color: {COLOR['text_primary']};
                font-size: 22px;
                font-weight: 900;
            }}
            QLabel#detailsHint {{
                color: {COLOR['text_secondary']};
                font-size: 15px;
                font-weight: 700;
            }}
            """
        )
        layout = QVBoxLayout(container)
        layout.setContentsMargins(SPACING["xl"], SPACING["lg"], SPACING["xl"], SPACING["lg"])
        layout.setSpacing(SPACING["md"])

        title = QLabel("Наряд-допуск")
        title.setObjectName("detailsTitle")
        header_row = QWidget()
        header_layout = QHBoxLayout(header_row)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(SPACING["sm"])
        header_layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        header_layout.addStretch(1)
        header_layout.addWidget(self.new_permit_button, alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        hint = QLabel("Оберіть наряд у таблиці зліва або натисніть «Новий наряд» у верхній частині картки.")
        hint.setObjectName("detailsHint")
        hint.setWordWrap(True)
        layout.addWidget(header_row)
        layout.addWidget(hint)
        layout.addWidget(self.participants_panel)
        layout.addWidget(self.editor)
        layout.addWidget(self.open_employee_button)
        layout.addStretch()
        self.setWidget(container)

    def show_row(self, row: WorkPermitWorkspaceRow) -> None:
        self._current_employee_number = row.employee_numbers[0] if row.employee_numbers else None
        self.participants_panel.set_row(row)
        self.editor.set_row(row)

    def _emit_employee_request(self) -> None:
        personnel_number = self.editor.current_employee_personnel_number() or self._current_employee_number
        if personnel_number:
            self.employee_requested.emit(personnel_number)

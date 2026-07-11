from pathlib import Path

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QLabel, QPushButton, QScrollArea, QVBoxLayout, QWidget

from osah.domain.entities.access_role import AccessRole
from osah.domain.entities.employee import Employee
from osah.domain.entities.medical_workspace_row import MedicalWorkspaceRow
from osah.ui.qt.design.tokens import COLOR, RADIUS, SPACING
from osah.ui.qt.screens.medical.medical_record_editor import MedicalRecordEditor


class MedicalRecordDetailsPane(QScrollArea):
    """Right details and editor pane for medical admission records. / Права панель меддопуску."""

    employee_requested = Signal(str)

    def __init__(self, database_path: Path, employees: tuple[Employee, ...], access_role: AccessRole) -> None:
        super().__init__()
        self.setWidgetResizable(True)
        self.setMinimumWidth(420)
        self.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        self._current_personnel_number: str | None = None
        self.editor = MedicalRecordEditor(database_path, employees, access_role)
        self.open_employee_button = QPushButton("Відкрити картку працівника")
        self.open_employee_button.setProperty("variant", "secondary")
        self.open_employee_button.clicked.connect(self._emit_employee_request)
        self.show_empty_state()

    def show_empty_state(self) -> None:
        container = QWidget()
        container.setObjectName("medicalDetailsContainer")
        container.setStyleSheet(
            f"""
            QWidget#medicalDetailsContainer {{
                background: rgba(255, 255, 255, 0.95);
                border: 1px solid #D9E2EC;
                border-radius: {RADIUS['xxl']}px;
            }}
            QLabel#detailsTitle {{
                color: {COLOR['text_primary']};
                font-size: 22px;
                font-weight: 900;
            }}
            QLabel#detailsLead {{
                color: {COLOR['text_secondary']};
                font-size: 15px;
                font-weight: 700;
            }}
            """
        )
        layout = QVBoxLayout(container)
        layout.setContentsMargins(SPACING["xl"], SPACING["lg"], SPACING["xl"], SPACING["lg"])
        layout.setSpacing(SPACING["md"])
        title = QLabel("Меддопуск")
        title.setObjectName("detailsTitle")
        hint = QLabel("Оберіть запис у реєстрі або створіть новий. Діагнози тут не зберігаються.")
        hint.setObjectName("detailsLead")
        hint.setWordWrap(True)
        layout.addWidget(title)
        layout.addWidget(hint)
        layout.addWidget(self.editor)
        layout.addWidget(self.open_employee_button)
        layout.addStretch()
        self.setWidget(container)

    def show_row(self, row: MedicalWorkspaceRow) -> None:
        self._current_personnel_number = row.employee_personnel_number
        self.editor.set_row(row)

    def _emit_employee_request(self) -> None:
        if self._current_personnel_number:
            self.employee_requested.emit(self._current_personnel_number)

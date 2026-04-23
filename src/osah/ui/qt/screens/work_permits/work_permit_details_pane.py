from pathlib import Path

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QLabel, QPushButton, QScrollArea, QVBoxLayout, QWidget

from osah.domain.entities.employee import Employee
from osah.domain.entities.work_permit_workspace_row import WorkPermitWorkspaceRow
from osah.ui.qt.design.tokens import COLOR, SPACING
from osah.ui.qt.screens.work_permits.permit_participants_panel import PermitParticipantsPanel
from osah.ui.qt.screens.work_permits.work_permit_editor import WorkPermitEditor


class WorkPermitDetailsPane(QScrollArea):
    """Права панель деталей і редактора наряду-допуску.
    Right details and editor pane for work permits.
    """

    employee_requested = Signal(str)

    def __init__(self, database_path: Path, employees: tuple[Employee, ...]) -> None:
        super().__init__()
        self.setWidgetResizable(True)
        self.setMinimumWidth(380)
        self._current_employee_number: str | None = None
        self.participants_panel = PermitParticipantsPanel()
        self.editor = WorkPermitEditor(database_path, employees)
        self.open_employee_button = QPushButton("Відкрити картку учасника")
        self.open_employee_button.setProperty("variant", "secondary")
        self.open_employee_button.clicked.connect(self._emit_employee_request)
        self.show_empty_state()

    # ###### ПОРОЖНІЙ СТАН / EMPTY STATE ######
    def show_empty_state(self) -> None:
        """Показує редактор у режимі нового наряду.
        Shows the editor in new work permit mode.
        """

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(SPACING["lg"], SPACING["lg"], SPACING["lg"], SPACING["lg"])
        layout.setSpacing(SPACING["md"])
        title = QLabel("Наряд-допуск")
        title.setStyleSheet("font-size: 15px; font-weight: 900;")
        hint = QLabel("Оберіть наряд у реєстрі або створіть новий контрольований наряд.")
        hint.setWordWrap(True)
        hint.setStyleSheet(f"color: {COLOR['text_secondary']};")
        layout.addWidget(title)
        layout.addWidget(hint)
        layout.addWidget(self.participants_panel)
        layout.addWidget(self.editor)
        layout.addWidget(self.open_employee_button)
        layout.addStretch()
        self.setWidget(container)

    # ###### ПОКАЗ РЯДКА / SHOW ROW ######
    def show_row(self, row: WorkPermitWorkspaceRow) -> None:
        """Показує вибраний наряд у деталях і формі редагування.
        Shows the selected work permit in details and edit form.
        """

        self._current_employee_number = row.employee_numbers[0] if row.employee_numbers else None
        self.participants_panel.set_row(row)
        self.editor.set_row(row)

    # ###### ЗАПИТ КАРТКИ / EMPLOYEE REQUEST ######
    def _emit_employee_request(self) -> None:
        """Передає запит відкрити картку першого учасника наряду.
        Emits a request to open the first participant card.
        """

        if self._current_employee_number:
            self.employee_requested.emit(self._current_employee_number)

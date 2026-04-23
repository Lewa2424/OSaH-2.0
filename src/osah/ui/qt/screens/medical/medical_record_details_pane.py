from pathlib import Path

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QLabel, QPushButton, QScrollArea, QVBoxLayout, QWidget

from osah.domain.entities.employee import Employee
from osah.domain.entities.medical_workspace_row import MedicalWorkspaceRow
from osah.ui.qt.design.tokens import COLOR, SPACING
from osah.ui.qt.screens.medical.medical_record_editor import MedicalRecordEditor


class MedicalRecordDetailsPane(QScrollArea):
    """Права панель деталей і редактора меддопуску.
    Right details and editor pane for medical admission records.
    """

    employee_requested = Signal(str)

    def __init__(self, database_path: Path, employees: tuple[Employee, ...]) -> None:
        super().__init__()
        self.setWidgetResizable(True)
        self.setMinimumWidth(360)
        self._current_personnel_number: str | None = None
        self.editor = MedicalRecordEditor(database_path, employees)
        self.open_employee_button = QPushButton("Відкрити картку працівника")
        self.open_employee_button.setProperty("variant", "secondary")
        self.open_employee_button.clicked.connect(self._emit_employee_request)
        self.show_empty_state()

    # ###### ПОКАЗ ПОРОЖНЬОГО СТАНУ / SHOW EMPTY STATE ######
    def show_empty_state(self) -> None:
        """Показує редактор у режимі нового медичного запису.
        Shows the editor in new medical record mode.
        """

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(SPACING["lg"], SPACING["lg"], SPACING["lg"], SPACING["lg"])
        layout.setSpacing(SPACING["md"])
        title = QLabel("Меддопуск")
        title.setStyleSheet("font-size: 15px; font-weight: 900;")
        hint = QLabel("Оберіть запис у реєстрі або створіть новий. Діагнози тут не зберігаються.")
        hint.setWordWrap(True)
        hint.setStyleSheet(f"color: {COLOR['text_secondary']};")
        layout.addWidget(title)
        layout.addWidget(hint)
        layout.addWidget(self.editor)
        layout.addWidget(self.open_employee_button)
        layout.addStretch()
        self.setWidget(container)

    # ###### ПОКАЗ РЯДКА / SHOW ROW ######
    def show_row(self, row: MedicalWorkspaceRow) -> None:
        """Показує вибраний медичний запис у формі редагування.
        Shows the selected medical record in the edit form.
        """

        self._current_personnel_number = row.employee_personnel_number
        self.editor.set_row(row)

    # ###### ЗАПИТ КАРТКИ ПРАЦІВНИКА / EMPLOYEE CARD REQUEST ######
    def _emit_employee_request(self) -> None:
        """Передає запит відкрити картку поточного працівника.
        Emits a request to open the current employee card.
        """

        if self._current_personnel_number:
            self.employee_requested.emit(self._current_personnel_number)

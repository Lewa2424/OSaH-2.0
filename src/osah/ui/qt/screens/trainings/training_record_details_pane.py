from pathlib import Path

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QLabel, QPushButton, QScrollArea, QVBoxLayout, QWidget

from osah.domain.entities.employee import Employee
from osah.domain.entities.training_workspace_row import TrainingWorkspaceRow
from osah.ui.qt.design.tokens import COLOR, SPACING
from osah.ui.qt.screens.trainings.training_record_editor import TrainingRecordEditor


class TrainingRecordDetailsPane(QScrollArea):
    """Права панель деталей і редактора інструктажу.
    Right details and editor pane for a training record.
    """

    employee_requested = Signal(str)

    def __init__(self, database_path: Path, employees: tuple[Employee, ...]) -> None:
        super().__init__()
        self.setWidgetResizable(True)
        self.setMinimumWidth(360)
        self._current_personnel_number: str | None = None
        self.editor = TrainingRecordEditor(database_path, employees)
        self.open_employee_button = QPushButton("Відкрити картку працівника")
        self.open_employee_button.setProperty("variant", "secondary")
        self.open_employee_button.clicked.connect(self._emit_employee_request)
        self.show_empty_state()

    # ###### ПОРОЖНІЙ СТАН / EMPTY STATE ######
    def show_empty_state(self) -> None:
        """Показує редактор у режимі нового запису без вибраного рядка.
        Shows the editor in new-record mode without a selected row.
        """

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(SPACING["lg"], SPACING["lg"], SPACING["lg"], SPACING["lg"])
        title = QLabel("Запис інструктажу")
        title.setStyleSheet("font-size: 15px; font-weight: 900;")
        hint = QLabel("Оберіть запис у реєстрі або створіть новий.")
        hint.setStyleSheet(f"color: {COLOR['text_secondary']};")
        layout.addWidget(title)
        layout.addWidget(hint)
        layout.addWidget(self.editor)
        layout.addWidget(self.open_employee_button)
        layout.addStretch()
        self.setWidget(container)

    # ###### ПОКАЗ РЯДКА / SHOW ROW ######
    def show_row(self, row: TrainingWorkspaceRow) -> None:
        """Показує вибраний рядок у формі редагування.
        Shows selected row in the edit form.
        """

        self._current_personnel_number = row.employee_personnel_number
        self.editor.set_row(row)

    def _emit_employee_request(self) -> None:
        """Передає запит відкрити картку працівника з вибраного запису.
        Emits a request to open the employee card from the selected record.
        """

        if self._current_personnel_number:
            self.employee_requested.emit(self._current_personnel_number)

from pathlib import Path

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QComboBox, QFormLayout, QLineEdit, QPushButton, QTextEdit, QVBoxLayout, QWidget

from osah.application.services.create_training_record import create_training_record
from osah.application.services.update_training_record import update_training_record
from osah.domain.entities.employee import Employee
from osah.domain.entities.training_type import TrainingType
from osah.domain.entities.training_workspace_row import TrainingWorkspaceRow
from osah.domain.services.format_training_type_label import format_training_type_label
from osah.domain.services.format_ui_date import format_ui_date
from osah.ui.qt.components.form_feedback_label import FormFeedbackLabel
from osah.ui.qt.design.tokens import SPACING


class TrainingRecordEditor(QWidget):
    """Форма створення і редагування одного запису інструктажу.
    Form for creating and editing one training record.
    """

    saved = Signal()

    def __init__(self, database_path: Path, employees: tuple[Employee, ...]) -> None:
        super().__init__()
        self._database_path = database_path
        self._current_record_id: int | None = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING["md"])

        form = QFormLayout()
        self.employee_input = QComboBox()
        for employee in employees:
            if employee.employment_status.strip().lower() == "active":
                self.employee_input.addItem(f"{employee.full_name} ({employee.personnel_number})", employee.personnel_number)
        form.addRow("Працівник", self.employee_input)

        self.type_input = QComboBox()
        for training_type in TrainingType:
            self.type_input.addItem(format_training_type_label(training_type), training_type.value)
        form.addRow("Тип", self.type_input)

        self.event_date_input = QLineEdit()
        self.event_date_input.setPlaceholderText("ДД.ММ.ГГГГ")
        form.addRow("Дата проведення", self.event_date_input)

        self.next_date_input = QLineEdit()
        self.next_date_input.setPlaceholderText("ДД.ММ.ГГГГ")
        form.addRow("Наступний контроль", self.next_date_input)

        self.conducted_by_input = QLineEdit()
        form.addRow("Проводив", self.conducted_by_input)

        self.note_input = QTextEdit()
        self.note_input.setMaximumHeight(80)
        form.addRow("Примітка", self.note_input)
        layout.addLayout(form)

        self.feedback_label = FormFeedbackLabel()
        layout.addWidget(self.feedback_label)

        self.save_button = QPushButton("Зберегти запис")
        self.save_button.setProperty("variant", "accent")
        self.save_button.clicked.connect(self._save_record)
        layout.addWidget(self.save_button)

        self.new_button = QPushButton("Новий запис")
        self.new_button.setProperty("variant", "secondary")
        self.new_button.clicked.connect(self.clear_form)
        layout.addWidget(self.new_button)

    def set_row(self, row: TrainingWorkspaceRow) -> None:
        """Заповнює форму вибраним записом або шаблоном для відсутнього запису.
        Fills the form with selected record or a template for a missing record.
        """

        self._current_record_id = row.record_id
        self.employee_input.setCurrentIndex(max(0, self.employee_input.findData(row.employee_personnel_number)))
        if row.training_type:
            self.type_input.setCurrentIndex(max(0, self.type_input.findData(row.training_type.value)))
        self.event_date_input.setText("" if row.event_date == "-" else format_ui_date(row.event_date))
        self.next_date_input.setText("" if row.next_control_date == "-" else format_ui_date(row.next_control_date))
        self.conducted_by_input.setText("" if row.conducted_by == "-" else row.conducted_by)
        self.note_input.setPlainText(row.note_text)
        self.save_button.setText("Створити запис" if row.is_missing else "Зберегти зміни")

    def clear_form(self) -> None:
        """Готує форму до створення нового запису.
        Prepares the form for creating a new record.
        """

        self._current_record_id = None
        self.event_date_input.clear()
        self.next_date_input.clear()
        self.conducted_by_input.clear()
        self.note_input.clear()
        self.save_button.setText("Створити запис")

    def _save_record(self) -> None:
        """Зберігає запис через application service і повідомляє екран про оновлення.
        Saves the record through application service and notifies the screen to refresh.
        """

        try:
            if self._current_record_id is None:
                create_training_record(
                    self._database_path,
                    str(self.employee_input.currentData()),
                    str(self.type_input.currentData()),
                    self.event_date_input.text(),
                    self.next_date_input.text(),
                    self.conducted_by_input.text(),
                    self.note_input.toPlainText(),
                )
            else:
                update_training_record(
                    self._database_path,
                    self._current_record_id,
                    str(self.employee_input.currentData()),
                    str(self.type_input.currentData()),
                    self.event_date_input.text(),
                    self.next_date_input.text(),
                    self.conducted_by_input.text(),
                    self.note_input.toPlainText(),
                )
        except ValueError as error:
            self.feedback_label.show_error(str(error))
            return

        self.feedback_label.show_success("Запис інструктажу збережено.")
        self.saved.emit()

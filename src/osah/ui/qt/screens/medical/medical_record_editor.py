from pathlib import Path

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QComboBox, QFormLayout, QLineEdit, QPushButton, QTextEdit, QVBoxLayout, QWidget

from osah.application.services.create_medical_record import create_medical_record
from osah.application.services.update_medical_record import update_medical_record
from osah.domain.entities.employee import Employee
from osah.domain.entities.medical_decision import MedicalDecision
from osah.domain.entities.medical_workspace_row import MedicalWorkspaceRow
from osah.domain.services.format_medical_decision_label import format_medical_decision_label
from osah.ui.qt.components.form_feedback_label import FormFeedbackLabel
from osah.ui.qt.design.tokens import SPACING


class MedicalRecordEditor(QWidget):
    """Форма створення і редагування одного медичного запису.
    Form for creating and editing one medical record.
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

        self.decision_input = QComboBox()
        for decision in MedicalDecision:
            self.decision_input.addItem(format_medical_decision_label(decision), decision.value)
        form.addRow("Рішення", self.decision_input)

        self.valid_from_input = QLineEdit()
        self.valid_from_input.setPlaceholderText("YYYY-MM-DD")
        form.addRow("Початок", self.valid_from_input)
        self.valid_until_input = QLineEdit()
        self.valid_until_input.setPlaceholderText("YYYY-MM-DD")
        form.addRow("Закінчення", self.valid_until_input)
        self.restriction_input = QTextEdit()
        self.restriction_input.setMaximumHeight(90)
        form.addRow("Обмеження", self.restriction_input)
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

    def set_row(self, row: MedicalWorkspaceRow) -> None:
        """Заповнює форму вибраним медичним записом.
        Fills the form with a selected medical record.
        """

        self._current_record_id = row.record_id
        self.employee_input.setCurrentIndex(max(0, self.employee_input.findData(row.employee_personnel_number)))
        self.decision_input.setCurrentIndex(max(0, self.decision_input.findData(row.medical_decision.value)))
        self.valid_from_input.setText(row.valid_from)
        self.valid_until_input.setText(row.valid_until)
        self.restriction_input.setPlainText(row.restriction_note)
        self.save_button.setText("Зберегти зміни")

    def clear_form(self) -> None:
        """Готує форму до створення нового запису.
        Prepares the form for creating a new record.
        """

        self._current_record_id = None
        self.decision_input.setCurrentIndex(0)
        self.valid_from_input.clear()
        self.valid_until_input.clear()
        self.restriction_input.clear()
        self.save_button.setText("Створити запис")

    def _save_record(self) -> None:
        """Зберігає запис через application service і оновлює екран.
        Saves the record through application service and refreshes the screen.
        """

        try:
            if self._current_record_id is None:
                create_medical_record(
                    self._database_path,
                    str(self.employee_input.currentData()),
                    self.valid_from_input.text(),
                    self.valid_until_input.text(),
                    str(self.decision_input.currentData()),
                    self.restriction_input.toPlainText(),
                )
            else:
                update_medical_record(
                    self._database_path,
                    self._current_record_id,
                    str(self.employee_input.currentData()),
                    self.valid_from_input.text(),
                    self.valid_until_input.text(),
                    str(self.decision_input.currentData()),
                    self.restriction_input.toPlainText(),
                )
        except ValueError as error:
            self.feedback_label.show_error(str(error))
            return
        self.feedback_label.show_success("Медичний запис збережено.")
        self.saved.emit()

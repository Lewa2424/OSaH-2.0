from pathlib import Path

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QCheckBox, QComboBox, QFormLayout, QLineEdit, QPushButton, QTextEdit, QVBoxLayout, QWidget

from osah.application.services.create_ppe_record import create_ppe_record
from osah.application.services.update_ppe_record import update_ppe_record
from osah.domain.entities.employee import Employee
from osah.domain.entities.ppe_workspace_row import PpeWorkspaceRow
from osah.domain.services.format_ui_date import format_ui_date
from osah.ui.qt.components.form_feedback_label import FormFeedbackLabel
from osah.ui.qt.design.tokens import SPACING


class PpeRecordEditor(QWidget):
    """Форма створення і редагування одного запису ЗІЗ.
    Form for creating and editing one PPE record.
    """

    saved = Signal()

    def __init__(self, database_path: Path, employees: tuple[Employee, ...], ppe_names: tuple[str, ...]) -> None:
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

        self.ppe_input = QComboBox()
        self.ppe_input.setEditable(True)
        for ppe_name in ppe_names:
            self.ppe_input.addItem(ppe_name, ppe_name)
        form.addRow("Тип ЗІЗ", self.ppe_input)

        self.required_input = QCheckBox("Положено за нормою")
        self.required_input.setChecked(True)
        form.addRow("Норма", self.required_input)

        self.issued_input = QCheckBox("Фактично видано")
        self.issued_input.setChecked(True)
        form.addRow("Факт", self.issued_input)

        self.issue_date_input = QLineEdit()
        self.issue_date_input.setPlaceholderText("ДД.ММ.ГГГГ")
        form.addRow("Дата видачі", self.issue_date_input)

        self.replacement_date_input = QLineEdit()
        self.replacement_date_input.setPlaceholderText("ДД.ММ.ГГГГ")
        form.addRow("Дата заміни", self.replacement_date_input)

        self.quantity_input = QLineEdit()
        form.addRow("Кількість", self.quantity_input)

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

    def set_row(self, row: PpeWorkspaceRow) -> None:
        """Заповнює форму вибраною позицією ЗІЗ.
        Fills the form with a selected PPE item.
        """

        self._current_record_id = row.record_id
        self.employee_input.setCurrentIndex(max(0, self.employee_input.findData(row.employee_personnel_number)))
        self.ppe_input.setCurrentText(row.ppe_name)
        self.required_input.setChecked(row.is_required)
        self.issued_input.setChecked(row.is_issued)
        self.issue_date_input.setText(format_ui_date(row.issue_date))
        self.replacement_date_input.setText(format_ui_date(row.replacement_date))
        self.quantity_input.setText(str(row.quantity))
        self.note_input.setPlainText(row.note_text)
        self.save_button.setText("Зберегти зміни")

    def clear_form(self) -> None:
        """Готує форму до створення нового запису.
        Prepares the form for creating a new record.
        """

        self._current_record_id = None
        self.ppe_input.setCurrentIndex(0)
        self.required_input.setChecked(True)
        self.issued_input.setChecked(True)
        self.issue_date_input.clear()
        self.replacement_date_input.clear()
        self.quantity_input.clear()
        self.note_input.clear()
        self.save_button.setText("Створити запис")

    def _save_record(self) -> None:
        """Зберігає запис через application service і оновлює екран.
        Saves the record through application service and refreshes the screen.
        """

        try:
            if self._current_record_id is None:
                create_ppe_record(
                    self._database_path,
                    str(self.employee_input.currentData()),
                    self.ppe_input.currentText(),
                    self.required_input.isChecked(),
                    self.issued_input.isChecked(),
                    self.issue_date_input.text(),
                    self.replacement_date_input.text(),
                    self.quantity_input.text(),
                    self.note_input.toPlainText(),
                )
            else:
                update_ppe_record(
                    self._database_path,
                    self._current_record_id,
                    str(self.employee_input.currentData()),
                    self.ppe_input.currentText(),
                    self.required_input.isChecked(),
                    self.issued_input.isChecked(),
                    self.issue_date_input.text(),
                    self.replacement_date_input.text(),
                    self.quantity_input.text(),
                    self.note_input.toPlainText(),
                )
        except ValueError as error:
            self.feedback_label.show_error(str(error))
            return
        self.feedback_label.show_success("Запис ЗІЗ збережено.")
        self.saved.emit()

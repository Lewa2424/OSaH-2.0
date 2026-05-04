from pathlib import Path

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QComboBox, QFormLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit, QVBoxLayout, QWidget

from osah.application.services.create_ppe_record import create_ppe_record
from osah.application.services.update_ppe_record import update_ppe_record
from osah.domain.services.build_default_ppe_names import build_default_ppe_names
from osah.domain.entities.employee import Employee
from osah.domain.entities.ppe_compliance_check_state import PpeComplianceCheckState
from osah.domain.entities.ppe_provision_status import PpeProvisionStatus
from osah.domain.entities.ppe_workspace_row import PpeWorkspaceRow
from osah.domain.services.format_ui_date import format_ui_date
from osah.ui.qt.components.basis_note_panel import BasisNotePanel
from osah.ui.qt.components.date_line_edit import DateLineEdit
from osah.ui.qt.components.form_feedback_label import FormFeedbackLabel
from osah.ui.qt.components.info_tooltip_icon import InfoTooltipIcon
from osah.ui.qt.design.tokens import SPACING
from osah.ui.qt.hints.normative_hints import PPE_COMPLIANCE_HINT, PPE_PROVISION_HINT, PPE_REPLACEMENT_HINT


class PpeRecordEditor(QWidget):
    """Форма создания и редактирования одной записи СИЗ.
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
        for ppe_name in tuple(sorted({*ppe_names, *build_default_ppe_names()})):
            self.ppe_input.addItem(ppe_name, ppe_name)
        form.addRow("Тип ЗІЗ", self.ppe_input)

        self.provision_status_input = QComboBox()
        self.provision_status_input.addItem("Не відстежувалось раніше", PpeProvisionStatus.LEGACY_NOT_TRACKED.value)
        self.provision_status_input.addItem("Положено, але не видано", PpeProvisionStatus.REQUIRED_NOT_ISSUED.value)
        self.provision_status_input.addItem("Видано", PpeProvisionStatus.ISSUED.value)
        self.provision_status_input.addItem("Не потрібно", PpeProvisionStatus.NOT_REQUIRED.value)
        form.addRow(self._with_info("Статус забезпечення", PPE_PROVISION_HINT), self.provision_status_input)

        self.compliance_state_input = QComboBox()
        self.compliance_state_input.addItem("Не відстежувалось раніше", PpeComplianceCheckState.LEGACY_NOT_TRACKED.value)
        self.compliance_state_input.addItem("Перевірено", PpeComplianceCheckState.CHECKED.value)
        self.compliance_state_input.addItem("Не перевірено", PpeComplianceCheckState.NOT_CHECKED.value)
        form.addRow(self._with_info("Відповідність перевірено", PPE_COMPLIANCE_HINT), self.compliance_state_input)

        self.required_input = QComboBox()
        self.required_input.addItem("Так", "1")
        self.required_input.addItem("Ні", "0")
        form.addRow("Положено за нормою", self.required_input)

        self.issued_input = QComboBox()
        self.issued_input.addItem("Так", "1")
        self.issued_input.addItem("Ні", "0")
        form.addRow("Фактично видано", self.issued_input)

        self.issue_date_input = DateLineEdit()
        self.issue_date_input.setPlaceholderText("ДД.ММ.ГГГГ")
        form.addRow("Дата видачі", self.issue_date_input)

        self.replacement_date_input = DateLineEdit()
        self.replacement_date_input.setPlaceholderText("ДД.ММ.ГГГГ")
        form.addRow(self._with_info("Дата заміни", PPE_REPLACEMENT_HINT), self.replacement_date_input)

        self.quantity_input = QLineEdit()
        form.addRow("Кількість", self.quantity_input)

        self.note_input = QTextEdit()
        self.note_input.setMaximumHeight(80)
        form.addRow("Примітка", self.note_input)
        layout.addLayout(form)

        self.basis_panel = BasisNotePanel()
        self.basis_panel.setVisible(False)
        layout.addWidget(self.basis_panel)

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

    def _with_info(self, text: str, tooltip_text: str) -> QWidget:
        container = QWidget()
        row = QHBoxLayout(container)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(0)
        row.addWidget(QLabel(text))
        row.addWidget(InfoTooltipIcon(tooltip_text))
        row.addStretch()
        return container

    def set_row(self, row: PpeWorkspaceRow) -> None:
        self._current_record_id = row.record_id
        self.employee_input.setCurrentIndex(max(0, self.employee_input.findData(row.employee_personnel_number)))
        self.ppe_input.setCurrentText(row.ppe_name)
        self.required_input.setCurrentIndex(0 if row.is_required else 1)
        self.issued_input.setCurrentIndex(0 if row.is_issued else 1)
        self.issue_date_input.setText(format_ui_date(row.issue_date))
        self.replacement_date_input.setText(format_ui_date(row.replacement_date))
        self.quantity_input.setText(str(row.quantity))
        self.note_input.setPlainText(row.note_text)
        self.provision_status_input.setCurrentIndex(max(0, self.provision_status_input.findData(row.provision_status.value)))
        self.compliance_state_input.setCurrentIndex(max(0, self.compliance_state_input.findData(row.compliance_check_state.value)))
        self.basis_panel.set_values(row.basis_text, row.basis_note)
        self.save_button.setText("Зберегти зміни")

    def clear_form(self) -> None:
        self._current_record_id = None
        self.ppe_input.setCurrentIndex(0)
        self.required_input.setCurrentIndex(0)
        self.issued_input.setCurrentIndex(0)
        self.provision_status_input.setCurrentIndex(0)
        self.compliance_state_input.setCurrentIndex(0)
        self.issue_date_input.clear()
        self.replacement_date_input.clear()
        self.quantity_input.clear()
        self.note_input.clear()
        self.basis_panel.clear()
        self.save_button.setText("Створити запис")

    def _save_record(self) -> None:
        basis_text, basis_note = self.basis_panel.values()
        try:
            if self._current_record_id is None:
                create_ppe_record(
                    self._database_path,
                    str(self.employee_input.currentData()),
                    self.ppe_input.currentText(),
                    str(self.required_input.currentData()) == "1",
                    str(self.issued_input.currentData()) == "1",
                    self.issue_date_input.text(),
                    self.replacement_date_input.text(),
                    self.quantity_input.text(),
                    self.note_input.toPlainText(),
                    str(self.provision_status_input.currentData()),
                    str(self.compliance_state_input.currentData()),
                    basis_text,
                    basis_note,
                )
            else:
                update_ppe_record(
                    self._database_path,
                    self._current_record_id,
                    str(self.employee_input.currentData()),
                    self.ppe_input.currentText(),
                    str(self.required_input.currentData()) == "1",
                    str(self.issued_input.currentData()) == "1",
                    self.issue_date_input.text(),
                    self.replacement_date_input.text(),
                    self.quantity_input.text(),
                    self.note_input.toPlainText(),
                    str(self.provision_status_input.currentData()),
                    str(self.compliance_state_input.currentData()),
                    basis_text,
                    basis_note,
                )
        except ValueError as error:
            self.feedback_label.show_error(str(error))
            return
        self.feedback_label.show_success("Запис ЗІЗ збережено.")
        self.saved.emit()

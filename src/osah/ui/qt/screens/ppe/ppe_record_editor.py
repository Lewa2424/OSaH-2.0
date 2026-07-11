from pathlib import Path

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QComboBox, QFormLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit, QVBoxLayout, QWidget

from osah.application.services.create_ppe_record import create_ppe_record
from osah.application.services.update_ppe_record import update_ppe_record
from osah.domain.entities.access_role import AccessRole
from osah.domain.entities.employee import Employee
from osah.domain.entities.ppe_compliance_check_state import PpeComplianceCheckState
from osah.domain.entities.ppe_provision_status import PpeProvisionStatus
from osah.domain.entities.ppe_workspace_row import PpeWorkspaceRow
from osah.domain.services.build_default_ppe_names import build_default_ppe_names
from osah.domain.services.format_ui_date import format_ui_date
from osah.ui.qt.components.basis_note_panel import BasisNotePanel
from osah.ui.qt.components.date_line_edit import DateLineEdit
from osah.ui.qt.components.form_feedback_label import FormFeedbackLabel
from osah.ui.qt.components.info_tooltip_icon import InfoTooltipIcon
from osah.ui.qt.design.tokens import COLOR, RADIUS, SPACING
from osah.ui.qt.hints.normative_hints import PPE_COMPLIANCE_HINT, PPE_PROVISION_HINT, PPE_REPLACEMENT_HINT


class PpeRecordEditor(QWidget):
    """Форма створення і редагування однієї позиції ЗІЗ.
    Form for creating and editing one PPE record.
    """

    saved = Signal()

    def __init__(
        self,
        database_path: Path,
        employees: tuple[Employee, ...],
        ppe_names: tuple[str, ...],
        access_role: AccessRole,
    ) -> None:
        super().__init__()
        self._database_path = database_path
        self._access_role = access_role
        self._read_only = access_role != AccessRole.INSPECTOR
        self._current_record_id: int | None = None
        self._locked_employee_number: str | None = None
        self.setStyleSheet(
            f"""
            QComboBox, QLineEdit, QTextEdit {{
                background: #FFFFFF;
                color: {COLOR['text_primary']};
                border: 1px solid #CBD6E2;
                border-radius: {RADIUS['lg']}px;
                font-size: 14px;
                font-weight: 600;
            }}
            QComboBox, QLineEdit {{
                min-height: 40px;
                padding: 0 14px;
            }}
            QTextEdit {{
                padding: 10px 12px;
            }}
            QLabel {{
                color: {COLOR['text_secondary']};
                font-size: 14px;
                font-weight: 700;
            }}
            QPushButton {{
                min-height: 42px;
                padding: 0 18px;
                border-radius: {RADIUS['lg']}px;
                font-size: 14px;
                font-weight: 800;
            }}
            """
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING["md"])

        form = QFormLayout()
        self.employee_input = QComboBox()
        for employee in employees:
            if employee.employment_status.strip().lower() == "active":
                self.employee_input.addItem(f"{employee.full_name} ({employee.personnel_number})", employee.personnel_number)
        form.addRow("Працівник", self.employee_input)
        self.employee_input.setVisible(False)

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
        self.issue_date_input.setPlaceholderText("ДД.ММ.РРРР")
        form.addRow("Дата видачі", self.issue_date_input)

        self.replacement_date_input = DateLineEdit()
        self.replacement_date_input.setPlaceholderText("ДД.ММ.РРРР")
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
        self.new_button.setVisible(False)
        layout.addWidget(self.new_button)
        self._apply_read_only_mode()

    def _with_info(self, text: str, tooltip_text: str) -> QWidget:
        container = QWidget()
        row = QHBoxLayout(container)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(0)
        row.addWidget(QLabel(text))
        row.addWidget(InfoTooltipIcon(tooltip_text))
        row.addStretch()
        return container

    def set_locked_employee(self, employee_personnel_number: str) -> None:
        """Фіксує працівника для картки ЗІЗ.
        Locks the employee context for the PPE card.
        """

        self._locked_employee_number = employee_personnel_number
        self.employee_input.setCurrentIndex(max(0, self.employee_input.findData(employee_personnel_number)))

    def set_row(self, row: PpeWorkspaceRow) -> None:
        self._current_record_id = row.record_id
        self.set_locked_employee(row.employee_personnel_number)
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
        self._apply_read_only_mode()

    def prepare_card_create_mode(self, employee_personnel_number: str, ppe_name: str | None = None) -> None:
        """Готує картку до створення нової позиції ЗІЗ для працівника.
        Prepares the card for creating a new PPE item for the employee.
        """

        self.set_locked_employee(employee_personnel_number)
        self.clear_form()
        if ppe_name:
            self.ppe_input.setCurrentText(ppe_name)

    def clear_form(self) -> None:
        self._current_record_id = None
        if self._locked_employee_number is not None:
            self.employee_input.setCurrentIndex(max(0, self.employee_input.findData(self._locked_employee_number)))
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
        self._apply_read_only_mode()

    def current_selection_context(self) -> tuple[int | None, str | None]:
        """Повертає контекст вибору для відновлення після reload.
        Returns selection context for restoration after reload.
        """

        personnel_number = self.employee_input.currentData()
        if self._current_record_id is None:
            return None, str(personnel_number) if personnel_number is not None else self._locked_employee_number
        return self._current_record_id, str(personnel_number) if personnel_number is not None else self._locked_employee_number

    def _save_record(self) -> None:
        if self._read_only:
            self.feedback_label.show_error("Режим read-only: збереження недоступне.")
            return
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
                    access_role=self._access_role,
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
                    access_role=self._access_role,
                )
        except ValueError as error:
            self.feedback_label.show_error(str(error))
            return
        self.feedback_label.show_success("Запис ЗІЗ збережено.")
        self.saved.emit()

    def _apply_read_only_mode(self) -> None:
        """Disables mutating controls while keeping the current PPE card visible."""

        for widget in (
            self.ppe_input,
            self.provision_status_input,
            self.compliance_state_input,
            self.required_input,
            self.issued_input,
            self.issue_date_input,
            self.replacement_date_input,
            self.quantity_input,
            self.note_input,
        ):
            widget.setEnabled(not self._read_only)
        self.save_button.setVisible(not self._read_only)
        self.save_button.setEnabled(not self._read_only)
        self.new_button.setVisible(not self._read_only and self.new_button.isVisible())
        self.new_button.setEnabled(not self._read_only)

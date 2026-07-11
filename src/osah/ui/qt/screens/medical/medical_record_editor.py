from pathlib import Path

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QComboBox, QFormLayout, QHBoxLayout, QLabel, QPushButton, QTextEdit, QVBoxLayout, QWidget

from osah.application.services.create_medical_record import create_medical_record
from osah.application.services.update_medical_record import update_medical_record
from osah.domain.entities.access_role import AccessRole
from osah.domain.entities.employee import Employee
from osah.domain.entities.medical_decision import MedicalDecision
from osah.domain.entities.medical_exam_basis import MedicalExamBasis
from osah.domain.entities.medical_workspace_row import MedicalWorkspaceRow
from osah.domain.services.format_medical_decision_label import format_medical_decision_label
from osah.domain.services.format_ui_date import format_ui_date
from osah.ui.qt.components.basis_note_panel import BasisNotePanel
from osah.ui.qt.components.checkable_options_menu_button import CheckableOptionsMenuButton
from osah.ui.qt.components.date_line_edit import DateLineEdit
from osah.ui.qt.components.form_feedback_label import FormFeedbackLabel
from osah.ui.qt.components.info_tooltip_icon import InfoTooltipIcon
from osah.ui.qt.design.tokens import COLOR, RADIUS, SPACING
from osah.ui.qt.hints.normative_hints import MEDICAL_BASIS_HINT, MEDICAL_DECISION_HINT, MEDICAL_RESTRICTIONS_HINT


class MedicalRecordEditor(QWidget):
    """Форма створення і редагування одного медичного запису.
    Form for creating and editing one medical record.
    """

    saved = Signal()

    def __init__(self, database_path: Path, employees: tuple[Employee, ...], access_role: AccessRole) -> None:
        super().__init__()
        self._database_path = database_path
        self._access_role = access_role
        self._read_only = access_role != AccessRole.INSPECTOR
        self._current_record_id: int | None = None
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

        self.basis_input = QComboBox()
        self.basis_input.addItem("Не відстежувалось раніше", MedicalExamBasis.LEGACY_NOT_TRACKED.value)
        self.basis_input.addItem("Шкідливі або небезпечні фактори", MedicalExamBasis.HARMFUL_OR_DANGEROUS_FACTORS.value)
        self.basis_input.addItem("Важкі роботи", MedicalExamBasis.HEAVY_WORK.value)
        self.basis_input.addItem("Професійний добір", MedicalExamBasis.PROFESSIONAL_SELECTION.value)
        self.basis_input.addItem("Вік до 21 року", MedicalExamBasis.UNDER_21.value)
        self.basis_input.addItem("Внутрішній список підприємства", MedicalExamBasis.INTERNAL_LIST.value)
        self.basis_input.addItem("Інше", MedicalExamBasis.OTHER.value)
        form.addRow(self._with_info("Підстава медогляду", MEDICAL_BASIS_HINT), self.basis_input)

        self.decision_input = QComboBox()
        for decision in MedicalDecision:
            self.decision_input.addItem(format_medical_decision_label(decision), decision.value)
        form.addRow(self._with_info("Рішення", MEDICAL_DECISION_HINT), self.decision_input)

        self.valid_from_input = DateLineEdit()
        self.valid_from_input.setPlaceholderText("ДД.ММ.РРРР")
        form.addRow("Початок", self.valid_from_input)

        self.valid_until_input = DateLineEdit()
        self.valid_until_input.setPlaceholderText("ДД.ММ.РРРР")
        form.addRow("Закінчення", self.valid_until_input)

        self.restriction_input = QTextEdit()
        self.restriction_input.setMaximumHeight(90)
        form.addRow(self._with_info("Обмеження", MEDICAL_RESTRICTIONS_HINT), self.restriction_input)

        self._restriction_option_values = (
            "висота",
            "нічні роботи",
            "підйом тягарів",
            "замкнуті простори",
            "робота з механізмами",
            "інше",
        )
        self.restriction_selector = CheckableOptionsMenuButton("Швидкий вибір обмежень", self._restriction_option_values)
        self.restriction_selector.values_changed.connect(self._apply_restriction_selection)
        form.addRow("", self.restriction_selector)

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

    def _append_restriction_chip(self, text: str) -> None:
        current = self.restriction_input.toPlainText().strip()
        parts = [part.strip() for part in current.split(",") if part.strip()]
        if text not in parts:
            parts.append(text)
        self.restriction_input.setPlainText(", ".join(parts))

    def _apply_restriction_selection(self, selected_values: tuple[str, ...]) -> None:
        """Оновлює текст обмежень за відміченими пунктами, не затираючи довільний опис.
        Updates restriction text from checked options without overwriting custom notes.
        """

        current_text = self.restriction_input.toPlainText().strip()
        parts = [part.strip() for part in current_text.split(",") if part.strip()]
        custom_parts = [part for part in parts if part not in self._restriction_option_values]
        merged_parts = list(selected_values) + custom_parts
        self.restriction_input.setPlainText(", ".join(merged_parts))

    def _sync_restriction_selector_from_text(self, restriction_text: str) -> None:
        """Синхронізує popup-вибір зі значенням текстового поля.
        Synchronizes popup selection with the text field value.
        """

        parts = [part.strip() for part in restriction_text.split(",") if part.strip()]
        self.restriction_selector.set_checked_values(
            tuple(part for part in parts if part in self._restriction_option_values)
        )

    def set_row(self, row: MedicalWorkspaceRow) -> None:
        self._current_record_id = row.record_id
        self.employee_input.setCurrentIndex(max(0, self.employee_input.findData(row.employee_personnel_number)))
        self.decision_input.setCurrentIndex(max(0, self.decision_input.findData(row.medical_decision.value)))
        self.basis_input.setCurrentIndex(max(0, self.basis_input.findData(row.medical_exam_basis.value)))
        self.valid_from_input.setText(format_ui_date(row.valid_from))
        self.valid_until_input.setText(format_ui_date(row.valid_until))
        self.restriction_input.setPlainText(row.restriction_note)
        self._sync_restriction_selector_from_text(row.restriction_note)
        self.basis_panel.set_values(row.basis_text, row.basis_note)
        self.save_button.setText("Зберегти зміни")
        self._apply_read_only_mode()

    def clear_form(self) -> None:
        self._current_record_id = None
        self.decision_input.setCurrentIndex(0)
        self.basis_input.setCurrentIndex(0)
        self.valid_from_input.clear()
        self.valid_until_input.clear()
        self.restriction_input.clear()
        self.restriction_selector.clear_checked_values()
        self.basis_panel.clear()
        self.save_button.setText("Створити запис")
        self._apply_read_only_mode()

    def _save_record(self) -> None:
        if self._read_only:
            self.feedback_label.show_error("Режим read-only: збереження недоступне.")
            return
        basis_text, basis_note = self.basis_panel.values()
        try:
            if self._current_record_id is None:
                create_medical_record(
                    self._database_path,
                    str(self.employee_input.currentData()),
                    self.valid_from_input.text(),
                    self.valid_until_input.text(),
                    str(self.decision_input.currentData()),
                    self.restriction_input.toPlainText(),
                    str(self.basis_input.currentData()),
                    basis_text,
                    basis_note,
                    access_role=self._access_role,
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
                    str(self.basis_input.currentData()),
                    basis_text,
                    basis_note,
                    access_role=self._access_role,
                )
        except ValueError as error:
            self.feedback_label.show_error(str(error))
            return
        self.feedback_label.show_success("Медичний запис збережено.")
        self.saved.emit()

    def _apply_read_only_mode(self) -> None:
        """Disables record mutation controls while preserving field visibility."""

        for widget in (
            self.employee_input,
            self.basis_input,
            self.decision_input,
            self.valid_from_input,
            self.valid_until_input,
            self.restriction_input,
            self.restriction_selector,
        ):
            widget.setEnabled(not self._read_only)
        self.save_button.setVisible(not self._read_only)
        self.save_button.setEnabled(not self._read_only)
        self.new_button.setVisible(not self._read_only)
        self.new_button.setEnabled(not self._read_only)

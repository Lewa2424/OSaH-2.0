from pathlib import Path

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QComboBox, QFormLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit, QVBoxLayout, QWidget

from osah.application.services.create_work_permit_record import create_work_permit_record
from osah.application.services.load_employee_work_readiness import load_employee_work_readiness
from osah.application.services.update_work_permit_record import update_work_permit_record
from osah.domain.entities.app_section import AppSection
from osah.domain.entities.employee import Employee
from osah.domain.entities.employee_readiness_level import EmployeeReadinessLevel
from osah.domain.entities.work_permit_participant_role import WorkPermitParticipantRole
from osah.domain.entities.work_permit_target_training_status import WorkPermitTargetTrainingStatus
from osah.domain.entities.work_permit_workspace_row import WorkPermitWorkspaceRow
from osah.domain.services.format_ui_datetime import format_ui_datetime
from osah.domain.services.format_work_permit_participant_role_label import format_work_permit_participant_role_label
from osah.ui.qt.components.basis_note_panel import BasisNotePanel
from osah.ui.qt.components.date_line_edit import DateLineEdit
from osah.ui.qt.components.form_feedback_label import FormFeedbackLabel
from osah.ui.qt.components.info_tooltip_icon import InfoTooltipIcon
from osah.ui.qt.design.tokens import SPACING
from osah.ui.qt.hints.normative_hints import (
    WORK_PERMIT_KIND_HINT,
    WORK_PERMIT_PARTICIPANT_READINESS_HINT,
    WORK_PERMIT_TARGET_TRAINING_HINT,
)


class WorkPermitEditor(QWidget):
    """Форма создания и редактирования наряда-допуска.
    Form for creating and editing a work permit.
    """

    saved = Signal()
    module_navigation_requested = Signal(AppSection, str)

    def __init__(self, database_path: Path, employees: tuple[Employee, ...]) -> None:
        super().__init__()
        self._database_path = database_path
        self._current_record_id: int | None = None
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING["md"])
        form = QFormLayout()

        self.permit_number_input = QLineEdit()
        form.addRow("Номер", self.permit_number_input)

        self.work_kind_input = QLineEdit()
        self.work_kind_input.setPlaceholderText("Наприклад: вогневі, газонебезпечні, висотні, ремонтні...")
        form.addRow(self._with_info("Вид робіт", WORK_PERMIT_KIND_HINT), self.work_kind_input)

        self.work_location_input = QLineEdit()
        form.addRow("Місце", self.work_location_input)

        self.starts_at_input = QLineEdit()
        self.starts_at_input.setPlaceholderText("ДД.ММ.ГГГГ HH:MM")
        form.addRow("Початок", self.starts_at_input)

        self.ends_at_input = QLineEdit()
        self.ends_at_input.setPlaceholderText("ДД.ММ.ГГГГ HH:MM")
        form.addRow("Завершення", self.ends_at_input)

        self.responsible_input = QLineEdit()
        form.addRow("Відповідальний", self.responsible_input)
        self.issuer_input = QLineEdit()
        form.addRow("Допускаючий", self.issuer_input)

        self.employee_input = QComboBox()
        for employee in employees:
            if employee.employment_status.strip().lower() == "active":
                self.employee_input.addItem(f"{employee.full_name} ({employee.personnel_number})", employee.personnel_number)
        self.employee_input.currentIndexChanged.connect(lambda _index: self._refresh_readiness_panel())
        form.addRow("Учасник", self.employee_input)

        self.role_input = QComboBox()
        for role in WorkPermitParticipantRole:
            self.role_input.addItem(format_work_permit_participant_role_label(role), role.value)
        form.addRow("Роль", self.role_input)

        self.target_training_status_input = QComboBox()
        self.target_training_status_input.addItem("Не відстежувалось раніше", WorkPermitTargetTrainingStatus.LEGACY_NOT_TRACKED.value)
        self.target_training_status_input.addItem("Невідомо", WorkPermitTargetTrainingStatus.UNKNOWN.value)
        self.target_training_status_input.addItem("Не потрібно", WorkPermitTargetTrainingStatus.NOT_REQUIRED.value)
        self.target_training_status_input.addItem("Потрібно, але не проведено", WorkPermitTargetTrainingStatus.REQUIRED_NOT_DONE.value)
        self.target_training_status_input.addItem("Проведено", WorkPermitTargetTrainingStatus.DONE.value)
        form.addRow(self._with_info("Цільовий інструктаж", WORK_PERMIT_TARGET_TRAINING_HINT), self.target_training_status_input)

        self.target_training_date_input = DateLineEdit()
        self.target_training_date_input.setPlaceholderText("ДД.ММ.ГГГГ")
        form.addRow("Дата інструктажу", self.target_training_date_input)

        self.target_training_conducted_by_input = QLineEdit()
        form.addRow("Хто провів", self.target_training_conducted_by_input)

        self.target_training_note_input = QLineEdit()
        self.target_training_note_input.setPlaceholderText("Коментар / посилання на запис")
        form.addRow("Коментар", self.target_training_note_input)

        self.note_input = QTextEdit()
        self.note_input.setMaximumHeight(70)
        form.addRow("Примітка", self.note_input)
        layout.addLayout(form)

        self._readiness_title = self._with_info("Стан учасника", WORK_PERMIT_PARTICIPANT_READINESS_HINT)
        layout.addWidget(self._readiness_title)
        self._training_readiness_label = QLabel("Інструктажі: -")
        self._medical_readiness_label = QLabel("Медицина: -")
        self._ppe_readiness_label = QLabel("ЗІЗ: -")
        layout.addWidget(self._training_readiness_label)
        layout.addWidget(self._medical_readiness_label)
        layout.addWidget(self._ppe_readiness_label)

        readiness_actions = QHBoxLayout()
        self._open_training_button = QPushButton("Відкрити інструктажі")
        self._open_training_button.clicked.connect(lambda: self._open_module(AppSection.TRAININGS))
        self._open_medical_button = QPushButton("Відкрити медицину")
        self._open_medical_button.clicked.connect(lambda: self._open_module(AppSection.MEDICAL))
        self._open_ppe_button = QPushButton("Відкрити ЗІЗ")
        self._open_ppe_button.clicked.connect(lambda: self._open_module(AppSection.PPE))
        readiness_actions.addWidget(self._open_training_button)
        readiness_actions.addWidget(self._open_medical_button)
        readiness_actions.addWidget(self._open_ppe_button)
        layout.addLayout(readiness_actions)

        self.basis_panel = BasisNotePanel()
        self.basis_panel.setVisible(False)
        layout.addWidget(self.basis_panel)

        self.feedback_label = FormFeedbackLabel()
        layout.addWidget(self.feedback_label)

        self.save_button = QPushButton("Зберегти наряд")
        self.save_button.setProperty("variant", "accent")
        self.save_button.clicked.connect(self._save_record)
        layout.addWidget(self.save_button)

        self.new_button = QPushButton("Новий наряд")
        self.new_button.setProperty("variant", "secondary")
        self.new_button.clicked.connect(self.clear_form)
        layout.addWidget(self.new_button)
        self._refresh_readiness_panel()

    def _with_info(self, text: str, tooltip_text: str) -> QWidget:
        container = QWidget()
        row = QHBoxLayout(container)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(0)
        row.addWidget(QLabel(text))
        row.addWidget(InfoTooltipIcon(tooltip_text))
        row.addStretch()
        return container

    def set_row(self, row: WorkPermitWorkspaceRow) -> None:
        self._current_record_id = row.record_id
        self.permit_number_input.setText(row.permit_number)
        self.work_kind_input.setText(row.work_kind)
        self.work_location_input.setText(row.work_location)
        self.starts_at_input.setText(format_ui_datetime(row.starts_at))
        self.ends_at_input.setText(format_ui_datetime(row.ends_at))
        self.responsible_input.setText(row.responsible_person)
        self.issuer_input.setText(row.issuer_person)
        if row.record.participants:
            participant = row.record.participants[0]
            self.employee_input.setCurrentIndex(max(0, self.employee_input.findData(participant.employee_personnel_number)))
            self.role_input.setCurrentIndex(max(0, self.role_input.findData(participant.participant_role.value)))
        self.note_input.setPlainText(row.record.note_text)
        self.target_training_status_input.setCurrentIndex(max(0, self.target_training_status_input.findData(row.record.target_training_status.value)))
        self.target_training_date_input.setText(row.record.target_training_date)
        self.target_training_conducted_by_input.setText(row.record.target_training_conducted_by)
        self.target_training_note_input.setText(row.record.target_training_note)
        self.basis_panel.set_values(row.record.basis_text, row.record.basis_note)
        self.save_button.setText("Зберегти зміни")
        self._refresh_readiness_panel()

    def clear_form(self) -> None:
        self._current_record_id = None
        for field in (
            self.permit_number_input,
            self.work_kind_input,
            self.work_location_input,
            self.starts_at_input,
            self.ends_at_input,
            self.responsible_input,
            self.issuer_input,
            self.target_training_date_input,
            self.target_training_conducted_by_input,
            self.target_training_note_input,
        ):
            field.clear()
        self.note_input.clear()
        self.basis_panel.clear()
        self.target_training_status_input.setCurrentIndex(0)
        self.save_button.setText("Створити наряд")
        self._refresh_readiness_panel()

    def _refresh_readiness_panel(self) -> None:
        personnel_number = str(self.employee_input.currentData() or "").strip()
        if not personnel_number:
            self._training_readiness_label.setText("Інструктажі: немає даних")
            self._medical_readiness_label.setText("Медицина: немає даних")
            self._ppe_readiness_label.setText("ЗІЗ: немає даних")
            return
        readiness = load_employee_work_readiness(self._database_path, personnel_number)
        self._training_readiness_label.setText(f"Інструктажі: {self._readiness_text(readiness.training_level)}. {readiness.training_message}")
        self._medical_readiness_label.setText(f"Медицина: {self._readiness_text(readiness.medical_level)}. {readiness.medical_message}")
        self._ppe_readiness_label.setText(f"ЗІЗ: {self._readiness_text(readiness.ppe_level)}. {readiness.ppe_message}")

    def _readiness_text(self, level: EmployeeReadinessLevel) -> str:
        mapping = {
            EmployeeReadinessLevel.NORMAL: "Норма",
            EmployeeReadinessLevel.WARNING: "Увага",
            EmployeeReadinessLevel.CRITICAL: "Критично",
            EmployeeReadinessLevel.UNKNOWN: "Немає даних",
        }
        return mapping[level]

    def _open_module(self, section: AppSection) -> None:
        personnel_number = str(self.employee_input.currentData() or "").strip()
        if personnel_number:
            self.module_navigation_requested.emit(section, personnel_number)

    def _save_record(self) -> None:
        basis_text, basis_note = self.basis_panel.values()
        try:
            if self._current_record_id is None:
                create_work_permit_record(
                    self._database_path,
                    self.permit_number_input.text(),
                    self.work_kind_input.text(),
                    self.work_location_input.text(),
                    self.starts_at_input.text(),
                    self.ends_at_input.text(),
                    self.responsible_input.text(),
                    self.issuer_input.text(),
                    str(self.employee_input.currentData()),
                    str(self.role_input.currentData()),
                    self.note_input.toPlainText(),
                    str(self.target_training_status_input.currentData()),
                    self.target_training_date_input.text(),
                    self.target_training_conducted_by_input.text(),
                    self.target_training_note_input.text(),
                    basis_text,
                    basis_note,
                )
            else:
                update_work_permit_record(
                    self._database_path,
                    self._current_record_id,
                    self.permit_number_input.text(),
                    self.work_kind_input.text(),
                    self.work_location_input.text(),
                    self.starts_at_input.text(),
                    self.ends_at_input.text(),
                    self.responsible_input.text(),
                    self.issuer_input.text(),
                    str(self.employee_input.currentData()),
                    str(self.role_input.currentData()),
                    self.note_input.toPlainText(),
                    str(self.target_training_status_input.currentData()),
                    self.target_training_date_input.text(),
                    self.target_training_conducted_by_input.text(),
                    self.target_training_note_input.text(),
                    basis_text,
                    basis_note,
                )
        except ValueError as error:
            self.feedback_label.show_error(str(error))
            return
        self.feedback_label.show_success("Наряд-допуск збережено.")
        self.saved.emit()

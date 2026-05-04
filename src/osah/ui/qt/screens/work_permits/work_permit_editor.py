from pathlib import Path

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QComboBox, QFormLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit, QVBoxLayout, QWidget

from osah.application.services.create_work_permit_record import create_work_permit_record
from osah.application.services.load_employee_work_readiness import load_employee_work_readiness
from osah.application.services.update_work_permit_record import update_work_permit_record
from osah.domain.entities.app_section import AppSection
from osah.domain.entities.employee import Employee
from osah.domain.entities.employee_readiness_level import EmployeeReadinessLevel
from osah.domain.entities.work_permit_participant import WorkPermitParticipant
from osah.domain.entities.work_permit_participant_role import WorkPermitParticipantRole
from osah.domain.entities.work_permit_target_training_status import WorkPermitTargetTrainingStatus
from osah.domain.entities.work_permit_workspace_row import WorkPermitWorkspaceRow
from osah.domain.services.format_ui_datetime import format_ui_datetime
from osah.domain.services.format_work_permit_participant_role_label import format_work_permit_participant_role_label
from osah.domain.services.format_work_permit_target_training_status_label import format_work_permit_target_training_status_label
from osah.domain.services.normalize_work_permit_target_training_status import normalize_work_permit_target_training_status
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
    """Форма створення і редагування наряду-допуску.
    Form for creating and editing a work permit.
    """

    saved = Signal()
    module_navigation_requested = Signal(AppSection, str)

    def __init__(self, database_path: Path, employees: tuple[Employee, ...]) -> None:
        super().__init__()
        self._database_path = database_path
        self._current_record_id: int | None = None
        self._active_employees = tuple(
            employee for employee in employees if employee.employment_status.strip().lower() == "active"
        )
        self._participants: tuple[WorkPermitParticipant, ...] = ()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING["md"])

        self._participants_summary_label = QLabel("Учасники: 0")
        self._participants_summary_label.setWordWrap(True)
        layout.addWidget(self._participants_summary_label)

        layout.addWidget(self._section_title("Дані наряду"))
        permit_form = QFormLayout()

        self.permit_number_input = QLineEdit()
        permit_form.addRow("Номер", self.permit_number_input)

        self.work_kind_input = QLineEdit()
        self.work_kind_input.setPlaceholderText(
            "Наприклад: вогневі, газонебезпечні, висотні, ремонтні, вантажопідіймальні."
        )
        permit_form.addRow(self._with_info("Вид робіт", WORK_PERMIT_KIND_HINT), self.work_kind_input)

        self.work_location_input = QLineEdit()
        permit_form.addRow("Місце", self.work_location_input)

        self.starts_at_input = QLineEdit()
        self.starts_at_input.setPlaceholderText("ДД.ММ.РРРР HH:MM")
        permit_form.addRow("Початок", self.starts_at_input)

        self.ends_at_input = QLineEdit()
        self.ends_at_input.setPlaceholderText("ДД.ММ.РРРР HH:MM")
        permit_form.addRow("Завершення", self.ends_at_input)

        self.responsible_input = QLineEdit()
        permit_form.addRow("Керівник робіт", self.responsible_input)

        self.issuer_input = QLineEdit()
        permit_form.addRow("Допускаючий", self.issuer_input)

        self.note_input = QTextEdit()
        self.note_input.setMaximumHeight(76)
        permit_form.addRow("Примітка", self.note_input)
        layout.addLayout(permit_form)

        layout.addWidget(self._section_title("Цільовий інструктаж"))
        target_form = QFormLayout()

        self.target_training_status_input = QComboBox()
        for status in (
            WorkPermitTargetTrainingStatus.LEGACY_NOT_TRACKED,
            WorkPermitTargetTrainingStatus.NOT_DONE,
            WorkPermitTargetTrainingStatus.DONE_PASSED,
            WorkPermitTargetTrainingStatus.DONE_FAILED,
        ):
            self.target_training_status_input.addItem(
                format_work_permit_target_training_status_label(status),
                status.value,
            )
        target_form.addRow(
            self._with_info("Стан цільового інструктажу", WORK_PERMIT_TARGET_TRAINING_HINT),
            self.target_training_status_input,
        )

        self.target_training_date_input = DateLineEdit()
        self.target_training_date_input.setPlaceholderText("ДД.ММ.РРРР")
        target_form.addRow("Дата інструктажу", self.target_training_date_input)

        self.target_training_conducted_by_input = QLineEdit()
        target_form.addRow("Хто провів", self.target_training_conducted_by_input)

        self.target_training_note_input = QTextEdit()
        self.target_training_note_input.setMaximumHeight(64)
        target_form.addRow("Коментар", self.target_training_note_input)
        layout.addLayout(target_form)

        layout.addWidget(self._section_title("Учасники та перевірка стану"))
        participant_form = QFormLayout()

        self.employee_input = QComboBox()
        self.employee_input.currentIndexChanged.connect(self._handle_current_participant_changed)
        participant_form.addRow("Поточний учасник", self.employee_input)

        self.role_input = QComboBox()
        for role in WorkPermitParticipantRole:
            self.role_input.addItem(format_work_permit_participant_role_label(role), role.value)
        participant_form.addRow("Роль", self.role_input)
        layout.addLayout(participant_form)

        self._readiness_title = self._with_info("Стан учасника", WORK_PERMIT_PARTICIPANT_READINESS_HINT)
        self._training_readiness_label = QLabel("Інструктажі: -")
        self._medical_readiness_label = QLabel("Медицина: -")
        self._ppe_readiness_label = QLabel("ЗІЗ: -")
        layout.addWidget(self._readiness_title)
        layout.addWidget(self._training_readiness_label)
        layout.addWidget(self._medical_readiness_label)
        layout.addWidget(self._ppe_readiness_label)

        readiness_actions = QHBoxLayout()
        self._open_training_button = QPushButton("Відкрити інструктажі")
        self._open_training_button.setProperty("variant", "secondary")
        self._open_training_button.clicked.connect(lambda: self._open_module(AppSection.TRAININGS))
        self._open_medical_button = QPushButton("Відкрити медицину")
        self._open_medical_button.setProperty("variant", "secondary")
        self._open_medical_button.clicked.connect(lambda: self._open_module(AppSection.MEDICAL))
        self._open_ppe_button = QPushButton("Відкрити ЗІЗ")
        self._open_ppe_button.setProperty("variant", "secondary")
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

        self.clear_form()

    def current_employee_personnel_number(self) -> str:
        """Повертає табельний номер поточного учасника.
        Returns the current participant personnel number.
        """

        return str(self.employee_input.currentData() or "").strip()

    def set_row(self, row: WorkPermitWorkspaceRow) -> None:
        """Заповнює форму значеннями вибраного наряду.
        Populates the form with the selected permit values.
        """

        self._current_record_id = row.record_id
        self._participants = row.record.participants
        self._set_participant_options(self._participants, row.employee_numbers[0] if row.employee_numbers else None)
        self._update_participants_summary()

        self.permit_number_input.setText(row.permit_number)
        self.work_kind_input.setText(row.work_kind)
        self.work_location_input.setText(row.work_location)
        self.starts_at_input.setText(format_ui_datetime(row.starts_at))
        self.ends_at_input.setText(format_ui_datetime(row.ends_at))
        self.responsible_input.setText(row.responsible_person)
        self.issuer_input.setText(row.issuer_person)
        self.note_input.setPlainText(row.record.note_text)

        normalized_status = normalize_work_permit_target_training_status(row.record.target_training_status)
        self.target_training_status_input.setCurrentIndex(
            max(0, self.target_training_status_input.findData(normalized_status.value))
        )
        self.target_training_date_input.setText(row.record.target_training_date)
        self.target_training_conducted_by_input.setText(row.record.target_training_conducted_by)
        self.target_training_note_input.setPlainText(row.record.target_training_note)
        self.basis_panel.set_values(row.record.basis_text, row.record.basis_note)
        self.save_button.setText("Зберегти зміни")
        self._sync_role_for_current_participant()
        self._refresh_readiness_panel()

    def clear_form(self) -> None:
        """Очищує форму та переводить редактор у режим нового наряду.
        Clears the form and switches the editor to new permit mode.
        """

        self._current_record_id = None
        self._participants = ()
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
        ):
            field.clear()
        self.note_input.clear()
        self.target_training_note_input.clear()
        self.basis_panel.clear()
        self.target_training_status_input.setCurrentIndex(0)
        self._set_participant_options(None, None)
        self._update_participants_summary()
        self.save_button.setText("Створити наряд")
        self._refresh_readiness_panel()

    def _section_title(self, text: str) -> QLabel:
        """Створює простий внутрішній заголовок блоку форми.
        Creates a simple internal section heading for the form.
        """

        title = QLabel(text)
        title.setStyleSheet("font-size: 14px; font-weight: 900;")
        return title

    def _with_info(self, text: str, tooltip_text: str) -> QWidget:
        """Повертає підпис поля з нормативною підказкою.
        Returns a field label with a normative tooltip.
        """

        container = QWidget()
        row = QHBoxLayout(container)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(0)
        row.addWidget(QLabel(text))
        row.addWidget(InfoTooltipIcon(tooltip_text))
        row.addStretch()
        return container

    def _set_participant_options(
        self,
        participants: tuple[WorkPermitParticipant, ...] | None,
        selected_personnel_number: str | None,
    ) -> None:
        """Налаштовує список поточних учасників для редагування або створення.
        Configures current participant choices for editing or creation.
        """

        self.employee_input.blockSignals(True)
        self.employee_input.clear()
        if participants:
            for participant in participants:
                self.employee_input.addItem(
                    f"{participant.employee_full_name} ({participant.employee_personnel_number})",
                    participant.employee_personnel_number,
                )
            target_personnel_number = selected_personnel_number or participants[0].employee_personnel_number
        else:
            for employee in self._active_employees:
                self.employee_input.addItem(f"{employee.full_name} ({employee.personnel_number})", employee.personnel_number)
            target_personnel_number = selected_personnel_number

        if target_personnel_number:
            self.employee_input.setCurrentIndex(max(0, self.employee_input.findData(target_personnel_number)))
        elif self.employee_input.count():
            self.employee_input.setCurrentIndex(0)
        self.employee_input.blockSignals(False)
        self._sync_role_for_current_participant()

    def _update_participants_summary(self) -> None:
        """Оновлює короткий текст із кількістю та переліком учасників.
        Updates the short text with participant count and names.
        """

        if self._participants:
            names = ", ".join(participant.employee_full_name for participant in self._participants)
            self._participants_summary_label.setText(f"Учасники: {len(self._participants)} — {names}")
            return
        current_text = self.employee_input.currentText().strip()
        if current_text:
            self._participants_summary_label.setText(f"Учасники: 1 — {current_text}")
            return
        self._participants_summary_label.setText("Учасники: 0")

    def _handle_current_participant_changed(self) -> None:
        """Синхронізує роль і стан після зміни поточного учасника.
        Synchronizes role and readiness after current participant change.
        """

        self._sync_role_for_current_participant()
        self._refresh_readiness_panel()
        if self._current_record_id is None:
            self._update_participants_summary()

    def _sync_role_for_current_participant(self) -> None:
        """Підтягує роль вибраного учасника у форму.
        Loads the selected participant role into the form.
        """

        personnel_number = self.current_employee_personnel_number()
        if not personnel_number or not self._participants:
            return
        for participant in self._participants:
            if participant.employee_personnel_number == personnel_number:
                self.role_input.setCurrentIndex(max(0, self.role_input.findData(participant.participant_role.value)))
                return

    def _effective_participants(self) -> tuple[WorkPermitParticipant, ...]:
        """Формує склад учасників, який потрібно зберегти.
        Builds the participant set that should be saved.
        """

        current_number = self.current_employee_personnel_number()
        current_role = WorkPermitParticipantRole(str(self.role_input.currentData() or WorkPermitParticipantRole.EXECUTOR.value))
        current_text = self.employee_input.currentText().strip()
        if self._participants:
            updated: list[WorkPermitParticipant] = []
            for participant in self._participants:
                if participant.employee_personnel_number == current_number:
                    updated.append(
                        WorkPermitParticipant(
                            employee_personnel_number=participant.employee_personnel_number,
                            employee_full_name=participant.employee_full_name,
                            participant_role=current_role,
                        )
                    )
                else:
                    updated.append(participant)
            return tuple(updated)

        if not current_number:
            return ()
        full_name = current_text.rsplit("(", 1)[0].strip() if "(" in current_text else current_text
        return (
            WorkPermitParticipant(
                employee_personnel_number=current_number,
                employee_full_name=full_name,
                participant_role=current_role,
            ),
        )

    def _refresh_readiness_panel(self) -> None:
        """Оновлює текстову панель стану для поточного учасника.
        Refreshes the textual readiness panel for the current participant.
        """

        personnel_number = self.current_employee_personnel_number()
        if not personnel_number:
            self._training_readiness_label.setText("Інструктажі: немає даних")
            self._medical_readiness_label.setText("Медицина: немає даних")
            self._ppe_readiness_label.setText("ЗІЗ: немає даних")
            return
        readiness = load_employee_work_readiness(self._database_path, personnel_number)
        self._training_readiness_label.setText(
            f"Інструктажі: {self._readiness_text(readiness.training_level)}. {readiness.training_message}"
        )
        self._medical_readiness_label.setText(
            f"Медицина: {self._readiness_text(readiness.medical_level)}. {readiness.medical_message}"
        )
        self._ppe_readiness_label.setText(f"ЗІЗ: {self._readiness_text(readiness.ppe_level)}. {readiness.ppe_message}")

    def _readiness_text(self, level: EmployeeReadinessLevel) -> str:
        """Повертає короткий текст рівня готовності для UI.
        Returns a short readiness level text for the UI.
        """

        mapping = {
            EmployeeReadinessLevel.NORMAL: "Норма",
            EmployeeReadinessLevel.WARNING: "Увага",
            EmployeeReadinessLevel.CRITICAL: "Критично",
            EmployeeReadinessLevel.UNKNOWN: "Немає даних",
        }
        return mapping[level]

    def _open_module(self, section: AppSection) -> None:
        """Відкриває пов'язаний модуль для поточного учасника.
        Opens a related module for the current participant.
        """

        personnel_number = self.current_employee_personnel_number()
        if personnel_number:
            self.module_navigation_requested.emit(section, personnel_number)

    def _save_record(self) -> None:
        """Створює або оновлює наряд-допуск через application services.
        Creates or updates a work permit through application services.
        """

        basis_text, basis_note = self.basis_panel.values()
        participants = self._effective_participants()
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
                    self.current_employee_personnel_number(),
                    str(self.role_input.currentData() or ""),
                    self.note_input.toPlainText(),
                    str(self.target_training_status_input.currentData() or ""),
                    self.target_training_date_input.text(),
                    self.target_training_conducted_by_input.text(),
                    self.target_training_note_input.toPlainText(),
                    basis_text,
                    basis_note,
                    participants=participants,
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
                    self.current_employee_personnel_number(),
                    str(self.role_input.currentData() or ""),
                    self.note_input.toPlainText(),
                    str(self.target_training_status_input.currentData() or ""),
                    self.target_training_date_input.text(),
                    self.target_training_conducted_by_input.text(),
                    self.target_training_note_input.toPlainText(),
                    basis_text,
                    basis_note,
                    participants=participants,
                )
        except ValueError as error:
            self.feedback_label.show_error(str(error))
            return
        self.feedback_label.show_success("Наряд-допуск збережено.")
        self.saved.emit()
